import logging
import warnings
from typing import Any, Dict, Optional, Union

from nexla_sdk.models.metrics.enums import ResourceType
from nexla_sdk.models.metrics.responses import (
    MetricsByRunResponse,
    MetricsResponse,
    ResourceFlowLogsResponse,
    ResourceFlowMetricsResponse,
)
from nexla_sdk.resources.base_resource import BaseResource

logger = logging.getLogger(__name__)


def _warn_if_seconds_timestamp(value: int, param_name: str) -> None:
    if isinstance(value, (int, float)) and 0 < abs(value) < 1e10:
        warnings.warn(
            f"{param_name} looks like seconds; API expects milliseconds",
            RuntimeWarning,
            stacklevel=3,
        )


class MetricsResource(BaseResource):
    """
    Resource for retrieving metrics.

    Note: This resource already uses strongly-typed Pydantic models
    for all return types and doesn't follow standard CRUD patterns,
    so no additional typed overrides are needed.
    """

    def __init__(self, client):
        super().__init__(client)
        self._path = ""  # Metrics endpoints are distributed

    def get_resource_daily_metrics(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        from_date: str,
        to_date: Optional[str] = None,
    ) -> MetricsResponse:
        """
        Get daily metrics for a resource.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (optional)

        Returns:
            Daily metrics
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        path = f"/{resource_type_value}/{resource_id}/metrics"
        params = {"from": from_date, "aggregate": 1}
        if to_date:
            params["to"] = to_date

        response = self._make_request("GET", path, params=params)
        return MetricsResponse(**response)

    def get_resource_metrics_by_run(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        groupby: Optional[str] = None,
        orderby: Optional[str] = None,
        page: Optional[int] = None,
        size: Optional[int] = None,
    ) -> MetricsByRunResponse:
        """
        Get metrics by run for a resource.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            groupby: Group by field (runId, lastWritten)
            orderby: Order by field (runId, lastWritten)
            page: Page number
            size: Page size

        Returns:
            Metrics by run
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        path = f"/{resource_type_value}/{resource_id}/metrics/run_summary"
        params = {}
        if groupby:
            params["groupby"] = groupby
        if orderby:
            params["orderby"] = orderby
        if page:
            params["page"] = page
        if size:
            params["size"] = size

        response = self._make_request("GET", path, params=params)
        return MetricsByRunResponse(**response)

    def get_rate_limits(self) -> Dict[str, Any]:
        """
        Get current rate limit and usage.

        Returns:
            Rate limit information
        """
        path = "/limits"
        return self._make_request("GET", path)

    def publish_raw(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Publish raw metrics (super user only)."""
        return self._make_request("POST", "/metrics/raw", json=payload)

    def get_resource_flow_metrics(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        metric_type: str = None,
    ) -> Dict[str, Any]:
        """
        Get flow metrics for a specific resource.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            metric_type: Specific metric type to retrieve (optional)

        Returns:
            Flow metrics for the resource
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        if metric_type:
            path = f"/{resource_type_value}/{resource_id}/flow/{metric_type}"
        else:
            path = f"/{resource_type_value}/{resource_id}/flow"
        return self._make_request("GET", path)

    def get_flow_metrics_summary(self, period: str) -> Dict[str, Any]:
        """
        Get flow metrics summary for a given period.

        Args:
            period: Time period for the summary (e.g., 'daily', 'total')

        Returns:
            Flow metrics summary
        """
        path = f"/data_flows/metrics/{period}"
        return self._make_request("GET", path)

    # Convenience wrappers for flow-level logs/metrics
    def get_flow_metrics(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        from_date: str,
        to_date: Optional[str] = None,
        groupby: Optional[str] = None,
        orderby: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Union[ResourceFlowMetricsResponse, Dict[str, Any]]:
        """
        Get flow metrics for a flow node keyed by resource ID.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (optional)
            groupby: Group metrics by field
            orderby: Order metrics by field
            page: Page number
            per_page: Items per page

        Returns:
            ResourceFlowMetricsResponse with metrics data and pagination,
            or raw dict if response doesn't match expected schema.
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        path = f"/{resource_type_value}/{resource_id}/flow/metrics"
        params = {"from": from_date}
        if to_date:
            params["to"] = to_date
        if groupby:
            params["groupby"] = groupby
        if orderby:
            params["orderby"] = orderby
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", path, params=params)
        try:
            return ResourceFlowMetricsResponse.model_validate(response)
        except Exception as exc:
            logger.debug(
                "ResourceFlowMetricsResponse validation failed, returning raw dict: %s",
                exc,
            )
            return response

    def get_flow_logs(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        run_id: int,
        from_ts: int,
        to_ts: Optional[int] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Union[ResourceFlowLogsResponse, Dict[str, Any]]:
        """
        Get flow logs for a flow run keyed by resource ID.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            run_id: Run ID
            from_ts: Start timestamp (Unix timestamp in milliseconds)
            to_ts: End timestamp in milliseconds (optional)
            page: Page number
            per_page: Items per page

        Returns:
            ResourceFlowLogsResponse with log entries and pagination metadata,
            or raw dict if response doesn't match expected schema.
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        path = f"/{resource_type_value}/{resource_id}/flow/logs"
        params = {"run_id": run_id, "from": from_ts}
        _warn_if_seconds_timestamp(from_ts, "from_ts")
        if to_ts is not None:
            _warn_if_seconds_timestamp(to_ts, "to_ts")
            params["to"] = to_ts
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", path, params=params)
        try:
            return ResourceFlowLogsResponse.model_validate(response)
        except Exception as exc:
            logger.debug(
                "ResourceFlowLogsResponse validation failed, returning raw dict: %s",
                exc,
            )
            return response
