from datetime import datetime
from typing import Any, Dict, List, Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.flexible_enums import (
    FlexibleConnectionType,
    FlexibleConnectorType,
)


class Owner(BaseModel):
    """User who owns a resource."""

    id: int
    full_name: str
    email: str
    email_verified_at: Optional[datetime] = None


class Organization(BaseModel):
    """Organization details."""

    id: int
    name: str
    email_domain: Optional[str] = None
    email: Optional[str] = None
    client_identifier: Optional[str] = None
    org_webhook_host: Optional[str] = None
    cluster_id: Optional[int] = None
    new_cluster_id: Optional[int] = None
    cluster_status: Optional[str] = None
    status: Optional[str] = None
    self_signup: Optional[bool] = None
    features_enabled: Optional[List[str]] = None
    org_tier: Optional[Dict[str, Any]] = None


class Connector(BaseModel):
    """Connector information."""

    id: int
    type: FlexibleConnectorType
    connection_type: FlexibleConnectionType
    name: str
    description: str
    nexset_api_compatible: bool


class LogEntry(BaseModel):
    """Audit log entry."""

    id: int
    item_type: str
    item_id: int
    event: str
    change_summary: List[str]
    object_changes: Dict[str, List[Any]]
    request_ip: str
    request_user_agent: str
    request_url: str
    user: Dict[str, Any]
    org_id: int
    owner_id: int
    owner_email: str
    created_at: datetime
    association_resource: Optional[Dict[str, Any]] = None
    # admin-api returns the impersonating user's numeric id, not a string.
    impersonator_id: Optional[int] = None


class FlowNode(BaseModel):
    """Flow node in a data pipeline."""

    id: int
    origin_node_id: int
    parent_node_id: Optional[int] = None
    data_source_id: Optional[int] = None
    data_set_id: Optional[int] = None
    data_sink_id: Optional[int] = None
    status: Optional[str] = None
    project_id: Optional[int] = None
    flow_type: Optional[str] = None
    ingestion_mode: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    children: Optional[List["FlowNode"]] = None
