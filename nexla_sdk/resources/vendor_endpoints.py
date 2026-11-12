from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from nexla_sdk.models.vendor_endpoints.requests import (
    VendorEndpointCreate,
    VendorEndpointUpdate,
)
from nexla_sdk.models.vendor_endpoints.responses import VendorEndpoint
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class VendorEndpointsResource(BaseResource[VendorEndpoint]):
    """Resource for managing vendor endpoints."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/vendor_endpoints"
        self._model_class = VendorEndpoint

    def list(self, **kwargs: Any) -> List[VendorEndpoint]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        return super().list(**kwargs)

    def get(self, vendor_endpoint_id: int) -> VendorEndpoint:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
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
        return cast(Dict[str, Any], self._make_request("PUT", self._path, json=payload))

    def delete_all(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return cast(
            Dict[str, Any], self._make_request("DELETE", self._path, json=payload)
        )
