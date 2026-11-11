from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.vendor_endpoints.requests import (
    VendorEndpointCreate,
    VendorEndpointUpdate,
)
from nexla_sdk.models.vendor_endpoints.responses import VendorEndpoint
from nexla_sdk.resources.base_resource import BaseResource


class VendorEndpointsResource(BaseResource):
    """Resource for managing vendor endpoints."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/vendor_endpoints"
        self._model_class = VendorEndpoint

    def list(self, **kwargs) -> List[VendorEndpoint]:
        return super().list(**kwargs)

    def get(self, vendor_endpoint_id: int) -> VendorEndpoint:
        return super().get(vendor_endpoint_id)

    def create(
        self, data: Union[VendorEndpointCreate, Dict[str, Any]]
    ) -> VendorEndpoint:
        return super().create(data)

    def update(
        self,
        vendor_endpoint_id: int,
        data: Union[VendorEndpointUpdate, Dict[str, Any]],
    ) -> VendorEndpoint:
        return super().update(vendor_endpoint_id, data)

    def delete(self, vendor_endpoint_id: int) -> Dict[str, Any]:
        return super().delete(vendor_endpoint_id)

    def update_all(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", self._path, json=payload)

    def delete_all(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._make_request("DELETE", self._path, json=payload)
