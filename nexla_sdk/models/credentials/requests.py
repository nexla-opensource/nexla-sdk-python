from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class CredentialCreate(BaseModel):
    """Request model for creating a credential."""

    name: str
    credentials_type: str
    description: Optional[str] = None

    # For templatized APIs; int
    auth_template_id: Optional[int] = None
    vendor_id: Optional[int] = None
    template_config: Optional[Dict[str, Any]] = None

    # For Core Connectors (Non-templatized)
    credentials: Optional[Dict[str, Any]] = None


class CredentialUpdate(BaseModel):
    """Request model for updating a credential."""

    name: Optional[str] = None
    description: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None


class ProbeTreeRequest(BaseModel):
    """Request for probing storage structure."""

    depth: int
    path: Optional[str] = None  # For file systems
    database: Optional[str] = None  # For databases
    table: Optional[str] = None  # For databases


class ProbeSampleRequest(BaseModel):
    """Request for previewing connector content."""

    # For file connectors
    path: Optional[str] = None
