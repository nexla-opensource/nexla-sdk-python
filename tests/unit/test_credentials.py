"""Unit tests for credentials resource."""

import pytest
from pydantic import ValidationError

from nexla_sdk.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NexlaError,
    NotFoundError,
    RateLimitError,
    ResourceConflictError,
    ServerError,
)
from nexla_sdk.exceptions import ValidationError as SDKValidationError
from nexla_sdk.http_client import HttpClientError
from nexla_sdk.models.credentials.requests import (
    CredentialCreate,
    ProbeSampleRequest,
    ProbeTreeRequest,
)
from nexla_sdk.models.credentials.responses import (
    Credential,
    ProbeSampleResponse,
    ProbeTreeResponse,
)
from tests.utils import (
    MockResponseBuilder,
    assert_model_list_valid,
    assert_model_valid,
    create_http_error,
)


@pytest.mark.unit
class TestCredentialsResourceUnit:
    """Unit tests for CredentialsResource using mocks."""

    def test_list_credentials_success(
        self, mock_client, mock_http_client, sample_credentials_list
    ):
        """Test listing credentials with successful response."""
        # Arrange
        mock_http_client.add_response("/data_credentials", sample_credentials_list)

        # Act
        credentials = mock_client.credentials.list()

        # Assert
        assert len(credentials) == 3
        assert_model_list_valid(credentials, Credential)
        mock_http_client.assert_request_made("GET", "/data_credentials")

        # Verify first credential structure
        first_credential = credentials[0]
        assert first_credential.id is not None
        assert first_credential.name is not None
        assert first_credential.credentials_type is not None

    def test_list_credentials_with_filters(
        self, mock_client, mock_http_client, sample_credentials_list
    ):
        """Test listing credentials with filters."""
        # Arrange
        mock_http_client.add_response("/data_credentials", sample_credentials_list)

        # Act
        credentials = mock_client.credentials.list(
            credentials_type="s3", access_role="owner", page=1, per_page=10
        )

        # Assert
        assert len(credentials) == 3

        # Verify request parameters
        request = mock_http_client.get_request()
        assert (
            "credentials_type=s3" in request["url"]
            or request.get("params", {}).get("credentials_type") == "s3"
        )

    def test_get_credential_success(
        self, mock_client, mock_http_client, sample_credential_response
    ):
        """Test getting a single credential."""
        # Arrange
        credential_id = 123
        mock_http_client.add_response(
            f"/data_credentials/{credential_id}", sample_credential_response
        )

        # Act
        credential = mock_client.credentials.get(credential_id)

        # Assert
        assert_model_valid(credential, {"id": sample_credential_response["id"]})
        mock_http_client.assert_request_made(
            "GET", f"/data_credentials/{credential_id}"
        )

    def test_get_credential_with_expand(
        self, mock_client, mock_http_client, sample_credential_response
    ):
        """Test getting a credential with expand option."""
        # Arrange
        credential_id = 123
        mock_http_client.add_response(
            f"/data_credentials/{credential_id}", sample_credential_response
        )

        # Act
        credential = mock_client.credentials.get(credential_id, expand=True)

        # Assert
        assert isinstance(credential, Credential)
        request = mock_http_client.get_request()
        # Check for expand parameter
        assert (
            "expand=1" in request["url"] or request.get("params", {}).get("expand") == 1
        )

    def test_create_credential_success(
        self,
        mock_client,
        mock_http_client,
        sample_credential_data,
        sample_credential_response,
    ):
        """Test creating a credential successfully."""
        # Arrange
        mock_http_client.add_response("/data_credentials", sample_credential_response)
        create_request = CredentialCreate(**sample_credential_data)

        # Act
        credential = mock_client.credentials.create(create_request)

        # Assert
        assert isinstance(credential, Credential)
        mock_http_client.assert_request_made("POST", "/data_credentials")

        # Verify the request body
        request = mock_http_client.get_request()
        assert "json" in request
        assert request["json"]["name"] == sample_credential_data["name"]
        assert (
            request["json"]["credentials_type"]
            == sample_credential_data["credentials_type"]
        )

    def test_create_credential_with_dict(
        self,
        mock_client,
        mock_http_client,
        sample_credential_data,
        sample_credential_response,
    ):
        """Test creating a credential with dict input."""
        # Arrange
        mock_http_client.add_response("/data_credentials", sample_credential_response)

        # Act
        credential = mock_client.credentials.create(sample_credential_data)

        # Assert
        assert isinstance(credential, Credential)
        mock_http_client.assert_request_made("POST", "/data_credentials")

    def test_update_credential_success(
        self, mock_client, mock_http_client, sample_credential_response
    ):
        """Test updating a credential."""
        # Arrange
        credential_id = 123
        update_data = {
            "name": "Updated Credential Name",
            "description": "Updated description",
        }
        updated_response = sample_credential_response.copy()
        updated_response.update(update_data)

        mock_http_client.add_response(
            f"/data_credentials/{credential_id}", updated_response
        )

        # Act
        credential = mock_client.credentials.update(credential_id, update_data)

        # Assert
        assert isinstance(credential, Credential)
        assert credential.name == update_data["name"]
        mock_http_client.assert_request_made(
            "PUT", f"/data_credentials/{credential_id}"
        )

    def test_delete_credential_success(self, mock_client, mock_http_client):
        """Test deleting a credential."""
        # Arrange
        credential_id = 123
        delete_response = {"status": "success", "message": "Credential deleted"}
        mock_http_client.add_response(
            f"/data_credentials/{credential_id}", delete_response
        )

        # Act
        result = mock_client.credentials.delete(credential_id)

        # Assert
        assert result["status"] == "success"
        mock_http_client.assert_request_made(
            "DELETE", f"/data_credentials/{credential_id}"
        )

    def test_probe_credential_success(self, mock_client, mock_http_client):
        """Test probing a credential successfully."""
        # Arrange
        credential_id = 123
        probe_response = MockResponseBuilder.probe_response()
        mock_http_client.add_response(
            f"/data_credentials/{credential_id}/probe", probe_response
        )

        # Act
        result = mock_client.credentials.probe(credential_id)

        # Assert
        assert result["status"] == "success"
        mock_http_client.assert_request_made(
            "GET", f"/data_credentials/{credential_id}/probe"
        )

    def test_probe_credential_none_response(self, mock_client, mock_http_client):
        """Test probing a credential with None response."""
        # Arrange
        credential_id = 123
        mock_http_client.add_response(f"/data_credentials/{credential_id}/probe", None)

        # Act
        result = mock_client.credentials.probe(credential_id)

        # Assert
        assert result["status"] == "success"
        assert "Credential probe completed successfully" in result["message"]

    def test_probe_tree_success(
        self, mock_client, mock_http_client, sample_probe_tree_request
    ):
        """Test probing tree structure successfully."""
        # Arrange
        credential_id = 123
        tree_response = MockResponseBuilder.probe_tree_response("s3")
        mock_http_client.add_response(
            f"/data_credentials/{credential_id}/probe/tree", tree_response
        )

        probe_request = ProbeTreeRequest(**sample_probe_tree_request)

        # Act
        result = mock_client.credentials.probe_tree(credential_id, probe_request)

        # Assert
        assert isinstance(result, ProbeTreeResponse)
        assert result.status == "ok"
        assert result.connection_type == "s3"
        mock_http_client.assert_request_made(
            "POST", f"/data_credentials/{credential_id}/probe/tree"
        )

    def test_probe_sample_success(
        self, mock_client, mock_http_client, sample_probe_sample_request
    ):
        """Test probing sample data successfully."""
        # Arrange
        credential_id = 123
        sample_response = MockResponseBuilder.probe_sample_response("s3")
        mock_http_client.add_response(
            f"/data_credentials/{credential_id}/probe/sample", sample_response
        )

        probe_request = ProbeSampleRequest(**sample_probe_sample_request)

        # Act
        result = mock_client.credentials.probe_sample(credential_id, probe_request)

        # Assert
        assert isinstance(result, ProbeSampleResponse)
        assert result.status == "ok"
        assert result.connection_type == "s3"
        mock_http_client.assert_request_made(
            "POST", f"/data_credentials/{credential_id}/probe/sample"
        )


@pytest.mark.unit
class TestCredentialsErrorHandling:
    """Test error handling for credentials operations."""

    def test_get_credential_not_found(self, mock_client, mock_http_client):
        """Test getting a non-existent credential."""
        # Arrange
        credential_id = 999
        error = create_http_error(
            404,
            "Credential not found",
            {"resource_type": "credential", "resource_id": str(credential_id)},
        )

        # Set up mock to return error for the specific GET request
        mock_http_client.add_response(f"/data_credentials/{credential_id}", error)

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            mock_client.credentials.get(credential_id)

        assert exc_info.value.resource_id == str(credential_id)

    def test_create_credential_validation_error(self, mock_client):
        """Test creating credential with invalid data."""
        # Arrange - missing required fields
        invalid_data = {"name": ""}  # Empty name

        # Act & Assert
        with pytest.raises(ValidationError):
            CredentialCreate(**invalid_data)

    def test_authentication_error_during_list(self, mock_client, mock_http_client):
        """Test handling authentication errors during API calls."""
        # Arrange
        auth_error = create_http_error(
            401, "Authentication failed. Check your service key."
        )

        # Mock both the credentials list request AND the session token obtain request
        # to return 401 errors so the retry also fails
        mock_http_client.add_response("/data_credentials", auth_error)
        mock_http_client.add_response("/token", auth_error)

        # Act & Assert
        with pytest.raises(AuthenticationError):
            mock_client.credentials.list()

    def test_server_error_during_list(self, mock_client, mock_http_client):
        """Test handling server errors during API calls."""
        # Arrange
        error = create_http_error(500, "Internal server error")
        mock_http_client.add_response("/data_credentials", error)

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.credentials.list()

        assert exc_info.value.status_code == 500

    @pytest.mark.parametrize(
        "status_code,expected_exception",
        [
            (400, SDKValidationError),
            (403, AuthorizationError),
            (404, NotFoundError),
            (409, ResourceConflictError),
            (422, SDKValidationError),
            (429, RateLimitError),
            (500, ServerError),
        ],
    )
    def test_various_http_errors_during_list(
        self, mock_client, mock_http_client, status_code, expected_exception
    ):
        """Test handling of various HTTP error codes during list operations."""
        # Arrange
        error = create_http_error(status_code, f"Error {status_code}")
        mock_http_client.add_response("/data_credentials", error)

        # Act & Assert
        with pytest.raises(expected_exception):
            mock_client.credentials.list()

    def test_network_error_simulation(self, mock_client, mock_http_client):
        """Test handling of network-level errors."""

        # Arrange - simulate a network error
        network_error = HttpClientError("Connection timeout")
        mock_http_client.add_response("/data_credentials", network_error)

        # Act & Assert
        with pytest.raises(NexlaError):
            mock_client.credentials.list()


@pytest.mark.unit
class TestCredentialsModels:
    """Test credential model validation and serialization."""

    def test_credential_model_creation(self, sample_credential_response):
        """Test creating a Credential model from response data."""
        # Act
        credential = Credential(**sample_credential_response)

        # Assert
        assert credential.id == sample_credential_response["id"]
        assert credential.name == sample_credential_response["name"]
        assert (
            credential.credentials_type
            == sample_credential_response["credentials_type"]
        )

    def test_credential_model_with_missing_optional_fields(self):
        """Test creating a Credential model with minimal data."""
        # Arrange
        minimal_data = {"id": 123, "name": "Test Credential", "credentials_type": "s3"}

        # Act
        credential = Credential(**minimal_data)

        # Assert
        assert credential.id == 123
        assert credential.name == "Test Credential"
        assert credential.credentials_type == "s3"
        assert credential.description is None
        assert credential.tags == []  # Default factory should provide empty list

    def test_credential_create_model_validation(self):
        """Test CredentialCreate model validation."""
        # Valid data
        valid_data = {
            "name": "Test Credential",
            "credentials_type": "s3",
            "credentials": {"access_key": "test", "secret_key": "test"},
        }

        # Act & Assert - should not raise
        credential_create = CredentialCreate(**valid_data)
        assert credential_create.name == "Test Credential"
        assert credential_create.credentials_type == "s3"

    def test_credential_create_missing_required_fields(self):
        """Test CredentialCreate with missing required fields."""
        # Arrange - missing name
        invalid_data = {"credentials_type": "s3"}

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            CredentialCreate(**invalid_data)

        # Check that the error mentions the missing field
        error_details = str(exc_info.value)
        assert "name" in error_details

    def test_probe_tree_request_model(self):
        """Test ProbeTreeRequest model."""
        # Test with file system data
        file_data = {"depth": 3, "path": "/test/path"}
        probe_request = ProbeTreeRequest(**file_data)
        assert probe_request.depth == 3
        assert probe_request.path == "/test/path"

        # Test with database data
        db_data = {"depth": 2, "database": "testdb", "table": "testtable"}
        probe_request = ProbeTreeRequest(**db_data)
        assert probe_request.depth == 2
        assert probe_request.database == "testdb"
        assert probe_request.table == "testtable"

    def test_probe_sample_request_model(self):
        """Test ProbeSampleRequest model."""
        # Test with path only
        path_data = {"path": "/test/file.json"}
        probe_request = ProbeSampleRequest(**path_data)
        assert probe_request.path == "/test/file.json"

    def test_model_serialization(self, sample_credential_response):
        """Test model serialization to dict and JSON."""
        # Act
        credential = Credential(**sample_credential_response)

        # Test to_dict
        credential_dict = credential.to_dict()
        assert isinstance(credential_dict, dict)
        assert credential_dict["id"] == sample_credential_response["id"]

        # Test to_json
        credential_json = credential.to_json()
        assert isinstance(credential_json, str)
        assert str(sample_credential_response["id"]) in credential_json

    def test_model_string_representation(self, sample_credential_response):
        """Test model string representation."""
        # Act
        credential = Credential(**sample_credential_response)

        # Assert
        str_repr = str(credential)
        assert "Credential" in str_repr
        assert str(credential.id) in str_repr
        assert credential.name in str_repr
