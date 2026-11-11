"""Unit tests for flexible enum handling."""

from nexla_sdk.models.destinations.enums import DestinationFormat, DestinationType
from nexla_sdk.models.destinations.responses import Destination
from nexla_sdk.models.flexible_enums import flexible_enum_validator
from nexla_sdk.models.nexsets.responses import DataSinkSimplified, Nexset


class TestFlexibleEnumValidator:
    """Test the flexible enum validator."""

    def test_known_value_returns_enum(self):
        """Known values should return enum members."""
        validator = flexible_enum_validator(DestinationType)
        result = validator("s3")
        assert result == DestinationType.S3
        assert isinstance(result, DestinationType)

    def test_unknown_value_returns_string(self):
        """Unknown values should return as raw strings."""
        validator = flexible_enum_validator(DestinationType)
        result = validator("new_unknown_connector")
        assert result == "new_unknown_connector"
        assert isinstance(result, str)

    def test_none_returns_none(self):
        """None should remain None."""
        validator = flexible_enum_validator(DestinationType)
        result = validator(None)
        assert result is None

    def test_enum_instance_returns_unchanged(self):
        """Enum instances should pass through unchanged."""
        validator = flexible_enum_validator(DestinationType)
        result = validator(DestinationType.S3)
        assert result == DestinationType.S3


class TestFlexibleEnumInModels:
    """Test flexible enums in Pydantic models."""

    def test_destination_with_known_sink_format(self):
        """Destination should accept known sink_format values."""
        data = {
            "id": 1,
            "name": "Test Dest",
            "status": "ACTIVE",
            "sink_type": "s3",
            "sink_format": "json",
        }
        dest = Destination(**data)
        assert dest.sink_format == DestinationFormat.JSON

    def test_destination_with_unknown_sink_format(self):
        """Destination should accept unknown sink_format values."""
        data = {
            "id": 1,
            "name": "Test Dest",
            "status": "ACTIVE",
            "sink_type": "s3",
            "sink_format": "new_format_2025",
        }
        dest = Destination(**data)
        assert dest.sink_format == "new_format_2025"

    def test_destination_with_none_sink_format(self):
        """Destination should accept None for sink_format."""
        data = {
            "id": 1,
            "name": "Test Dest",
            "status": "ACTIVE",
            "sink_type": "s3",
        }
        dest = Destination(**data)
        assert dest.sink_format is None

    def test_data_sink_simplified_with_known_sink_type(self):
        """DataSinkSimplified should accept known sink_type values."""
        data = {
            "id": 1,
            "name": "Test Sink",
            "sinkType": "snowflake",
        }
        sink = DataSinkSimplified(**data)
        assert sink.sink_type == DestinationType.SNOWFLAKE

    def test_data_sink_simplified_with_unknown_sink_type(self):
        """DataSinkSimplified should accept unknown sink_type values."""
        data = {
            "id": 1,
            "name": "Test Sink",
            "sinkType": "new_connector_type",
        }
        sink = DataSinkSimplified(**data)
        assert sink.sink_type == "new_connector_type"

    def test_nexset_with_unknown_sink_type_in_data_sinks(self):
        """Nexset should handle data_sinks with unknown sink types."""
        data = {
            "id": 1,
            "name": "Test Nexset",
            "data_sinks": [
                {"id": 1, "name": "Known Sink", "sinkType": "s3"},
                {"id": 2, "name": "Unknown Sink", "sinkType": "future_connector"},
            ],
        }
        nexset = Nexset(**data)
        assert len(nexset.data_sinks) == 2
        assert nexset.data_sinks[0].sink_type == DestinationType.S3
        assert nexset.data_sinks[1].sink_type == "future_connector"


class TestSerializationRoundTrip:
    """Test that flexible enums serialize correctly."""

    def test_known_value_serializes_as_string(self):
        """Known enum values should serialize to their string values."""
        data = {
            "id": 1,
            "name": "Test",
            "status": "ACTIVE",
            "sink_type": "s3",
            "sink_format": "json",
        }
        dest = Destination(**data)
        serialized = dest.model_dump()
        # With use_enum_values=True, should be string "json"
        assert serialized["sink_format"] == "json"

    def test_unknown_value_serializes_unchanged(self):
        """Unknown string values should serialize unchanged."""
        data = {
            "id": 1,
            "name": "Test",
            "status": "ACTIVE",
            "sink_type": "s3",
            "sink_format": "unknown_format",
        }
        dest = Destination(**data)
        serialized = dest.model_dump()
        assert serialized["sink_format"] == "unknown_format"

    def test_json_serialization_with_unknown_value(self):
        """Unknown values should serialize to JSON correctly."""
        data = {
            "id": 1,
            "name": "Test",
            "sinkType": "future_connector",
        }
        sink = DataSinkSimplified(**data)
        json_str = sink.model_dump_json()
        assert "future_connector" in json_str
