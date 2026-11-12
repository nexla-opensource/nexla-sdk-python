"""Auth template models."""

from nexla_sdk.models.auth_templates.requests import (
    AuthParameterCreate,
    AuthTemplateCreate,
    AuthTemplateUpdate,
)
from nexla_sdk.models.auth_templates.responses import (
    AuthParameter,  # Deprecated alias for backward compatibility
    AuthTemplate,
    AuthTemplateParameter,
)

__all__ = [
    "AuthTemplate",
    "AuthTemplateCreate",
    "AuthTemplateUpdate",
    "AuthTemplateParameter",
    "AuthParameterCreate",
    # Deprecated - use AuthTemplateParameter instead
    "AuthParameter",
]
