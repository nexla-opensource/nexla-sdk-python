from typing import TYPE_CHECKING, Any, Dict, cast

from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class SearchHealthResource(BaseResource[Any]):
    """Resource for search health endpoints."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/search_health"
        self._model_class = None

    def get(self) -> Dict[str, Any]:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
        return cast(Dict[str, Any], self._make_request("GET", self._path))

    def test(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], self._make_request("GET", f"{self._path}/test"))
