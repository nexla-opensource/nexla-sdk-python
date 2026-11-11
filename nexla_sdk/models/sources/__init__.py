from typing import TYPE_CHECKING, Any

from nexla_sdk.models.sources.enums import (
    FlowType,
    IngestMethod,
    SourceStatus,
    SourceType,
)

if TYPE_CHECKING:
    from nexla_sdk.models.sources.requests import (
        SourceCopyOptions,
        SourceCreate,
        SourceUpdate,
    )
    from nexla_sdk.models.sources.responses import DataSetBrief, RunInfo, Source

__all__ = [
    # Enums
    "SourceStatus",
    "SourceType",
    "IngestMethod",
    "FlowType",
    # Responses
    "Source",
    "DataSetBrief",
    "RunInfo",
    # Requests
    "SourceCreate",
    "SourceUpdate",
    "SourceCopyOptions",
]


def __getattr__(name: str) -> Any:
    if name in {"SourceCreate", "SourceUpdate", "SourceCopyOptions"}:
        from nexla_sdk.models.sources import requests as _requests

        return getattr(_requests, name)
    if name in {"Source", "DataSetBrief", "RunInfo"}:
        from nexla_sdk.models.sources import responses as _responses

        return getattr(_responses, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
