"""Unit tests for flow triggers resource."""

import pytest

from nexla_sdk.models.flow_triggers.requests import FlowTriggerCreate
from nexla_sdk.models.flow_triggers.responses import FlowTrigger
from tests.utils import assert_model_list_valid, assert_model_valid

# Sample response data
SAMPLE_FLOW_TRIGGER = {
    "id": 123,
    "owner": {"id": 1, "full_name": "Test User", "email": "test@example.com"},
    "org": {"id": 1, "name": "Test Org"},
    "status": "ACTIVE",
    "triggering_event_type": "DATA_SINK_WRITE_DONE",
    "triggering_origin_node_id": 100,
    "triggering_flow_node_id": 101,
    "triggering_resource_type": "data_sink",
    "triggering_resource_id": 200,
    "triggered_event_type": "DATA_SOURCE_READ_START",
    "triggered_origin_node_id": 300,
    "triggered_resource_type": "data_source",
    "triggered_resource_id": 400,
    "updated_at": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z",
}

SAMPLE_FLOW_TRIGGERS_LIST = [
    SAMPLE_FLOW_TRIGGER,
    {**SAMPLE_FLOW_TRIGGER, "id": 124, "status": "PAUSED"},
    {**SAMPLE_FLOW_TRIGGER, "id": 125},
]


@pytest.fixture
def sample_flow_trigger_response():
    """Sample flow trigger response."""
    return SAMPLE_FLOW_TRIGGER.copy()


@pytest.fixture
def sample_flow_triggers_list():
    """Sample flow triggers list response."""
    return [t.copy() for t in SAMPLE_FLOW_TRIGGERS_LIST]


@pytest.mark.unit
class TestFlowTriggersResource:
    """Unit tests for FlowTriggersResource using mocks."""

    def test_list_flow_triggers_success(
        self, mock_client, mock_http_client, sample_flow_triggers_list
    ):
        """Test listing flow triggers with successful response."""
        mock_http_client.add_response("/flow_triggers", sample_flow_triggers_list)

        triggers = mock_client.flow_triggers.list()

        assert len(triggers) == 3
        assert_model_list_valid(triggers, FlowTrigger)
        mock_http_client.assert_request_made("GET", "/flow_triggers")

    def test_list_flow_triggers_with_pagination(
        self, mock_client, mock_http_client, sample_flow_triggers_list
    ):
        """Test listing flow triggers with pagination."""
        mock_http_client.add_response("/flow_triggers", sample_flow_triggers_list)

        triggers = mock_client.flow_triggers.list(page=1, per_page=10)

        assert len(triggers) == 3

    def test_list_all_flow_triggers_success(
        self, mock_client, mock_http_client, sample_flow_triggers_list
    ):
        """Test listing all flow triggers (super user)."""
        mock_http_client.add_response("/flow_triggers/all", sample_flow_triggers_list)

        triggers = mock_client.flow_triggers.list_all()

        assert len(triggers) == 3
        mock_http_client.assert_request_made("GET", "/flow_triggers/all")

    def test_list_all_flow_triggers_with_pagination(
        self, mock_client, mock_http_client, sample_flow_triggers_list
    ):
        """Test listing all flow triggers with pagination."""
        mock_http_client.add_response("/flow_triggers/all", sample_flow_triggers_list)

        triggers = mock_client.flow_triggers.list_all(page=1, per_page=50)

        assert len(triggers) == 3

    def test_get_flow_trigger_success(
        self, mock_client, mock_http_client, sample_flow_trigger_response
    ):
        """Test getting a single flow trigger."""
        trigger_id = 123
        mock_http_client.add_response(
            f"/flow_triggers/{trigger_id}", sample_flow_trigger_response
        )

        trigger = mock_client.flow_triggers.get(trigger_id)

        assert_model_valid(trigger, {"id": trigger_id})
        mock_http_client.assert_request_made("GET", f"/flow_triggers/{trigger_id}")

    def test_create_flow_trigger_success(
        self, mock_client, mock_http_client, sample_flow_trigger_response
    ):
        """Test creating a flow trigger."""
        mock_http_client.add_response("/flow_triggers", sample_flow_trigger_response)

        create_data = FlowTriggerCreate(
            triggering_event_type="DATA_SINK_WRITE_DONE",
            triggered_event_type="DATA_SOURCE_READ_START",
            data_sink_id=200,
            data_source_id=400,
        )
        trigger = mock_client.flow_triggers.create(create_data)

        assert_model_valid(trigger, {"triggering_event_type": "DATA_SINK_WRITE_DONE"})
        mock_http_client.assert_request_made("POST", "/flow_triggers")

    def test_create_flow_trigger_with_node_ids(
        self, mock_client, mock_http_client, sample_flow_trigger_response
    ):
        """Test creating a flow trigger with node IDs."""
        mock_http_client.add_response("/flow_triggers", sample_flow_trigger_response)

        create_data = FlowTriggerCreate(
            triggering_event_type="DATA_SINK_WRITE_DONE",
            triggered_event_type="DATA_SOURCE_READ_START",
            triggering_flow_node_id=101,
            triggered_origin_node_id=300,
        )
        trigger = mock_client.flow_triggers.create(create_data)

        assert trigger.triggering_flow_node_id == 101

    def test_delete_flow_trigger_success(self, mock_client, mock_http_client):
        """Test deleting a flow trigger."""
        trigger_id = 123
        mock_http_client.add_response(f"/flow_triggers/{trigger_id}", {"success": True})

        result = mock_client.flow_triggers.delete(trigger_id)

        assert result["success"] is True
        mock_http_client.assert_request_made("DELETE", f"/flow_triggers/{trigger_id}")

    def test_activate_flow_trigger_success(
        self, mock_client, mock_http_client, sample_flow_trigger_response
    ):
        """Test activating a flow trigger."""
        trigger_id = 123
        activated_response = {**sample_flow_trigger_response, "status": "ACTIVE"}
        mock_http_client.add_response(
            f"/flow_triggers/{trigger_id}/activate", activated_response
        )

        trigger = mock_client.flow_triggers.activate(trigger_id)

        assert trigger.status == "ACTIVE"
        mock_http_client.assert_request_made(
            "PUT", f"/flow_triggers/{trigger_id}/activate"
        )

    def test_pause_flow_trigger_success(
        self, mock_client, mock_http_client, sample_flow_trigger_response
    ):
        """Test pausing a flow trigger."""
        trigger_id = 123
        paused_response = {**sample_flow_trigger_response, "status": "PAUSED"}
        mock_http_client.add_response(
            f"/flow_triggers/{trigger_id}/pause", paused_response
        )

        trigger = mock_client.flow_triggers.pause(trigger_id)

        assert trigger.status == "PAUSED"
        mock_http_client.assert_request_made(
            "PUT", f"/flow_triggers/{trigger_id}/pause"
        )


@pytest.mark.unit
class TestFlowTriggerModels:
    """Unit tests for flow trigger models."""

    def test_flow_trigger_model_validation(self, sample_flow_trigger_response):
        """Test FlowTrigger model parses valid data correctly."""
        trigger = FlowTrigger.model_validate(sample_flow_trigger_response)

        assert trigger.id == 123
        assert trigger.status == "ACTIVE"
        assert trigger.triggering_event_type == "DATA_SINK_WRITE_DONE"
        assert trigger.triggered_event_type == "DATA_SOURCE_READ_START"
        assert trigger.triggering_resource_type == "data_sink"
        assert trigger.triggered_resource_type == "data_source"

    def test_flow_trigger_with_owner_and_org(self, sample_flow_trigger_response):
        """Test FlowTrigger model parses owner and org correctly."""
        trigger = FlowTrigger.model_validate(sample_flow_trigger_response)

        assert trigger.owner is not None
        assert trigger.owner.id == 1
        assert trigger.org is not None
        assert trigger.org.id == 1

    def test_flow_trigger_create_model_serialization(self):
        """Test FlowTriggerCreate model serialization."""
        create_data = FlowTriggerCreate(
            triggering_event_type="DATA_SINK_WRITE_DONE",
            triggered_event_type="DATA_SOURCE_READ_START",
            data_sink_id=100,
            data_source_id=200,
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["triggering_event_type"] == "DATA_SINK_WRITE_DONE"
        assert data["triggered_event_type"] == "DATA_SOURCE_READ_START"
        assert data["data_sink_id"] == 100
        assert data["data_source_id"] == 200

    def test_flow_trigger_create_with_resource_type(self):
        """Test FlowTriggerCreate model with explicit resource types."""
        create_data = FlowTriggerCreate(
            triggering_event_type="DATA_SINK_WRITE_DONE",
            triggered_event_type="DATA_SOURCE_READ_START",
            triggering_resource_id=100,
            triggering_resource_type="data_sink",
            triggered_resource_id=200,
            triggered_resource_type="data_source",
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["triggering_resource_type"] == "data_sink"
        assert data["triggered_resource_type"] == "data_source"

    def test_flow_trigger_create_with_owner(self):
        """Test FlowTriggerCreate model with owner/org."""
        create_data = FlowTriggerCreate(
            triggering_event_type="DATA_SOURCE_READ_DONE",
            triggered_event_type="DATA_SOURCE_READ_START",
            triggering_flow_node_id=100,
            triggered_origin_node_id=200,
            owner_id=5,
            org_id=10,
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["owner_id"] == 5
        assert data["org_id"] == 10


@pytest.mark.unit
class TestFlowTriggersImmutability:
    """Test that flow triggers are immutable (update is not supported)."""

    def test_update_raises_not_implemented(self, mock_client):
        """Flow triggers are immutable; update should raise NotImplementedError."""
        with pytest.raises(NotImplementedError, match="immutable"):
            mock_client.flow_triggers.update(123, {"status": "ACTIVE"})
