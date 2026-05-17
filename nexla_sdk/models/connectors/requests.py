"""Connector request models."""

from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel


class ConnectorUpdate(BaseModel):
    """Request model for updating a connector (super user only)."""

    name: Optional[str] = None
    description: Optional[str] = None
    nexset_api_compatible: Optional[bool] = None
    sync_api_compatible: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
