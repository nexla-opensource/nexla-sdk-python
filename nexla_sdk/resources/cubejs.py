from typing import TYPE_CHECKING, Any, Dict

from nexla_sdk.resources.base_resource import BaseResource
from nexla_sdk.utils.deprecation import missing_route

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class CubeJsResource(BaseResource):
    """Resource for Cube.js query endpoint."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/cubejs"
        self._model_class = None

    @missing_route("POST", "/cubejs/query")
    def query(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"{self._path}/query", json=payload)
