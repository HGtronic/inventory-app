"""
Tests for task and purchase order API endpoints.

Both resources live in memory; conftest.py resets them before each test.
"""
import pytest

TASKS_URL = "/api/tasks"
PURCHASE_ORDERS_URL = "/api/purchase-orders"


@pytest.fixture
def new_task():
    """A valid task payload, shaped like the one TasksModal sends."""
    return {"title": "Count Tokyo safety stock", "priority": "high", "dueDate": "2025-10-20"}


@pytest.fixture
def new_purchase_order():
    """A valid purchase order payload for backlog item 1 (FLT-405)."""
    return {
        "backlog_item_id": "1",
        "supplier_name": "Industrial Supply Co",
        "quantity": 350,
        "unit_cost": 14.25,
        "expected_delivery_date": "2025-10-15",
        "notes": "Expedite if possible",
    }


class TestTaskEndpoints:
    """Test suite for task endpoints."""

    def test_get_tasks_empty_initially(self, client):
        """Test that the task list starts empty."""
        response = client.get(TASKS_URL)
        assert response.status_code == 200
        assert response.json() == []

    def test_create_task(self, client, new_task):
        """Test creating a task returns 201 and the client's task shape."""
        response = client.post(TASKS_URL, json=new_task)
        assert response.status_code == 201

        task = response.json()
        assert set(task) == {"id", "title", "priority", "dueDate", "status"}
        assert task["title"] == new_task["title"]
        assert task["priority"] == "high"
        assert task["dueDate"] == "2025-10-20"
        assert task["status"] == "pending"

    def test_task_ids_are_strings_distinct_from_mock_ids(self, client, new_task):
        """Test that task IDs are strings, so they never equal the client's numeric mock-task IDs."""
        task = client.post(TASKS_URL, json=new_task).json()
        assert isinstance(task["id"], str)
        assert task["id"].startswith("task-")

    def test_created_task_appears_in_list(self, client, new_task):
        """Test that created tasks are listed, newest first."""
        first = client.post(TASKS_URL, json=new_task).json()
        second = client.post(TASKS_URL, json={**new_task, "title": "Second task"}).json()

        listed = client.get(TASKS_URL).json()
        assert [t["id"] for t in listed] == [second["id"], first["id"]]

    def test_create_task_defaults_priority_to_medium(self, client, new_task):
        """Test that priority is optional and defaults to medium."""
        del new_task["priority"]
        response = client.post(TASKS_URL, json=new_task)
        assert response.status_code == 201
        assert response.json()["priority"] == "medium"

    def test_create_task_trims_title(self, client, new_task):
        """Test that surrounding whitespace is stripped from the title."""
        response = client.post(TASKS_URL, json={**new_task, "title": "  Padded title  "})
        assert response.status_code == 201
        assert response.json()["title"] == "Padded title"

    @pytest.mark.parametrize("payload_override", [
        {"title": ""},
        {"title": "   "},
        {"priority": "urgent"},
        {"dueDate": "not-a-date"},
        {"dueDate": None},
    ])
    def test_create_task_rejects_invalid_input(self, client, new_task, payload_override):
        """Test that invalid task payloads are rejected with 422."""
        response = client.post(TASKS_URL, json={**new_task, **payload_override})
        assert response.status_code == 422

    def test_toggle_task_flips_status_both_ways(self, client, new_task):
        """Test that PATCH toggles pending -> completed -> pending."""
        task_id = client.post(TASKS_URL, json=new_task).json()["id"]

        response = client.patch(f"{TASKS_URL}/{task_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

        response = client.patch(f"{TASKS_URL}/{task_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "pending"

    def test_delete_task(self, client, new_task):
        """Test that DELETE returns 204 and removes the task."""
        task_id = client.post(TASKS_URL, json=new_task).json()["id"]

        response = client.delete(f"{TASKS_URL}/{task_id}")
        assert response.status_code == 204
        assert client.get(TASKS_URL).json() == []

    def test_task_ids_not_reused_after_delete(self, client, new_task):
        """Test that deleting the newest task doesn't let the next task reuse its ID."""
        first_id = client.post(TASKS_URL, json=new_task).json()["id"]
        second_id = client.post(TASKS_URL, json=new_task).json()["id"]
        client.delete(f"{TASKS_URL}/{second_id}")

        third_id = client.post(TASKS_URL, json=new_task).json()["id"]
        assert third_id not in (first_id, second_id)

    @pytest.mark.parametrize("method", ["patch", "delete"])
    def test_nonexistent_task(self, client, method):
        """Test that toggling or deleting a missing task returns 404."""
        response = getattr(client, method)(f"{TASKS_URL}/task-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestPurchaseOrderEndpoints:
    """Test suite for purchase order endpoints."""

    def test_create_purchase_order(self, client, new_purchase_order):
        """Test creating a purchase order returns 201 with the stored fields."""
        response = client.post(PURCHASE_ORDERS_URL, json=new_purchase_order)
        assert response.status_code == 201

        po = response.json()
        assert po["id"].startswith("PO-")
        assert po["backlog_item_id"] == "1"
        assert po["supplier_name"] == "Industrial Supply Co"
        assert po["quantity"] == 350
        assert abs(po["unit_cost"] - 14.25) < 0.01
        assert po["expected_delivery_date"] == "2025-10-15"
        assert po["status"] == "Pending"
        assert po["notes"] == "Expedite if possible"
        assert "T" in po["created_date"]

    def test_get_purchase_order_by_backlog_item(self, client, new_purchase_order):
        """Test fetching the purchase order created for a backlog item."""
        created = client.post(PURCHASE_ORDERS_URL, json=new_purchase_order).json()

        response = client.get(f"{PURCHASE_ORDERS_URL}/1")
        assert response.status_code == 200
        assert response.json() == created

    def test_get_purchase_order_for_item_without_one(self, client):
        """Test that a backlog item without a purchase order returns 404."""
        response = client.get(f"{PURCHASE_ORDERS_URL}/2")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_backlog_flags_item_after_purchase_order(self, client, new_purchase_order):
        """Test that /api/backlog reports has_purchase_order once a PO exists."""
        before = {b["id"]: b["has_purchase_order"] for b in client.get("/api/backlog").json()}
        assert before["1"] is False

        client.post(PURCHASE_ORDERS_URL, json=new_purchase_order)

        after = {b["id"]: b["has_purchase_order"] for b in client.get("/api/backlog").json()}
        assert after["1"] is True
        # Other items are unaffected.
        assert after["2"] is False

    def test_second_purchase_order_for_same_item_conflicts(self, client, new_purchase_order):
        """Test that a backlog item can only have one purchase order."""
        assert client.post(PURCHASE_ORDERS_URL, json=new_purchase_order).status_code == 201

        response = client.post(PURCHASE_ORDERS_URL, json=new_purchase_order)
        assert response.status_code == 409
        assert "already has a purchase order" in response.json()["detail"]

    def test_purchase_order_for_unknown_backlog_item(self, client, new_purchase_order):
        """Test that ordering for a missing backlog item returns 404."""
        response = client.post(PURCHASE_ORDERS_URL, json={**new_purchase_order, "backlog_item_id": "999"})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_purchase_order_ids_are_unique(self, client, new_purchase_order):
        """Test that purchase orders for different backlog items get distinct IDs."""
        first = client.post(PURCHASE_ORDERS_URL, json=new_purchase_order).json()
        second = client.post(PURCHASE_ORDERS_URL, json={**new_purchase_order, "backlog_item_id": "2"}).json()
        assert first["id"] != second["id"]

    def test_purchase_order_notes_optional(self, client, new_purchase_order):
        """Test that notes can be omitted."""
        del new_purchase_order["notes"]
        response = client.post(PURCHASE_ORDERS_URL, json=new_purchase_order)
        assert response.status_code == 201
        assert response.json()["notes"] is None

    @pytest.mark.parametrize("payload_override", [
        {"supplier_name": ""},
        {"supplier_name": "   "},
        {"quantity": 0},
        {"quantity": -5},
        {"unit_cost": 0},
        {"expected_delivery_date": "2025-13-45"},
    ])
    def test_create_purchase_order_rejects_invalid_input(self, client, new_purchase_order, payload_override):
        """Test that invalid purchase order payloads are rejected with 422."""
        response = client.post(PURCHASE_ORDERS_URL, json={**new_purchase_order, **payload_override})
        assert response.status_code == 422
