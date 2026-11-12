from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class DestinationCreate(BaseModel):
    """Request model for creating a destination."""

    name: str
    sink_type: str
    data_credentials_id: int
    data_set_id: int
    description: Optional[str] = None

    # In case of Core Sinks only
    sink_config: Optional[Dict[str, Any]] = None

    # In case of Templatized API only
    vendor_endpoint_id: Optional[int] = None
    template_config: Optional[Dict[str, Any]] = None


class DestinationUpdate(BaseModel):
    """Request model for updating a destination."""

    name: Optional[str] = None
    description: Optional[str] = None
    sink_config: Optional[Dict[str, Any]] = None
    data_credentials_id: Optional[int] = None
    data_set_id: Optional[int] = None


class DestinationCopyOptions(BaseModel):
    """Options for copying a destination."""

    reuse_data_credentials: bool = False
    copy_access_controls: bool = False
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
