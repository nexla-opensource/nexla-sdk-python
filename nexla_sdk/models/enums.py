from enum import Enum


class AccessRole(str, Enum):
    """Access roles for resources (lower-case backend values).

    The backend also accepts upper-case forms (app/api/v1/shared/schemas.py:45-72).
    """

    OWNER = "owner"
    OWNER_ONLY = "owner_only"
    ADMIN = "admin"
    ADMIN_ONLY = "admin_only"
    OPERATOR = "operator"
    COLLABORATOR = "collaborator"
    COLLABORATOR_ONLY = "collaborator_only"
    SHARER = "sharer"
    SHARER_ONLY = "sharer_only"
    MEMBER = "member"
    ALL = "all"


class ResourceStatus(str, Enum):
    """Common resource status values."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAFT = "DRAFT"
    DELETED = "DELETED"
    ERROR = "ERROR"
    INIT = "INIT"
    PROCESSING = "PROCESSING"


class ResourceType(str, Enum):
    """Resource types in Nexla."""

    ORG = "ORG"
    USER = "USER"
    TEAM = "TEAM"
    DATA_FLOW = "DATA_FLOW"
    CUSTOM_DATA_FLOW = "CUSTOM_DATA_FLOW"
    SOURCE = "SOURCE"
    DATASET = "DATASET"
    SINK = "SINK"
    DATA_MAP = "DATA_MAP"
    DATA_SCHEMA = "DATA_SCHEMA"
    DATA_CREDENTIAL = "DATA_CREDENTIAL"
    PROJECT = "PROJECT"
    CODE_CONTAINER = "CODE_CONTAINER"
    TRANSFORM = "TRANSFORM"
    FLOW = "FLOW"
    PIPELINE = "PIPELINE"


class NotificationLevel(str, Enum):
    """Notification levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    RECOVERED = "RECOVERED"
    RESOLVED = "RESOLVED"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""

    APP = "APP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    SLACK = "SLACK"
    WEBHOOKS = "WEBHOOKS"


class UserTier(str, Enum):
    """User account tiers."""

    FREE = "FREE"
    TRIAL = "TRIAL"
    PAID = "PAID"
    FREE_FOREVER = "FREE_FOREVER"


class UserStatus(str, Enum):
    """User account status."""

    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"
    SOURCE_COUNT_CAPPED = "SOURCE_COUNT_CAPPED"
    SOURCE_DATA_CAPPED = "SOURCE_DATA_CAPPED"
    TRIAL_EXPIRED = "TRIAL_EXPIRED"


class OrgMembershipStatus(str, Enum):
    """Organization membership status."""

    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"


class ConnectorCategory(str, Enum):
    """Connector categories."""

    FILE = "file"
    DATABASE = "database"
    NOSQL = "nosql"
    STREAMING = "streaming"
    API = "api"
    VECTOR_DB = "vector_db"
    SPECIAL = "special"
