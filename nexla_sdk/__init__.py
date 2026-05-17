"""Nexla Python SDK for data integration and automation."""

# Package version
try:
    from importlib.metadata import PackageNotFoundError, version  # Python 3.8+
except Exception:  # pragma: no cover
    version = None
    PackageNotFoundError = Exception

try:  # Prefer distribution name for accurate version resolution
    __version__ = version("nexla-sdk") if version else "unknown"
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

# Import main client
from nexla_sdk.client import NexlaClient

# Import exceptions
from nexla_sdk.exceptions import (
    AuthenticationError,
    AuthorizationError,
    CredentialError,
    FlowError,
    NexlaError,
    NotFoundError,
    RateLimitError,
    ResourceConflictError,
    ServerError,
    TransformError,
    ValidationError,
)

# Import common models
from nexla_sdk.models import (
    BaseModel,
    Connector,
    FlowNode,
    LogEntry,
    Organization,
    Owner,
)

# Import enums
from nexla_sdk.models.enums import (
    AccessRole,
    ConnectorCategory,
    NotificationChannel,
    NotificationLevel,
    OrgMembershipStatus,
    ResourceStatus,
    ResourceType,
    UserStatus,
    UserTier,
)
from nexla_sdk.raw_operations import RawOperationsClient

# Import resources
from nexla_sdk.resources import (
    ApprovalRequestsResource,
    AsyncTasksResource,
    AttributeTransformsResource,
    CodeContainersResource,
    CredentialsResource,
    DataSchemasResource,
    DestinationsResource,
    DocContainersResource,
    FlowsResource,
    GenAIResource,
    LookupsResource,
    MarketplaceResource,
    MetricsResource,
    NexsetsResource,
    NotificationsResource,
    OrganizationsResource,
    OrgAuthConfigsResource,
    ProjectsResource,
    RuntimesResource,
    SelfSignupResource,
    SourcesResource,
    TeamsResource,
    TransformsResource,
    UsersResource,
)

__all__ = [
    # Client
    "NexlaClient",
    "RawOperationsClient",
    # Resources
    "CredentialsResource",
    "FlowsResource",
    "SourcesResource",
    "DestinationsResource",
    "NexsetsResource",
    "LookupsResource",
    "UsersResource",
    "OrganizationsResource",
    "TeamsResource",
    "ProjectsResource",
    "NotificationsResource",
    "MetricsResource",
    "CodeContainersResource",
    "TransformsResource",
    "AttributeTransformsResource",
    "AsyncTasksResource",
    "ApprovalRequestsResource",
    "RuntimesResource",
    "MarketplaceResource",
    "OrgAuthConfigsResource",
    "GenAIResource",
    "SelfSignupResource",
    "DocContainersResource",
    "DataSchemasResource",
    # Models
    "BaseModel",
    "Owner",
    "Organization",
    "Connector",
    "LogEntry",
    "FlowNode",
    # Exceptions
    "NexlaError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "ResourceConflictError",
    "CredentialError",
    "FlowError",
    "TransformError",
    # Enums
    "AccessRole",
    "ResourceStatus",
    "ResourceType",
    "NotificationLevel",
    "NotificationChannel",
    "UserTier",
    "UserStatus",
    "OrgMembershipStatus",
    "ConnectorCategory",
]
