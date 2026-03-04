from typing import Any, Dict, Optional

from nexla_sdk.models.metrics.enums import ResourceType
from nexla_sdk.models.metrics.responses import MetricsByRunResponse, MetricsResponse
from nexla_sdk.resources.base_resource import BaseResource


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
        resource_type: ResourceType,
        resource_id: int,
        from_date: str,
        to_date: Optional[str] = None,
    ) -> MetricsResponse:
        """
        Get daily metrics for a resource.

        Args:
            resource_type: Type of resource (data_sources, data_sets, data_sinks)
            resource_id: Resource ID
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (optional)

        Returns:
            Daily metrics
        """
        path = f"/{resource_type}/{resource_id}/metrics"
        params = {"from": from_date, "aggregate": 1}
        if to_date:
            params["to"] = to_date

        response = self._make_request("GET", path, params=params)
        return MetricsResponse(**response)

    def get_resource_metrics_by_run(
        self,
        resource_type: ResourceType,
        resource_id: int,
        groupby: Optional[str] = None,
        orderby: Optional[str] = None,
        page: Optional[int] = None,
        size: Optional[int] = None,
    ) -> MetricsByRunResponse:
        """
        Get metrics by run for a resource.

        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            groupby: Group by field (runId, lastWritten)
            orderby: Order by field (runId, lastWritten)
            page: Page number
            size: Page size

        Returns:
            Metrics by run
        """
        path = f"/{resource_type}/{resource_id}/metrics/run_summary"
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

    def get_resource_flow_metrics(
        self,
        resource_type: str,
        resource_id: int,
        metric_type: str = None,
    ) -> Dict[str, Any]:
        """
        Get flow metrics for a specific resource.

        Args:
            resource_type: Type of resource (e.g., data_source, data_set, data_sink)
            resource_id: Resource ID
            metric_type: Specific metric type to retrieve (optional)

        Returns:
            Flow metrics for the resource
        """
        if metric_type:
            path = f"/{resource_type}s/{resource_id}/flow/{metric_type}"
        else:
            path = f"/{resource_type}s/{resource_id}/flow"
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
        resource_type: str,
        resource_id: int,
        from_date: str,
        to_date: str = None,
        groupby: str = None,
        orderby: str = None,
        page: int = None,
        per_page: int = None,
    ) -> Dict[str, Any]:
        path = f"/data_flows/{resource_type}/{resource_id}/metrics"
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
        return self._make_request("GET", path, params=params)

    def get_flow_logs(
        self,
        resource_type: str,
        resource_id: int,
        run_id: int,
        from_ts: int,
        to_ts: int = None,
        page: int = None,
        per_page: int = None,
    ) -> Dict[str, Any]:
        path = f"/data_flows/{resource_type}/{resource_id}/logs"
        params = {"run_id": run_id, "from": from_ts}
        if to_ts is not None:
            params["to"] = to_ts
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self._make_request("GET", path, params=params)
