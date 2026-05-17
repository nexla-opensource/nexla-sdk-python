from typing import TYPE_CHECKING, Any

from nexla_sdk.models.destinations.enums import (
    DestinationFormat,
    DestinationStatus,
    DestinationType,
)

if TYPE_CHECKING:
    from nexla_sdk.models.destinations.requests import (
        DestinationCopyOptions,
        DestinationCreate,
        DestinationUpdate,
    )
    from nexla_sdk.models.destinations.responses import (
        DataMapInfo,
        DataSetInfo,
        Destination,
    )

__all__ = [
    # Enums
    "DestinationStatus",
    "DestinationType",
    "DestinationFormat",
    # Responses
    "Destination",
    "DataSetInfo",
    "DataMapInfo",
    # Requests
    "DestinationCreate",
    "DestinationUpdate",
    "DestinationCopyOptions",
]


def __getattr__(name: str) -> Any:
    if name in {"DestinationCreate", "DestinationUpdate", "DestinationCopyOptions"}:
        from nexla_sdk.models.destinations import requests as _requests

        return getattr(_requests, name)
    if name in {"Destination", "DataSetInfo", "DataMapInfo"}:
        from nexla_sdk.models.destinations import responses as _responses

        return getattr(_responses, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
