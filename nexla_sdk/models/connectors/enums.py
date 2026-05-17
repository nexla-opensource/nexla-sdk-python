"""Connector enums for the /connectors endpoint."""

from enum import Enum


class ConnectorType(str, Enum):
    """All supported connector types.

    This is the comprehensive enum used by the /connectors endpoint.
    It includes all source and destination connector types.
    """

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
    DATA_MAP = "data_map"

    # Vector Databases
    PINECONE = "pinecone"


class ConnectionType(str, Enum):
    """Connection type categories for connectors.

    Maps to the `connection_type` field in Connector responses.
    """

    FILE = "file"
    DATABASE = "database"
    NOSQL = "nosql"
    STREAMING = "streaming"
    API = "api"
    VECTOR_DB = "vector_db"
    SPECIAL = "special"
    DATA_LAKE = "data_lake"
