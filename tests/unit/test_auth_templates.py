"""Unit tests for auth templates resource."""

import pytest

from nexla_sdk.models.auth_templates.requests import (
    AuthTemplateCreate,
    AuthTemplateUpdate,
)
from nexla_sdk.models.auth_templates.responses import AuthTemplate
from tests.utils import assert_model_list_valid, assert_model_valid

# Sample response data
SAMPLE_AUTH_TEMPLATE = {
    "id": 123,
    "name": "oauth2_standard",
    "display_name": "OAuth 2.0 Standard",
    "description": "Standard OAuth 2.0 authentication template",
    "config": {},
    "credentials_type": "oauth2",
    "vendor_id": 456,
    "vendor": {"id": 456, "name": "salesforce", "display_name": "Salesforce"},
    "auth_parameters": [
        {
            "id": 1,
            "name": "client_id",
            "display_name": "Client ID",
            "param_type": "string",
            "required": True,
        },
        {
            "id": 2,
            "name": "client_secret",
            "display_name": "Client Secret",
            "param_type": "password",
            "required": True,
        },
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

SAMPLE_AUTH_TEMPLATES_LIST = [
    SAMPLE_AUTH_TEMPLATE,
    {**SAMPLE_AUTH_TEMPLATE, "id": 124, "name": "api_key", "display_name": "API Key"},
    {
        **SAMPLE_AUTH_TEMPLATE,
        "id": 125,
        "name": "basic_auth",
        "display_name": "Basic Auth",
    },
]


@pytest.fixture
def sample_auth_template_response():
    """Sample auth template response."""
    return SAMPLE_AUTH_TEMPLATE.copy()


@pytest.fixture
def sample_auth_templates_list():
    """Sample auth templates list response."""
    return [t.copy() for t in SAMPLE_AUTH_TEMPLATES_LIST]


@pytest.mark.unit
class TestAuthTemplatesResource:
    """Unit tests for AuthTemplatesResource using mocks."""

    def test_list_auth_templates_success(
        self, mock_client, mock_http_client, sample_auth_templates_list
    ):
        """Test listing auth templates with successful response."""
        mock_http_client.add_response("/auth_templates", sample_auth_templates_list)

        templates = mock_client.auth_templates.list()

        assert len(templates) == 3
        assert_model_list_valid(templates, AuthTemplate)
        mock_http_client.assert_request_made("GET", "/auth_templates")

    def test_get_auth_template_by_id(
        self, mock_client, mock_http_client, sample_auth_template_response
    ):
        """Test getting an auth template by ID."""
        template_id = 123
        mock_http_client.add_response(
            f"/auth_templates/{template_id}", sample_auth_template_response
        )

        template = mock_client.auth_templates.get(template_id)

        assert_model_valid(template, {"id": template_id})
        mock_http_client.assert_request_made("GET", f"/auth_templates/{template_id}")

    def test_get_auth_template_by_name(
        self, mock_client, mock_http_client, sample_auth_template_response
    ):
        """Test getting an auth template by name."""
        mock_http_client.add_response("/auth_templates", sample_auth_template_response)

        template = mock_client.auth_templates.get_by_name("oauth2_standard")

        assert template.name == "oauth2_standard"
        mock_http_client.assert_request_made("GET", "/auth_templates")

    def test_create_auth_template_success(
        self, mock_client, mock_http_client, sample_auth_template_response
    ):
        """Test creating an auth template."""
        mock_http_client.add_response("/auth_templates", sample_auth_template_response)

        create_data = AuthTemplateCreate(
            name="new_template",
            vendor_id=456,
            display_name="New Template",
        )
        template = mock_client.auth_templates.create(create_data)

        assert_model_valid(template, {"name": "oauth2_standard"})
        mock_http_client.assert_request_made("POST", "/auth_templates")

    def test_update_auth_template_success(
        self, mock_client, mock_http_client, sample_auth_template_response
    ):
        """Test updating an auth template."""
        template_id = 123
        updated_response = {**sample_auth_template_response, "description": "Updated"}
        mock_http_client.add_response(
            f"/auth_templates/{template_id}", updated_response
        )

        update_data = AuthTemplateUpdate(description="Updated")
        template = mock_client.auth_templates.update(template_id, update_data)

        assert template.description == "Updated"
        mock_http_client.assert_request_made("PUT", f"/auth_templates/{template_id}")

    def test_delete_auth_template_success(self, mock_client, mock_http_client):
        """Test deleting an auth template."""
        template_id = 123
        mock_http_client.add_response(
            f"/auth_templates/{template_id}", {"success": True}
        )

        result = mock_client.auth_templates.delete(template_id)

        assert result["success"] is True
        mock_http_client.assert_request_made("DELETE", f"/auth_templates/{template_id}")


@pytest.mark.unit
class TestAuthTemplateModels:
    """Unit tests for auth template models."""

    def test_auth_template_model_validation(self, sample_auth_template_response):
        """Test AuthTemplate model parses valid data correctly."""
        template = AuthTemplate.model_validate(sample_auth_template_response)

        assert template.id == 123
        assert template.name == "oauth2_standard"
        assert template.display_name == "OAuth 2.0 Standard"
        assert template.vendor.id == 456
        assert len(template.auth_parameters) == 2

    def test_auth_template_model_with_minimal_data(self):
        """Test AuthTemplate model with minimal required fields."""
        minimal_data = {
            "id": 1,
        }
        template = AuthTemplate.model_validate(minimal_data)

        assert template.id == 1
        assert template.name is None
        assert template.auth_parameters == []

    def test_auth_template_create_model_serialization(self):
        """Test AuthTemplateCreate model serialization."""
        create_data = AuthTemplateCreate(
            name="new_template",
            vendor_id=456,
            display_name="New Template",
            description="A new auth template",
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["name"] == "new_template"
        assert data["vendor_id"] == 456
        assert data["display_name"] == "New Template"

    def test_auth_template_update_model_serialization(self):
        """Test AuthTemplateUpdate model serialization."""
        update_data = AuthTemplateUpdate(
            display_name="Updated Name",
            description="Updated description",
        )

        data = update_data.model_dump(exclude_none=True)

        assert data["display_name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert "name" not in data
        assert "vendor_id" not in data
