from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from nexla_sdk.models.code_containers.requests import (
    CodeContainerCreate,
    CodeContainerUpdate,
)
from nexla_sdk.models.code_containers.responses import CodeContainer
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class CodeContainersResource(BaseResource[CodeContainer]):
    """Resource for managing code containers."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/code_containers"
        self._model_class = CodeContainer

    def list(self, **kwargs: Any) -> List[CodeContainer]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        """
        List code containers with optional filters.

        Args:
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of code containers

        Examples:
            client.code_containers.list(page=1, per_page=20)
        """
        return super().list(**kwargs)

    def get(self, code_container_id: int, expand: bool = False) -> CodeContainer:
        """Get a code container by ID.

        Examples:
            client.code_containers.get(1001)
        """
        return super().get(code_container_id, expand)

    def create(self, data: Union[CodeContainerCreate, Dict[str, Any]]) -> CodeContainer:
        """Create a new code container.

        Examples:
            client.code_containers.create(CodeContainerCreate(name="my-container", ...))
        """
        return super().create(data)

    def update(
        self, code_container_id: int, data: Union[CodeContainerUpdate, Dict[str, Any]]
    ) -> CodeContainer:
        """Update an existing code container.

        Examples:
            client.code_containers.update(1001, CodeContainerUpdate(name="renamed"))
        """
        return super().update(code_container_id, data)

    def delete(self, code_container_id: int) -> Dict[str, Any]:
        """Delete a code container by ID."""
        return super().delete(code_container_id)

    def copy(self, code_container_id: int) -> CodeContainer:  # type: ignore[override]  # keeps public copy() signature; base copy() also takes options
        """Copy a code container by ID."""
        return super().copy(code_container_id)

    def list_public(self) -> List[CodeContainer]:  # type: ignore[override]  # keeps public list_public() signature; base also takes positional page
        """List publicly shared code containers."""
        path = f"{self._path}/public"
        response = self._make_request("GET", path)
        return cast(List[CodeContainer], self._parse_response(response))

    def list_accessible(self, **params: Any) -> List[CodeContainer]:
        return super().list_accessible(**params)

    def repo(self, code_container_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{code_container_id}/repo"
        return cast(Dict[str, Any], self._make_request("GET", path))

    def error_functions(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], self._make_request("GET", "/error_functions"))

    def search(self, filters: Dict[str, Any], **params: Any) -> List[CodeContainer]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params: Any) -> List[CodeContainer]:
        return super().search_tags(tags, **params)

    def get_schema(self, method: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the JSON schema for code containers.

        Args:
            method: HTTP method the schema describes: get, post, or put.
                Omit it to get the schema for all three methods.

        Returns:
            JSON schema
        """
        params = {"method": method} if method is not None else {}
        return cast(
            Dict[str, Any],
            self._make_request("GET", f"{self._path}/schema", params=params),
        )
