"""Resource for managing vendors."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.vendors.requests import VendorCreate, VendorUpdate
from nexla_sdk.models.vendors.responses import Vendor
from nexla_sdk.resources.base_resource import BaseResource


class VendorsResource(BaseResource):
    """Resource for managing vendors.

    Vendors represent third-party service providers that can be
    connected via auth templates and endpoints.

    Write operations (create, update, delete) require super user access.

    Examples:
        # List all vendors
        vendors = client.vendors.list()

        # Get a vendor by ID
        vendor = client.vendors.get(123)

        # Get a vendor by name
        vendor = client.vendors.get_by_name("salesforce")

        # Create a vendor (super user only)
        vendor = client.vendors.create(VendorCreate(
            name="new_vendor",
            display_name="New Vendor"
        ))

        # Update a vendor (super user only)
        vendor = client.vendors.update(123, VendorUpdate(
            description="Updated description"
        ))

        # Delete a vendor (super user only)
        client.vendors.delete(123)
    """

    def __init__(self, client):
        """Initialize the vendors resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/vendors"
        self._model_class = Vendor

    def list(
        self,
        expand: bool = False,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ) -> List[Vendor]:
        """List vendors.

        Args:
            expand: Include nested auth_templates and vendor_endpoints
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            List of vendors
        """
        params = kwargs.copy()
        if expand:
            params["expand"] = "true"
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", self._path, params=params)
        return self._parse_response(response)

    def get(self, vendor_id: int, expand: bool = False) -> Vendor:
        """Get vendor by ID.

        Args:
            vendor_id: Vendor ID
            expand: Include nested auth_templates and vendor_endpoints

        Returns:
            Vendor instance
        """
        path = f"{self._path}/{vendor_id}"
        params = {"expand": "true"} if expand else {}
        response = self._make_request("GET", path, params=params)
        return self._parse_response(response)

    def get_by_name(self, vendor_name: str, expand: bool = False) -> Vendor:
        """Get vendor by name.

        Args:
            vendor_name: Vendor name
            expand: Include nested auth_templates and vendor_endpoints

        Returns:
            Vendor instance
        """
        params = {"vendor_name": vendor_name}
        if expand:
            params["expand"] = "true"
        response = self._make_request("GET", self._path, params=params)
        return self._parse_response(response)

    def create(self, data: Union[VendorCreate, Dict[str, Any]]) -> Vendor:
        """Create a new vendor (super user only).

        Args:
            data: Vendor creation data

        Returns:
            Created vendor
        """
        return super().create(data)

    def update(
        self, vendor_id: int, data: Union[VendorUpdate, Dict[str, Any]]
    ) -> Vendor:
        """Update a vendor (super user only).

        Args:
            vendor_id: Vendor ID
            data: Updated vendor data

        Returns:
            Updated vendor
        """
        return super().update(vendor_id, data)

    def update_by_name(
        self, vendor_name: str, data: Union[VendorUpdate, Dict[str, Any]]
    ) -> Vendor:
        """Update a vendor by name (super user only).

        Args:
            vendor_name: Vendor name
            data: Updated vendor data

        Returns:
            Updated vendor
        """
        params = {"vendor_name": vendor_name}
        serialized_data = self._serialize_data(data)
        response = self._make_request(
            "PUT", self._path, json=serialized_data, params=params
        )
        return self._parse_response(response)

    def delete(self, vendor_id: int) -> Dict[str, Any]:
        """Delete a vendor (super user only).

        Args:
            vendor_id: Vendor ID

        Returns:
            Response with status
        """
        return super().delete(vendor_id)

    def delete_by_name(self, vendor_name: str) -> Dict[str, Any]:
        """Delete a vendor by name (super user only).

        Args:
            vendor_name: Vendor name

        Returns:
            Response with status
        """
        params = {"vendor_name": vendor_name}
        return self._make_request("DELETE", self._path, params=params)

    def update_all(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update vendors via collection endpoint."""
        return self._make_request("PUT", self._path, json=payload)

    def delete_all(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete vendors via collection endpoint."""
        return self._make_request("DELETE", self._path, json=payload or {})

    def delete_auth_template(
        self, vendor_id: int, auth_template_id: int
    ) -> Dict[str, Any]:
        """Delete an auth template from a vendor (super user only).

        Args:
            vendor_id: Vendor ID
            auth_template_id: Auth template ID

        Returns:
            Response with status
        """
        path = f"{self._path}/{vendor_id}/auth_templates/{auth_template_id}"
        return self._make_request("DELETE", path)
