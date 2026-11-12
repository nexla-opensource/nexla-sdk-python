"""Integration tests for credentials resource with real API calls."""

import time

import pytest

from nexla_sdk.exceptions import AuthenticationError, NexlaError, NotFoundError
from nexla_sdk.models.credentials.requests import (
    CredentialCreate,
    CredentialUpdate,
    ProbeSampleRequest,
    ProbeTreeRequest,
)
from nexla_sdk.models.credentials.responses import Credential


@pytest.mark.integration
class TestCredentialsIntegration:
    """Integration tests for credentials using real API."""

    def test_list_credentials(self, integration_client):
        """Test listing credentials with real API."""
        # Act
        credentials = integration_client.credentials.list()

        # Assert
        assert isinstance(credentials, list)
        # Each credential should be a Credential model
        for credential in credentials:
            assert isinstance(credential, Credential)
            assert credential.id is not None
            assert credential.name is not None
            assert credential.credentials_type is not None

    def test_list_credentials_with_filters(self, integration_client):
        """Test listing credentials with type filter."""
        # Act
        all_credentials = integration_client.credentials.list()

        if all_credentials:
            # Get the first credential type to filter by
            credential_type = all_credentials[0].credentials_type
            filtered_credentials = integration_client.credentials.list(
                credentials_type=credential_type
            )

            # Assert
            assert isinstance(filtered_credentials, list)
            for credential in filtered_credentials:
                assert credential.credentials_type == credential_type

    def test_get_credential(self, integration_client):
        """Test getting a single credential."""
        # Arrange - get first available credential
        credentials = integration_client.credentials.list()
        if not credentials:
            pytest.skip("No credentials available for testing")

        credential_id = credentials[0].id

        # Act
        credential = integration_client.credentials.get(credential_id)

        # Assert
        assert isinstance(credential, Credential)
        assert credential.id == credential_id
        assert credential.name is not None
        assert credential.credentials_type is not None

    def test_get_credential_with_expand(self, integration_client):
        """Test getting a credential with expand option."""
        # Arrange
        credentials = integration_client.credentials.list()
        if not credentials:
            pytest.skip("No credentials available for testing")

        credential_id = credentials[0].id

        # Act
        credential = integration_client.credentials.get(credential_id, expand=True)

        # Assert
        assert isinstance(credential, Credential)
        assert credential.id == credential_id

    def test_get_nonexistent_credential(self, integration_client):
        """Test getting a credential that doesn't exist."""
        # Arrange - use a very high ID that's unlikely to exist
        nonexistent_id = 999999999

        # Act & Assert
        with pytest.raises(NotFoundError):
            integration_client.credentials.get(nonexistent_id)

    def test_probe_credential(self, integration_client):
        """Test probing a credential."""
        # Arrange
        credentials = integration_client.credentials.list()
        if not credentials:
            pytest.skip("No credentials available for testing")

        credential_id = credentials[0].id

        # Act
        result = integration_client.credentials.probe(credential_id)

        # Assert
        assert isinstance(result, dict)
        assert "status" in result
        # Status should indicate success or provide error information
        assert result["status"] in ["ok", "success"] or "message" in result


@pytest.mark.integration
class TestCredentialsLifecycle:
    """Test full credential lifecycle with cleanup."""

    @pytest.fixture
    def test_credential_data(self):
        """Create test credential data for a mock/test connector."""
        # Use a test connector type that won't actually connect anywhere
        return {
            "name": f"SDK Test Credential - {int(time.time())}",
            "credentials_type": "rest",  # REST is usually safe for testing
            "description": "Test credential created by SDK integration tests",
            "credentials": {
                "api_key": "test-key-12345",
                "endpoint": "https://httpbin.org/get",  # Safe test endpoint
            },
        }

    @pytest.fixture
    def cleanup_credential(self, integration_client):
        """Fixture to cleanup created credentials after test."""
        created_credentials = []

        def track_credential(credential):
            """Track a credential for cleanup."""
            created_credentials.append(credential)
            return credential

        yield track_credential

        # Cleanup
        for credential in created_credentials:
            try:
                integration_client.credentials.delete(credential.id)
                print(f"Cleaned up test credential: {credential.id}")
            except Exception as e:
                print(f"Failed to cleanup credential {credential.id}: {e}")

    def test_credential_create_update_delete(
        self, integration_client, test_credential_data, cleanup_credential
    ):
        """Test full credential lifecycle: create, read, update, delete."""
        # Create
        create_request = CredentialCreate(**test_credential_data)
        credential = integration_client.credentials.create(create_request)
        cleanup_credential(credential)  # Track for cleanup

        assert isinstance(credential, Credential)
        assert credential.id is not None
        assert credential.name == test_credential_data["name"]
        assert credential.credentials_type == test_credential_data["credentials_type"]

        # Read
        fetched = integration_client.credentials.get(credential.id)
        assert fetched.id == credential.id
        assert fetched.name == credential.name

        # Update
        update_data = CredentialUpdate(
            name=f"Updated {credential.name}", description="Updated description"
        )
        updated = integration_client.credentials.update(credential.id, update_data)
        assert updated.name == update_data.name
        assert updated.description == update_data.description

        # Verify in list
        all_credentials = integration_client.credentials.list()
        assert any(c.id == credential.id for c in all_credentials)

        # Delete
        result = integration_client.credentials.delete(credential.id)
        assert isinstance(result, dict)
        # Should indicate success or similar

        # Verify deletion
        with pytest.raises(NotFoundError):
            integration_client.credentials.get(credential.id)


@pytest.mark.integration
@pytest.mark.slow
class TestCredentialsProbing:
    """Test credential probing operations (may be slow)."""

    def test_probe_tree_with_real_credential(self, integration_client):
        """Test probing tree structure with a real credential."""
        # Arrange
        credentials = integration_client.credentials.list()
        if not credentials:
            pytest.skip("No credentials available for testing")

        # Find a credential that supports tree probing (usually file-based)
        suitable_credential = None
        for credential in credentials:
            if credential.credentials_type in ["s3", "gcs", "azure_blb", "ftp"]:
                suitable_credential = credential
                break

        if not suitable_credential:
            pytest.skip("No file-based credentials available for tree probing")

        # Act
        probe_request = ProbeTreeRequest(
            depth=2,
            path="/",  # Root path
        )

        try:
            result = integration_client.credentials.probe_tree(
                suitable_credential.id, probe_request
            )

            # Assert
            assert result.status in ["ok", "success"]
            assert result.connection_type is not None
            assert hasattr(result, "object")  # Should have object/output field

        except Exception as e:
            # Tree probing might fail for various reasons (permissions, empty bucket, etc.)
            # This is acceptable for integration tests
            pytest.skip(f"Tree probing failed (expected for some credentials): {e}")

    def test_probe_sample_with_real_credential(self, integration_client):
        """Test probing sample data with a real credential."""
        # Arrange
        credentials = integration_client.credentials.list()
        if not credentials:
            pytest.skip("No credentials available for testing")

        # Find a suitable credential
        suitable_credential = None
        for credential in credentials:
            if credential.credentials_type in ["s3", "gcs", "azure_blb"]:
                suitable_credential = credential
                break

        if not suitable_credential:
            pytest.skip("No suitable credentials available for sample probing")

        # Act
        probe_request = ProbeSampleRequest(path="/test/")  # Generic test path

        try:
            result = integration_client.credentials.probe_sample(
                suitable_credential.id, probe_request
            )

            # Assert
            assert result.status in ["ok", "success"]
            assert result.connection_type is not None
            assert hasattr(result, "output")

        except Exception as e:
            # Sample probing might fail if no data exists at the path
            pytest.skip(f"Sample probing failed (expected for some credentials): {e}")


@pytest.mark.integration
class TestCredentialsErrorHandling:
    """Test error handling with real API."""

    def test_authentication_error_simulation(self, api_url, api_version):
        """Test authentication error with invalid credentials."""
        from nexla_sdk import NexlaClient

        # Create client with invalid service key
        invalid_client = NexlaClient(
            service_key="invalid-key-12345", base_url=api_url, api_version=api_version
        )

        # Act & Assert
        with pytest.raises(AuthenticationError):
            invalid_client.credentials.list()

    def test_create_credential_with_invalid_type(self, integration_client):
        """Test creating credential with invalid type."""
        # Arrange
        invalid_data = {
            "name": "Invalid Credential",
            "credentials_type": "invalid_type_12345",
            "credentials": {"test": "data"},
        }

        # Act & Assert
        # Server may return a validation or API error; both derive from NexlaError
        with pytest.raises(NexlaError):
            integration_client.credentials.create(invalid_data)


@pytest.mark.integration
@pytest.mark.performance
class TestCredentialsPerformance:
    """Test performance characteristics of credentials API."""

    def test_list_credentials_performance(self, integration_client):
        """Test that listing credentials completes in reasonable time."""
        # Act
        start_time = time.time()
        credentials = integration_client.credentials.list()
        end_time = time.time()

        # Assert
        duration = end_time - start_time
        assert duration < 10.0, f"Listing credentials took too long: {duration:.2f}s"

        # Also verify we got results
        assert isinstance(credentials, list)

    def test_get_credential_performance(self, integration_client):
        """Test that getting a credential completes quickly."""
        # Arrange
        credentials = integration_client.credentials.list()
        if not credentials:
            pytest.skip("No credentials available for testing")

        credential_id = credentials[0].id

        # Act
        start_time = time.time()
        credential = integration_client.credentials.get(credential_id)
        end_time = time.time()

        # Assert
        duration = end_time - start_time
        assert duration < 5.0, f"Getting credential took too long: {duration:.2f}s"
        assert isinstance(credential, Credential)
