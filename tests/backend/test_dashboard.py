"""
Tests for dashboard API endpoints.
"""
import pytest


class TestDashboardEndpoints:
    """Test suite for dashboard-related endpoints."""

    def test_get_dashboard_summary(self, client):
        """Test getting dashboard summary."""
        response = client.get("/api/dashboard/summary")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

        # Check required fields
        required_fields = [
            "total_inventory_value",
            "low_stock_items",
            "pending_orders",
            "total_backlog_items",
            "total_orders_value"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_dashboard_summary_data_types(self, client):
        """Test that dashboard summary has correct data types."""
        response = client.get("/api/dashboard/summary")
        data = response.json()

        assert isinstance(data["total_inventory_value"], (int, float))
        assert isinstance(data["low_stock_items"], int)
        assert isinstance(data["pending_orders"], int)
        assert isinstance(data["total_backlog_items"], int)
        assert isinstance(data["total_orders_value"], (int, float))

    def test_dashboard_summary_non_negative_values(self, client):
        """Test that dashboard summary values are non-negative."""
        response = client.get("/api/dashboard/summary")
        data = response.json()

        assert data["total_inventory_value"] >= 0
        assert data["low_stock_items"] >= 0
        assert data["pending_orders"] >= 0
        assert data["total_backlog_items"] >= 0
        assert data["total_orders_value"] >= 0

    def test_dashboard_summary_with_warehouse_filter(self, client):
        """Test dashboard summary with warehouse filter."""
        response = client.get("/api/dashboard/summary?warehouse=San Francisco")
        assert response.status_code == 200

        data = response.json()
        assert "total_inventory_value" in data
        assert "total_orders_value" in data

    def test_dashboard_summary_with_category_filter(self, client):
        """Test dashboard summary with category filter."""
        response = client.get("/api/dashboard/summary?category=Sensors")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_dashboard_summary_with_status_filter(self, client):
        """Test dashboard summary with status filter."""
        response = client.get("/api/dashboard/summary?status=Processing")
        assert response.status_code == 200

        data = response.json()
        # Pending orders should reflect the filter
        assert "pending_orders" in data

    def test_dashboard_summary_with_month_filter(self, client):
        """Test dashboard summary with month filter."""
        response = client.get("/api/dashboard/summary?month=2025-01")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_dashboard_summary_with_multiple_filters(self, client):
        """Test dashboard summary with multiple filters."""
        response = client.get(
            "/api/dashboard/summary?warehouse=London&category=Sensors&status=Delivered&month=2025-01"
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        # All required fields should still be present
        assert "total_inventory_value" in data
        assert "total_orders_value" in data

    def test_dashboard_summary_with_all_filters(self, client):
        """Test that 'all' filter values work correctly."""
        response = client.get(
            "/api/dashboard/summary?warehouse=all&category=all&status=all&month=all"
        )
        assert response.status_code == 200

        # Should return same as no filters
        response_no_filter = client.get("/api/dashboard/summary")
        assert response.json() == response_no_filter.json()

    def test_dashboard_summary_power_supplies_filter(self, client):
        """Test dashboard summary with Power Supplies category filter."""
        response = client.get("/api/dashboard/summary?category=Power Supplies")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        # Should have inventory value for Power Supplies items
        assert data["total_inventory_value"] >= 0

    def test_dashboard_pending_orders_calculation(self, client):
        """Test that pending orders are calculated correctly."""
        # Get all orders
        orders_response = client.get("/api/orders")
        all_orders = orders_response.json()

        # Count processing and backordered orders
        pending_count = sum(
            1 for order in all_orders
            if order["status"].lower() in ["processing", "backordered"]
        )

        # Get dashboard summary
        dashboard_response = client.get("/api/dashboard/summary")
        dashboard_data = dashboard_response.json()

        assert dashboard_data["pending_orders"] == pending_count

    def test_dashboard_low_stock_items_calculation(self, client):
        """Test that low stock items are calculated correctly."""
        # Get all inventory
        inventory_response = client.get("/api/inventory")
        all_inventory = inventory_response.json()

        # Count items at or below reorder point
        low_stock_count = sum(
            1 for item in all_inventory
            if item["quantity_on_hand"] <= item["reorder_point"]
        )

        # Get dashboard summary
        dashboard_response = client.get("/api/dashboard/summary")
        dashboard_data = dashboard_response.json()

        assert dashboard_data["low_stock_items"] == low_stock_count

    def test_dashboard_inventory_value_calculation(self, client):
        """Test that total inventory value is calculated correctly."""
        # Get all inventory
        inventory_response = client.get("/api/inventory")
        all_inventory = inventory_response.json()

        # Calculate total value
        expected_value = sum(
            item["quantity_on_hand"] * item["unit_cost"]
            for item in all_inventory
        )

        # Get dashboard summary
        dashboard_response = client.get("/api/dashboard/summary")
        dashboard_data = dashboard_response.json()

        # Allow small floating point differences
        assert abs(dashboard_data["total_inventory_value"] - expected_value) < 0.01


KPI_FIELDS = [
    "inventory_turnover",
    "orders_fulfilled",
    "total_orders",
    "order_fill_rate",
    "avg_delivery_days",
    "avg_promised_lead_days",
]


def _days(start, end):
    from datetime import datetime
    return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 86400


class TestDashboardKpis:
    """Test suite for the KPI fields of /api/dashboard/summary.

    Each test recomputes a KPI from /api/orders and /api/inventory so the
    summary is checked against the raw data, not against hard-coded numbers.
    """

    def test_kpi_fields_present(self, client):
        """Test that the summary includes every KPI field."""
        data = client.get("/api/dashboard/summary").json()
        for field in KPI_FIELDS:
            assert field in data

    def test_orders_fulfilled_counts_delivered_orders(self, client):
        """Test that orders_fulfilled is the number of delivered orders, out of all orders."""
        orders = client.get("/api/orders").json()
        data = client.get("/api/dashboard/summary").json()

        assert data["total_orders"] == len(orders)
        assert data["orders_fulfilled"] == sum(1 for o in orders if o["status"] == "Delivered")

    def test_order_fill_rate_excludes_backordered(self, client):
        """Test that the fill rate is the share of orders that are not backordered."""
        orders = client.get("/api/orders").json()
        not_backordered = sum(1 for o in orders if o["status"] != "Backordered")
        data = client.get("/api/dashboard/summary").json()

        assert abs(data["order_fill_rate"] - not_backordered / len(orders) * 100) < 0.05

    def test_avg_delivery_days_calculation(self, client):
        """Test average delivery time and promised lead time over delivered orders."""
        orders = client.get("/api/orders").json()
        timed = [o for o in orders if o["status"] == "Delivered" and o.get("actual_delivery")]
        expected_delivery = sum(_days(o["order_date"], o["actual_delivery"]) for o in timed) / len(timed)
        expected_promised = sum(_days(o["order_date"], o["expected_delivery"]) for o in timed) / len(timed)

        data = client.get("/api/dashboard/summary").json()
        assert abs(data["avg_delivery_days"] - expected_delivery) < 0.05
        assert abs(data["avg_promised_lead_days"] - expected_promised) < 0.05

    def test_inventory_turnover_calculation(self, client):
        """Test turnover = annualized cost of shipped/delivered units / inventory value."""
        orders = client.get("/api/orders").json()
        inventory = client.get("/api/inventory").json()
        unit_cost = {item["sku"]: item["unit_cost"] for item in inventory}
        cogs = sum(
            line["quantity"] * unit_cost[line["sku"]]
            for o in orders if o["status"] in ("Delivered", "Shipped")
            for line in o["items"]
        )
        inventory_value = sum(i["quantity_on_hand"] * i["unit_cost"] for i in inventory)
        months = len({o["order_date"][:7] for o in orders})

        data = client.get("/api/dashboard/summary").json()
        assert abs(data["inventory_turnover"] - cogs * 12 / months / inventory_value) < 0.01

    def test_inventory_turnover_annualizes_single_month(self, client):
        """Test that a one-month view scales cost of goods sold by 12."""
        orders = client.get("/api/orders?month=2025-03").json()
        inventory = client.get("/api/inventory").json()
        unit_cost = {item["sku"]: item["unit_cost"] for item in inventory}
        cogs = sum(
            line["quantity"] * unit_cost[line["sku"]]
            for o in orders if o["status"] in ("Delivered", "Shipped")
            for line in o["items"]
        )
        inventory_value = sum(i["quantity_on_hand"] * i["unit_cost"] for i in inventory)

        data = client.get("/api/dashboard/summary?month=2025-03").json()
        assert abs(data["inventory_turnover"] - cogs * 12 / inventory_value) < 0.01

    def test_kpis_follow_filters(self, client):
        """Test that KPIs are computed from the filtered orders."""
        orders = client.get("/api/orders?warehouse=Tokyo&month=Q2-2025").json()
        data = client.get("/api/dashboard/summary?warehouse=Tokyo&month=Q2-2025").json()

        assert data["total_orders"] == len(orders)
        assert data["orders_fulfilled"] == sum(1 for o in orders if o["status"] == "Delivered")

    def test_kpis_empty_period_are_null(self, client):
        """Test that ratio KPIs are null, not 0, when no orders match."""
        data = client.get("/api/dashboard/summary?month=2030-01").json()

        assert data["total_orders"] == 0
        assert data["orders_fulfilled"] == 0
        assert data["order_fill_rate"] is None
        assert data["avg_delivery_days"] is None
        assert data["avg_promised_lead_days"] is None

    def test_backordered_filter_has_no_delivery_kpis(self, client):
        """Test that a backordered-only view has a 0% fill rate and no delivery times."""
        data = client.get("/api/dashboard/summary?status=backordered").json()

        assert data["total_orders"] > 0
        assert data["order_fill_rate"] == 0
        assert data["avg_delivery_days"] is None
