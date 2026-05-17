"""Unit tests for validators resource."""

import pytest

from nexla_sdk.models.validators.requests import (
    ValidatorCopyOptions,
    ValidatorCreate,
    ValidatorUpdate,
)
from nexla_sdk.models.validators.responses import Validator
from tests.utils import assert_model_list_valid, assert_model_valid

# Sample response data
SAMPLE_VALIDATOR = {
    "id": 123,
    "name": "Test Validator",
    "description": "A test validator",
    "resource_type": "validator",
    "code_type": "python",
    "output_type": "record",
    "code": "def validate(record): return record['value'] > 0",
    "code_config": {},
    "code_encoding": "none",
    "custom_config": {},
    "reusable": True,
    "public": False,
    "managed": False,
    "owner": {"id": 1, "full_name": "Test User", "email": "test@example.com"},
    "org": {"id": 1, "name": "Test Org", "email_domain": "example.com"},
    "access_roles": ["owner"],
    "data_sets": [1, 2],
    "tags": ["test", "validation"],
    "copied_from_id": None,
    "updated_at": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z",
}

SAMPLE_VALIDATORS_LIST = [
    SAMPLE_VALIDATOR,
    {**SAMPLE_VALIDATOR, "id": 124, "name": "Another Validator"},
    {**SAMPLE_VALIDATOR, "id": 125, "name": "Third Validator"},
]


@pytest.fixture
def sample_validator_response():
    """Sample validator response."""
    return SAMPLE_VALIDATOR.copy()


@pytest.fixture
def sample_validators_list():
    """Sample validators list response."""
    return [v.copy() for v in SAMPLE_VALIDATORS_LIST]


@pytest.mark.unit
class TestValidatorsResource:
    """Unit tests for ValidatorsResource using mocks."""

    def test_list_validators_success(
        self, mock_client, mock_http_client, sample_validators_list
    ):
        """Test listing validators with successful response."""
        mock_http_client.add_response("/validators", sample_validators_list)

        validators = mock_client.validators.list()

        assert len(validators) == 3
        assert_model_list_valid(validators, Validator)
        mock_http_client.assert_request_made("GET", "/validators")

    def test_list_validators_with_filters(
        self, mock_client, mock_http_client, sample_validators_list
    ):
        """Test listing validators with filters."""
        mock_http_client.add_response("/validators", sample_validators_list)

        validators = mock_client.validators.list(
            access_role="owner", page=1, per_page=10, expand=True
        )

        assert len(validators) == 3
        request = mock_http_client.get_request()
        assert "expand" in str(request)

    def test_list_public_validators(
        self, mock_client, mock_http_client, sample_validators_list
    ):
        """Test listing public validators."""
        mock_http_client.add_response("/validators/public", sample_validators_list)

        validators = mock_client.validators.list_public()

        assert len(validators) == 3
        mock_http_client.assert_request_made("GET", "/validators/public")

    def test_get_validator_success(
        self, mock_client, mock_http_client, sample_validator_response
    ):
        """Test getting a single validator."""
        validator_id = 123
        mock_http_client.add_response(
            f"/validators/{validator_id}", sample_validator_response
        )

        validator = mock_client.validators.get(validator_id)

        assert_model_valid(validator, {"id": validator_id})
        mock_http_client.assert_request_made("GET", f"/validators/{validator_id}")

    def test_create_validator_success(
        self, mock_client, mock_http_client, sample_validator_response
    ):
        """Test creating a validator."""
        mock_http_client.add_response("/validators", sample_validator_response)

        create_data = ValidatorCreate(
            name="Test Validator",
            code_type="python",
            code="def validate(record): return True",
        )
        validator = mock_client.validators.create(create_data)

        assert_model_valid(validator, {"name": "Test Validator"})
        mock_http_client.assert_request_made("POST", "/validators")

    def test_update_validator_success(
        self, mock_client, mock_http_client, sample_validator_response
    ):
        """Test updating a validator."""
        validator_id = 123
        updated_response = {**sample_validator_response, "name": "Updated Validator"}
        mock_http_client.add_response(f"/validators/{validator_id}", updated_response)

        update_data = ValidatorUpdate(name="Updated Validator")
        validator = mock_client.validators.update(validator_id, update_data)

        assert validator.name == "Updated Validator"
        mock_http_client.assert_request_made("PUT", f"/validators/{validator_id}")

    def test_delete_validator_success(self, mock_client, mock_http_client):
        """Test deleting a validator."""
        validator_id = 123
        mock_http_client.add_response(f"/validators/{validator_id}", {"success": True})

        result = mock_client.validators.delete(validator_id)

        assert result["success"] is True
        mock_http_client.assert_request_made("DELETE", f"/validators/{validator_id}")

    def test_copy_validator_success(
        self, mock_client, mock_http_client, sample_validator_response
    ):
        """Test copying a validator."""
        validator_id = 123
        copied_response = {
            **sample_validator_response,
            "id": 200,
            "copied_from_id": 123,
        }
        mock_http_client.add_response(
            f"/validators/{validator_id}/copy", copied_response
        )

        options = ValidatorCopyOptions(owner_id=2)
        validator = mock_client.validators.copy(validator_id, options)

        assert validator.id == 200
        assert validator.copied_from_id == 123
        mock_http_client.assert_request_made("POST", f"/validators/{validator_id}/copy")

    def test_get_tags_success(self, mock_client, mock_http_client):
        """Test getting validator tags."""
        validator_id = 123
        tags = ["tag1", "tag2", "tag3"]
        mock_http_client.add_response(f"/validators/{validator_id}/tags", tags)

        result = mock_client.validators.get_tags(validator_id)

        assert result == tags
        mock_http_client.assert_request_made("GET", f"/validators/{validator_id}/tags")

    def test_set_tags_success(self, mock_client, mock_http_client):
        """Test setting validator tags."""
        validator_id = 123
        new_tags = ["new_tag1", "new_tag2"]
        mock_http_client.add_response(f"/validators/{validator_id}/tags", new_tags)

        result = mock_client.validators.set_tags(validator_id, new_tags)

        assert result == new_tags
        mock_http_client.assert_request_made("POST", f"/validators/{validator_id}/tags")

    def test_add_tags_success(self, mock_client, mock_http_client):
        """Test adding validator tags."""
        validator_id = 123
        updated_tags = ["tag1", "tag2", "new_tag"]
        mock_http_client.add_response(f"/validators/{validator_id}/tags", updated_tags)

        result = mock_client.validators.add_tags(validator_id, ["new_tag"])

        assert result == updated_tags
        mock_http_client.assert_request_made("PUT", f"/validators/{validator_id}/tags")

    def test_remove_tags_success(self, mock_client, mock_http_client):
        """Test removing validator tags."""
        validator_id = 123
        remaining_tags = ["tag1"]
        mock_http_client.add_response(
            f"/validators/{validator_id}/tags", remaining_tags
        )

        result = mock_client.validators.remove_tags(validator_id, ["tag2"])

        assert result == remaining_tags
        mock_http_client.assert_request_made(
            "DELETE", f"/validators/{validator_id}/tags"
        )

    def test_search_tags_success(
        self, mock_client, mock_http_client, sample_validators_list
    ):
        """Test searching validators by tags."""
        mock_http_client.add_response("/validators/search_tags", sample_validators_list)

        validators = mock_client.validators.search_tags(["test", "validation"])

        assert len(validators) == 3
        mock_http_client.assert_request_made("POST", "/validators/search_tags")


@pytest.mark.unit
class TestValidatorModels:
    """Unit tests for validator models."""

    def test_validator_model_validation(self, sample_validator_response):
        """Test Validator model parses valid data correctly."""
        validator = Validator.model_validate(sample_validator_response)

        assert validator.id == 123
        assert validator.name == "Test Validator"
        assert validator.code_type == "python"
        assert validator.resource_type == "validator"
        assert validator.reusable is True
        assert validator.public is False
        assert "test" in validator.tags

    def test_validator_create_model_serialization(self):
        """Test ValidatorCreate model serialization."""
        create_data = ValidatorCreate(
            name="My Validator",
            code_type="python",
            code="def validate(r): return True",
            tags=["validation"],
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["name"] == "My Validator"
        assert data["code_type"] == "python"
        assert "tags" in data
        assert data["resource_type"] == "validator"

    def test_validator_update_model_serialization(self):
        """Test ValidatorUpdate model serialization."""
        update_data = ValidatorUpdate(
            name="Updated Name",
            description="Updated description",
        )

        data = update_data.model_dump(exclude_none=True)

        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        # code_type should not be present since it wasn't set
        assert "code_type" not in data

    def test_validator_copy_options_serialization(self):
        """Test ValidatorCopyOptions model serialization."""
        options = ValidatorCopyOptions(
            owner_id=5,
            copy_access_controls=True,
        )

        data = options.model_dump(exclude_none=True)

        assert data["owner_id"] == 5
        assert data["copy_access_controls"] is True
