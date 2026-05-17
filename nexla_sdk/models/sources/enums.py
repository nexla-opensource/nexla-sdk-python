"""Enums for sources."""

from enum import Enum


class SourceStatus(str, Enum):
    """Source status values."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DRAFT = "DRAFT"
    DELETED = "DELETED"
    ERROR = "ERROR"


class SourceType(str, Enum):
    """Supported source types."""

    # File Systems
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLB = "azure_blb"
    AZURE_DATA_LAKE = "azure_data_lake"
    FTP = "ftp"
    DROPBOX = "dropbox"
    BOX = "box"
    GDRIVE = "gdrive"
    SHAREPOINT = "sharepoint"
    MIN_IO_S3 = "min_io_s3"
    WEBDAV = "webdav"

    # Databases - Traditional RDBMS
    MYSQL = "mysql"
    POSTGRES = "postgres"
    SUPABASE = "supabase"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    ORACLE_AUTONOMOUS = "oracle_autonomous"
    AS400 = "as400"
    DB2 = "db2"
    SYBASE = "sybase"
    HANA_JDBC = "hana_jdbc"
    NETSUITE_JDBC = "netsuite_jdbc"

    # Databases - Cloud Data Warehouses
    REDSHIFT = "redshift"
    SNOWFLAKE = "snowflake"
    SNOWFLAKE_DCR = "snowflake_dcr"
    BIGQUERY = "bigquery"
    DATABRICKS = "databricks"
    AWS_ATHENA = "aws_athena"
    AZURE_SYNAPSE = "azure_synapse"
    FIREBOLT = "firebolt"
    TERADATA = "teradata"
    HIVE = "hive"

    # Databases - Google Cloud SQL
    CLOUDSQL_MYSQL = "cloudsql_mysql"
    CLOUDSQL_POSTGRES = "cloudsql_postgres"
    CLOUDSQL_SQLSERVER = "cloudsql_sqlserver"

    # Databases - Google Cloud
    GCP_ALLOYDB = "gcp_alloydb"
    GCP_SPANNER = "gcp_spanner"

    # Delta Lake / Iceberg
    DELTA_LAKE_AZURE_BLB = "delta_lake_azure_blb"
    DELTA_LAKE_AZURE_DATA_LAKE = "delta_lake_azure_data_lake"
    DELTA_LAKE_S3 = "delta_lake_s3"
    S3_ICEBERG = "s3_iceberg"

    # NoSQL
    MONGO = "mongo"
    DYNAMODB = "dynamodb"
    FIREBASE = "firebase"

    # Streaming / Messaging
    KAFKA = "kafka"
    CONFLUENT_KAFKA = "confluent_kafka"
    GOOGLE_PUBSUB = "google_pubsub"
    JMS = "jms"
    TIBCO = "tibco"

    # APIs
    REST = "rest"
    SOAP = "soap"
    NEXLA_REST = "nexla_rest"

    # Special
    FILE_UPLOAD = "file_upload"
    EMAIL = "email"
    NEXLA_MONITOR = "nexla_monitor"

    # Vector Databases
    PINECONE = "pinecone"


class IngestMethod(str, Enum):
    """Data ingestion methods."""

    BATCH = "BATCH"
    STREAMING = "STREAMING"
    REAL_TIME = "REAL_TIME"
    SCHEDULED = "SCHEDULED"
    POLL = "POLL"


class FlowType(str, Enum):
    """Flow processing types."""

    BATCH = "batch"
    STREAMING = "streaming"
    REAL_TIME = "real_time"
