from typing import Any, Dict

from nexla_sdk.resources.base_resource import BaseResource


class CubeJsResource(BaseResource):
    """Resource for Cube.js query endpoint."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/cubejs"
        self._model_class = None

    def query(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"{self._path}/query", json=payload)
