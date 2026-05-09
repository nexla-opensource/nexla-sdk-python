"""Unit tests for connector enum handling."""

import pytest

from nexla_sdk.models.connectors.enums import ConnectionType, ConnectorType
from nexla_sdk.models.credentials.enums import CredentialType
from nexla_sdk.models.destinations.enums import DestinationType
from nexla_sdk.models.sources.enums import SourceType


@pytest.mark.unit
class TestConnectorEnumCoverage:
    """Test that connector enums have consistent coverage."""

    def test_source_type_has_all_base_connectors(self):
        """SourceType should include core file and database connectors."""
        base_connectors = [
            "s3",
            "gcs",
            "azure_blb",
            "mysql",
            "postgres",
            "snowflake",
            "bigquery",
            "kafka",
            "rest",
        ]
        source_values = [e.value for e in SourceType]
        for connector in base_connectors:
            assert connector in source_values, f"SourceType missing {connector}"

    def test_destination_type_has_all_base_connectors(self):
        """DestinationType should include core connectors."""
        base_connectors = [
            "s3",
            "gcs",
            "azure_blb",
            "mysql",
            "postgres",
            "snowflake",
            "bigquery",
            "kafka",
            "rest",
            "pinecone",
        ]
        dest_values = [e.value for e in DestinationType]
        for connector in base_connectors:
            assert connector in dest_values, f"DestinationType missing {connector}"

    def test_connector_type_is_superset(self):
        """ConnectorType should be a superset of Source and Destination types."""
        connector_values = set(e.value for e in ConnectorType)
        source_values = set(e.value for e in SourceType)
        dest_values = set(e.value for e in DestinationType)

        # All source types should be in ConnectorType
        missing_from_connector = source_values - connector_values
        assert (
            len(missing_from_connector) == 0
        ), f"ConnectorType missing source types: {missing_from_connector}"

        # All destination types should be in ConnectorType
        missing_from_connector = dest_values - connector_values
        assert (
            len(missing_from_connector) == 0
        ), f"ConnectorType missing destination types: {missing_from_connector}"

    def test_source_type_has_cloud_database_connectors(self):
        """SourceType should include cloud database connectors."""
        cloud_dbs = [
            "cloudsql_mysql",
            "cloudsql_postgres",
            "cloudsql_sqlserver",
            "gcp_alloydb",
            "gcp_spanner",
            "azure_synapse",
            "aws_athena",
        ]
        source_values = [e.value for e in SourceType]
        for connector in cloud_dbs:
            assert connector in source_values, f"SourceType missing {connector}"

    def test_source_type_has_data_lake_connectors(self):
        """SourceType should include data lake connectors."""
        data_lakes = [
            "delta_lake_s3",
            "delta_lake_azure_blb",
            "delta_lake_azure_data_lake",
            "s3_iceberg",
        ]
        source_values = [e.value for e in SourceType]
        for connector in data_lakes:
            assert connector in source_values, f"SourceType missing {connector}"


@pytest.mark.unit
class TestFlexibleEnumsInResponses:
    """Test flexible enum behavior in response models."""

    def test_source_with_known_type(self):
        """Source should accept known source_type values."""
        from nexla_sdk.models.sources.responses import Source

        data = {
            "id": 1,
            "name": "Test Source",
            "status": "ACTIVE",
            "source_type": "s3",
        }
        source = Source(**data)
        assert source.source_type == SourceType.S3

    def test_source_with_unknown_type(self):
        """Source should accept unknown source_type values as strings."""
        from nexla_sdk.models.sources.responses import Source

        data = {
            "id": 1,
            "name": "Test Source",
            "status": "ACTIVE",
            "source_type": "new_future_connector_2026",
        }
        source = Source(**data)
        assert source.source_type == "new_future_connector_2026"

    def test_destination_with_known_type(self):
        """Destination should accept known sink_type values."""
        from nexla_sdk.models.destinations.responses import Destination

        data = {
            "id": 1,
            "name": "Test Dest",
            "status": "ACTIVE",
            "sink_type": "snowflake",
        }
        dest = Destination(**data)
        assert dest.sink_type == DestinationType.SNOWFLAKE

    def test_destination_with_unknown_type(self):
        """Destination should accept unknown sink_type values."""
        from nexla_sdk.models.destinations.responses import Destination

        data = {
            "id": 1,
            "name": "Test Dest",
            "status": "ACTIVE",
            "sink_type": "quantum_database_2030",
        }
        dest = Destination(**data)
        assert dest.sink_type == "quantum_database_2030"

    def test_credential_with_known_type(self):
        """Credential should accept known credentials_type values."""
        from nexla_sdk.models.credentials.responses import Credential

        data = {
            "id": 1,
            "name": "Test Cred",
            "credentials_type": "s3",
        }
        cred = Credential(**data)
        assert cred.credentials_type == CredentialType.S3

    def test_credential_with_unknown_type(self):
        """Credential should accept unknown credentials_type values."""
        from nexla_sdk.models.credentials.responses import Credential

        data = {
            "id": 1,
            "name": "Test Cred",
            "credentials_type": "new_cloud_provider",
        }
        cred = Credential(**data)
        assert cred.credentials_type == "new_cloud_provider"


@pytest.mark.unit
class TestConnectorResponseModel:
    """Test Connector model with flexible enums."""

    def test_connector_with_known_type(self):
        """Connector should accept known type values."""
        from nexla_sdk.models.connectors.responses import Connector

        data = {
            "id": 123,
            "type": "s3",
            "connection_type": "file",
            "name": "Amazon S3",
            "description": "S3 connector",
        }
        connector = Connector(**data)
        assert connector.type == ConnectorType.S3
        assert connector.connection_type == ConnectionType.FILE

    def test_connector_with_unknown_type(self):
        """Connector should accept unknown type values."""
        from nexla_sdk.models.connectors.responses import Connector

        data = {
            "id": 123,
            "type": "new_connector",
            "connection_type": "quantum",
            "name": "New Connector",
            "description": "Future connector",
        }
        connector = Connector(**data)
        assert connector.type == "new_connector"
        assert connector.connection_type == "quantum"

    def test_common_connector_with_known_type(self):
        """Common Connector model should accept known type values."""
        from nexla_sdk.models.common import Connector

        data = {
            "id": 123,
            "type": "postgres",
            "connection_type": "database",
            "name": "PostgreSQL",
            "description": "PostgreSQL connector",
            "nexset_api_compatible": True,
        }
        connector = Connector(**data)
        assert connector.type == ConnectorType.POSTGRES
        assert connector.connection_type == ConnectionType.DATABASE

    def test_common_connector_with_unknown_type(self):
        """Common Connector model should accept unknown type values."""
        from nexla_sdk.models.common import Connector

        data = {
            "id": 123,
            "type": "future_db",
            "connection_type": "hyperscale",
            "name": "Future DB",
            "description": "Future connector",
            "nexset_api_compatible": False,
        }
        connector = Connector(**data)
        assert connector.type == "future_db"
        assert connector.connection_type == "hyperscale"


@pytest.mark.unit
class TestEnumSerialization:
    """Test that flexible enums serialize correctly."""

    def test_known_enum_serializes_to_string(self):
        """Known enum values should serialize to their string values."""
        from nexla_sdk.models.sources.responses import Source

        data = {
            "id": 1,
            "name": "Test",
            "status": "ACTIVE",
            "source_type": "s3",
        }
        source = Source(**data)
        serialized = source.model_dump()
        assert serialized["source_type"] == "s3"
        assert isinstance(serialized["source_type"], str)

    def test_unknown_value_serializes_unchanged(self):
        """Unknown string values should serialize unchanged."""
        from nexla_sdk.models.sources.responses import Source

        data = {
            "id": 1,
            "name": "Test",
            "status": "ACTIVE",
            "source_type": "future_type",
        }
        source = Source(**data)
        serialized = source.model_dump()
        assert serialized["source_type"] == "future_type"

    def test_destination_serialization(self):
        """Destination with flexible types should serialize correctly."""
        from nexla_sdk.models.destinations.responses import Destination

        data = {
            "id": 1,
            "name": "Test",
            "status": "ACTIVE",
            "sink_type": "snowflake",
            "connector_type": "snowflake",
        }
        dest = Destination(**data)
        serialized = dest.model_dump()
        assert serialized["sink_type"] == "snowflake"
        assert serialized["connector_type"] == "snowflake"


@pytest.mark.unit
class TestConnectionTypeEnum:
    """Test ConnectionType enum values."""

    def test_connection_type_categories(self):
        """ConnectionType should have all expected categories."""
        expected = [
            "file",
            "database",
            "nosql",
            "streaming",
            "api",
            "vector_db",
            "special",
            "data_lake",
        ]
        values = [e.value for e in ConnectionType]
        for category in expected:
            assert category in values, f"ConnectionType missing {category}"
