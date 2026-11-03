"""
Tests for restocking API endpoints (budget recommendations and restock orders).
"""
from datetime import datetime, timedelta

import pytest

import main

RECOMMENDATIONS_URL = "/api/restocking/recommendations"
ORDERS_URL = "/api/restocking/orders"

# Expected values follow docs/restocking-tab-plan.md and server/data/demand_forecasts.json.
FULL_RESTOCK_COST = 36365.50
PRIORITY_ORDER = ["GSK-203", "WDG-001", "FLT-405", "CTL-330", "SNR-420", "VLV-506", "BRG-102"]
FULLY_STOCKED_SKUS = {"MTR-304", "PSU-501"}


@pytest.fixture
def worked_example_order():
    """The lines the $15,000 worked example recommends."""
    return {
        "budget": 15000,
        "items": [
            {"item_sku": "GSK-203", "quantity": 380},
            {"item_sku": "WDG-001", "quantity": 175},
            {"item_sku": "FLT-405", "quantity": 100},
            {"item_sku": "CTL-330", "quantity": 15},
        ],
    }


class TestRestockRecommendations:
    """Test suite for GET /api/restocking/recommendations."""

    def test_get_recommendations_without_budget(self, client):
        """Test that omitting the budget funds the full restock."""
        response = client.get(RECOMMENDATIONS_URL)
        assert response.status_code == 200

        data = response.json()
        assert abs(data["full_restock_cost"] - FULL_RESTOCK_COST) < 0.01
        assert abs(data["budget"] - FULL_RESTOCK_COST) < 0.01
        assert abs(data["allocated"] - FULL_RESTOCK_COST) < 0.01
        assert abs(data["remaining"]) < 0.01
        assert data["uncovered_count"] == 0
        assert [item["item_sku"] for item in data["items"]] == PRIORITY_ORDER
        assert all(not item["partial"] for item in data["items"])

    def test_recommendation_structure(self, client):
        """Test that each recommendation has the documented fields and types."""
        response = client.get(RECOMMENDATIONS_URL)
        data = response.json()

        for key in ["budget", "full_restock_cost", "allocated", "remaining", "uncovered_count", "items"]:
            assert key in data

        for item in data["items"]:
            assert isinstance(item["item_sku"], str)
            assert isinstance(item["item_name"], str)
            assert item["trend"] in ["increasing", "stable", "decreasing"]
            assert isinstance(item["recommended_quantity"], int)
            assert isinstance(item["shortfall"], int)
            assert isinstance(item["quantity_on_order"], int)
            assert isinstance(item["lead_time_days"], int)
            assert isinstance(item["partial"], bool)
            assert 0 < item["recommended_quantity"] <= item["shortfall"]
            assert abs(item["line_total"] - item["recommended_quantity"] * item["unit_cost"]) < 0.01

    def test_shortfall_calculation(self, client):
        """Test that shortfall is forecast minus stock on hand and on order."""
        response = client.get(RECOMMENDATIONS_URL)
        for item in response.json()["items"]:
            expected = item["forecasted_demand"] - item["quantity_on_hand"] - item["quantity_on_order"]
            assert item["shortfall"] == expected

    def test_fully_stocked_items_excluded(self, client):
        """Test that items with no shortfall are never recommended."""
        response = client.get(RECOMMENDATIONS_URL)
        skus = {item["item_sku"] for item in response.json()["items"]}
        assert skus.isdisjoint(FULLY_STOCKED_SKUS)

    def test_zero_budget(self, client):
        """Test that a zero budget recommends nothing."""
        response = client.get(f"{RECOMMENDATIONS_URL}?budget=0")
        assert response.status_code == 200

        data = response.json()
        assert data["items"] == []
        assert data["allocated"] == 0
        assert data["remaining"] == 0
        assert data["uncovered_count"] == len(PRIORITY_ORDER)

    def test_worked_example_budget(self, client):
        """Test the $15,000 worked example: three full lines plus a partial line."""
        response = client.get(f"{RECOMMENDATIONS_URL}?budget=15000")
        assert response.status_code == 200

        data = response.json()
        lines = [
            (item["item_sku"], item["recommended_quantity"], item["line_total"], item["partial"])
            for item in data["items"]
        ]
        assert lines == [
            ("GSK-203", 380, 2432.0, False),
            ("WDG-001", 175, 7437.5, False),
            ("FLT-405", 100, 1425.0, False),
            ("CTL-330", 15, 3675.0, True),
        ]
        assert abs(data["allocated"] - 14969.50) < 0.01
        assert abs(data["remaining"] - 30.50) < 0.01
        assert data["uncovered_count"] == 4

    def test_allocation_stops_at_partial_line(self, client):
        """Test strict priority: nothing is bought after a line that can't be fully funded."""
        # $2,500 fully covers GSK-203 ($2,432) and leaves $68, which buys
        # 1 unit of WDG-001 ($42.50). The cheaper FLT-405 ($14.25) is still skipped.
        response = client.get(f"{RECOMMENDATIONS_URL}?budget=2500")
        data = response.json()

        lines = [(item["item_sku"], item["recommended_quantity"], item["partial"]) for item in data["items"]]
        assert lines == [("GSK-203", 380, False), ("WDG-001", 1, True)]
        assert abs(data["remaining"] - 25.50) < 0.01

    def test_partial_line_skipped_when_no_unit_fits(self, client):
        """Test that a budget too small for one unit of the next item adds no line."""
        # GSK-203 costs exactly $2,432; $5 more can't buy a $42.50 widget.
        response = client.get(f"{RECOMMENDATIONS_URL}?budget=2437")
        data = response.json()

        assert [item["item_sku"] for item in data["items"]] == ["GSK-203"]
        assert data["uncovered_count"] == len(PRIORITY_ORDER) - 1

    def test_budget_above_full_cost(self, client):
        """Test that extra budget beyond the full restock cost stays unallocated."""
        response = client.get(f"{RECOMMENDATIONS_URL}?budget=50000")
        data = response.json()

        assert abs(data["allocated"] - FULL_RESTOCK_COST) < 0.01
        assert abs(data["remaining"] - (50000 - FULL_RESTOCK_COST)) < 0.01
        assert data["uncovered_count"] == 0

    def test_negative_budget_rejected(self, client):
        """Test that a negative budget fails validation."""
        response = client.get(f"{RECOMMENDATIONS_URL}?budget=-1")
        assert response.status_code == 422

    def test_non_numeric_budget_rejected(self, client):
        """Test that a non-numeric budget fails validation."""
        response = client.get(f"{RECOMMENDATIONS_URL}?budget=lots")
        assert response.status_code == 422

    @pytest.mark.parametrize("budget", ["inf", "Infinity", "1e999", "1e12"])
    def test_unbounded_budget_rejected(self, client, budget):
        """Test that infinite or absurdly large budgets fail validation instead of overflowing."""
        response = client.get(f"{RECOMMENDATIONS_URL}?budget={budget}")
        assert response.status_code == 422

    def test_decreasing_trend_ranked_last(self, client, monkeypatch):
        """Test that trend outranks coverage: decreasing demand is restocked last."""
        base = {"current_demand": 100, "period": "Next 30 days", "unit_cost": 1.0, "lead_time_days": 5}
        monkeypatch.setattr(main, "demand_forecasts", [
            # Lowest coverage, but falling demand.
            {**base, "id": "1", "item_sku": "DEC-1", "item_name": "Falling", "trend": "decreasing",
             "forecasted_demand": 100, "quantity_on_hand": 0},
            {**base, "id": "2", "item_sku": "STB-1", "item_name": "Flat", "trend": "stable",
             "forecasted_demand": 100, "quantity_on_hand": 50},
            # Highest coverage, but rising demand.
            {**base, "id": "3", "item_sku": "INC-1", "item_name": "Rising", "trend": "increasing",
             "forecasted_demand": 100, "quantity_on_hand": 90},
        ])

        response = client.get(RECOMMENDATIONS_URL)
        assert [item["item_sku"] for item in response.json()["items"]] == ["INC-1", "STB-1", "DEC-1"]


class TestRestockOrders:
    """Test suite for /api/restocking/orders."""

    def test_get_orders_empty(self, client):
        """Test that no restock orders exist before any are placed."""
        response = client.get(ORDERS_URL)
        assert response.status_code == 200
        assert response.json() == []

    def test_create_order(self, client, worked_example_order):
        """Test placing the worked example order."""
        response = client.post(ORDERS_URL, json=worked_example_order)
        assert response.status_code == 201

        order = response.json()
        assert order["id"] == "1"
        assert order["order_number"].startswith("RST-")
        assert order["order_number"].endswith("-0001")
        assert order["status"] == "Submitted"
        assert abs(order["total_cost"] - 14969.50) < 0.01
        assert order["budget"] == 15000
        assert [line["item_sku"] for line in order["items"]] == ["GSK-203", "WDG-001", "FLT-405", "CTL-330"]

    def test_order_lead_time_is_slowest_line(self, client, worked_example_order):
        """Test that the order lead time is the max line lead time and sets delivery date."""
        response = client.post(ORDERS_URL, json=worked_example_order)
        order = response.json()

        assert order["lead_time_days"] == max(line["lead_time_days"] for line in order["items"]) == 18

        order_date = datetime.fromisoformat(order["order_date"])
        expected_delivery = datetime.fromisoformat(order["expected_delivery"])
        assert expected_delivery - order_date == timedelta(days=18)

    def test_order_prices_come_from_server(self, client):
        """Test that line prices come from server data, ignoring any client price."""
        payload = {
            "budget": 1000,
            "items": [{"item_sku": "GSK-203", "quantity": 10, "unit_cost": 0.01}],
        }
        response = client.post(ORDERS_URL, json=payload)
        assert response.status_code == 201

        line = response.json()["items"][0]
        assert line["unit_cost"] == 6.40
        assert abs(line["line_total"] - 64.00) < 0.01

    def test_created_order_listed(self, client, worked_example_order):
        """Test that a placed order appears in the list, newest first."""
        client.post(ORDERS_URL, json=worked_example_order)
        client.post(ORDERS_URL, json={"budget": 500, "items": [{"item_sku": "BRG-102", "quantity": 12}]})

        response = client.get(ORDERS_URL)
        orders = response.json()
        assert [order["id"] for order in orders] == ["2", "1"]

    def test_order_reduces_recommendations(self, client, worked_example_order):
        """Test that ordered units count as on order and shrink later recommendations."""
        client.post(ORDERS_URL, json=worked_example_order)

        response = client.get(RECOMMENDATIONS_URL)
        items = {item["item_sku"]: item for item in response.json()["items"]}

        # Fully ordered lines drop out of the recommendations.
        for sku in ["GSK-203", "WDG-001", "FLT-405"]:
            assert sku not in items

        # The partial line remains, reduced by what is on order.
        assert items["CTL-330"]["quantity_on_order"] == 15
        assert items["CTL-330"]["shortfall"] == 56 - 15

    def test_on_order_stock_changes_ranking(self, client, worked_example_order):
        """Test that on-order units count toward coverage when ranking items."""
        client.post(ORDERS_URL, json=worked_example_order)

        # CTL-330 coverage rises from 40/96 to (40 + 15)/96 = 0.573, now above
        # SNR-420 at 90/182 = 0.495, so SNR-420 moves ahead of it.
        response = client.get(RECOMMENDATIONS_URL)
        skus = [item["item_sku"] for item in response.json()["items"]]
        assert skus == ["SNR-420", "CTL-330", "VLV-506", "BRG-102"]

    def test_everything_ordered(self, client):
        """Test that once every shortfall is on order, nothing is left to recommend."""
        plan = client.get(RECOMMENDATIONS_URL).json()
        payload = {
            "budget": plan["full_restock_cost"],
            "items": [{"item_sku": i["item_sku"], "quantity": i["recommended_quantity"]} for i in plan["items"]],
        }
        assert client.post(ORDERS_URL, json=payload).status_code == 201

        data = client.get(RECOMMENDATIONS_URL).json()
        assert data["items"] == []
        assert data["full_restock_cost"] == 0
        assert data["uncovered_count"] == 0

    def test_resubmitting_same_order_rejected(self, client, worked_example_order):
        """Test that the same order can't be placed twice."""
        assert client.post(ORDERS_URL, json=worked_example_order).status_code == 201

        response = client.post(ORDERS_URL, json=worked_example_order)
        assert response.status_code == 400
        assert "shortfall" in response.json()["detail"]
        assert len(client.get(ORDERS_URL).json()) == 1

    def test_unknown_sku_rejected(self, client):
        """Test that an unknown SKU is rejected."""
        response = client.post(ORDERS_URL, json={"budget": 1000, "items": [{"item_sku": "NOPE-999", "quantity": 1}]})
        assert response.status_code == 400
        assert "NOPE-999" in response.json()["detail"]

    def test_duplicate_sku_rejected(self, client):
        """Test that the same SKU twice in one order is rejected."""
        payload = {
            "budget": 1000,
            "items": [{"item_sku": "GSK-203", "quantity": 1}, {"item_sku": "GSK-203", "quantity": 1}],
        }
        response = client.post(ORDERS_URL, json=payload)
        assert response.status_code == 400
        assert "duplicate" in response.json()["detail"].lower()

    def test_quantity_above_shortfall_rejected(self, client):
        """Test that ordering more than the shortfall is rejected."""
        response = client.post(ORDERS_URL, json={"budget": 10000, "items": [{"item_sku": "GSK-203", "quantity": 381}]})
        assert response.status_code == 400
        assert "shortfall" in response.json()["detail"]

    def test_fully_stocked_item_rejected(self, client):
        """Test that an item with no shortfall can't be ordered."""
        response = client.post(ORDERS_URL, json={"budget": 10000, "items": [{"item_sku": "PSU-501", "quantity": 1}]})
        assert response.status_code == 400

    def test_total_above_budget_rejected(self, client):
        """Test that an order costing more than its budget is rejected."""
        response = client.post(ORDERS_URL, json={"budget": 100, "items": [{"item_sku": "GSK-203", "quantity": 380}]})
        assert response.status_code == 400
        assert "budget" in response.json()["detail"]

    def test_total_exactly_at_budget_accepted(self, client):
        """Test that an order costing exactly the budget is accepted."""
        response = client.post(ORDERS_URL, json={"budget": 2432, "items": [{"item_sku": "GSK-203", "quantity": 380}]})
        assert response.status_code == 201

    def test_budget_compared_to_the_cent(self, client):
        """Test that a total one cent over budget is rejected (12 x $28.75 = $345.00)."""
        line = [{"item_sku": "BRG-102", "quantity": 12}]
        assert client.post(ORDERS_URL, json={"budget": 344.99, "items": line}).status_code == 400
        assert client.post(ORDERS_URL, json={"budget": 345.00, "items": line}).status_code == 201

    # 1e307 used to overflow when converted to cents. A literal like 1e400 (which
    # json parses to inf) is also rejected, but FastAPI's default 422 handler then
    # can't serialize the inf input back, so that case isn't asserted here.
    @pytest.mark.parametrize("budget", [1e307, 1e12])
    def test_unbounded_order_budget_rejected(self, client, budget):
        """Test that an absurdly large order budget fails validation instead of overflowing."""
        payload = {"budget": budget, "items": [{"item_sku": "BRG-102", "quantity": 1}]}
        response = client.post(ORDERS_URL, json=payload)
        assert response.status_code == 422

    def test_rejected_order_not_stored(self, client):
        """Test that a rejected order leaves no partial state behind."""
        payload = {
            "budget": 10000,
            "items": [{"item_sku": "GSK-203", "quantity": 10}, {"item_sku": "NOPE-999", "quantity": 1}],
        }
        assert client.post(ORDERS_URL, json=payload).status_code == 400
        assert client.get(ORDERS_URL).json() == []

    @pytest.mark.parametrize("payload", [
        {"budget": 1000, "items": []},
        {"budget": 1000, "items": [{"item_sku": "GSK-203", "quantity": 0}]},
        {"budget": 1000, "items": [{"item_sku": "GSK-203", "quantity": -5}]},
        {"budget": -1, "items": [{"item_sku": "GSK-203", "quantity": 1}]},
        {"items": [{"item_sku": "GSK-203", "quantity": 1}]},
    ])
    def test_invalid_payload_rejected(self, client, payload):
        """Test that malformed requests fail validation."""
        response = client.post(ORDERS_URL, json=payload)
        assert response.status_code == 422
