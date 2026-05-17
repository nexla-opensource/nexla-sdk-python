from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import Connector, Organization, Owner
from nexla_sdk.models.flexible_enums import FlexibleCredentialType


class Credential(BaseModel):
    """Data credential response model."""

    id: int
    name: str
    credentials_type: FlexibleCredentialType
    owner: Optional[Owner] = None
    org: Optional[Organization] = None
    access_roles: Optional[List[str]] = None
    verified_status: Optional[str] = None
    connector: Optional[Connector] = None

    description: Optional[str] = None
    credentials_version: Optional[str] = None
    api_keys: Optional[List[Dict[str, Any]]] = None
    credentials_non_secure_data: Optional[Dict[str, Any]] = None
    verified_at: Optional[datetime] = None
    copied_from_id: Optional[int] = None
    template_config: Optional[Dict[str, Any]] = None
    vendor: Optional[Dict[str, Any]] = None
    auth_template: Optional[Dict[str, Any]] = None
    referenced_resource_ids: Optional[Dict[str, List[int]]] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    managed: bool = False

    @field_validator("access_roles", mode="before")
    @classmethod
    def validate_access_roles(cls, v):
        """Handle access_roles with None values."""
        if v is None:
            return None
        if isinstance(v, list):
            return [role for role in v if role is not None]
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        """Handle None tags."""
        if v is None:
            return []
        return v


class ProbeTreeResponse(BaseModel):
    """Response from credential probe tree operation."""

    status: str
    message: str
    connection_type: str
    object: Dict[str, Any]


class ProbeSampleResponse(BaseModel):
    """Response from credential probe sample operation."""

    status: str
    message: str
    connection_type: str
    output: Dict[str, Any]
