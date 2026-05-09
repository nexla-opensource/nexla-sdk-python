"""Helper utilities for flexible enum handling in Pydantic models.

These utilities allow enums to gracefully accept unknown values from API responses
without raising validation errors. Unknown values are preserved as strings.
"""

from enum import Enum
from typing import Type, TypeVar, Union

from pydantic import BeforeValidator
from typing_extensions import Annotated  # typing.Annotated only landed in 3.9

# Import directly from .enums modules to avoid circular imports through __init__.py
from nexla_sdk.models.connectors.enums import ConnectionType, ConnectorType
from nexla_sdk.models.credentials.enums import CredentialType
from nexla_sdk.models.destinations.enums import DestinationFormat, DestinationType
from nexla_sdk.models.enums import ConnectorCategory
from nexla_sdk.models.sources.enums import SourceType

E = TypeVar("E", bound=Enum)


def flexible_enum_validator(enum_cls: Type[E]):
    """Create a validator that accepts enum values or unknown strings.

    Args:
        enum_cls: The enum class to validate against

    Returns:
        A validator function that returns the enum member for known values,
        or the raw string for unknown values.
    """

    def validator(v):
        if v is None:
            return None
        if isinstance(v, enum_cls):
            return v
        if isinstance(v, str):
            try:
                return enum_cls(v)
            except ValueError:
                # Unknown value - return as string
                return v
        return v

    return validator


def FlexibleEnum(enum_cls: Type[E]) -> Type[Union[E, str]]:
    """Create a flexible enum type annotation for Pydantic models.

    This creates an Annotated type that accepts either a valid enum value
    or any string. Known values are returned as enum members; unknown values
    are returned as raw strings.

    Usage:
        sink_type: Optional[FlexibleEnum(DestinationType)] = None

    Args:
        enum_cls: The enum class to create a flexible version of

    Returns:
        An Annotated type suitable for Pydantic model fields
    """
    return Annotated[
        Union[enum_cls, str], BeforeValidator(flexible_enum_validator(enum_cls))
    ]


# Pre-defined flexible connector types for convenience
FlexibleDestinationType = FlexibleEnum(DestinationType)
FlexibleDestinationFormat = FlexibleEnum(DestinationFormat)
FlexibleSourceType = FlexibleEnum(SourceType)
FlexibleCredentialType = FlexibleEnum(CredentialType)
FlexibleConnectorCategory = FlexibleEnum(ConnectorCategory)

# Flexible types for connectors resource
FlexibleConnectorType = FlexibleEnum(ConnectorType)
FlexibleConnectionType = FlexibleEnum(ConnectionType)
