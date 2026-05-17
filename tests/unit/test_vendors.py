"""Unit tests for vendors resource."""

import pytest

from nexla_sdk.models.vendors.requests import VendorCreate, VendorUpdate
from nexla_sdk.models.vendors.responses import Vendor
from tests.utils import assert_model_list_valid, assert_model_valid

# Sample response data
SAMPLE_VENDOR = {
    "id": 123,
    "name": "salesforce",
    "display_name": "Salesforce",
    "description": "Salesforce CRM connector",
    "config": {},
    "small_logo": "https://example.com/sf-small.png",
    "logo": "https://example.com/sf.png",
    "connection_type": "api",
    "auth_templates": [1, 2],
    "vendor_endpoints": [],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

SAMPLE_VENDORS_LIST = [
    SAMPLE_VENDOR,
    {**SAMPLE_VENDOR, "id": 124, "name": "hubspot", "display_name": "HubSpot"},
    {**SAMPLE_VENDOR, "id": 125, "name": "zendesk", "display_name": "Zendesk"},
]


@pytest.fixture
def sample_vendor_response():
    """Sample vendor response."""
    return SAMPLE_VENDOR.copy()


@pytest.fixture
def sample_vendors_list():
    """Sample vendors list response."""
    return [v.copy() for v in SAMPLE_VENDORS_LIST]


@pytest.mark.unit
class TestVendorsResource:
    """Unit tests for VendorsResource using mocks."""

    def test_list_vendors_success(
        self, mock_client, mock_http_client, sample_vendors_list
    ):
        """Test listing vendors with successful response."""
        mock_http_client.add_response("/vendors", sample_vendors_list)

        vendors = mock_client.vendors.list()

        assert len(vendors) == 3
        assert_model_list_valid(vendors, Vendor)
        mock_http_client.assert_request_made("GET", "/vendors")

    def test_get_vendor_by_id(
        self, mock_client, mock_http_client, sample_vendor_response
    ):
        """Test getting a vendor by ID."""
        vendor_id = 123
        mock_http_client.add_response(f"/vendors/{vendor_id}", sample_vendor_response)

        vendor = mock_client.vendors.get(vendor_id)

        assert_model_valid(vendor, {"id": vendor_id})
        mock_http_client.assert_request_made("GET", f"/vendors/{vendor_id}")

    def test_get_vendor_by_name(
        self, mock_client, mock_http_client, sample_vendor_response
    ):
        """Test getting a vendor by name."""
        mock_http_client.add_response("/vendors", sample_vendor_response)

        vendor = mock_client.vendors.get_by_name("salesforce")

        assert vendor.name == "salesforce"
        mock_http_client.assert_request_made("GET", "/vendors")

    def test_create_vendor_success(
        self, mock_client, mock_http_client, sample_vendor_response
    ):
        """Test creating a vendor."""
        mock_http_client.add_response("/vendors", sample_vendor_response)

        create_data = VendorCreate(
            name="new_vendor",
            display_name="New Vendor",
        )
        vendor = mock_client.vendors.create(create_data)

        assert_model_valid(vendor, {"name": "salesforce"})
        mock_http_client.assert_request_made("POST", "/vendors")

    def test_update_vendor_success(
        self, mock_client, mock_http_client, sample_vendor_response
    ):
        """Test updating a vendor."""
        vendor_id = 123
        updated_response = {**sample_vendor_response, "description": "Updated desc"}
        mock_http_client.add_response(f"/vendors/{vendor_id}", updated_response)

        update_data = VendorUpdate(description="Updated desc")
        vendor = mock_client.vendors.update(vendor_id, update_data)

        assert vendor.description == "Updated desc"
        mock_http_client.assert_request_made("PUT", f"/vendors/{vendor_id}")

    def test_delete_vendor_success(self, mock_client, mock_http_client):
        """Test deleting a vendor."""
        vendor_id = 123
        mock_http_client.add_response(f"/vendors/{vendor_id}", {"success": True})

        result = mock_client.vendors.delete(vendor_id)

        assert result["success"] is True
        mock_http_client.assert_request_made("DELETE", f"/vendors/{vendor_id}")

    def test_delete_auth_template_from_vendor(self, mock_client, mock_http_client):
        """Test deleting an auth template from a vendor."""
        vendor_id = 123
        template_id = 456
        mock_http_client.add_response(
            f"/vendors/{vendor_id}/auth_templates/{template_id}", {"success": True}
        )

        result = mock_client.vendors.delete_auth_template(vendor_id, template_id)

        assert result["success"] is True
        mock_http_client.assert_request_made(
            "DELETE", f"/vendors/{vendor_id}/auth_templates/{template_id}"
        )


@pytest.mark.unit
class TestVendorModels:
    """Unit tests for vendor models."""

    def test_vendor_model_validation(self, sample_vendor_response):
        """Test Vendor model parses valid data correctly."""
        vendor = Vendor.model_validate(sample_vendor_response)

        assert vendor.id == 123
        assert vendor.name == "salesforce"
        assert vendor.display_name == "Salesforce"
        assert len(vendor.auth_templates) == 2

    def test_vendor_model_with_minimal_data(self):
        """Test Vendor model with minimal required fields."""
        minimal_data = {
            "id": 1,
        }
        vendor = Vendor.model_validate(minimal_data)

        assert vendor.id == 1
        assert vendor.name is None
        assert vendor.auth_templates == []

    def test_vendor_create_model_serialization(self):
        """Test VendorCreate model serialization."""
        create_data = VendorCreate(
            name="new_vendor",
            display_name="New Vendor",
            description="A new vendor",
        )

        data = create_data.model_dump(exclude_none=True)

        assert data["name"] == "new_vendor"
        assert data["display_name"] == "New Vendor"
        assert data["description"] == "A new vendor"

    def test_vendor_update_model_serialization(self):
        """Test VendorUpdate model serialization."""
        update_data = VendorUpdate(
            display_name="Updated Name",
            description="Updated description",
        )

        data = update_data.model_dump(exclude_none=True)

        assert data["display_name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert "name" not in data
