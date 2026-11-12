from typing import TYPE_CHECKING, Any, Dict, List, Union, cast

from nexla_sdk.models.runtimes.requests import RuntimeCreate, RuntimeUpdate
from nexla_sdk.models.runtimes.responses import Runtime
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class RuntimesResource(BaseResource[Runtime]):
    """Resource for managing custom runtimes."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/runtimes"
        self._model_class = Runtime

    def list(self) -> List[Runtime]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        """List custom runtimes."""
        response = self._make_request("GET", self._path)
        return cast(List[Runtime], self._parse_response(response))

    def create(self, data: Union[RuntimeCreate, Dict[str, Any]]) -> Runtime:
        """Create a new custom runtime."""
        payload = self._serialize_data(data)
        response = self._make_request("POST", self._path, json=payload)
        return cast(Runtime, self._parse_response(response))

    def get(self, runtime_id: int) -> Runtime:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
        """Get a custom runtime by ID."""
        path = f"{self._path}/{runtime_id}"
        response = self._make_request("GET", path)
        return cast(Runtime, self._parse_response(response))

    def update(
        self, runtime_id: int, data: Union[RuntimeUpdate, Dict[str, Any]]
    ) -> Runtime:
        """Update a custom runtime by ID."""
        path = f"{self._path}/{runtime_id}"
        payload = self._serialize_data(data)
        response = self._make_request("PUT", path, json=payload)
        return cast(Runtime, self._parse_response(response))

    def delete(self, runtime_id: int) -> Dict[str, Any]:
        """Delete a custom runtime by ID."""
        path = f"{self._path}/{runtime_id}"
        return cast(Dict[str, Any], self._make_request("DELETE", path))

    def activate(self, runtime_id: int) -> Runtime:
        """Activate a custom runtime."""
        path = f"{self._path}/{runtime_id}/activate"
        response = self._make_request("PUT", path)
        return cast(Runtime, self._parse_response(response))

    def pause(self, runtime_id: int) -> Runtime:
        """Pause a custom runtime."""
        path = f"{self._path}/{runtime_id}/pause"
        response = self._make_request("PUT", path)
        return cast(Runtime, self._parse_response(response))
