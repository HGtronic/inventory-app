# Restocking Tab: Implementation Plan

> **Status (2026-11-03): implemented.** All 10 steps are done. The backend suite passes (111 tests), and the browser checks in step 10 passed.
>
> Changes made after review:
> - Budgets are capped at `MAX_BUDGET` (1e9) and non-finite values are rejected, which prevents an overflow 500.
> - Forecast data is validated at startup.
> - Place Order requires the plan on screen to match the slider.
> - A failed restock-orders request no longer hides customer orders.

## Goal

Add a **Restocking** tab where the user:

1. Sets an available budget with a slider.
2. Sees which demand-forecast items to restock within that budget.
3. Clicks **Place Order** to submit the restocking order.
4. Finds the submitted order in the existing **Orders** tab, in a new **Submitted Orders** section that shows delivery lead time.

## Decisions

| Topic | Decision |
|---|---|
| Cost and stock data | Add `unit_cost`, `quantity_on_hand` and `lead_time_days` to each record in `server/data/demand_forecasts.json`, and to the `DemandForecast` model. |
| Allocation | Priority fill with a partial last line. Rank items by urgency, fully restock each in order, then buy as many units of the next item as the remaining budget allows. Stop there. |
| Lead time | Per item (`lead_time_days`). An order's lead time is its slowest line. Expected delivery is the order date plus that lead time. |
| Persistence | A backend in-memory list, separate from customer orders. It survives page reloads and is lost on server restart, like the rest of this mock-data app. Dashboard revenue is unaffected. |

Defaults chosen without asking (each one is easy to change):

- **On-order stock counts toward coverage.** Units on submitted restock orders are subtracted from the shortfall. Without this, placing an order leaves the recommendations unchanged and invites ordering the same items twice.
- **Recommendations are read-only in v1.** The user changes the budget and the list recalculates. Per-line editing is out of scope, but the POST payload already takes explicit lines, so editing can be added later without API changes.
- **Strict priority.** Allocation stops at the first item that can't be fully covered, even if a cheaper, lower-priority item would still fit in the leftover money.
- **The backend owns the algorithm.** That keeps it testable with the existing pytest setup and makes the server the only source of prices. The slider requests are debounced.
- **Global filters don't apply.** The FilterBar has no effect on Restocking (same as Demand) or on the Submitted Orders section, because restock orders have no warehouse or category.

## Key Facts From the Codebase

- `demand_forecasts.json` has 9 records with `item_sku`, `item_name`, `current_demand`, `forecasted_demand`, `trend` and `period`. They have no cost, stock or lead time.
- Only `PSU-501` of those 9 SKUs exists in `inventory.json`, which is why the fields go on the forecast records instead of being joined from inventory.
- `backlog_items.json` already records `quantity_available` for `FLT-405` (850), `MTR-304` (35), `VLV-506` (100) and `WDG-001` (275). The proposed on-hand values below reuse these so the two tabs agree.
- `server/generate_data.py` only rewrites `orders.json`, so the new forecast fields are safe from regeneration.
- `purchase_orders.json`, the `PurchaseOrder` model and `api.createPurchaseOrder()` are an unrelated, unfinished backlog feature: they have no backend route and no callers. Don't reuse them. A restock order has many lines, while a purchase order is tied to one backlog item.
- Money is stored in USD. The UI converts to JPY at display time through `formatCurrency(amount, currentCurrency)` in `client/src/utils/currency.js`.
- i18n: every UI string needs a key in both `client/src/locales/en.js` and `ja.js`, and `t()` fills `{placeholder}` params.

## Proposed Data

These values get added to `server/data/demand_forecasts.json`. Shortfall = `max(0, forecasted_demand - quantity_on_hand - quantity_on_order)`.

| SKU | Item | Trend | Forecast | On hand | Unit cost | Lead time | Shortfall | Full restock cost |
|---|---|---|---|---|---|---|---|---|
| WDG-001 | Industrial Widget Type A | increasing | 450 | 275 | 42.50 | 10 d | 175 | 7,437.50 |
| BRG-102 | Steel Bearing Assembly | stable | 152 | 140 | 28.75 | 7 d | 12 | 345.00 |
| GSK-203 | High-Temperature Gasket | increasing | 600 | 220 | 6.40 | 5 d | 380 | 2,432.00 |
| MTR-304 | Electric Motor 5HP | decreasing | 35 | 35 | 685.00 | 21 d | 0 | - |
| FLT-405 | Oil Filter Cartridge | increasing | 950 | 850 | 14.25 | 6 d | 100 | 1,425.00 |
| VLV-506 | Pressure Relief Valve | stable | 121 | 100 | 132.00 | 14 d | 21 | 2,772.00 |
| PSU-501 | 5V 10A Switching Power Supply | stable | 252 | 420 | 18.99 | 7 d | 0 | - |
| SNR-420 | Temperature Sensor Module | stable | 182 | 90 | 89.50 | 12 d | 92 | 8,234.00 |
| CTL-330 | Logic Controller Board | stable | 96 | 40 | 245.00 | 18 d | 56 | 13,720.00 |

Full restock cost is **$36,365.50**, so the slider maximum is **$36,500** (rounded up to the $500 step). `PSU-501` uses its real `inventory.json` cost and stock.

## Allocation Algorithm

1. **Candidates:** forecast items with shortfall > 0.
2. **Sort** by:
   1. Trend: `increasing`, then `stable`, then `decreasing`.
   2. Stock coverage, `(quantity_on_hand + quantity_on_order) / forecasted_demand`, lowest first.
   3. `item_sku`, so the order is deterministic.
3. **Walk the sorted list** with `remaining = budget`:
   - If `shortfall * unit_cost <= remaining`, take the full shortfall.
   - Otherwise, take `floor(remaining / unit_cost)` units if that's more than 0, mark the line `partial`, and **stop**.
4. Round money to 2 decimals. `lead_time_days` for the order = max over its lines.

With the data above, the order is GSK-203, WDG-001, FLT-405, CTL-330, SNR-420, VLV-506, BRG-102.

**Worked example (budget $15,000):** this doubles as a test case.

| Line | Qty | Line total | Lead time |
|---|---|---|---|
| GSK-203 | 380 | 2,432.00 | 5 d |
| WDG-001 | 175 | 7,437.50 | 10 d |
| FLT-405 | 100 | 1,425.00 | 6 d |
| CTL-330 (partial) | 15 | 3,675.00 | 18 d |

Allocated $14,969.50, remaining $30.50, order lead time 18 days, 4 items not fully covered.

## Implementation Steps

### 1. Backend data and model (`server/`)

- [ ] Add `unit_cost`, `quantity_on_hand` and `lead_time_days` to all 9 records in `server/data/demand_forecasts.json`, using the table above.
- [ ] Add the same three fields, required, to `DemandForecast` in `server/main.py`. This follows CLAUDE.md rule 3: update the Pydantic models whenever the JSON shape changes.

### 2. Recommendation endpoint (`server/main.py`)

- [ ] Add a module-level `restock_orders: list = []` for submitted orders.
- [ ] Add `quantity_on_order(sku)`, which sums the line quantities for that SKU across `restock_orders`.
- [ ] Add `get_restock_candidates()`, which returns the forecasts with on-order and shortfall computed, filtered to shortfall > 0 and sorted as described above.
- [ ] Add `allocate_budget(candidates, budget)`, which implements the walk. **Comment the ordering rule, the strict stop at the partial line, and the on-order subtraction** (CLAUDE.md asks for comments on non-obvious logic).
- [ ] Add models:
  - `RestockRecommendation`: `item_sku`, `item_name`, `trend`, `forecasted_demand`, `quantity_on_hand`, `quantity_on_order`, `shortfall`, `recommended_quantity`, `unit_cost`, `line_total`, `lead_time_days`, `partial`.
  - `RestockRecommendationResponse`: `budget`, `full_restock_cost`, `allocated`, `remaining`, `uncovered_count`, `items`.
- [ ] Add `GET /api/restocking/recommendations?budget=<float>`.
  - `budget` is optional with `ge=0`. When omitted, it defaults to `full_restock_cost`. The frontend uses that first call to learn the slider maximum.
  - `uncovered_count` = candidates not fully funded (partial lines included).

### 3. Restock order endpoints (`server/main.py`)

- [ ] Add models:
  - `RestockOrderLineRequest`: `item_sku`, `quantity` (`int`, `gt=0`).
  - `CreateRestockOrderRequest`: `budget` (`ge=0`), `items` (`min_length=1`).
  - `RestockOrderLine`: `item_sku`, `item_name`, `quantity`, `unit_cost`, `line_total`, `lead_time_days`.
  - `RestockOrder`: `id`, `order_number`, `status`, `order_date`, `items`, `total_cost`, `budget`, `lead_time_days`, `expected_delivery`.
- [ ] Add `POST /api/restocking/orders`, returning `201` and the created `RestockOrder`.
  - Price every line from server data. The request carries no prices, so the client can't set them.
  - Reject with `400`:
    - an unknown SKU
    - duplicate SKUs
    - a quantity above the item's current shortfall (this also blocks double submits)
    - a total above the budget
  - `order_number` = `RST-{year}-{NNNN}` (sequential), `status` = `"Submitted"`, `order_date` = now in ISO format.
  - `lead_time_days` = max over lines, and `expected_delivery` = `order_date + lead_time_days`.
- [ ] Add `GET /api/restocking/orders`, returning `List[RestockOrder]` with the newest first.

### 4. Backend tests (`tests/backend/`, use the **backend-api-test** skill)

- [ ] In `conftest.py`, add an autouse fixture that calls `main.restock_orders.clear()` before each test, so in-memory state doesn't leak between tests.
- [ ] In `test_misc_endpoints.py`, extend the demand structure test to assert the 3 new fields.
- [ ] New `test_restocking.py`:
  - [ ] No budget: `full_restock_cost == 36365.50`, all 7 candidates fully covered.
  - [ ] `budget=0`: no items, `uncovered_count == 7`.
  - [ ] `budget=15000`: matches the worked example (lines, partial flag, allocated, remaining).
  - [ ] Negative budget returns `422`.
  - [ ] Zero-shortfall SKUs (`MTR-304`, `PSU-501`) never appear.
  - [ ] A valid POST returns `201` with `lead_time_days == 18`, `expected_delivery == order_date + 18 days`, and server-side pricing. The order then appears in `GET /api/restocking/orders`.
  - [ ] After a POST, recommendations show `quantity_on_order` and a reduced shortfall for the ordered SKUs.
  - [ ] Each `400` case: unknown SKU, duplicate SKU, quantity above shortfall, total above budget.
  - [ ] Empty `items` returns `422`.
- [ ] Run `cd server && uv run pytest ../tests/backend -v`.

### 5. API client (`client/src/api.js`)

- [ ] `getRestockRecommendations(budget)`: omits the param when `budget` is `null`.
- [ ] `getRestockOrders()`
- [ ] `createRestockOrder({ budget, items })`

### 6. Restocking view (delegate to **vue-expert**, per CLAUDE.md)

- [ ] New `client/src/views/Restocking.vue`, using the Composition API and following `Orders.vue` / `Demand.vue` conventions (`page-header`, `stats-grid`, `card`, `table-container`, `badge`).
- [ ] On mount, call `getRestockRecommendations(null)` to get `full_restock_cost`. Set the slider max to that value rounded up to the $500 step, set the budget to half of it rounded down to the step (`Math.floor(max / 2 / 500) * 500`, so $18,000), then fetch recommendations.
- [ ] **Budget slider:** `<input type="range">`, `min=0`, `step=500`, `v-model.number="budget"`. Values are in USD. Labels use `formatCurrency(..., currentCurrency)` so JPY displays correctly. Show "Full restock cost" next to it.
- [ ] Watch `budget` and refetch after a 250 ms debounce. Ignore stale responses with a request counter, so a slow early response can't overwrite a newer one.
- [ ] **Stat cards:** Budget, Allocated, Remaining, Items Recommended.
- [ ] **Recommendations table** (`:key="item.item_sku"`) with columns SKU, Item, Trend badge, Forecast, On hand, On order, Shortfall, Order qty (with a "Partial" badge), Unit cost, Line total, Lead time. Below it, show "N items not covered by this budget" when `uncovered_count > 0`.
- [ ] **Empty states:** "All forecast items are fully stocked or already on order" (no candidates) and "Increase the budget to see recommendations" (budget too low for anything).
- [ ] **Place Order button:** disabled when there are no lines or a submission is in flight, with the label switching to "Placing order...". It POSTs `{ budget, items: [{ item_sku, quantity }] }`.
  - On success: show an inline confirmation (no `alert()`, no emojis) with the order number, lead time and a `router-link` to `/orders`, then refetch recommendations. They shrink because of on-order stock.
  - On a `400`: show the server's `detail` inline and refetch.
- [ ] `client/src/main.js`: add `{ path: '/restocking', component: Restocking }`.
- [ ] `client/src/App.vue`: add a nav `router-link` after Demand Forecast, using `t('nav.restocking')`.

### 7. Submitted Orders section (delegate to **vue-expert**)

- [ ] In `client/src/views/Orders.vue`, load `api.getRestockOrders()` alongside `api.getOrders(filters)` with `Promise.all`. Restock orders are not filtered, and the watcher may refetch them, which is harmless.
- [ ] Add a "Submitted Orders (N)" card **above** "All Orders". Its table (`:key="order.id"`) has columns Order #, Order date, Items (same `<details>` dropdown as the existing table, showing qty @ unit cost), Total cost, **Lead time** ("18 days"), Expected delivery, and Status (badge `info`, "Submitted").
- [ ] Empty state: "No submitted restock orders yet", with a link to `/restocking`.
- [ ] Leave the status stat cards and the "All Orders" count as customer orders only.

### 8. Translations (`client/src/locales/en.js` and `ja.js`)

| Key | EN | JA |
|---|---|---|
| `nav.restocking` | Restocking | 在庫補充 |
| `restocking.title` | Restocking | 在庫補充 |
| `restocking.description` | Set a budget and order what the demand forecast needs most | 予算を設定し、需要予測で優先度の高い品目を発注します |
| `restocking.budget` | Available Budget | 利用可能予算 |
| `restocking.fullRestockCost` | Full restock cost: {amount} | 全品目補充コスト: {amount} |
| `restocking.allocated` | Allocated | 割当額 |
| `restocking.remaining` | Remaining | 残額 |
| `restocking.itemsRecommended` | Items Recommended | 推奨品目数 |
| `restocking.recommendations` | Recommended Items | 推奨品目 |
| `restocking.notCovered` | {count} items not covered by this budget | この予算では{count}品目が対象外です |
| `restocking.partial` | Partial | 一部 |
| `restocking.placeOrder` | Place Order | 発注する |
| `restocking.placing` | Placing order... | 発注中... |
| `restocking.orderPlaced` | Order {orderNumber} submitted. Expected delivery in {days} days. | 発注 {orderNumber} を送信しました。{days}日後に納品予定です。 |
| `restocking.viewInOrders` | View in Orders | 注文一覧で表示 |
| `restocking.allStocked` | All forecast items are fully stocked or already on order. | すべての予測品目は在庫が十分か、発注済みです。 |
| `restocking.budgetTooLow` | Increase the budget to see recommendations. | 推奨品目を表示するには予算を増やしてください。 |
| `restocking.table.*` | SKU, Item, Trend, Forecast, On Hand, On Order, Shortfall, Order Qty, Unit Cost, Line Total, Lead Time | SKU, 品目, 傾向, 予測, 在庫数, 発注済み数, 不足数, 発注数, 単価, 小計, リードタイム |
| `orders.submittedOrders` | Submitted Orders | 発注済み補充注文 |
| `orders.noSubmittedOrders` | No submitted restock orders yet. | 発注済みの補充注文はまだありません。 |
| `orders.leadTimeDays` | {days} days | {days}日 |
| `orders.table.leadTime` | Lead Time | リードタイム |
| `orders.table.totalCost` | Total Cost | 合計金額 |
| `status.submitted` | Submitted | 発注済み |

`Orders.vue` renders status through `` t(`status.${status.toLowerCase()}`) ``, so `status.submitted` is required.

### 9. Docs

- [ ] `CLAUDE.md`, under API Endpoints: add `GET /api/restocking/recommendations` (`budget`), `GET /api/restocking/orders` and `POST /api/restocking/orders`.
- [ ] `CLAUDE.md` / `server/CLAUDE.md`: mention the three new demand forecast fields.

### 10. Verify

- [ ] Run the backend tests (step 4); all of them should pass.
- [ ] With Playwright MCP against `http://localhost:3000`:
  1. Open `/restocking`. The slider starts at $18,000 and the max is $36,500.
  2. Set the budget to $15,000 and check the table against the worked example.
  3. Click **Place Order** and check that the confirmation shows the `RST-` number and 18 days.
  4. Check that recommendations refresh: GSK-203, WDG-001 and FLT-405 are gone, and CTL-330 shows 15 on order.
  5. Open `/orders` and check that Submitted Orders lists the order with lead time "18 days" and the right expected delivery date.
  6. Switch to Japanese and check that labels translate and amounts show in yen.
  7. Check the browser console for errors.
- [ ] Run the **code-reviewer** agent over the diff.

## Out of Scope (v1)

- Editing or deselecting recommended lines.
- Cancelling, receiving or delivering restock orders. On-order quantities never turn into on-hand stock.
- Persistence across server restarts.
- Global filters (warehouse/category) on Restocking and Submitted Orders.
- Japanese product names for the forecast items. The Demand tab already shows them in English.

## Notes on the Current Checkout

- The API port is configurable and defaults to **8001**: the backend reads `API_PORT`, and the client reads `VITE_API_BASE_URL`. On this machine another service holds 8001, so the backend runs with `API_PORT=8002`, and a gitignored `client/.env` sets `VITE_API_BASE_URL=http://localhost:8002/api`. New code must go through `api.js` and must not hard-code URLs.
- Existing issues unrelated to this feature: `api.js` calls `/tasks` and `/purchase-orders`, and the backend has neither route.
