"""Unit tests for flows resource."""

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
        from_ts = 1704067200
        mock_response = MockResponseBuilder.flow_logs_response(log_count=3)
        mock_http_client.add_response(
            f"/data_flows/{resource_type}/{resource_id}/logs", mock_response
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

        # Verify request
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/data_flows/{resource_type}/{resource_id}/logs" in last_request["url"]
        assert last_request["params"]["run_id"] == run_id
        assert last_request["params"]["from"] == from_ts

    def test_get_logs_with_pagination(self, mock_client, mock_http_client):
        """Test get_logs with pagination parameters."""
        # Arrange
        mock_response = MockResponseBuilder.flow_logs_response()
        mock_http_client.add_response("/data_flows/data_sets/5061/logs", mock_response)

        # Act
        mock_client.flows.get_logs(
            resource_type="data_sets",
            resource_id=5061,
            run_id=100,
            from_ts=1704067200,
            page=2,
            per_page=25,
        )

        # Assert
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["page"] == 2
        assert last_request["params"]["per_page"] == 25

    def test_get_logs_all_parameters(self, mock_client, mock_http_client):
        """Test get_logs with all parameters."""
        # Arrange
        mock_response = MockResponseBuilder.flow_logs_response()
        mock_http_client.add_response("/data_flows/data_sinks/5029/logs", mock_response)

        # Act
        mock_client.flows.get_logs(
            resource_type="data_sinks",
            resource_id=5029,
            run_id=456,
            from_ts=1704067200,
            to_ts=1704153600,
            page=1,
            per_page=50,
        )

        # Assert
        last_request = mock_http_client.get_last_request()
        assert last_request["params"]["run_id"] == 456
        assert last_request["params"]["from"] == 1704067200
        assert last_request["params"]["to"] == 1704153600
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

    def test_get_metrics_success(self, mock_client, mock_http_client):
        """Test get_metrics returns FlowMetricsApiResponse model."""
        # Arrange
        resource_type = "data_sources"
        resource_id = 5023
        from_date = "2024-01-01"
        mock_response = MockResponseBuilder.flow_metrics_api_response()
        mock_http_client.add_response(
            f"/data_flows/{resource_type}/{resource_id}/metrics", mock_response
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
        assert (
            f"/data_flows/{resource_type}/{resource_id}/metrics" in last_request["url"]
        )
        assert last_request["params"]["from"] == from_date

    def test_get_metrics_with_groupby(self, mock_client, mock_http_client):
        """Test get_metrics with groupby parameter."""
        # Arrange
        mock_response = MockResponseBuilder.flow_metrics_api_response()
        mock_http_client.add_response(
            "/data_flows/data_sets/5061/metrics", mock_response
        )

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
        mock_http_client.add_response(
            "/data_flows/data_sets/5061/metrics", mock_response
        )

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
        mock_http_client.add_response(
            "/data_flows/data_sinks/5029/metrics", mock_response
        )

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
