"""Request models for sources."""

from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class SourceCreate(BaseModel):
    """Request model for creating a source."""

    name: str
    source_type: str
    data_credentials_id: Optional[int] = None
    description: Optional[str] = None

    # For Core Connectors
    source_config: Optional[Dict[str, Any]] = None

    # For Templatized APIs
    vendor_endpoint_id: Optional[int] = None
    ingest_method: Optional[str] = None
    template_config: Optional[Dict[str, Any]] = None


class SourceUpdate(BaseModel):
    """Request model for updating a source."""

    name: Optional[str] = None
    description: Optional[str] = None
    source_config: Optional[Dict[str, Any]] = None
    data_credentials_id: Optional[int] = None


class SourceCopyOptions(BaseModel):
    """Options for copying a source."""

    reuse_data_credentials: bool = False
    copy_access_controls: bool = False
    owner_id: Optional[int] = None
    org_id: Optional[int] = None
