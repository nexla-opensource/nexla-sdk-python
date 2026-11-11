from typing import TYPE_CHECKING, Any

from nexla_sdk.models.credentials.enums import CredentialType, VerifiedStatus

if TYPE_CHECKING:
    from nexla_sdk.models.credentials.requests import (
        CredentialCreate,
        CredentialUpdate,
        ProbeSampleRequest,
        ProbeTreeRequest,
    )
    from nexla_sdk.models.credentials.responses import (
        Credential,
        ProbeSampleResponse,
        ProbeTreeResponse,
    )

__all__ = [
    # Enums
    "CredentialType",
    "VerifiedStatus",
    # Responses
    "Credential",
    "ProbeTreeResponse",
    "ProbeSampleResponse",
    # Requests
    "CredentialCreate",
    "CredentialUpdate",
    "ProbeTreeRequest",
    "ProbeSampleRequest",
]


def __getattr__(name: str) -> Any:
    if name in {
        "CredentialCreate",
        "CredentialUpdate",
        "ProbeTreeRequest",
        "ProbeSampleRequest",
    }:
        from nexla_sdk.models.credentials import requests as _requests

        return getattr(_requests, name)
    if name in {"Credential", "ProbeTreeResponse", "ProbeSampleResponse"}:
        from nexla_sdk.models.credentials import responses as _responses

        return getattr(_responses, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
