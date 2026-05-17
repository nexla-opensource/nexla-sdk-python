"""Connector models."""

from typing import TYPE_CHECKING, Any

from nexla_sdk.models.connectors.enums import ConnectionType, ConnectorType

if TYPE_CHECKING:
    from nexla_sdk.models.connectors.requests import ConnectorUpdate
    from nexla_sdk.models.connectors.responses import Connector

__all__ = [
    "Connector",
    "ConnectorType",
    "ConnectionType",
    "ConnectorUpdate",
]


def __getattr__(name: str) -> Any:
    if name == "Connector":
        from nexla_sdk.models.connectors.responses import Connector

        return Connector
    if name == "ConnectorUpdate":
        from nexla_sdk.models.connectors.requests import ConnectorUpdate

        return ConnectorUpdate
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
