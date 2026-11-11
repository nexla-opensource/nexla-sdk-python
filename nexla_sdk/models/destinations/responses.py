from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Connector, Organization, Owner
from nexla_sdk.models.credentials.responses import Credential
from nexla_sdk.models.flexible_enums import (
    FlexibleDestinationFormat,
    FlexibleDestinationType,
)


class DataSetInfo(BaseModel):
    """Basic dataset information for destination."""

    id: int
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    version: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DataMapInfo(BaseModel):
    """Basic data map information for destination."""

    id: int
    owner_id: int
    org_id: int
    name: str
    description: Optional[str] = None
    public: bool
    created_at: datetime
    updated_at: datetime


class Destination(BaseModel):
    """Destination (data sink) response model."""

    id: int
    name: str
    status: str
    sink_type: FlexibleDestinationType
    connector_type: Optional[FlexibleDestinationType] = None
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    access_roles: Optional[List[str]] = None
    managed: Optional[bool] = None
    connector: Optional[Connector] = None

    description: Optional[str] = None
    data_set_id: Optional[int] = None
    data_map_id: Optional[int] = None
    data_source_id: Optional[int] = None
    sink_format: Optional[FlexibleDestinationFormat] = None
    sink_config: Optional[Dict[str, Any]] = None
    sink_schedule: Optional[str] = None
    in_memory: bool = False
    data_set: Optional[DataSetInfo] = None
    data_map: Optional[DataMapInfo] = None
    data_credentials_id: Optional[int] = None
    data_credentials: Optional[Credential] = None
    copied_from_id: Optional[int] = None
    flow_type: Optional[str] = None
    has_template: Optional[bool] = None
    vendor_endpoint: Optional[Dict[str, Any]] = None
    vendor: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
