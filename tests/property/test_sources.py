"""Property-based tests for sources using hypothesis."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.strategies import composite

from nexla_sdk.models.sources.requests import (
    SourceCopyOptions,
    SourceCreate,
    SourceUpdate,
)
from nexla_sdk.models.sources.responses import DataSetBrief, RunInfo, Source


# Custom strategies for generating test data
@composite
def source_dict(draw):
    """Generate random source data for property testing."""
    return {
        "id": draw(st.integers(min_value=1, max_value=999999)),
        # Avoid whitespace/control chars in names
        "name": draw(
            st.text(
                alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                min_size=1,
                max_size=200,
            )
        ),
        "status": draw(
            st.sampled_from(["ACTIVE", "PAUSED", "DRAFT", "DELETED", "ERROR", "INIT"])
        ),
        "source_type": draw(
            st.sampled_from(["s3", "postgres", "mysql", "api_push", "ftp", "gcs"])
        ),
        "description": draw(
            st.one_of(
                st.none(),
                st.text(
                    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                    max_size=1000,
                ),
            )
        ),
        "ingest_method": draw(
            st.one_of(st.none(), st.sampled_from(["POLL", "API", "STREAMING"]))
        ),
        "source_format": draw(
            st.one_of(st.none(), st.sampled_from(["JSON", "CSV", "XML", "PARQUET"]))
        ),
        "managed": draw(st.booleans()),
        "auto_generated": draw(st.booleans()),
        "access_roles": draw(
            st.lists(
                st.sampled_from(["owner", "admin", "collaborator", "operator"]),
                min_size=1,
                max_size=4,
                unique=True,
            )
        ),
        "tags": draw(
            st.lists(
                st.text(
                    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                    min_size=1,
                    max_size=50,
                ),
                max_size=10,
            )
        ),
        "created_at": draw(st.one_of(st.none(), st.datetimes())),
        "updated_at": draw(st.one_of(st.none(), st.datetimes())),
    }


@composite
def source_create_dict(draw):
    """Generate random source creation data."""
    return {
        # Avoid whitespace/control chars in names
        "name": draw(
            st.text(
                alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                min_size=1,
                max_size=200,
            )
        ),
        "source_type": draw(
            st.sampled_from(["s3", "postgres", "mysql", "api_push", "ftp", "gcs"])
        ),
        # Avoid whitespace/control chars to match the model's str_strip_whitespace
        "description": draw(
            st.one_of(
                st.none(),
                st.text(
                    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                    max_size=1000,
                ),
            )
        ),
        # Required field must be int
        "data_credentials_id": draw(st.integers(min_value=1, max_value=999999)),
        "ingest_method": draw(
            st.one_of(st.none(), st.sampled_from(["POLL", "API", "STREAMING"]))
        ),
    }


@composite
def dataset_brief_dict(draw):
    """Generate random dataset brief data."""
    return {
        "id": draw(st.integers(min_value=1, max_value=999999)),
        "owner_id": draw(st.integers(min_value=1, max_value=999999)),
        "org_id": draw(st.integers(min_value=1, max_value=999999)),
        "name": draw(
            st.one_of(
                st.none(),
                st.text(
                    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                    min_size=1,
                    max_size=200,
                ),
            )
        ),
        "description": draw(
            st.one_of(
                st.none(),
                st.text(
                    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                    max_size=1000,
                ),
            )
        ),
        "version": draw(st.one_of(st.none(), st.integers(min_value=1, max_value=100))),
        "created_at": draw(st.one_of(st.none(), st.datetimes())),
        "updated_at": draw(st.one_of(st.none(), st.datetimes())),
    }


@pytest.mark.unit
class TestSourceModelProperties:
    """Property-based tests for Source model."""

    @given(source_dict())
    def test_source_model_handles_various_inputs(self, source_data):
        """Test that Source model handles various valid inputs correctly."""
        # Act & Assert - Should not raise validation errors
        source = Source(**source_data)

        # Basic assertions
        assert source.id == source_data["id"]
        assert source.name == source_data["name"]
        assert source.status == source_data["status"]
        assert source.source_type == source_data["source_type"]
        assert source.access_roles == source_data["access_roles"]

        # Optional fields should be handled correctly
        assert source.description == source_data.get("description")
        assert source.managed == source_data.get("managed", False)
        assert source.auto_generated == source_data.get("auto_generated", False)

        # Lists should default to empty if None
        expected_tags = source_data.get("tags", [])
        if expected_tags is None:
            expected_tags = []
        assert source.tags == expected_tags

    @given(source_dict())
    def test_source_model_serialization(self, source_data):
        """Test that Source model can be serialized and deserialized."""
        # Arrange
        source = Source(**source_data)

        # Act
        serialized = source.model_dump()
        deserialized = Source(**serialized)

        # Assert
        assert deserialized.id == source.id
        assert deserialized.name == source.name
        assert deserialized.status == source.status
        assert deserialized.source_type == source.source_type

    @given(st.lists(source_dict(), min_size=0, max_size=10))
    def test_source_list_handling(self, sources_data):
        """Test handling lists of sources with various sizes."""
        # Act
        sources = [Source(**data) for data in sources_data]

        # Assert
        assert len(sources) == len(sources_data)
        for i, source in enumerate(sources):
            assert source.id == sources_data[i]["id"]
            assert source.name == sources_data[i]["name"]

    @given(source_create_dict())
    def test_source_create_model_properties(self, create_data):
        """Test SourceCreate model with various inputs."""
        # Act & Assert - Should not raise validation errors
        source_create = SourceCreate(**create_data)

        assert source_create.name == create_data["name"]
        assert source_create.source_type == create_data["source_type"]
        assert source_create.description == create_data.get("description")
        assert source_create.data_credentials_id == create_data.get(
            "data_credentials_id"
        )
        assert source_create.ingest_method == create_data.get("ingest_method")

    @given(
        st.one_of(
            st.none(),
            st.text(
                alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                min_size=1,
                max_size=200,
            ),
        ),
        st.one_of(
            st.none(),
            st.text(
                alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                max_size=1000,
            ),
        ),
    )
    def test_source_update_model_properties(self, name, description):
        """Test SourceUpdate model with various optional fields."""
        # Act
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description

        source_update = SourceUpdate(**update_data)

        # Assert - Account for str_strip_whitespace which may strip whitespace
        assert source_update.name == name
        assert source_update.description == description

    @given(
        st.booleans(),
        st.booleans(),
        st.one_of(st.none(), st.integers(min_value=1, max_value=999999)),
        st.one_of(st.none(), st.integers(min_value=1, max_value=999999)),
    )
    def test_source_copy_options_properties(
        self, reuse_creds, copy_access, owner_id, org_id
    ):
        """Test SourceCopyOptions with various combinations."""
        # Act
        options = SourceCopyOptions(
            reuse_data_credentials=reuse_creds,
            copy_access_controls=copy_access,
            owner_id=owner_id,
            org_id=org_id,
        )

        # Assert
        assert options.reuse_data_credentials == reuse_creds
        assert options.copy_access_controls == copy_access
        assert options.owner_id == owner_id
        assert options.org_id == org_id


@pytest.mark.unit
class TestDataSetBriefProperties:
    """Property-based tests for DataSetBrief model."""

    @given(dataset_brief_dict())
    def test_dataset_brief_model_properties(self, dataset_data):
        """Test DataSetBrief model with various inputs."""
        # Act & Assert
        dataset = DataSetBrief(**dataset_data)

        assert dataset.id == dataset_data["id"]
        assert dataset.owner_id == dataset_data["owner_id"]
        assert dataset.org_id == dataset_data["org_id"]
        assert dataset.name == dataset_data.get("name")
        assert dataset.description == dataset_data.get("description")
        assert dataset.version == dataset_data.get("version")

    @given(st.lists(dataset_brief_dict(), min_size=0, max_size=5))
    def test_multiple_datasets_handling(self, datasets_data):
        """Test handling multiple datasets."""
        # Act
        datasets = [DataSetBrief(**data) for data in datasets_data]

        # Assert
        assert len(datasets) == len(datasets_data)
        for i, dataset in enumerate(datasets):
            assert dataset.id == datasets_data[i]["id"]


@pytest.mark.unit
class TestRunInfoProperties:
    """Property-based tests for RunInfo model."""

    @given(st.integers(min_value=1, max_value=999999), st.datetimes())
    def test_run_info_model_properties(self, run_id, created_at):
        """Test RunInfo model with various inputs."""
        # Act
        run_info = RunInfo(id=run_id, created_at=created_at)

        # Assert
        assert run_info.id == run_id
        assert run_info.created_at == created_at

    @given(
        st.lists(
            st.fixed_dictionaries(
                {
                    "id": st.integers(min_value=1, max_value=999999),
                    "created_at": st.datetimes(),
                }
            ),
            min_size=0,
            max_size=10,
        )
    )
    def test_multiple_run_infos(self, run_data_list):
        """Test handling multiple run info objects."""
        # Act
        run_infos = []
        for run_data in run_data_list:
            if (
                isinstance(run_data, dict)
                and "id" in run_data
                and "created_at" in run_data
            ):
                run_infos.append(RunInfo(**run_data))

        # Assert
        assert len(run_infos) <= len(run_data_list)


@pytest.mark.unit
class TestSourceModelEdgeCases:
    """Test edge cases and boundary conditions for source models."""

    @given(
        st.text(
            alphabet=st.characters(min_codepoint=33, max_codepoint=126),
            min_size=1,
            max_size=1000,
        )
    )
    def test_source_name_variations(self, name):
        """Test source names with various characters and lengths."""
        # Act
        source_data = {
            "id": 123,
            "name": name,
            "status": "ACTIVE",
            "source_type": "s3",
            "access_roles": ["owner"],
        }

        source = Source(**source_data)

        # Assert
        assert source.name == name
        assert len(source.name) >= 1

    @given(
        st.lists(
            st.text(
                alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                min_size=1,
                max_size=50,
            ),
            min_size=0,
            max_size=20,
            unique=True,
        )
    )
    def test_source_tags_variations(self, tags):
        """Test source tags with various combinations."""
        # Act
        source_data = {
            "id": 123,
            "name": "Test Source",
            "status": "ACTIVE",
            "source_type": "s3",
            "access_roles": ["owner"],
            "tags": tags,
        }

        source = Source(**source_data)

        # Assert
        assert source.tags == tags
        assert len(source.tags) == len(set(tags))  # Should maintain uniqueness

    @given(
        st.lists(
            st.sampled_from(["owner", "admin", "collaborator", "operator"]),
            min_size=1,
            max_size=4,
            unique=True,
        )
    )
    def test_access_roles_combinations(self, roles):
        """Test various access role combinations."""
        # Act
        source_data = {
            "id": 123,
            "name": "Test Source",
            "status": "ACTIVE",
            "source_type": "s3",
            "access_roles": roles,
        }

        source = Source(**source_data)

        # Assert
        assert source.access_roles == roles
        assert len(source.access_roles) >= 1  # Should have at least one role

    @given(
        st.one_of(
            st.none(),
            st.text(
                alphabet=st.characters(min_codepoint=33, max_codepoint=126),
                max_size=2000,
            ),
        )
    )
    def test_description_length_handling(self, description):
        """Test handling descriptions of various lengths including None."""
        # Act
        source_data = {
            "id": 123,
            "name": "Test Source",
            "status": "ACTIVE",
            "source_type": "s3",
            "access_roles": ["owner"],
            "description": description,
        }

        source = Source(**source_data)

        # Assert
        assert source.description == description

    @settings(max_examples=50)
    @given(
        st.integers(min_value=1, max_value=999999),
        st.text(
            alphabet=st.characters(min_codepoint=33, max_codepoint=126),
            min_size=1,
            max_size=100,
        ),
        st.sampled_from(["ACTIVE", "PAUSED", "DRAFT", "DELETED", "ERROR", "INIT"]),
        st.sampled_from(
            ["s3", "postgres", "mysql", "api_push", "ftp", "gcs", "bigquery"]
        ),
    )
    def test_source_core_fields_combinations(
        self, source_id, name, status, source_type
    ):
        """Test combinations of core required fields."""
        # Act
        source_data = {
            "id": source_id,
            "name": name,
            "status": status,
            "source_type": source_type,
            "access_roles": ["owner"],
        }

        source = Source(**source_data)

        # Assert
        assert source.id == source_id
        assert source.name == name
        assert source.status == status
        assert source.source_type == source_type
        assert "owner" in source.access_roles
