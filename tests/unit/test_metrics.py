import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.models.metrics.enums import ResourceType, UserMetricResourceType
from nexla_sdk.models.metrics.responses import (
    MetricsByRunResponse,
    MetricsResponse,
    ResourceFlowLogsResponse,
    ResourceFlowMetricsResponse,
)
from tests.utils.mock_builders import MockResponseBuilder

pytestmark = pytest.mark.unit


@pytest.fixture
def client(mock_client: NexlaClient) -> NexlaClient:
    return mock_client


class TestMetricsResource:
    def test_resource_metrics_rate_limits_and_flow_helpers(
        self, client, mock_http_client
    ):
        mock_http_client.queue_response({"status": 200, "metrics": []})
        m = client.metrics.get_resource_daily_metrics(
            ResourceType.DATA_SOURCES,
            42,
            from_date="2024-01-01",
            to_date="2024-01-31",
        )
        assert isinstance(m, MetricsResponse)
        mock_http_client.assert_request_made("GET", "/data_sources/42/metrics")

        mock_http_client.queue_response(
            {"status": 200, "metrics": {"data": [], "meta": {}}}
        )
        br = client.metrics.get_resource_metrics_by_run(
            ResourceType.DATA_SOURCES,
            42,
            groupby="runId",
            orderby="lastWritten",
            page=1,
            size=10,
        )
        assert isinstance(br, MetricsByRunResponse)
        mock_http_client.assert_request_made(
            "GET", "/data_sources/42/metrics/run_summary"
        )

        mock_http_client.clear_responses()
        mock_http_client.add_response("/limits", {"rate_limit": {"limit": 1000}})
        rl = client.metrics.get_rate_limits()
        assert "rate_limit" in rl

        mock_http_client.clear_responses()
        mock_http_client.add_response("/data_sources/1/flow/metrics", {"status": "ok"})
        fm = client.metrics.get_flow_metrics(
            "data_sources",
            1,
            from_date="2024-01-01",
            to_date="2024-01-31",
            groupby="runId",
            orderby="lastWritten",
            page=1,
            per_page=50,
        )
        assert fm.get("status") == "ok"

        mock_http_client.clear_responses()
        mock_http_client.add_response("/data_sources/1/flow/logs", {"status": "ok"})
        fl = client.metrics.get_flow_logs(
            "data_sources",
            1,
            run_id=123,
            from_ts=1000000000000,
            to_ts=2000000000000,
            page=1,
            per_page=100,
        )
        assert fl.get("status") == "ok"

    def test_resource_flow_metrics_accepts_canonical_resource_type(
        self, client, mock_http_client
    ):
        mock_http_client.add_response("/data_sources/42/flow", {"status": "ok"})

        metrics = client.metrics.get_resource_flow_metrics("data_sources", 42)

        assert metrics["status"] == "ok"
        mock_http_client.assert_request_made("GET", "/data_sources/42/flow")

        mock_http_client.clear_requests()
        mock_http_client.clear_responses()
        mock_http_client.add_response("/data_sets/43/flow/records", {"status": "ok"})

        metrics = client.metrics.get_resource_flow_metrics(
            ResourceType.DATA_SETS, 43, metric_type="records"
        )

        assert metrics["status"] == "ok"
        mock_http_client.assert_request_made("GET", "/data_sets/43/flow/records")

    def test_resource_flow_metrics_rejects_singular_resource_type(
        self, client, mock_http_client
    ):
        with pytest.raises(ValueError, match="Invalid resource_type 'data_set'"):
            client.metrics.get_resource_flow_metrics("data_set", 43)

        assert mock_http_client.requests == []

    def test_flow_helpers_accept_resource_type_enum(self, client, mock_http_client):
        mock_http_client.add_response(
            "/data_sinks/44/flow/metrics",
            MockResponseBuilder.flow_metrics_api_response(),
        )

        metrics = client.metrics.get_flow_metrics(
            ResourceType.DATA_SINKS,
            44,
            from_date="2024-01-01",
        )

        assert isinstance(metrics, ResourceFlowMetricsResponse)
        assert metrics.status == 200
        mock_http_client.assert_request_made("GET", "/data_sinks/44/flow/metrics")

        mock_http_client.clear_requests()
        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/data_sources/45/flow/logs",
            MockResponseBuilder.flow_logs_response(log_count=1),
        )

        logs = client.metrics.get_flow_logs(
            ResourceType.DATA_SOURCES,
            45,
            run_id=123,
            from_ts=1000000000000,
        )

        assert isinstance(logs, ResourceFlowLogsResponse)
        assert logs.status == 200
        assert len(logs.logs) == 1
        mock_http_client.assert_request_made("GET", "/data_sources/45/flow/logs")

    def test_flow_helpers_return_raw_dict_for_unmodeled_response(
        self, client, mock_http_client
    ):
        mock_http_client.add_response("/data_sinks/44/flow/metrics", {"status": "ok"})

        metrics = client.metrics.get_flow_metrics(
            ResourceType.DATA_SINKS,
            44,
            from_date="2024-01-01",
        )

        assert metrics == {"status": "ok"}

    def test_flow_logs_warn_for_seconds_timestamp(self, client, mock_http_client):
        mock_http_client.add_response("/data_sources/45/flow/logs", {"status": "ok"})

        with pytest.warns(RuntimeWarning, match="from_ts looks like seconds"):
            client.metrics.get_flow_logs(
                ResourceType.DATA_SOURCES,
                45,
                run_id=123,
                from_ts=1700000000,
            )

    def test_user_daily_metrics_serializes_resource_type_enum(
        self, client, mock_http_client
    ):
        mock_http_client.add_response("/users/7/metrics", {"status": "ok"})

        metrics = client.users.get_daily_metrics(
            7,
            UserMetricResourceType.SOURCE,
            from_date="2024-01-01",
        )

        assert metrics["status"] == "ok"
        mock_http_client.assert_request_made(
            "GET",
            "/users/7/metrics",
            params={"resource_type": "SOURCE", "from": "2024-01-01", "aggregate": 1},
        )


class TestNewMetricsMethods:
    """Tests for newly added metrics methods."""

    @pytest.fixture
    def client(self, mock_client: NexlaClient) -> NexlaClient:
        return mock_client

    def test_publish_raw(self, client, mock_http_client):
        """Test publish_raw sends POST to /metrics/raw."""
        mock_http_client.clear_responses()
        mock_http_client.add_response("/metrics/raw", {"status": "ok"})

        result = client.metrics.publish_raw({"event": "test"})

        assert result == {"status": "ok"}
        mock_http_client.assert_request_made("POST", "/metrics/raw")

    def test_get_flow_metrics_summary(self, client, mock_http_client):
        """Test get_flow_metrics_summary with a period."""
        mock_http_client.clear_responses()
        mock_http_client.add_response("/data_flows/metrics/daily", {"status": "ok"})

        result = client.metrics.get_flow_metrics_summary(period="daily")

        assert result == {"status": "ok"}
        mock_http_client.assert_request_made("GET", "/data_flows/metrics/daily")
