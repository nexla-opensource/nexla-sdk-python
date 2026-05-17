"""Connector response models."""

from datetime import datetime
from typing import Any, Dict, Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.flexible_enums import (
    FlexibleConnectionType,
    FlexibleConnectorType,
)


class Connector(BaseModel):
    """Connector response model.

    Connectors define connection types for data sources and destinations.
    """

    id: int
    type: Optional[FlexibleConnectorType] = None
    connection_type: Optional[FlexibleConnectionType] = None
    name: Optional[str] = None
    description: Optional[str] = None
    nexset_api_compatible: Optional[bool] = None
    sync_api_compatible: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
