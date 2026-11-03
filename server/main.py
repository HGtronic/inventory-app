import itertools
import os
import threading
from datetime import date, datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from mock_data import inventory_items, orders, demand_forecasts, backlog_items, spending_summary, monthly_spending, category_spending, recent_transactions, purchase_orders

app = FastAPI(title="Factory Inventory Management System")

# Quarter mapping for date filtering
QUARTER_MAP = {
    'Q1-2025': ['2025-01', '2025-02', '2025-03'],
    'Q2-2025': ['2025-04', '2025-05', '2025-06'],
    'Q3-2025': ['2025-07', '2025-08', '2025-09'],
    'Q4-2025': ['2025-10', '2025-11', '2025-12']
}

def filter_by_month(items: list, month: Optional[str]) -> list:
    """Filter items by month/quarter based on order_date field"""
    if not month or month == 'all':
        return items

    if month.startswith('Q'):
        # Handle quarters
        if month in QUARTER_MAP:
            months = QUARTER_MAP[month]
            return [item for item in items if any(m in item.get('order_date', '') for m in months)]
    else:
        # Direct month match
        return [item for item in items if month in item.get('order_date', '')]

    return items

def apply_filters(items: list, warehouse: Optional[str] = None, category: Optional[str] = None,
                 status: Optional[str] = None) -> list:
    """Apply common filters to a list of items"""
    filtered = items

    if warehouse and warehouse != 'all':
        filtered = [item for item in filtered if item.get('warehouse') == warehouse]

    if category and category != 'all':
        filtered = [item for item in filtered if item.get('category', '').lower() == category.lower()]

    if status and status != 'all':
        filtered = [item for item in filtered if item.get('status', '').lower() == status.lower()]

    return filtered

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class InventoryItem(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_point: int
    unit_cost: float
    location: str
    last_updated: str

class Order(BaseModel):
    id: str
    order_number: str
    customer: str
    items: List[dict]
    status: str
    order_date: str
    expected_delivery: str
    total_value: float
    actual_delivery: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None

class DemandForecast(BaseModel):
    id: str
    item_sku: str
    item_name: str
    current_demand: int
    forecasted_demand: int
    trend: str
    period: str
    unit_cost: float = Field(gt=0)
    quantity_on_hand: int = Field(ge=0)
    lead_time_days: int = Field(ge=0)

class BacklogItem(BaseModel):
    id: str
    order_id: str
    item_sku: str
    item_name: str
    quantity_needed: int
    quantity_available: int
    days_delayed: int
    priority: str
    has_purchase_order: Optional[bool] = False

class PurchaseOrder(BaseModel):
    id: str
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: str
    created_date: str
    notes: Optional[str] = None

class CreatePurchaseOrderRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    backlog_item_id: str
    supplier_name: str = Field(min_length=1, max_length=200)
    quantity: int = Field(gt=0)
    unit_cost: float = Field(gt=0)
    expected_delivery_date: date
    notes: Optional[str] = Field(None, max_length=1000)

TaskPriority = Literal["high", "medium", "low"]

class Task(BaseModel):
    # The client's task objects (TasksModal, the mock tasks in useAuth) use
    # camelCase `dueDate`, so the field is aliased to keep that JSON contract.
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    priority: TaskPriority
    due_date: str = Field(alias="dueDate")
    status: Literal["pending", "completed"]

class CreateTaskRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    priority: TaskPriority = "medium"
    due_date: date = Field(alias="dueDate")

class RestockRecommendation(BaseModel):
    item_sku: str
    item_name: str
    trend: str
    forecasted_demand: int
    quantity_on_hand: int
    quantity_on_order: int
    shortfall: int
    recommended_quantity: int
    unit_cost: float
    line_total: float
    lead_time_days: int
    partial: bool

class RestockRecommendationResponse(BaseModel):
    budget: float
    full_restock_cost: float
    allocated: float
    remaining: float
    uncovered_count: int
    items: List[RestockRecommendation]

class RestockOrderLineRequest(BaseModel):
    item_sku: str
    quantity: int = Field(gt=0)

# Upper bound for any budget. Without it a huge or infinite float overflows
# when converted to cents and the request fails with a 500 instead of a 422.
MAX_BUDGET = 1_000_000_000

class CreateRestockOrderRequest(BaseModel):
    budget: float = Field(ge=0, le=MAX_BUDGET, allow_inf_nan=False)
    items: List[RestockOrderLineRequest] = Field(min_length=1)

class RestockOrderLine(BaseModel):
    item_sku: str
    item_name: str
    quantity: int
    unit_cost: float
    line_total: float
    lead_time_days: int

class RestockOrder(BaseModel):
    id: str
    order_number: str
    status: str
    order_date: str
    items: List[RestockOrderLine]
    total_cost: float
    budget: float
    lead_time_days: int
    expected_delivery: str

# Submitted restock orders. Held in memory like the rest of the mock data: they
# survive page reloads but reset when the server restarts. Kept apart from the
# customer `orders` list so restock spending never counts as dashboard revenue.
restock_orders: List[dict] = []
# Serializes order creation so two concurrent submits can't both pass the
# shortfall check and order the same units twice.
restock_orders_lock = threading.Lock()

# Validate forecast data at startup: allocate_budget divides by unit cost, so a
# zero or negative cost in demand_forecasts.json must stop the server here
# rather than surface later as a ZeroDivisionError on a request.
for _forecast in demand_forecasts:
    DemandForecast(**_forecast)

# Restock priority by demand trend: rising demand first, falling demand last.
TREND_PRIORITY = {"increasing": 0, "stable": 1, "decreasing": 2}

def to_cents(amount: float) -> int:
    """Convert dollars to integer cents so budget math has no float drift."""
    return round(amount * 100)

def quantity_on_order(sku: str) -> int:
    """Units of a SKU already on submitted restock orders."""
    return sum(
        line["quantity"]
        for order in restock_orders
        for line in order["items"]
        if line["item_sku"] == sku
    )

def get_restock_candidates() -> List[dict]:
    """Forecast items that still need stock, most urgent first.

    Shortfall subtracts units already on submitted restock orders, so after an
    order is placed those items shrink or drop out of the recommendations
    instead of being suggested (and bought) a second time.
    """
    candidates = []
    for forecast in demand_forecasts:
        on_order = quantity_on_order(forecast["item_sku"])
        covered = forecast["quantity_on_hand"] + on_order
        shortfall = max(0, forecast["forecasted_demand"] - covered)
        if shortfall == 0:
            continue
        candidates.append({
            **forecast,
            "quantity_on_order": on_order,
            "shortfall": shortfall,
            # Share of forecast demand already covered. Relative, so a gap of 50
            # motors and a gap of 500 gaskets compare fairly. forecasted_demand
            # is > 0 here because shortfall > 0.
            "coverage": covered / forecast["forecasted_demand"],
        })

    # Urgency: trend first, then lowest coverage, then SKU for a stable order.
    candidates.sort(key=lambda c: (
        TREND_PRIORITY.get(c["trend"], len(TREND_PRIORITY)),
        c["coverage"],
        c["item_sku"],
    ))
    return candidates

def allocate_budget(candidates: List[dict], budget_cents: int) -> List[dict]:
    """Priority fill: fully restock each candidate in order while money lasts.

    The first candidate that doesn't fully fit gets as many whole units as the
    remaining budget buys (flagged `partial`), and allocation stops there, even
    if a cheaper, lower-priority item would still fit. Strict priority keeps
    the most urgent item first in line for any extra budget.
    """
    remaining = budget_cents
    lines = []
    for candidate in candidates:
        unit_cents = to_cents(candidate["unit_cost"])
        full_cost = candidate["shortfall"] * unit_cents
        if full_cost <= remaining:
            quantity, partial = candidate["shortfall"], False
        else:
            quantity, partial = remaining // unit_cents, True

        if quantity > 0:
            line_cents = quantity * unit_cents
            remaining -= line_cents
            lines.append({
                "item_sku": candidate["item_sku"],
                "item_name": candidate["item_name"],
                "trend": candidate["trend"],
                "forecasted_demand": candidate["forecasted_demand"],
                "quantity_on_hand": candidate["quantity_on_hand"],
                "quantity_on_order": candidate["quantity_on_order"],
                "shortfall": candidate["shortfall"],
                "recommended_quantity": quantity,
                "unit_cost": candidate["unit_cost"],
                "line_total": line_cents / 100,
                "lead_time_days": candidate["lead_time_days"],
                "partial": partial,
            })

        if partial:
            break
    return lines

# API endpoints
@app.get("/")
def root():
    return {"message": "Factory Inventory Management System API", "version": "1.0.0"}

@app.get("/api/inventory", response_model=List[InventoryItem])
def get_inventory(
    warehouse: Optional[str] = None,
    category: Optional[str] = None
):
    """Get all inventory items with optional filtering"""
    return apply_filters(inventory_items, warehouse, category)

@app.get("/api/inventory/{item_id}", response_model=InventoryItem)
def get_inventory_item(item_id: str):
    """Get a specific inventory item"""
    item = next((item for item in inventory_items if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/api/orders", response_model=List[Order])
def get_orders(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get all orders with optional filtering"""
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)
    return filtered_orders

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    """Get a specific order"""
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/demand", response_model=List[DemandForecast])
def get_demand_forecasts():
    """Get demand forecasts"""
    return demand_forecasts

@app.get("/api/backlog", response_model=List[BacklogItem])
def get_backlog():
    """Get backlog items with purchase order status"""
    # Add has_purchase_order flag to each backlog item
    result = []
    for item in backlog_items:
        item_dict = dict(item)
        # Check if this backlog item has a purchase order
        has_po = any(po["backlog_item_id"] == item["id"] for po in purchase_orders)
        item_dict["has_purchase_order"] = has_po
        result.append(item_dict)
    return result

@app.get("/api/restocking/recommendations", response_model=RestockRecommendationResponse)
def get_restock_recommendations(
    budget: Optional[float] = Query(None, ge=0, le=MAX_BUDGET, allow_inf_nan=False)
):
    """Recommend forecast items to restock within a budget.

    Without `budget`, the budget defaults to the full restock cost, which tells
    the client the most that can usefully be spent (the slider maximum).
    """
    candidates = get_restock_candidates()
    full_cost_cents = sum(c["shortfall"] * to_cents(c["unit_cost"]) for c in candidates)
    budget_cents = full_cost_cents if budget is None else to_cents(budget)

    lines = allocate_budget(candidates, budget_cents)
    allocated_cents = sum(to_cents(line["line_total"]) for line in lines)
    fully_covered = sum(1 for line in lines if not line["partial"])

    return {
        "budget": budget_cents / 100,
        "full_restock_cost": full_cost_cents / 100,
        "allocated": allocated_cents / 100,
        "remaining": (budget_cents - allocated_cents) / 100,
        # Candidates not fully funded, including a partially funded last line.
        "uncovered_count": len(candidates) - fully_covered,
        "items": lines,
    }

@app.get("/api/restocking/orders", response_model=List[RestockOrder])
def get_restock_orders():
    """Get submitted restock orders, newest first."""
    return list(reversed(restock_orders))

@app.post("/api/restocking/orders", response_model=RestockOrder, status_code=201)
def create_restock_order(request: CreateRestockOrderRequest):
    """Submit a restock order.

    Prices come from server data, never from the client. Each line may order at
    most the item's current shortfall, which also blocks resubmitting an order
    that has already been placed.
    """
    with restock_orders_lock:
        forecasts_by_sku = {f["item_sku"]: f for f in demand_forecasts}
        shortfall_by_sku = {c["item_sku"]: c["shortfall"] for c in get_restock_candidates()}

        seen_skus = set()
        lines = []
        for requested in request.items:
            sku = requested.item_sku
            if sku in seen_skus:
                raise HTTPException(status_code=400, detail=f"Duplicate item {sku} in order")
            seen_skus.add(sku)

            forecast = forecasts_by_sku.get(sku)
            if not forecast:
                raise HTTPException(status_code=400, detail=f"Unknown item {sku}")

            shortfall = shortfall_by_sku.get(sku, 0)
            if requested.quantity > shortfall:
                raise HTTPException(
                    status_code=400,
                    detail=f"Quantity {requested.quantity} for {sku} exceeds its remaining shortfall of {shortfall}",
                )

            line_cents = requested.quantity * to_cents(forecast["unit_cost"])
            lines.append({
                "item_sku": sku,
                "item_name": forecast["item_name"],
                "quantity": requested.quantity,
                "unit_cost": forecast["unit_cost"],
                "line_total": line_cents / 100,
                "lead_time_days": forecast["lead_time_days"],
            })

        total_cents = sum(to_cents(line["line_total"]) for line in lines)
        budget_cents = to_cents(request.budget)
        if total_cents > budget_cents:
            raise HTTPException(
                status_code=400,
                detail=f"Order total {total_cents / 100:.2f} exceeds budget {budget_cents / 100:.2f}",
            )

        order_date = datetime.now().replace(microsecond=0)
        # An order arrives complete, so it waits for its slowest line.
        lead_time_days = max(line["lead_time_days"] for line in lines)
        sequence = len(restock_orders) + 1
        order = {
            "id": str(sequence),
            "order_number": f"RST-{order_date.year}-{sequence:04d}",
            "status": "Submitted",
            "order_date": order_date.isoformat(),
            "items": lines,
            "total_cost": total_cents / 100,
            "budget": budget_cents / 100,
            "lead_time_days": lead_time_days,
            "expected_delivery": (order_date + timedelta(days=lead_time_days)).isoformat(),
        }
        restock_orders.append(order)
        return order

def months_in_period(month: Optional[str]) -> int:
    """Number of calendar months a `month` filter value covers.

    No filter (or one filter_by_month ignores) means the whole dataset, whose
    length is the number of distinct order months in it.
    """
    if month and month != 'all':
        if month in QUARTER_MAP:
            return len(QUARTER_MAP[month])
        if not month.startswith('Q'):
            return 1
    return len({order["order_date"][:7] for order in orders if order.get("order_date")}) or 1

def days_between(start: str, end: str) -> float:
    return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 86400

def compute_kpis(filtered_orders: list, filtered_inventory: list, month: Optional[str]) -> dict:
    """Dashboard KPIs, computed from the same filtered data as the rest of the summary.

    Each value is None when its input set is empty, so the client can show "-"
    instead of a misleading 0.
    """
    total_orders = len(filtered_orders)
    delivered = [o for o in filtered_orders if o["status"] == "Delivered"]
    backordered = sum(1 for o in filtered_orders if o["status"] == "Backordered")

    # Inventory turnover = annualized cost of goods sold / inventory value. Only
    # shipped or delivered orders count as sold. Costs come from the full
    # inventory (a SKU's cost doesn't depend on the filters). The data has only a
    # current stock snapshot, so that stands in for average inventory. A one-month
    # view is scaled x12 and a quarter x4, so the result stays comparable to an
    # annual turnover goal.
    unit_cost_by_sku = {item["sku"]: item["unit_cost"] for item in inventory_items}
    cogs = sum(
        line["quantity"] * unit_cost_by_sku.get(line["sku"], 0)
        for o in filtered_orders if o["status"] in ("Delivered", "Shipped")
        for line in o.get("items", [])
    )
    inventory_value = sum(i["quantity_on_hand"] * i["unit_cost"] for i in filtered_inventory)
    annualized_cogs = cogs * 12 / months_in_period(month)
    inventory_turnover = round(annualized_cogs / inventory_value, 2) if inventory_value > 0 else None

    # Order fill rate = share of orders that could be filled from stock, i.e. not backordered.
    order_fill_rate = round((total_orders - backordered) / total_orders * 100, 1) if total_orders else None

    # The data has no ship date, so delivery time (order -> actual delivery) is
    # measured instead of processing time. Its goal is the lead time promised for
    # those same orders (order -> expected delivery), so both cover the same orders.
    timed = [o for o in delivered if o.get("actual_delivery") and o.get("expected_delivery")]
    avg_delivery_days = (
        round(sum(days_between(o["order_date"], o["actual_delivery"]) for o in timed) / len(timed), 1) if timed else None
    )
    avg_promised_lead_days = (
        round(sum(days_between(o["order_date"], o["expected_delivery"]) for o in timed) / len(timed), 1) if timed else None
    )

    return {
        "inventory_turnover": inventory_turnover,
        "orders_fulfilled": len(delivered),
        "total_orders": total_orders,
        "order_fill_rate": order_fill_rate,
        "avg_delivery_days": avg_delivery_days,
        "avg_promised_lead_days": avg_promised_lead_days,
    }

@app.get("/api/dashboard/summary")
def get_dashboard_summary(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get summary statistics for dashboard with optional filtering"""
    # Filter inventory
    filtered_inventory = apply_filters(inventory_items, warehouse, category)

    # Filter orders
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    total_inventory_value = sum(item["quantity_on_hand"] * item["unit_cost"] for item in filtered_inventory)
    low_stock_items = len([item for item in filtered_inventory if item["quantity_on_hand"] <= item["reorder_point"]])
    pending_orders = len([order for order in filtered_orders if order["status"] in ["Processing", "Backordered"]])
    total_backlog_items = len(backlog_items)

    return {
        "total_inventory_value": round(total_inventory_value, 2),
        "low_stock_items": low_stock_items,
        "pending_orders": pending_orders,
        "total_backlog_items": total_backlog_items,
        "total_orders_value": sum(order["total_value"] for order in filtered_orders),
        **compute_kpis(filtered_orders, filtered_inventory, month),
    }

@app.get("/api/spending/summary")
def get_spending_summary():
    """Get spending summary statistics"""
    return spending_summary

@app.get("/api/spending/monthly")
def get_monthly_spending():
    """Get monthly spending breakdown"""
    return monthly_spending

@app.get("/api/spending/categories")
def get_category_spending():
    """Get spending by category"""
    return category_spending

@app.get("/api/spending/transactions")
def get_recent_transactions():
    """Get recent transactions"""
    return recent_transactions

@app.get("/api/reports/quarterly")
def get_quarterly_reports():
    """Get quarterly performance reports"""
    # Calculate quarterly statistics from orders
    quarters = {}

    for order in orders:
        order_date = order.get('order_date', '')
        # Determine quarter
        if '2025-01' in order_date or '2025-02' in order_date or '2025-03' in order_date:
            quarter = 'Q1-2025'
        elif '2025-04' in order_date or '2025-05' in order_date or '2025-06' in order_date:
            quarter = 'Q2-2025'
        elif '2025-07' in order_date or '2025-08' in order_date or '2025-09' in order_date:
            quarter = 'Q3-2025'
        elif '2025-10' in order_date or '2025-11' in order_date or '2025-12' in order_date:
            quarter = 'Q4-2025'
        else:
            continue

        if quarter not in quarters:
            quarters[quarter] = {
                'quarter': quarter,
                'total_orders': 0,
                'total_revenue': 0,
                'delivered_orders': 0,
                'avg_order_value': 0
            }

        quarters[quarter]['total_orders'] += 1
        quarters[quarter]['total_revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            quarters[quarter]['delivered_orders'] += 1

    # Calculate averages and fulfillment rate
    result = []
    for q, data in quarters.items():
        if data['total_orders'] > 0:
            data['avg_order_value'] = round(data['total_revenue'] / data['total_orders'], 2)
            data['fulfillment_rate'] = round((data['delivered_orders'] / data['total_orders']) * 100, 1)
        result.append(data)

    # Sort by quarter
    result.sort(key=lambda x: x['quarter'])
    return result

@app.get("/api/reports/monthly-trends")
def get_monthly_trends():
    """Get month-over-month trends"""
    months = {}

    for order in orders:
        order_date = order.get('order_date', '')
        if not order_date:
            continue

        # Extract month (format: YYYY-MM-DD)
        month = order_date[:7]  # Gets YYYY-MM

        if month not in months:
            months[month] = {
                'month': month,
                'order_count': 0,
                'revenue': 0,
                'delivered_count': 0
            }

        months[month]['order_count'] += 1
        months[month]['revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            months[month]['delivered_count'] += 1

    # Convert to list and sort
    result = list(months.values())
    result.sort(key=lambda x: x['month'])
    return result

# Purchase orders for backlog items. `purchase_orders` is the list loaded from
# purchase_orders.json; new orders are appended in memory (reset on restart),
# which also flips `has_purchase_order` on /api/backlog.
purchase_orders_lock = threading.Lock()

@app.post("/api/purchase-orders", response_model=PurchaseOrder, status_code=201)
def create_purchase_order(request: CreatePurchaseOrderRequest):
    """Create a purchase order for a backlog item (at most one per item)."""
    # The lock covers the duplicate check and the append, so two concurrent
    # submits for the same backlog item can't both create an order.
    with purchase_orders_lock:
        if not any(item["id"] == request.backlog_item_id for item in backlog_items):
            raise HTTPException(status_code=404, detail=f"Backlog item {request.backlog_item_id} not found")

        if any(po["backlog_item_id"] == request.backlog_item_id for po in purchase_orders):
            raise HTTPException(
                status_code=409,
                detail=f"Backlog item {request.backlog_item_id} already has a purchase order",
            )

        purchase_order = {
            "id": f"PO-{len(purchase_orders) + 1:04d}",
            "backlog_item_id": request.backlog_item_id,
            "supplier_name": request.supplier_name,
            "quantity": request.quantity,
            "unit_cost": request.unit_cost,
            "expected_delivery_date": request.expected_delivery_date.isoformat(),
            "status": "Pending",
            "created_date": datetime.now().replace(microsecond=0).isoformat(),
            "notes": request.notes or None,
        }
        purchase_orders.append(purchase_order)
        return purchase_order

@app.get("/api/purchase-orders/{backlog_item_id}", response_model=PurchaseOrder)
def get_purchase_order_by_backlog_item(backlog_item_id: str):
    """Get the purchase order for a backlog item.

    Keyed by backlog item ID, not PO ID: the dashboard's "View PO" button only
    knows the backlog item, and each item has at most one purchase order.
    """
    purchase_order = next((po for po in purchase_orders if po["backlog_item_id"] == backlog_item_id), None)
    if not purchase_order:
        raise HTTPException(status_code=404, detail=f"Purchase order for backlog item {backlog_item_id} not found")
    return purchase_order

# Tasks created from the profile menu's task list, held in memory like the rest
# of the mock data. The client also shows built-in mock tasks from useAuth.js;
# those never reach the server.
tasks: List[dict] = []
tasks_lock = threading.Lock()
# IDs come from a counter rather than len(tasks) so a delete can't cause the
# next task to reuse an ID. They are strings ("task-1") so they never equal the
# client's numeric mock-task IDs, which App.vue uses to tell the two apart.
task_ids = itertools.count(1)

def find_task(task_id: str) -> dict:
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.get("/api/tasks", response_model=List[Task])
def get_tasks():
    """Get tasks, newest first."""
    return list(reversed(tasks))

@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(request: CreateTaskRequest):
    """Create a pending task."""
    with tasks_lock:
        task = {
            "id": f"task-{next(task_ids)}",
            "title": request.title,
            "priority": request.priority,
            "dueDate": request.due_date.isoformat(),
            "status": "pending",
        }
        tasks.append(task)
        return task

@app.patch("/api/tasks/{task_id}", response_model=Task)
def toggle_task(task_id: str):
    """Toggle a task between pending and completed.

    Takes no body: the client's checkbox only ever flips the status.
    """
    with tasks_lock:
        task = find_task(task_id)
        task["status"] = "completed" if task["status"] == "pending" else "pending"
        return task

@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    """Delete a task."""
    with tasks_lock:
        tasks.remove(find_task(task_id))

if __name__ == "__main__":
    import uvicorn
    # 8001 is the documented port. Set API_PORT to use another one (for example
    # when 8001 is taken locally), and point the client at it with
    # VITE_API_BASE_URL (see .env.example).
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("API_PORT", "8001")))
