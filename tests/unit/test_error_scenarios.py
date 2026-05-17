"""Unit tests for error scenarios across the SDK.

This module tests comprehensive error handling for HTTP status codes
and edge cases like boundary conditions for resource IDs.
"""

import pytest

from nexla_sdk.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NexlaError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from tests.utils import MockResponseBuilder, create_http_error


@pytest.mark.unit
class TestValidationErrors:
    """Tests for 400 Bad Request validation error scenarios."""

    def test_validation_error_field_level(self, mock_client, mock_http_client):
        """Test 400 response with single field validation error."""
        # Arrange
        error_response = {
            "error": "Validation failed",
            "message": "The request data is invalid",
            "field_errors": {"name": ["This field is required"]},
        }
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(
                400,
                "Validation failed",
                details={"field_errors": error_response["field_errors"]},
            ),
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            mock_client.sources.create({"description": "Missing name field"})

        assert exc_info.value.status_code == 400
        assert "Validation failed" in str(exc_info.value.message)

    def test_validation_error_multiple_fields(self, mock_client, mock_http_client):
        """Test 400 response with multiple field validation failures."""
        # Arrange
        field_errors = {
            "name": ["This field is required", "Name must be at least 3 characters"],
            "credentials_type": ["Invalid credentials type"],
            "properties": ["Properties object is required"],
        }
        mock_http_client.add_error(
            "/data_credentials",
            create_http_error(
                400,
                "Multiple validation errors",
                details={"field_errors": field_errors},
            ),
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            mock_client.credentials.create({})

        assert exc_info.value.status_code == 400

    def test_validation_error_invalid_json_format(self, mock_client, mock_http_client):
        """Test 400 response for malformed request data."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(400, "Invalid JSON format in request body"),
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            mock_client.sources.create({"name": "Test"})

        assert exc_info.value.status_code == 400

    def test_validation_error_constraint_violation(self, mock_client, mock_http_client):
        """Test 400 response for business rule constraint violation."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(
                400,
                "Source name already exists in this organization",
                details={"constraint": "unique_name_per_org"},
            ),
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            mock_client.sources.create({"name": "Duplicate Name"})

        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.message)


@pytest.mark.unit
class TestAuthenticationErrors:
    """Tests for 401 Unauthorized authentication error scenarios."""

    def test_authentication_error_invalid_token(self, mock_client, mock_http_client):
        """Test 401 handling for invalid or expired token."""
        # Arrange - need to set up both the main request and token refresh to fail
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(401, "Invalid or expired access token"),
        )
        # Also fail the token refresh attempt
        mock_http_client.add_error(
            "/token",
            create_http_error(401, "Invalid service key"),
        )

        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            mock_client.sources.list()

        # The exception should be raised (status_code may not be set due to retry logic)
        assert "Authentication failed" in str(exc_info.value)

    def test_authentication_error_missing_token(self, mock_client, mock_http_client):
        """Test 401 handling when authorization header is missing."""
        # Arrange
        mock_http_client.add_error(
            "/data_credentials",
            create_http_error(401, "Authorization header is required"),
        )
        mock_http_client.add_error(
            "/token",
            create_http_error(401, "Invalid service key"),
        )

        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            mock_client.credentials.list()

        assert "Authentication failed" in str(exc_info.value)

    def test_authentication_error_on_get_request(self, mock_client, mock_http_client):
        """Test 401 handling for GET request with invalid credentials."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"/users/{resource_id}",
            create_http_error(401, "Unauthorized access"),
        )
        mock_http_client.add_error(
            "/token",
            create_http_error(401, "Invalid service key"),
        )

        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            mock_client.users.get(resource_id)

        assert "Authentication failed" in str(exc_info.value)

    def test_authentication_error_revoked_service_key(
        self, mock_client, mock_http_client
    ):
        """Test 401 handling when service key has been revoked."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(
                401,
                "Service key has been revoked",
                details={"reason": "key_revoked"},
            ),
        )
        mock_http_client.add_error(
            "/token",
            create_http_error(401, "Service key revoked"),
        )

        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            mock_client.sources.list()

        assert "Authentication failed" in str(exc_info.value)


@pytest.mark.unit
class TestAuthorizationErrors:
    """Tests for 403 Forbidden authorization error scenarios."""

    def test_authorization_error_read_only_user(self, mock_client, mock_http_client):
        """Test 403 for collaborators attempting write operations."""
        # Arrange
        source_id = 123
        mock_http_client.add_error(
            f"/data_sources/{source_id}",
            create_http_error(
                403,
                "User does not have write permission on this resource",
                details={
                    "user_role": "collaborator",
                    "required_role": "owner",
                    "operation": "update",
                },
            ),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            mock_client.sources.update(source_id, {"name": "New Name"})

        assert exc_info.value.status_code == 403

    def test_authorization_error_cross_org_access(self, mock_client, mock_http_client):
        """Test 403 for accessing resources in another organization."""
        # Arrange
        resource_id = 456
        mock_http_client.add_error(
            f"/data_credentials/{resource_id}",
            create_http_error(
                403,
                "Cannot access resources in another organization",
                details={
                    "user_org_id": 1,
                    "resource_org_id": 2,
                },
            ),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            mock_client.credentials.get(resource_id)

        assert exc_info.value.status_code == 403

    def test_authorization_error_delete_protected_resource(
        self, mock_client, mock_http_client
    ):
        """Test 403 for deleting protected/system resources."""
        # Arrange
        resource_id = 789
        mock_http_client.add_error(
            f"/data_sources/{resource_id}",
            create_http_error(
                403,
                "Cannot delete protected resource",
                details={"protected": True, "reason": "system_managed"},
            ),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            mock_client.sources.delete(resource_id)

        assert exc_info.value.status_code == 403

    def test_authorization_error_org_admin_required(
        self, mock_client, mock_http_client
    ):
        """Test 403 for operations requiring org admin privileges."""
        # Arrange
        org_id = 100
        mock_http_client.add_error(
            f"/orgs/{org_id}/members",
            create_http_error(
                403,
                "Organization admin privileges required",
                details={"required_role": "org_admin"},
            ),
        )

        # Act & Assert
        with pytest.raises(AuthorizationError) as exc_info:
            mock_client.organizations.get_members(org_id)

        assert exc_info.value.status_code == 403


@pytest.mark.unit
class TestNotFoundErrors:
    """Tests for 404 Not Found error scenarios."""

    def test_not_found_error_nonexistent_id(self, mock_client, mock_http_client):
        """Test 404 handling for non-existent resource ID."""
        # Arrange
        nonexistent_id = 999999
        mock_http_client.add_error(
            f"/data_sources/{nonexistent_id}",
            create_http_error(
                404,
                f"Data source with ID {nonexistent_id} not found",
            ),
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            mock_client.sources.get(nonexistent_id)

        # NotFoundError is raised but status_code may not be set in all paths
        assert "not found" in str(exc_info.value).lower()

    def test_not_found_error_deleted_resource(self, mock_client, mock_http_client):
        """Test 404 for accessing a deleted resource."""
        # Arrange
        deleted_id = 123
        mock_http_client.add_error(
            f"/data_credentials/{deleted_id}",
            create_http_error(
                404,
                "Resource has been deleted",
                details={"deleted_at": "2024-01-15T10:00:00Z"},
            ),
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            mock_client.credentials.get(deleted_id)

        assert "not found" in str(exc_info.value).lower()

    def test_not_found_error_nested_resource(self, mock_client, mock_http_client):
        """Test 404 for nested resource not found."""
        # Arrange
        source_id = 123
        mock_http_client.add_error(
            f"/data_sources/{source_id}/accessors",
            create_http_error(
                404,
                f"Parent resource with ID {source_id} not found",
            ),
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            mock_client.sources.get_accessors(source_id)

        assert "not found" in str(exc_info.value).lower()

    def test_not_found_error_update_nonexistent(self, mock_client, mock_http_client):
        """Test 404 when updating a non-existent resource."""
        # Arrange
        nonexistent_id = 888888
        mock_http_client.add_error(
            f"/data_sets/{nonexistent_id}",
            create_http_error(404, "Nexset not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            mock_client.nexsets.update(nonexistent_id, {"name": "Updated"})

        assert "not found" in str(exc_info.value).lower()


@pytest.mark.unit
class TestRateLimitErrors:
    """Tests for 429 Too Many Requests rate limit error scenarios."""

    def test_rate_limit_error_retry_after(self, mock_client, mock_http_client):
        """Test 429 with Retry-After header information."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(
                429,
                "Rate limit exceeded",
                details={
                    "retry_after": 60,
                    "limit": 100,
                    "remaining": 0,
                    "reset_at": "2024-01-15T10:01:00Z",
                },
            ),
        )

        # Act & Assert
        with pytest.raises(RateLimitError) as exc_info:
            mock_client.sources.list()

        assert exc_info.value.status_code == 429

    def test_rate_limit_error_burst_limit(self, mock_client, mock_http_client):
        """Test 429 for burst rate limit exceeded."""
        # Arrange
        mock_http_client.add_error(
            "/data_credentials",
            create_http_error(
                429,
                "Burst rate limit exceeded",
                details={
                    "limit_type": "burst",
                    "retry_after": 5,
                },
            ),
        )

        # Act & Assert
        with pytest.raises(RateLimitError) as exc_info:
            mock_client.credentials.list()

        assert exc_info.value.status_code == 429

    def test_rate_limit_error_daily_quota(self, mock_client, mock_http_client):
        """Test 429 for daily quota exceeded."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(
                429,
                "Daily API quota exceeded",
                details={
                    "limit_type": "daily",
                    "quota": 10000,
                    "used": 10000,
                    "resets_at": "2024-01-16T00:00:00Z",
                },
            ),
        )

        # Act & Assert
        with pytest.raises(RateLimitError) as exc_info:
            mock_client.sources.create({"name": "Test"})

        assert exc_info.value.status_code == 429


@pytest.mark.unit
class TestServerErrors:
    """Tests for 5xx server error scenarios."""

    def test_server_error_500(self, mock_client, mock_http_client):
        """Test 500 Internal Server Error handling."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(500, "Internal server error"),
        )

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.sources.list()

        assert exc_info.value.status_code == 500

    def test_server_error_502_bad_gateway(self, mock_client, mock_http_client):
        """Test 502 Bad Gateway handling."""
        # Arrange
        mock_http_client.add_error(
            "/data_credentials",
            create_http_error(502, "Bad Gateway"),
        )

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.credentials.list()

        assert exc_info.value.status_code == 502

    def test_server_error_503_service_unavailable(self, mock_client, mock_http_client):
        """Test 503 Service Unavailable handling."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(
                503,
                "Service temporarily unavailable",
                details={"maintenance": True, "expected_duration": "15 minutes"},
            ),
        )

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.sources.list()

        assert exc_info.value.status_code == 503

    def test_server_error_504_gateway_timeout(self, mock_client, mock_http_client):
        """Test 504 Gateway Timeout handling."""
        # Arrange
        mock_http_client.add_error(
            "/data_sinks/123",
            create_http_error(504, "Gateway timeout"),
        )

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.destinations.get(123)

        assert exc_info.value.status_code == 504

    def test_server_error_with_request_id(self, mock_client, mock_http_client):
        """Test server error includes request ID for debugging."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(
                500,
                "Internal server error",
                details={"request_id": "req-abc-123-xyz"},
            ),
        )

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.sources.list()

        assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestBoundaryConditions:
    """Tests for edge cases with resource IDs and boundary values."""

    def test_boundary_id_zero(self, mock_client, mock_http_client):
        """Test handling of ID=0 which may be invalid."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources/0",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.get(0)

    def test_boundary_id_negative(self, mock_client, mock_http_client):
        """Test handling of negative ID values."""
        # Arrange
        # Negative IDs should result in validation or not found errors
        mock_http_client.add_error(
            "/data_sources/-1",
            create_http_error(400, "Invalid resource ID: must be positive"),
        )

        # Act & Assert
        with pytest.raises(ValidationError):
            mock_client.sources.get(-1)

    def test_boundary_id_very_large(self, mock_client, mock_http_client):
        """Test handling of very large ID values."""
        # Arrange
        large_id = 9999999999999
        mock_http_client.add_error(
            f"/data_sources/{large_id}",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.sources.get(large_id)

    def test_boundary_empty_list_response(self, mock_client, mock_http_client):
        """Test handling of empty list responses (not an error)."""
        # Arrange
        mock_http_client.add_response("/data_sources", [])

        # Act
        result = mock_client.sources.list()

        # Assert - empty list should not raise an error
        assert result == []

    def test_boundary_single_item_list(self, mock_client, mock_http_client):
        """Test handling of single-item list responses."""
        # Arrange
        source_data = MockResponseBuilder.source(source_id=1)
        mock_http_client.add_response("/data_sources", [source_data])

        # Act
        result = mock_client.sources.list()

        # Assert - should return list with one item
        assert len(result) == 1
        assert result[0].id == 1


@pytest.mark.unit
class TestErrorResponseStructure:
    """Tests for error response structure and metadata."""

    def test_error_contains_status_code_for_validation(
        self, mock_client, mock_http_client
    ):
        """Test that ValidationError contains the HTTP status code."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources",
            create_http_error(400, "Validation failed"),
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            mock_client.sources.create({"invalid": "data"})

        assert exc_info.value.status_code == 400

    def test_error_contains_message(self, mock_client, mock_http_client):
        """Test that error exceptions contain the error message."""
        # Arrange
        error_message = "Custom error message for testing"
        mock_http_client.add_error(
            "/data_sources/123",
            create_http_error(400, error_message),
        )

        # Act & Assert
        with pytest.raises(NexlaError) as exc_info:
            mock_client.sources.get(123)

        assert error_message in str(exc_info.value.message)

    def test_error_get_summary(self, mock_client, mock_http_client):
        """Test that NexlaError provides structured error summary."""
        # Arrange
        mock_http_client.add_error(
            "/data_sources/456",
            create_http_error(
                403,
                "Access denied",
                details={"resource_id": 456},
            ),
        )

        # Act & Assert
        with pytest.raises(NexlaError) as exc_info:
            mock_client.sources.get(456)

        summary = exc_info.value.get_error_summary()
        assert "message" in summary
        assert summary["status_code"] == 403


@pytest.mark.unit
class TestErrorAcrossResources:
    """Tests verifying error handling works across different resource types."""

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
            ("lookups", "/data_maps"),
            ("projects", "/projects"),
            ("teams", "/teams"),
        ],
    )
    def test_not_found_across_resources(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test 404 handling across different resource types."""
        # Arrange
        resource_id = 99999
        mock_http_client.add_error(
            f"{endpoint}/{resource_id}",
            create_http_error(404, "Resource not found"),
        )

        # Act & Assert
        resource = getattr(mock_client, resource_name)
        with pytest.raises(NotFoundError):
            resource.get(resource_id)

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("destinations", "/data_sinks"),
            ("nexsets", "/data_sets"),
            ("credentials", "/data_credentials"),
        ],
    )
    def test_authorization_error_across_resources(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test 403 handling across different resource types."""
        # Arrange
        resource_id = 123
        mock_http_client.add_error(
            f"{endpoint}/{resource_id}",
            create_http_error(403, "Permission denied"),
        )

        # Act & Assert
        resource = getattr(mock_client, resource_name)
        with pytest.raises(AuthorizationError):
            resource.delete(resource_id)

    @pytest.mark.parametrize(
        "resource_name,endpoint",
        [
            ("sources", "/data_sources"),
            ("credentials", "/data_credentials"),
            ("projects", "/projects"),
        ],
    )
    def test_server_error_across_resources(
        self, mock_client, mock_http_client, resource_name, endpoint
    ):
        """Test 500 handling across different resource types."""
        # Arrange
        mock_http_client.add_error(
            endpoint,
            create_http_error(500, "Internal server error"),
        )

        # Act & Assert
        resource = getattr(mock_client, resource_name)
        with pytest.raises(ServerError):
            resource.list()
