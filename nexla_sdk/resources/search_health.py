from typing import Any, Dict

from nexla_sdk.resources.base_resource import BaseResource


class SearchHealthResource(BaseResource):
    """Resource for search health endpoints."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/search_health"
        self._model_class = None

    def get(self) -> Dict[str, Any]:
        return self._make_request("GET", self._path)

    def test(self) -> Dict[str, Any]:
        return self._make_request("GET", f"{self._path}/test")
