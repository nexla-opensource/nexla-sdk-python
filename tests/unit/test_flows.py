"""Unit tests for flows resource."""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.exceptions import ServerError
from nexla_sdk.http_client import HttpClientError
from nexla_sdk.models.common import FlowNode
from nexla_sdk.models.flows.requests import FlowCopyOptions
from nexla_sdk.models.flows.responses import (
    DocsRecommendation,
    FlowLogsResponse,
    FlowMetrics,
    FlowMetricsApiResponse,
    FlowResponse,
)
from nexla_sdk.models.metrics.enums import ResourceType
from tests.utils.assertions import NexlaAssertions
from tests.utils.fixtures import MockHTTPClient
from tests.utils.mock_builders import MockDataFactory, MockResponseBuilder

pytestmark = pytest.mark.unit


class TestFlowsModels:
    """Tests for flow models validation."""

    def test_flow_response_model(self):
        """Test FlowResponse model with all fields."""
        factory = MockDataFactory()
        response_data = factory.create_mock_flow_response()
        response = FlowResponse.model_validate(response_data)
        assert len(response.flows) == len(response_data["flows"])

    def test_flow_metrics_model(self):
        """Test FlowMetrics model."""
        factory = MockDataFactory()
        metrics_data = factory.create_mock_flow_metrics()
        metrics = FlowMetrics.model_validate(metrics_data)
        assert metrics.records == metrics_data["records"]
        assert metrics.size == metrics_data["size"]

    def test_flow_logs_response_model(self):
        """Test FlowLogsResponse model."""
        response_data = MockResponseBuilder.flow_logs_response(log_count=3)
        response = FlowLogsResponse.model_validate(response_data)
        assert response.status == 200
        assert response.message == "Ok"
        assert len(response.logs) == 3
        assert response.meta.total_count == 3
        assert response.meta.page_count == 1
        assert response.meta.org_id == response_data["logs"]["meta"]["org_id"]
        assert response.meta.run_id == response_data["logs"]["meta"]["run_id"]
        assert response.logs[0].message == response_data["logs"]["data"][0]["log"]
        assert response.logs[0].level == response_data["logs"]["data"][0]["severity"]
        assert response.logs[0].run_id == response_data["logs"]["data"][0]["run_id"]
        assert response.logs[0].details == response_data["logs"]["data"][0]["details"]
        raw_timestamp = response_data["logs"]["data"][0]["timestamp"]
        assert response.logs[0].timestamp == datetime.fromtimestamp(
            raw_timestamp / 1000, tz=timezone.utc
        )

    def test_flow_logs_response_model_accepts_seconds_timestamp(self):
        """Test normal Unix-second timestamps are parsed as seconds."""
        response_data = MockResponseBuilder.flow_logs_response(
            log_count=1,
            logs={
                "data": [MockResponseBuilder.live_flow_log_entry(timestamp=1700000000)],
                "meta": {"current_page": 1, "pages_count": 1, "total_count": 1},
            },
        )

        response = FlowLogsResponse.model_validate(response_data)

        assert response.logs[0].timestamp == datetime.fromtimestamp(
            1700000000, tz=timezone.utc
        )

    def test_flow_metrics_api_response_model(self):
        """Test FlowMetricsApiResponse model."""
        response_data = MockResponseBuilder.flow_metrics_api_response()
        response = FlowMetricsApiResponse.model_validate(response_data)
        assert response.status == 200
        assert response.message == "Ok"
        assert response.metrics is not None

    def test_docs_recommendation_model(self):
        """Test DocsRecommendation model."""
        response_data = MockResponseBuilder.docs_recommendation_response(
            recommendation="Test recommendation", status="success"
        )
        response = DocsRecommendation.model_validate(response_data)
        assert response.recommendation == "Test recommendation"
        assert response.status == "success"

    def test_flow_node_model(self):
        """Test FlowNode model with nested children."""
        factory = MockDataFactory()
        node_data = factory.create_mock_flow_node(max_depth=2)
        node = FlowNode.model_validate(node_data)
        assert node.id == node_data["id"]
        if node_data.get("children"):
            assert len(node.children) == len(node_data["children"])


class TestFlowsUnit:
    """Unit tests for flows resource."""

    @pytest.fixture
    def mock_http_client(self) -> MockHTTPClient:
        """Create a mock HTTP client."""
        return MockHTTPClient()

    @pytest.fixture
    def mock_client(self, mock_http_client) -> NexlaClient:
        """Create a test client with mocked HTTP and access token auth."""
        # Use access_token to avoid token fetch call
        with patch(
            "nexla_sdk.client.RequestsHttpClient", return_value=mock_http_client
        ):
            client = NexlaClient(access_token="test-access-token")
        client.http_client = mock_http_client
        return client

    @pytest.fixture
    def mock_factory(self) -> MockDataFactory:
        """Create mock data factory."""
        return MockDataFactory()

    def test_list_flows(self, mock_client, mock_http_client, mock_factory):
        """Test listing all flows."""
        # Arrange
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response("/flows", mock_response)

        # Act
        flows = mock_client.flows.list()

        # Assert
        assert len(flows) == 1  # API returns single FlowResponse object for list
        assert isinstance(flows[0], FlowResponse)
        assert len(flows[0].flows) == len(mock_response["flows"])

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert "/flows" in last_request["url"]

    def test_list_flows_with_params(self, mock_client, mock_http_client, mock_factory):
        """Test listing flows with query parameters."""
        # Arrange
        mock_response = mock_factory.create_mock_flow_response(include_elements=False)
        mock_http_client.add_response("/flows", mock_response)

        # Act
        flows = mock_client.flows.list(flows_only=True, include_run_metrics=True)

        # Assert
        assert len(flows) == 1
        assert flows[0].data_sources is None  # No expanded elements

        # Verify request params
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["flows_only"] == 1
        assert last_request["params"]["include_run_metrics"] == 1

    def test_list_flows_with_access_role(
        self, mock_client, mock_http_client, mock_factory
    ):
        """Test listing flows with access_role parameter."""
        # Arrange
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response("/flows", mock_response)

        # Act
        flows = mock_client.flows.list(access_role="owner")

        # Assert
        assert len(flows) == 1
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["access_role"] == "owner"

    def test_get_flow(self, mock_client, mock_http_client, mock_factory):
        """Test getting a single flow by ID."""
        # Arrange
        flow_id = 5059
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response(f"/flows/{flow_id}", mock_response)

        # Act
        flow = mock_client.flows.get(flow_id)

        # Assert
        assert isinstance(flow, FlowResponse)
        NexlaAssertions.assert_flow_response(flow, mock_response)

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/flows/{flow_id}" in last_request["url"]

    def test_get_flow_by_resource(self, mock_client, mock_http_client, mock_factory):
        """Test getting flow by resource type and ID."""
        # Arrange
        resource_type = "data_sources"
        resource_id = 5023
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response(
            f"/{resource_type}/{resource_id}/flow", mock_response
        )

        # Act
        flow = mock_client.flows.get_by_resource(resource_type, resource_id)

        # Assert
        assert isinstance(flow, FlowResponse)

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/{resource_type}/{resource_id}/flow" in last_request["url"]

    def test_activate_flow(self, mock_client, mock_http_client, mock_factory):
        """Test activating a flow."""
        # Arrange
        flow_id = 5059
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response(f"/flows/{flow_id}/activate", mock_response)

        # Act
        flow = mock_client.flows.activate(flow_id)

        # Assert
        assert isinstance(flow, FlowResponse)

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "PUT"
        assert f"/flows/{flow_id}/activate" in last_request["url"]

    def test_activate_flow_all(self, mock_client, mock_http_client, mock_factory):
        """Test activating entire flow tree."""
        # Arrange
        flow_id = 5059
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response(f"/flows/{flow_id}/activate", mock_response)

        # Act
        mock_client.flows.activate(flow_id, all=True)

        # Assert
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["all"] == 1

    def test_pause_flow(self, mock_client, mock_http_client, mock_factory):
        """Test pausing a flow."""
        # Arrange
        flow_id = 5059
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response(f"/flows/{flow_id}/pause", mock_response)

        # Act
        flow = mock_client.flows.pause(flow_id)

        # Assert
        assert isinstance(flow, FlowResponse)

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "PUT"
        assert f"/flows/{flow_id}/pause" in last_request["url"]

    def test_pause_flow_async_mode(self, mock_client, mock_http_client, mock_factory):
        """Test pausing a flow with async_mode=True."""
        # Arrange
        flow_id = 5059
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response(f"/flows/{flow_id}/pause", mock_response)

        # Act
        mock_client.flows.pause(flow_id, async_mode=True)

        # Assert
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["async"] == 1

    def test_copy_flow(self, mock_client, mock_http_client, mock_factory):
        """Test copying a flow."""
        # Arrange
        flow_id = 5059
        copy_options = FlowCopyOptions(
            reuse_data_credentials=True,
            copy_access_controls=True,
            copy_dependent_data_flows=False,
            owner_id=123,
            org_id=456,
        )
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response(f"/flows/{flow_id}/copy", mock_response)

        # Act
        flow = mock_client.flows.copy(flow_id, copy_options)

        # Assert
        assert isinstance(flow, FlowResponse)

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "POST"
        assert f"/flows/{flow_id}/copy" in last_request["url"]
        assert last_request["json"]["reuse_data_credentials"] is True
        assert last_request["json"]["copy_access_controls"] is True
        assert last_request["json"]["owner_id"] == 123

    def test_delete_flow(self, mock_client, mock_http_client):
        """Test deleting a flow."""
        # Arrange
        flow_id = 5059
        mock_response = {"status": "ok"}
        mock_http_client.add_response(f"/flows/{flow_id}", mock_response)

        # Act
        result = mock_client.flows.delete(flow_id)

        # Assert
        assert result == mock_response

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "DELETE"
        assert f"/flows/{flow_id}" in last_request["url"]

    def test_delete_flow_active_error(self, mock_client, mock_http_client):
        """Test deleting active flow returns error."""
        # Arrange
        flow_id = 5059
        error_response = {
            "data_sources": [5023],
            "data_sets": [5059, 5061, 5062],
            "message": "Active flow resources must be paused before flow deletion!",
        }

        # Mock the HTTP client to raise HttpClientError
        mock_http_client.add_error(
            f"/flows/{flow_id}",
            HttpClientError(
                "Method not allowed", status_code=405, response=error_response
            ),
        )

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.flows.delete(flow_id)

        assert exc_info.value.status_code == 405
        assert "Active flow resources must be paused" in str(exc_info.value)

    def test_delete_by_resource(self, mock_client, mock_http_client):
        """Test deleting flow by resource."""
        # Arrange
        resource_type = "data_sources"
        resource_id = 5023
        mock_response = {"status": "ok"}
        mock_http_client.add_response(
            f"/{resource_type}/{resource_id}/flow", mock_response
        )

        # Act
        result = mock_client.flows.delete_by_resource(resource_type, resource_id)

        # Assert
        assert result == mock_response

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "DELETE"
        assert f"/{resource_type}/{resource_id}/flow" in last_request["url"]

    def test_activate_by_resource(self, mock_client, mock_http_client, mock_factory):
        """Test activating flow by resource."""
        # Arrange
        resource_type = "data_sets"
        resource_id = 5061
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response(
            f"/{resource_type}/{resource_id}/activate", mock_response
        )

        # Act
        flow = mock_client.flows.activate_by_resource(
            resource_type, resource_id, all=True
        )

        # Assert
        assert isinstance(flow, FlowResponse)

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "PUT"
        assert f"/{resource_type}/{resource_id}/activate" in last_request["url"]
        assert last_request["params"]["all"] == 1

    def test_pause_by_resource(self, mock_client, mock_http_client, mock_factory):
        """Test pausing flow by resource."""
        # Arrange
        resource_type = "data_sinks"
        resource_id = 5029
        mock_response = mock_factory.create_mock_flow_response()
        mock_http_client.add_response(
            f"/{resource_type}/{resource_id}/pause", mock_response
        )

        # Act
        flow = mock_client.flows.pause_by_resource(resource_type, resource_id)

        # Assert
        assert isinstance(flow, FlowResponse)

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "PUT"
        assert f"/{resource_type}/{resource_id}/pause" in last_request["url"]

    def test_get_run_status_uses_flow_id_path(self, mock_client, mock_http_client):
        """Test run status is keyed by flow ID."""
        mock_http_client.add_response("/flows/599305/run_status/123", {"status": "ok"})

        result = mock_client.flows.get_run_status(599305, 123)

        assert result["status"] == "ok"
        last_request = mock_http_client.get_last_request()
        assert "/flows/599305/run_status/123" in last_request["url"]

    def test_get_run_status_rejects_deprecated_resource_signature(
        self, mock_client, mock_http_client
    ):
        """Test run status fails clearly for the old resource-based signature."""
        with pytest.raises(TypeError, match="positional argument"):
            mock_client.flows.get_run_status("data_sources", 5023, 123)

        assert mock_http_client.requests == []

    def test_get_run_status_rejects_string_flow_id(self, mock_client, mock_http_client):
        """Test string flow IDs fail with a type-specific error."""
        with pytest.raises(TypeError, match="requires integer flow_id and run_id"):
            mock_client.flows.get_run_status("599305", 123)

        assert mock_http_client.requests == []

    def test_flow_logs_and_metrics_accept_resource_type_enum(
        self, mock_client, mock_http_client
    ):
        """Test flow log and metric helpers accept ResourceType enum members."""
        mock_http_client.add_response(
            "/data_sets/5061/flow/logs",
            MockResponseBuilder.flow_logs_response(log_count=1),
        )

        logs = mock_client.flows.get_logs(
            ResourceType.DATA_SETS,
            5061,
            run_id=100,
            from_ts=1704067200000,
        )

        assert isinstance(logs, FlowLogsResponse)
        last_request = mock_http_client.get_last_request()
        assert "/data_sets/5061/flow/logs" in last_request["url"]

        mock_http_client.clear_requests()
        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/data_sinks/5029/flow/metrics",
            MockResponseBuilder.flow_metrics_api_response(),
        )

        metrics = mock_client.flows.get_metrics(
            ResourceType.DATA_SINKS,
            5029,
            from_date="2024-01-01",
        )

        assert isinstance(metrics, FlowMetricsApiResponse)
        last_request = mock_http_client.get_last_request()
        assert "/data_sinks/5029/flow/metrics" in last_request["url"]

    @pytest.mark.parametrize(
        "call",
        [
            pytest.param(
                lambda flows: flows.get_by_resource("data_source", 1),
                id="get_by_resource",
            ),
            pytest.param(
                lambda flows: flows.activate_by_resource("data_source", 1),
                id="activate_by_resource",
            ),
            pytest.param(
                lambda flows: flows.pause_by_resource("data_source", 1),
                id="pause_by_resource",
            ),
            pytest.param(
                lambda flows: flows.get_logs("data_source", 1, run_id=1, from_ts=0),
                id="get_logs",
            ),
            pytest.param(
                lambda flows: flows.get_metrics(
                    "data_source", 1, from_date="2024-01-01"
                ),
                id="get_metrics",
            ),
        ],
    )
    def test_flow_resource_helpers_reject_invalid_resource_type(
        self, mock_client, mock_http_client, call
    ):
        """Test flow resource helpers reject singular resource type strings."""
        with pytest.raises(ValueError, match="Invalid resource_type 'data_source'"):
            call(mock_client.flows)

        assert mock_http_client.requests == []

    def test_flow_with_metrics(self, mock_client, mock_http_client, mock_factory):
        """Test flow response with metrics."""
        # Arrange
        mock_response = mock_factory.create_mock_flow_response()
        mock_response["metrics"] = [
            mock_factory.create_mock_flow_metrics() for _ in range(3)
        ]
        mock_http_client.add_response("/flows", mock_response)

        # Act
        flows = mock_client.flows.list(include_run_metrics=True)

        # Assert
        assert len(flows) == 1
        flow = flows[0]
        assert flow.metrics is not None
        assert len(flow.metrics) == 3
        assert all(isinstance(m, FlowMetrics) for m in flow.metrics)

    def test_flow_node_parsing(self, mock_client, mock_http_client, mock_factory):
        """Test parsing of nested flow node structure."""
        # Arrange
        # Create a deep flow structure
        mock_response = {"flows": [mock_factory.create_mock_flow_node(max_depth=4)]}
        mock_http_client.add_response("/flows", mock_response)

        # Act
        flows = mock_client.flows.list(flows_only=True)

        # Assert
        assert len(flows) == 1
        flow = flows[0]
        assert len(flow.flows) == 1

        # Check nested structure
        root_node = flow.flows[0]
        assert isinstance(root_node, FlowNode)
        assert root_node.parent_node_id is None  # Root node

        # Verify children exist and are properly parsed
        if root_node.children:
            for child in root_node.children:
                assert isinstance(child, FlowNode)
                assert child.parent_node_id == root_node.id

    def test_empty_flow_response(self, mock_client, mock_http_client):
        """Test handling empty flow response."""
        # Arrange
        mock_response = {"flows": []}
        mock_http_client.add_response("/flows", mock_response)

        # Act
        flows = mock_client.flows.list()

        # Assert
        assert len(flows) == 1
        assert len(flows[0].flows) == 0

    def test_validation_error_handling(self, mock_client, mock_http_client):
        """Test handling of invalid flow response."""
        # Arrange
        invalid_response = {
            "flows": [
                {
                    # Missing required 'id' field
                    "parent_data_set_id": None,
                    "data_source": {"id": 123},
                }
            ]
        }
        mock_http_client.add_response("/flows", invalid_response)

        # Act & Assert
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            mock_client.flows.list()

        # Check that the error mentions the missing fields
        error_str = str(exc_info.value)
        assert "id" in error_str
        assert "Field required" in error_str

    def test_docs_recommendation_success(self, mock_client, mock_http_client):
        """Test docs_recommendation returns DocsRecommendation model."""
        # Arrange
        flow_id = 5059
        mock_response = MockResponseBuilder.docs_recommendation_response(
            recommendation="This flow ingests data from S3 and transforms it.",
            status="success",
        )
        mock_http_client.add_response(
            f"/flows/{flow_id}/docs/recommendation", mock_response
        )

        # Act
        result = mock_client.flows.docs_recommendation(flow_id)

        # Assert
        assert isinstance(result, DocsRecommendation)
        assert (
            result.recommendation == "This flow ingests data from S3 and transforms it."
        )
        assert result.status == "success"

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "POST"
        assert f"/flows/{flow_id}/docs/recommendation" in last_request["url"]

    def test_get_logs_success(self, mock_client, mock_http_client):
        """Test get_logs returns FlowLogsResponse model."""
        # Arrange
        resource_type = "data_sources"
        resource_id = 5023
        run_id = 12345
        from_ts = 1704067200000
        mock_response = MockResponseBuilder.flow_logs_response(log_count=3)
        mock_http_client.add_response(
            f"/{resource_type}/{resource_id}/flow/logs", mock_response
        )

        # Act
        result = mock_client.flows.get_logs(
            resource_type=resource_type,
            resource_id=resource_id,
            run_id=run_id,
            from_ts=from_ts,
        )

        # Assert
        assert isinstance(result, FlowLogsResponse)
        assert result.status == 200
        assert result.message == "Ok"
        assert len(result.logs) == 3
        assert result.meta.total_count == 3

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/{resource_type}/{resource_id}/flow/logs" in last_request["url"]
        assert last_request["params"]["run_id"] == run_id
        assert last_request["params"]["from"] == from_ts

    def test_get_logs_with_pagination(self, mock_client, mock_http_client):
        """Test get_logs with pagination parameters."""
        # Arrange
        mock_response = MockResponseBuilder.flow_logs_response()
        mock_http_client.add_response("/data_sets/5061/flow/logs", mock_response)

        # Act
        mock_client.flows.get_logs(
            resource_type="data_sets",
            resource_id=5061,
            run_id=100,
            from_ts=1704067200000,
            page=2,
            per_page=25,
        )

        # Assert
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["page"] == 2
        assert last_request["params"]["per_page"] == 25

    def test_get_logs_warns_for_seconds_timestamp(self, mock_client, mock_http_client):
        """Test get_logs warns when timestamps look like seconds."""
        mock_response = MockResponseBuilder.flow_logs_response()
        mock_http_client.add_response("/data_sources/5023/flow/logs", mock_response)

        with pytest.warns(RuntimeWarning, match="from_ts looks like seconds"):
            mock_client.flows.get_logs(
                resource_type="data_sources",
                resource_id=5023,
                run_id=12345,
                from_ts=1700000000,
            )

    def test_get_logs_warns_for_seconds_to_timestamp(
        self, mock_client, mock_http_client
    ):
        """Test get_logs warns when to_ts looks like seconds."""
        mock_response = MockResponseBuilder.flow_logs_response()
        mock_http_client.add_response("/data_sources/5023/flow/logs", mock_response)

        with pytest.warns(RuntimeWarning, match="to_ts looks like seconds"):
            mock_client.flows.get_logs(
                resource_type="data_sources",
                resource_id=5023,
                run_id=12345,
                from_ts=1700000000000,
                to_ts=1700003600,
            )

    def test_get_logs_all_parameters(self, mock_client, mock_http_client):
        """Test get_logs with all parameters."""
        # Arrange
        mock_response = MockResponseBuilder.flow_logs_response()
        mock_http_client.add_response("/data_sinks/5029/flow/logs", mock_response)

        # Act
        mock_client.flows.get_logs(
            resource_type="data_sinks",
            resource_id=5029,
            run_id=456,
            from_ts=1704067200000,
            to_ts=1704153600000,
            page=1,
            per_page=50,
        )

        # Assert
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["run_id"] == 456
        assert last_request["params"]["from"] == 1704067200000
        assert last_request["params"]["to"] == 1704153600000
        assert last_request["params"]["page"] == 1
        assert last_request["params"]["per_page"] == 50

    def test_get_flow_logs_uses_flat_logs_path(self, mock_client, mock_http_client):
        """get_flow_logs hits /flows/:id/logs (not /flow/logs) and unix-encodes dates."""
        flow_id = 591210
        mock_http_client.add_response(
            f"/flows/{flow_id}/logs", {"status": 200, "logs": []}
        )

        mock_client.flows.get_flow_logs(
            flow_id=flow_id,
            from_date="2026-05-09",
            to_date="2026-05-10",
            severity="ERROR",
            run_id=42,
        )

        req = mock_http_client.get_last_request()
        assert req["method"] == "GET"
        assert req["url"].endswith(f"/flows/{flow_id}/logs")
        assert "/flow/logs" not in req["url"]
        assert req["params"]["severity"] == "ERROR"
        assert req["params"]["run_id"] == 42
        # 2026-05-09 00:00:00 UTC → 1778284800; 2026-05-10 → 1778371200
        assert req["params"]["from"] == 1778284800
        assert req["params"]["to"] == 1778371200

    def test_get_flow_logs_passes_through_unix_timestamps(
        self, mock_client, mock_http_client
    ):
        """get_flow_logs leaves unix-timestamp inputs unchanged."""
        mock_http_client.add_response("/flows/1/logs", {"status": 200, "logs": []})
        mock_client.flows.get_flow_logs(flow_id=1, from_date=1704067200, to_date="1704153600")
        req = mock_http_client.get_last_request()
        assert req["params"]["from"] == 1704067200
        assert req["params"]["to"] == 1704153600

    def test_search_flow_logs_uses_post_with_body(self, mock_client, mock_http_client):
        """search_flow_logs POSTs body params and unix-encodes from/to."""
        flow_id = 591210
        mock_http_client.add_response(
            f"/flows/{flow_id}/logs_v2", {"status": 200, "logs": []}
        )

        mock_client.flows.search_flow_logs(
            flow_id=flow_id,
            run_ids=[1778284990535, 1778284990536],
            severity="ERROR",
            log_type=["execution"],
            search_string="schema mismatch",
            from_date="2026-05-09",
            to_date="2026-05-09",
            size=100,
            facets=True,
        )

        req = mock_http_client.get_last_request()
        assert req["method"] == "POST"
        assert req["url"].endswith(f"/flows/{flow_id}/logs_v2")
        # body
        assert req["json"]["run_ids"] == [1778284990535, 1778284990536]
        assert req["json"]["severity"] == ["ERROR"]
        assert req["json"]["log_type"] == ["execution"]
        assert req["json"]["search_string"] == "schema mismatch"
        # query
        assert req["params"]["from"] == 1778284800
        assert req["params"]["to"] == 1778284800
        assert req["params"]["size"] == 100
        assert req["params"]["facets"] is True
        # body fields must NOT leak into the query string
        assert "severity" not in req["params"]
        assert "run_ids" not in req["params"]
        assert "search_string" not in req["params"]

    def test_search_flow_logs_accepts_run_ids_string(
        self, mock_client, mock_http_client
    ):
        """Comma-separated run_ids string is split into a list of ints."""
        mock_http_client.add_response("/flows/1/logs_v2", {"status": 200, "logs": []})
        mock_client.flows.search_flow_logs(flow_id=1, run_ids="10,20,30")
        req = mock_http_client.get_last_request()
        assert req["json"]["run_ids"] == [10, 20, 30]

    def test_get_active_flows_metrics_uses_data_flows_metrics_path(
        self, mock_client, mock_http_client
    ):
        """admin-api defines the route as /data_flows/metrics/active_flows_metrics.
        Calling /flows/active_flows_metrics 404s in production."""
        mock_http_client.add_response(
            "/data_flows/metrics/active_flows_metrics", {"metrics": []}
        )

        mock_client.flows.get_active_flows_metrics(
            from_date="2026-05-01", to_date="2026-05-13", org_id=484
        )

        req = mock_http_client.get_last_request()
        assert req["method"] == "GET"
        assert req["url"].endswith("/data_flows/metrics/active_flows_metrics")
        assert "/flows/active_flows_metrics" not in req["url"]
        assert req["params"]["from"] == "2026-05-01"
        assert req["params"]["to"] == "2026-05-13"
        assert req["params"]["org_id"] == 484

    def test_get_metrics_success(self, mock_client, mock_http_client):
        """Test get_metrics returns FlowMetricsApiResponse model."""
        # Arrange
        resource_type = "data_sources"
        resource_id = 5023
        from_date = "2024-01-01"
        mock_response = MockResponseBuilder.flow_metrics_api_response()
        mock_http_client.add_response(
            f"/{resource_type}/{resource_id}/flow/metrics", mock_response
        )

        # Act
        result = mock_client.flows.get_metrics(
            resource_type=resource_type, resource_id=resource_id, from_date=from_date
        )

        # Assert
        assert isinstance(result, FlowMetricsApiResponse)
        assert result.status == 200
        assert result.message == "Ok"
        assert result.metrics is not None

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/{resource_type}/{resource_id}/flow/metrics" in last_request["url"]
        assert last_request["params"]["from"] == from_date

    def test_get_metrics_with_groupby(self, mock_client, mock_http_client):
        """Test get_metrics with groupby parameter."""
        # Arrange
        mock_response = MockResponseBuilder.flow_metrics_api_response()
        mock_http_client.add_response("/data_sets/5061/flow/metrics", mock_response)

        # Act
        mock_client.flows.get_metrics(
            resource_type="data_sets",
            resource_id=5061,
            from_date="2024-01-01",
            groupby="runId",
        )

        # Assert
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["groupby"] == "runId"

    def test_get_metrics_with_orderby(self, mock_client, mock_http_client):
        """Test get_metrics with orderby parameter."""
        # Arrange
        mock_response = MockResponseBuilder.flow_metrics_api_response()
        mock_http_client.add_response("/data_sets/5061/flow/metrics", mock_response)

        # Act
        mock_client.flows.get_metrics(
            resource_type="data_sets",
            resource_id=5061,
            from_date="2024-01-01",
            orderby="created_at",
        )

        # Assert
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["orderby"] == "created_at"

    def test_get_metrics_all_parameters(self, mock_client, mock_http_client):
        """Test get_metrics with all parameters."""
        # Arrange
        mock_response = MockResponseBuilder.flow_metrics_api_response()
        mock_http_client.add_response("/data_sinks/5029/flow/metrics", mock_response)

        # Act
        mock_client.flows.get_metrics(
            resource_type="data_sinks",
            resource_id=5029,
            from_date="2024-01-01",
            to_date="2024-01-31",
            groupby="runId",
            orderby="created_at",
            page=2,
            per_page=100,
        )

        # Assert
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["from"] == "2024-01-01"
        assert last_request["params"]["to"] == "2024-01-31"
        assert last_request["params"]["groupby"] == "runId"
        assert last_request["params"]["orderby"] == "created_at"
        assert last_request["params"]["page"] == 2
        assert last_request["params"]["per_page"] == 100

    def test_copy_and_replace_credentials_source_and_sink(
        self, mock_client, mock_http_client, mock_factory
    ):
        """Test copy_and_replace_credentials updates source and sink credentials."""
        # Arrange
        original_source_id = 500
        original_sink_id = 600
        copied_source_id = 501
        copied_sink_id = 601
        new_source_cred = 20
        new_sink_cred = 30
        origin_node_id = 9999

        # Build a copy response with copied_from_id set
        copy_response = {
            "flows": [
                mock_factory.create_mock_flow_node(
                    origin_node_id=origin_node_id,
                )
            ],
            "data_sources": [
                mock_factory.create_mock_source(
                    id=copied_source_id,
                    copied_from_id=original_source_id,
                    data_credentials_id=10,
                )
            ],
            "data_sinks": [
                mock_factory.create_mock_destination(
                    id=copied_sink_id,
                    copied_from_id=original_sink_id,
                    data_credentials_id=10,
                )
            ],
        }

        # Build a re-fetch response (after credential updates)
        refetch_response = {
            "flows": [
                mock_factory.create_mock_flow_node(
                    origin_node_id=origin_node_id,
                )
            ],
            "data_sources": [
                mock_factory.create_mock_source(
                    id=copied_source_id,
                    copied_from_id=original_source_id,
                    data_credentials_id=new_source_cred,
                )
            ],
            "data_sinks": [
                mock_factory.create_mock_destination(
                    id=copied_sink_id,
                    copied_from_id=original_sink_id,
                    data_credentials_id=new_sink_cred,
                )
            ],
        }

        # Updated source response
        updated_source = mock_factory.create_mock_source(
            id=copied_source_id,
            data_credentials_id=new_source_cred,
        )

        # Updated sink response
        updated_sink = mock_factory.create_mock_destination(
            id=copied_sink_id,
            data_credentials_id=new_sink_cred,
        )

        mock_http_client.add_response("/flows/100/copy", copy_response)
        mock_http_client.add_response(
            f"/data_sources/{copied_source_id}", updated_source
        )
        mock_http_client.add_response(f"/data_sinks/{copied_sink_id}", updated_sink)
        mock_http_client.add_response(f"/flows/{origin_node_id}", refetch_response)

        # Act
        result = mock_client.flows.copy_and_replace_credentials(
            flow_id=100,
            resource_credential_mapping={
                original_source_id: new_source_cred,
                original_sink_id: new_sink_cred,
            },
        )

        # Assert
        assert isinstance(result, FlowResponse)

        # Verify copy request used reuse_data_credentials=True
        copy_requests = mock_http_client.get_requests_by_url_pattern("/flows/100/copy")
        assert len(copy_requests) == 1
        assert copy_requests[0]["json"]["reuse_data_credentials"] is True

        # Verify source update request
        source_updates = mock_http_client.get_requests_by_url_pattern(
            f"/data_sources/{copied_source_id}"
        )
        put_source = [r for r in source_updates if r["method"] == "PUT"]
        assert len(put_source) == 1
        assert put_source[0]["json"]["data_credentials_id"] == new_source_cred

        # Verify sink update request
        sink_updates = mock_http_client.get_requests_by_url_pattern(
            f"/data_sinks/{copied_sink_id}"
        )
        put_sink = [r for r in sink_updates if r["method"] == "PUT"]
        assert len(put_sink) == 1
        assert put_sink[0]["json"]["data_credentials_id"] == new_sink_cred

    def test_copy_and_replace_credentials_partial_mapping(
        self, mock_client, mock_http_client, mock_factory
    ):
        """Test that resources not in the mapping are left untouched."""
        # Arrange
        original_source_id = 500
        original_sink_a_id = 600
        original_sink_b_id = 700
        copied_source_id = 501
        copied_sink_a_id = 601
        copied_sink_b_id = 701
        new_cred = 20
        origin_node_id = 9999

        copy_response = {
            "flows": [
                mock_factory.create_mock_flow_node(origin_node_id=origin_node_id)
            ],
            "data_sources": [
                mock_factory.create_mock_source(
                    id=copied_source_id,
                    copied_from_id=original_source_id,
                    data_credentials_id=10,
                )
            ],
            "data_sinks": [
                mock_factory.create_mock_destination(
                    id=copied_sink_a_id,
                    copied_from_id=original_sink_a_id,
                    data_credentials_id=10,
                ),
                mock_factory.create_mock_destination(
                    id=copied_sink_b_id,
                    copied_from_id=original_sink_b_id,
                    data_credentials_id=50,
                ),
            ],
        }

        refetch_response = {
            "flows": [
                mock_factory.create_mock_flow_node(origin_node_id=origin_node_id)
            ],
            "data_sources": [
                mock_factory.create_mock_source(
                    id=copied_source_id,
                    copied_from_id=original_source_id,
                    data_credentials_id=new_cred,
                )
            ],
            "data_sinks": [
                mock_factory.create_mock_destination(
                    id=copied_sink_a_id,
                    copied_from_id=original_sink_a_id,
                    data_credentials_id=new_cred,
                ),
                mock_factory.create_mock_destination(
                    id=copied_sink_b_id,
                    copied_from_id=original_sink_b_id,
                    data_credentials_id=50,
                ),
            ],
        }

        updated_source = mock_factory.create_mock_source(
            id=copied_source_id, data_credentials_id=new_cred
        )
        updated_sink_a = mock_factory.create_mock_destination(
            id=copied_sink_a_id, data_credentials_id=new_cred
        )

        mock_http_client.add_response("/flows/100/copy", copy_response)
        mock_http_client.add_response(
            f"/data_sources/{copied_source_id}", updated_source
        )
        mock_http_client.add_response(f"/data_sinks/{copied_sink_a_id}", updated_sink_a)
        mock_http_client.add_response(f"/flows/{origin_node_id}", refetch_response)

        # Act — only map source and sink A, leave sink B untouched
        result = mock_client.flows.copy_and_replace_credentials(
            flow_id=100,
            resource_credential_mapping={
                original_source_id: new_cred,
                original_sink_a_id: new_cred,
                # original_sink_b_id intentionally NOT mapped
            },
        )

        # Assert
        assert isinstance(result, FlowResponse)

        # Sink B should NOT have been updated (no PUT to its endpoint)
        sink_b_requests = mock_http_client.get_requests_by_url_pattern(
            f"/data_sinks/{copied_sink_b_id}"
        )
        put_sink_b = [r for r in sink_b_requests if r["method"] == "PUT"]
        assert len(put_sink_b) == 0

    def test_copy_and_replace_credentials_preserves_copy_options(
        self, mock_client, mock_http_client, mock_factory
    ):
        """Test that extra copy options are preserved and reuse_data_credentials is forced True."""
        # Arrange
        origin_node_id = 9999
        copy_response = {
            "flows": [
                mock_factory.create_mock_flow_node(origin_node_id=origin_node_id)
            ],
            "data_sources": [],
            "data_sinks": [],
        }
        refetch_response = copy_response.copy()

        mock_http_client.add_response("/flows/100/copy", copy_response)
        mock_http_client.add_response(f"/flows/{origin_node_id}", refetch_response)

        # Act — pass copy_options with reuse_data_credentials=False (should be overridden)
        result = mock_client.flows.copy_and_replace_credentials(
            flow_id=100,
            resource_credential_mapping={},
            copy_options=FlowCopyOptions(
                reuse_data_credentials=False,
                copy_access_controls=True,
                owner_id=42,
            ),
        )

        # Assert
        assert isinstance(result, FlowResponse)

        copy_requests = mock_http_client.get_requests_by_url_pattern("/flows/100/copy")
        assert len(copy_requests) == 1
        # reuse_data_credentials should be forced True
        assert copy_requests[0]["json"]["reuse_data_credentials"] is True
        # Other options should be preserved
        assert copy_requests[0]["json"]["copy_access_controls"] is True
        assert copy_requests[0]["json"]["owner_id"] == 42

    def test_copy_and_replace_credentials_empty_mapping(
        self, mock_client, mock_http_client, mock_factory
    ):
        """Test with empty mapping — just copies the flow with no credential changes."""
        # Arrange
        origin_node_id = 9999
        copy_response = {
            "flows": [
                mock_factory.create_mock_flow_node(origin_node_id=origin_node_id)
            ],
            "data_sources": [
                mock_factory.create_mock_source(
                    id=501, copied_from_id=500, data_credentials_id=10
                )
            ],
            "data_sinks": [
                mock_factory.create_mock_destination(
                    id=601, copied_from_id=600, data_credentials_id=10
                )
            ],
        }
        refetch_response = copy_response.copy()

        mock_http_client.add_response("/flows/100/copy", copy_response)
        mock_http_client.add_response(f"/flows/{origin_node_id}", refetch_response)

        # Act
        result = mock_client.flows.copy_and_replace_credentials(
            flow_id=100,
            resource_credential_mapping={},
        )

        # Assert — no PUT requests should have been made
        assert isinstance(result, FlowResponse)
        put_requests = mock_http_client.get_requests_by_method("PUT")
        assert len(put_requests) == 0

    def test_copy_and_replace_credentials_with_target_project(
        self, mock_client, mock_http_client, mock_factory
    ):
        """Test that target_project_id moves the copied flow into the project."""
        # Arrange
        original_source_id = 500
        copied_source_id = 501
        new_cred = 20
        origin_node_id = 9999
        target_project_id = 42

        copy_response = {
            "flows": [
                mock_factory.create_mock_flow_node(origin_node_id=origin_node_id)
            ],
            "data_sources": [
                mock_factory.create_mock_source(
                    id=copied_source_id,
                    copied_from_id=original_source_id,
                    data_credentials_id=10,
                )
            ],
            "data_sinks": [],
        }

        updated_source = mock_factory.create_mock_source(
            id=copied_source_id, data_credentials_id=new_cred
        )

        # add_flows response (list of project data flows)
        add_flows_response = [
            {"id": 1, "project_id": target_project_id, "flow_node_id": origin_node_id}
        ]

        refetch_response = {
            "flows": [
                mock_factory.create_mock_flow_node(origin_node_id=origin_node_id)
            ],
            "data_sources": [
                mock_factory.create_mock_source(
                    id=copied_source_id,
                    copied_from_id=original_source_id,
                    data_credentials_id=new_cred,
                )
            ],
            "data_sinks": [],
        }

        mock_http_client.add_response("/flows/100/copy", copy_response)
        mock_http_client.add_response(
            f"/data_sources/{copied_source_id}", updated_source
        )
        mock_http_client.add_response(
            f"/projects/{target_project_id}/flows", add_flows_response
        )
        mock_http_client.add_response(f"/flows/{origin_node_id}", refetch_response)

        # Act
        result = mock_client.flows.copy_and_replace_credentials(
            flow_id=100,
            resource_credential_mapping={original_source_id: new_cred},
            target_project_id=target_project_id,
        )

        # Assert
        assert isinstance(result, FlowResponse)

        # Verify add_flows was called with the correct project and flow
        project_requests = mock_http_client.get_requests_by_url_pattern(
            f"/projects/{target_project_id}/flows"
        )
        put_project = [r for r in project_requests if r["method"] == "PUT"]
        assert len(put_project) == 1
        assert put_project[0]["json"]["flows"] == [origin_node_id]

    def test_copy_and_replace_credentials_no_target_project(
        self, mock_client, mock_http_client, mock_factory
    ):
        """Test that no project request is made when target_project_id is None."""
        # Arrange
        origin_node_id = 9999
        copy_response = {
            "flows": [
                mock_factory.create_mock_flow_node(origin_node_id=origin_node_id)
            ],
            "data_sources": [],
            "data_sinks": [],
        }
        refetch_response = copy_response.copy()

        mock_http_client.add_response("/flows/100/copy", copy_response)
        mock_http_client.add_response(f"/flows/{origin_node_id}", refetch_response)

        # Act — no target_project_id
        result = mock_client.flows.copy_and_replace_credentials(
            flow_id=100,
            resource_credential_mapping={},
        )

        # Assert — no project requests should have been made
        assert isinstance(result, FlowResponse)
        project_requests = mock_http_client.get_requests_by_url_pattern("/projects/")
        assert len(project_requests) == 0
