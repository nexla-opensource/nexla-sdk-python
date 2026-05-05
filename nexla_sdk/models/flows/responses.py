from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, Field, model_validator

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import FlowNode
from nexla_sdk.models.credentials.responses import Credential
from nexla_sdk.models.destinations.responses import Destination
from nexla_sdk.models.nexsets.responses import Nexset
from nexla_sdk.models.sources.responses import Source


class FlowMetrics(BaseModel):
    """Flow metrics information."""

    origin_node_id: int
    records: int
    size: int
    errors: int
    reporting_date: datetime
    run_id: int


class FlowLogEntry(BaseModel):
    """A single flow execution log entry."""

    timestamp: Optional[datetime] = None
    level: Optional[str] = None
    message: Optional[str] = None
    log: Optional[str] = None
    log_type: Optional[str] = None
    severity: Optional[str] = None
    resource_id: Optional[int] = None
    resource_type: Optional[str] = None
    run_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_live_log_fields(cls, data):
        """Map live API log fields onto the SDK's existing convenience names."""
        if not isinstance(data, dict):
            return data

        normalized = data.copy()
        if "message" not in normalized and "log" in normalized:
            normalized["message"] = normalized["log"]
        if "level" not in normalized and "severity" in normalized:
            normalized["level"] = normalized["severity"]
        return normalized


class FlowLogsMeta(BaseModel):
    """Metadata for flow logs pagination."""

    current_page: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("currentPage", "current_page"),
        serialization_alias="currentPage",
    )
    page_count: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("pageCount", "page_count", "pages_count"),
        serialization_alias="pageCount",
    )
    total_count: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("totalCount", "total_count"),
        serialization_alias="totalCount",
    )
    org_id: Optional[int] = None
    run_id: Optional[int] = None


class FlowLogsResponse(BaseModel):
    """Response from get_logs() containing flow execution logs.

    Attributes:
        status: Status code of the response (200 for success).
        message: Status message ("Ok" for success).
        logs: List of log entries.
        meta: Pagination metadata.
    """

    status: Optional[int] = None
    message: Optional[str] = None
    logs: List[FlowLogEntry] = Field(default_factory=list)
    meta: Optional[FlowLogsMeta] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_live_logs_shape(cls, data):
        """Flatten live API logs.data/logs.meta into the SDK response model."""
        if not isinstance(data, dict) or not isinstance(data.get("logs"), dict):
            return data

        logs = data["logs"]
        normalized = data.copy()
        normalized["logs"] = logs.get("data") or []
        if normalized.get("meta") is None:
            normalized["meta"] = logs.get("meta")
        return normalized


class FlowMetricData(BaseModel):
    """Flow metric data for a resource."""

    records: Optional[int] = None
    size: Optional[int] = None
    errors: Optional[int] = None
    run_id: Optional[int] = Field(default=None, alias="runId")
    reporting_date: Optional[datetime] = None


class FlowMetricsMeta(BaseModel):
    """Metadata for flow metrics pagination."""

    current_page: Optional[int] = Field(default=None, alias="currentPage")
    page_count: Optional[int] = Field(default=None, alias="pageCount")
    total_count: Optional[int] = Field(default=None, alias="totalCount")


class FlowMetricsData(BaseModel):
    """Flow metrics data container."""

    data: Optional[Dict[str, Any]] = None
    meta: Optional[FlowMetricsMeta] = None


class FlowMetricsApiResponse(BaseModel):
    """Response from get_metrics() containing flow metrics.

    Attributes:
        status: Status code of the response (200 for success).
        message: Status message ("Ok" for success).
        metrics: Metrics data including resource-keyed data and pagination.
    """

    status: Optional[int] = None
    message: Optional[str] = None
    metrics: Optional[FlowMetricsData] = None


class DocsRecommendation(BaseModel):
    """Response from docs_recommendation() with AI-generated documentation.

    Attributes:
        recommendation: The AI-generated documentation suggestion.
        status: Status of the recommendation request.
    """

    recommendation: Optional[str] = None
    status: Optional[str] = None


class FlowElements(BaseModel):
    """Flow elements containing all resources."""

    code_containers: List[Dict[str, Any]] = Field(default_factory=list)
    data_sources: List[Source] = Field(default_factory=list)
    data_sets: List[Nexset] = Field(default_factory=list)
    data_sinks: List[Destination] = Field(default_factory=list)
    data_credentials: List[Credential] = Field(default_factory=list)
    shared_data_sets: List[Dict[str, Any]] = Field(default_factory=list)
    orgs: List[Dict[str, Any]] = Field(default_factory=list)
    users: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)


class FlowResponse(BaseModel):
    """Flow response model."""

    flows: List[FlowNode]
    # Include flow elements when not flows_only
    code_containers: Optional[List[Dict[str, Any]]] = None
    data_sources: Optional[List[Source]] = None
    data_sets: Optional[List[Nexset]] = None
    data_sinks: Optional[List[Destination]] = None
    data_credentials: Optional[List[Credential]] = None
    shared_data_sets: Optional[List[Dict[str, Any]]] = None
    orgs: Optional[List[Dict[str, Any]]] = None
    users: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[List[FlowMetrics]] = None
