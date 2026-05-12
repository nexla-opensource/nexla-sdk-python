import logging
import warnings
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.destinations.requests import DestinationUpdate
from nexla_sdk.models.flows.requests import FlowCopyOptions
from nexla_sdk.models.projects.requests import ProjectFlowList
from nexla_sdk.models.flows.responses import (
    DocsRecommendation,
    FlowLogsResponse,
    FlowMetricsApiResponse,
    FlowResponse,
)
from nexla_sdk.models.metrics.enums import ResourceType
from nexla_sdk.models.sources.requests import SourceUpdate
from nexla_sdk.resources.base_resource import BaseResource

logger = logging.getLogger(__name__)


def _iso_date_to_unix_seconds(value: Any) -> Any:
    """
    Convert a YYYY-MM-DD string to a UTC unix-seconds integer for admin-api
    log endpoints, which run inputs through ``DateInterval.unix_to_db_datetime_str``.

    Numeric inputs (int/float, or all-digit strings) pass through unchanged so
    callers that already use unix timestamps keep working. Unrecognised values
    pass through unchanged for the server to handle. ``None`` returns ``None``.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    try:
        dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except (TypeError, ValueError):
        return value


class FlowsResource(BaseResource):
    """Resource for managing data flows."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/flows"
        self._model_class = FlowResponse

    def list(
        self,
        flows_only: bool = False,
        include_run_metrics: bool = False,
        access_role: Optional[str] = None,
        **kwargs,
    ) -> List[FlowResponse]:
        """
        List flows with optional filters.

        Args:
            flows_only: Only return flow structure without resource details
            include_run_metrics: Include run metrics in response
            access_role: Filter by access role (owner, collaborator, operator, admin)
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of flows

        Examples:
            client.flows.list(flows_only=True)
            client.flows.list(include_run_metrics=True, page=1, per_page=50)
            client.flows.list(access_role="owner")
        """
        params = kwargs.copy()
        if flows_only:
            params["flows_only"] = 1
        if include_run_metrics:
            params["include_run_metrics"] = 1
        if access_role:
            params["access_role"] = access_role

        response = self._make_request("GET", self._path, params=params)
        # API returns a single FlowResponse object for list
        return [self._parse_response(response)]

    def get(
        self, flow_id: int, flows_only: bool = False, include_run_metrics: bool = False
    ) -> FlowResponse:
        """
        Get flow by ID.

        Args:
            flow_id: Flow ID
            flows_only: Only return flow structure without resource details
            include_run_metrics: Include run metrics in response

        Returns:
            Flow response
        """
        path = f"{self._path}/{flow_id}"
        params = {}
        if flows_only:
            params["flows_only"] = 1
        if include_run_metrics:
            params["include_run_metrics"] = 1
        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def get_by_resource(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        flows_only: bool = False,
    ) -> FlowResponse:
        """
        Get flow by resource ID.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            flows_only: Only return flow structure

        Returns:
            Flow response
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        path = f"/{resource_type_value}/{resource_id}/flow"
        params = {"flows_only": 1} if flows_only else {}

        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def activate(
        self, flow_id: int, all: bool = False, full_tree: bool = False
    ) -> FlowResponse:
        """
        Activate a flow.

        Args:
            flow_id: Flow ID
            all: Activate entire flow tree

        Returns:
            Activated flow
        """
        path = f"{self._path}/{flow_id}/activate"
        params = {}
        if all:
            params["all"] = 1
        if full_tree:
            params["full_tree"] = 1

        response = self._make_request("PUT", path, params=params)
        return self._parse_response(response)

    def pause(
        self,
        flow_id: int,
        all: bool = False,
        full_tree: bool = False,
        async_mode: bool = False,
    ) -> FlowResponse:
        """
        Pause a flow.

        Args:
            flow_id: Flow ID
            all: Pause entire flow tree
            full_tree: Alias for 'all' parameter
            async_mode: Execute pause asynchronously

        Returns:
            Paused flow
        """
        path = f"{self._path}/{flow_id}/pause"
        params = {}
        if all:
            params["all"] = 1
        if full_tree:
            params["full_tree"] = 1
        if async_mode:
            params["async"] = 1

        response = self._make_request("PUT", path, params=params)
        return self._parse_response(response)

    def copy(
        self, flow_id: int, options: Optional[FlowCopyOptions] = None
    ) -> FlowResponse:
        """
        Copy a flow.

        Args:
            flow_id: Flow ID
            options: Copy options

        Returns:
            Copied flow
        """
        return super().copy(flow_id, options)

    def copy_and_replace_credentials(
        self,
        flow_id: int,
        resource_credential_mapping: Dict[int, int],
        copy_options: Optional[FlowCopyOptions] = None,
        target_project_id: Optional[int] = None,
    ) -> FlowResponse:
        """Copy a flow and replace credentials on specified resources.

        This convenience method copies a flow with ``reuse_data_credentials=True``
        so that all copied resources initially keep their original credentials,
        then updates the credentials for the resources listed in the mapping.

        The mapping keys are **original** resource IDs (source or sink IDs from
        the original flow).  After the copy, the method looks up the
        corresponding *copied* resources (via their ``copied_from_id`` field)
        and updates each one's ``data_credentials_id`` to the value specified
        in the mapping.

        Resources whose original IDs are **not** present in the mapping are
        left untouched and keep whatever credential they were copied with.

        Args:
            flow_id: The ID of the flow to copy.
            resource_credential_mapping: A dict mapping original resource IDs
                to the new credential IDs that should be set on the copied
                versions of those resources.
                ``{original_resource_id: new_credential_id}``
            copy_options: Optional additional copy options.  The
                ``reuse_data_credentials`` flag will always be forced to
                ``True`` regardless of the value passed here.
            target_project_id: Optional project ID to move the copied flow
                into.  When set, the copied flow is added to the specified
                project after credential replacement.

        Returns:
            The copied ``FlowResponse`` with credentials updated.

        Examples:
            Copy a flow and replace the credential on the source and one sink::

                copied = client.flows.copy_and_replace_credentials(
                    flow_id=100,
                    resource_credential_mapping={
                        500: 20,  # source 500 -> cred 20
                        600: 30,  # sink 600 -> cred 30
                    },
                )
        """
        # Build copy options, always forcing reuse_data_credentials=True
        if copy_options is None:
            copy_options = FlowCopyOptions(reuse_data_credentials=True)
        else:
            copy_options = copy_options.model_copy(
                update={"reuse_data_credentials": True}
            )

        # Step 1: Copy the flow
        copied_flow = self.copy(flow_id, copy_options)

        # Step 2: Update credentials on copied resources that match the mapping
        if copied_flow.data_sources:
            for source in copied_flow.data_sources:
                if (
                    source.copied_from_id is not None
                    and source.copied_from_id in resource_credential_mapping
                ):
                    new_cred_id = resource_credential_mapping[source.copied_from_id]
                    self.client.sources.update(
                        source.id,
                        SourceUpdate(data_credentials_id=new_cred_id),
                    )

        if copied_flow.data_sinks:
            for sink in copied_flow.data_sinks:
                if (
                    sink.copied_from_id is not None
                    and sink.copied_from_id in resource_credential_mapping
                ):
                    new_cred_id = resource_credential_mapping[sink.copied_from_id]
                    self.client.destinations.update(
                        sink.id,
                        DestinationUpdate(data_credentials_id=new_cred_id),
                    )

        # Step 3: Optionally move the copied flow into a target project
        origin_node_id = copied_flow.flows[0].origin_node_id
        if target_project_id is not None:
            self.client.projects.add_flows(
                target_project_id,
                ProjectFlowList(flows=[origin_node_id]),
            )

        # Step 4: Re-fetch the flow to return an up-to-date response
        return self.get(origin_node_id)

    def delete(self, flow_id: int) -> Dict[str, Any]:
        """
        Delete flow.

        Args:
            flow_id: Flow ID

        Returns:
            Response with status
        """
        return super().delete(flow_id)

    def delete_by_resource(
        self, resource_type: Union[ResourceType, str], resource_id: int
    ) -> Dict[str, Any]:
        """
        Delete flow by resource ID.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID

        Returns:
            Response status
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        path = f"/{resource_type_value}/{resource_id}/flow"
        return self._make_request("DELETE", path)

    def activate_by_resource(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        all: bool = False,
        full_tree: bool = False,
    ) -> FlowResponse:
        """
        Activate flow by resource ID.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            all: Activate entire flow tree

        Returns:
            Activated flow
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        path = f"/{resource_type_value}/{resource_id}/activate"
        params = {}
        if all:
            params["all"] = 1
        if full_tree:
            params["full_tree"] = 1

        response = self._make_request("PUT", path, params=params)
        return self._parse_response(response)

    def pause_by_resource(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        all: bool = False,
        full_tree: bool = False,
    ) -> FlowResponse:
        """
        Pause flow by resource ID.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            all: Pause entire flow tree

        Returns:
            Paused flow
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        path = f"/{resource_type_value}/{resource_id}/pause"
        params = {}
        if all:
            params["all"] = 1
        if full_tree:
            params["full_tree"] = 1

        response = self._make_request("PUT", path, params=params)
        return self._parse_response(response)

    def docs_recommendation(
        self, flow_id: int
    ) -> Union[DocsRecommendation, Dict[str, Any]]:
        """Generate AI suggestion for flow documentation.

        Args:
            flow_id: Flow ID

        Returns:
            DocsRecommendation with AI-generated documentation suggestion,
            or raw dict if response doesn't match expected schema.
        """
        path = f"{self._path}/{flow_id}/docs/recommendation"
        response = self._make_request("POST", path)
        try:
            return DocsRecommendation.model_validate(response)
        except Exception:
            return response

    def get_flow_logs(
        self,
        flow_id: int,
        from_date: str = None,
        to_date: str = None,
        severity: str = None,
        run_id: int = None,
        page: int = None,
        per_page: int = None,
    ) -> Dict[str, Any]:
        """
        Get execution logs for a specific flow.

        Args:
            flow_id: Flow ID
            from_date: Start date filter (YYYY-MM-DD)
            to_date: End date filter (YYYY-MM-DD)
            severity: Filter by log severity
            run_id: Filter by specific run ID
            page: Page number for pagination
            per_page: Items per page

        Returns:
            Flow execution logs
        """
        path = f"{self._path}/{flow_id}/logs"
        params = {}
        from_ts = _iso_date_to_unix_seconds(from_date)
        if from_ts is not None:
            params["from"] = from_ts
        to_ts = _iso_date_to_unix_seconds(to_date)
        if to_ts is not None:
            params["to"] = to_ts
        if severity is not None:
            params["severity"] = severity
        if run_id is not None:
            params["run_id"] = run_id
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self._make_request("GET", path, params=params)

    def search_flow_logs(
        self,
        flow_id: int,
        run_ids: Union[str, List[int]] = None,
        severity: Union[str, List[str]] = None,
        log_type: Union[str, List[str]] = None,
        search_string: str = None,
        from_date: str = None,
        to_date: str = None,
        size: int = None,
        sort: str = None,
        facets: bool = None,
    ) -> Dict[str, Any]:
        """
        Advanced search for flow execution logs.

        Calls ``POST /flows/:id/logs_v2``. ``severity``/``run_ids``/``log_type``/
        ``search_string`` are sent in the JSON body (the admin-api endpoint
        requires this); ``from``/``to``/``sort``/``size``/``facets`` are sent
        as query parameters.

        Args:
            flow_id: Flow ID
            run_ids: Run IDs to filter — comma-separated string or list of ints
            severity: Log severity (e.g. "ERROR") or list of severities
            log_type: Log type or list of log types
            search_string: Free-text search string
            from_date: Start date filter (YYYY-MM-DD)
            to_date: End date filter (YYYY-MM-DD)
            size: Page size
            sort: Sort directive
            facets: Whether to include facet aggregations in the response

        Returns:
            Matching flow logs
        """
        path = f"{self._path}/{flow_id}/logs_v2"

        body: Dict[str, Any] = {}
        if run_ids is not None:
            if isinstance(run_ids, str):
                parsed = [int(s) for s in run_ids.split(",") if s.strip()]
            else:
                parsed = [int(r) for r in run_ids]
            if parsed:
                body["run_ids"] = parsed
        if severity is not None:
            body["severity"] = [severity] if isinstance(severity, str) else list(severity)
        if log_type is not None:
            body["log_type"] = [log_type] if isinstance(log_type, str) else list(log_type)
        if search_string is not None:
            body["search_string"] = search_string

        params: Dict[str, Any] = {}
        from_ts = _iso_date_to_unix_seconds(from_date)
        if from_ts is not None:
            params["from"] = from_ts
        to_ts = _iso_date_to_unix_seconds(to_date)
        if to_ts is not None:
            params["to"] = to_ts
        if size is not None:
            params["size"] = size
        if sort is not None:
            params["sort"] = sort
        if facets is not None:
            params["facets"] = facets

        return self._make_request("POST", path, params=params, json=body)

    def get_org_health_summary(
        self,
        org_id: int = None,
        owner_id: int = None,
        from_date: str = None,
        to_date: str = None,
    ) -> Dict[str, Any]:
        """
        Get the overall health snapshot for an org's flows.

        Calls ``GET /health/org/all``. Returns aggregate counts of flows
        bucketed by their current health status (GREEN/YELLOW/RED) across
        the optional date window.

        Args:
            org_id: Organization ID (defaults server-side to current org)
            owner_id: Restrict to flows owned by this user
            from_date: Start date (YYYY-MM-DD, treated as UTC)
            to_date: End date (YYYY-MM-DD, treated as UTC)

        Returns:
            Aggregate health metrics for the org
        """
        params: Dict[str, Any] = {}
        if org_id is not None:
            params["org_id"] = org_id
        if owner_id is not None:
            params["owner_id"] = owner_id
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        return self._make_request("GET", "/health/org/all", params=params)

    def get_org_health_flows(
        self,
        org_id: int = None,
        owner_id: int = None,
        from_date: str = None,
        to_date: str = None,
        health_status: str = None,
        page: int = None,
        size: int = None,
        sort_by: str = None,
        sort_order: str = None,
    ) -> Dict[str, Any]:
        """
        List per-flow health status across an org. Use this to answer
        questions like "which flows had errors today" or "show me unhealthy
        flows in the last week".

        Calls ``GET /health/org/flows``. Each entry includes the flow's
        origin_node_id, current healthStatus, latestErrorCount,
        latestRecordCount, latestRunId, errorSummary, and updatedAtEpoch.

        Args:
            org_id: Organization ID (defaults server-side to current org)
            owner_id: Restrict to flows owned by this user
            from_date: Start date (YYYY-MM-DD, treated as UTC)
            to_date: End date (YYYY-MM-DD, treated as UTC)
            health_status: Filter to one of GREEN (OK), YELLOW (WARNING),
                or RED (ERROR). Case-insensitive.
            page: 1-based page number
            size: Page size
            sort_by: Field to sort by (e.g. ``run_id``, ``updated_at``)
            sort_order: ``asc`` or ``desc``

        Returns:
            Paginated list of flow health entries
        """
        params: Dict[str, Any] = {}
        if org_id is not None:
            params["org_id"] = org_id
        if owner_id is not None:
            params["owner_id"] = owner_id
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        if health_status is not None:
            params["health_status"] = health_status
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if sort_by is not None:
            params["sort_by"] = sort_by
        if sort_order is not None:
            params["sort_order"] = sort_order
        return self._make_request("GET", "/health/org/flows", params=params)

    def get_flow_health(self, flow_id: int) -> Dict[str, Any]:
        """
        Get detailed health information for a single flow.

        Calls ``GET /health/flow/:flow_id``. Returns the flow's current
        health status plus a breakdown of latest errors / records / run
        information; the inverse of :meth:`get_org_health_flows` for one
        specific flow.
        """
        return self._make_request("GET", f"/health/flow/{flow_id}")

    def get_active_flows_metrics(
        self, from_date: str = None, to_date: str = None, org_id: int = None
    ) -> Dict[str, Any]:
        """
        Get metrics for currently active flows.

        Args:
            from_date: Start date filter (YYYY-MM-DD)
            to_date: End date filter (YYYY-MM-DD)
            org_id: Organization ID filter

        Returns:
            Active flows metrics
        """
        path = f"{self._path}/active_flows_metrics"
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        if org_id is not None:
            params["org_id"] = org_id
        return self._make_request("GET", path, params=params)

    def get_run_status(
        self,
        flow_id: int,
        run_id: int,
    ) -> Dict[str, Any]:
        """
        Get status of a specific flow run.

        Args:
            flow_id: Flow ID
            run_id: Run ID

        Returns:
            Run status information
        """
        if not isinstance(flow_id, int) or not isinstance(run_id, int):
            raise TypeError("get_run_status() requires integer flow_id and run_id")

        path = f"{self._path}/{flow_id}/run_status/{run_id}"
        return self._make_request("GET", path)

    @staticmethod
    def _warn_if_seconds_timestamp(value: int, param_name: str) -> None:
        if isinstance(value, (int, float)) and 0 < abs(value) < 1e10:
            warnings.warn(
                f"{param_name} looks like seconds; API expects milliseconds",
                RuntimeWarning,
                stacklevel=3,
            )

    def get_logs(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        run_id: int,
        from_ts: int,
        to_ts: int = None,
        page: int = None,
        per_page: int = None,
    ) -> Union[FlowLogsResponse, Dict[str, Any]]:
        """Get flow execution logs for a specific run id of a flow.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            run_id: Run ID to get logs for
            from_ts: Start timestamp (Unix timestamp in milliseconds)
            to_ts: End timestamp (Unix timestamp in milliseconds)
            page: Page number for pagination
            per_page: Items per page

        Returns:
            FlowLogsResponse with log entries and pagination metadata,
            or raw dict if response doesn't match expected schema.
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        self._warn_if_seconds_timestamp(from_ts, "from_ts")
        if to_ts is not None:
            self._warn_if_seconds_timestamp(to_ts, "to_ts")
        path = f"/{resource_type_value}/{resource_id}/flow/logs"
        params = {
            "run_id": run_id,
            "from": from_ts,
        }
        if to_ts is not None:
            params["to"] = to_ts
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", path, params=params)
        try:
            return FlowLogsResponse.model_validate(response)
        except Exception as exc:
            logger.debug(
                "FlowLogsResponse validation failed, returning raw dict: %s", exc
            )
            return response

    def get_metrics(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        from_date: str,
        to_date: str = None,
        groupby: str = None,
        orderby: str = None,
        page: int = None,
        per_page: int = None,
    ) -> Union[FlowMetricsApiResponse, Dict[str, Any]]:
        """Get flow metrics for a flow node keyed by resource id.

        Args:
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            resource_id: Resource ID
            from_date: Start date (ISO format, e.g., '2023-01-17')
            to_date: End date (ISO format)
            groupby: Group metrics by field (e.g., 'runId')
            orderby: Order results by field ('runId' or 'created_at')
            page: Page number for pagination
            per_page: Items per page

        Returns:
            FlowMetricsApiResponse with metrics data and pagination,
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
            return FlowMetricsApiResponse.model_validate(response)
        except Exception as exc:
            logger.debug(
                "FlowMetricsApiResponse validation failed, returning raw dict: %s", exc
            )
            return response
