from typing import Any, Dict, List

from nexla_sdk.models.code_containers.requests import (
    CodeContainerCreate,
    CodeContainerUpdate,
)
from nexla_sdk.models.code_containers.responses import CodeContainer
from nexla_sdk.resources.base_resource import BaseResource


class CodeContainersResource(BaseResource):
    """Resource for managing code containers."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/code_containers"
        self._model_class = CodeContainer

    def list(self, **kwargs) -> List[CodeContainer]:
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

    def create(self, data: CodeContainerCreate) -> CodeContainer:
        """Create a new code container.

        Examples:
            client.code_containers.create(CodeContainerCreate(name="my-container", ...))
        """
        return super().create(data)

    def update(
        self, code_container_id: int, data: CodeContainerUpdate
    ) -> CodeContainer:
        """Update an existing code container.

        Examples:
            client.code_containers.update(1001, CodeContainerUpdate(name="renamed"))
        """
        return super().update(code_container_id, data)

    def delete(self, code_container_id: int) -> Dict[str, Any]:
        """Delete a code container by ID."""
        return super().delete(code_container_id)

    def copy(self, code_container_id: int) -> CodeContainer:
        """Copy a code container by ID."""
        return super().copy(code_container_id)

    def list_public(self) -> List[CodeContainer]:
        """List publicly shared code containers."""
        path = f"{self._path}/public"
        response = self._make_request("GET", path)
        return self._parse_response(response)

    def list_accessible(self, **params) -> List[CodeContainer]:
        return super().list_accessible(**params)

    def repo(self, code_container_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{code_container_id}/repo"
        return self._make_request("GET", path)

    def error_functions(self) -> Dict[str, Any]:
        return self._make_request("GET", "/error_functions")

    def search(self, filters: Dict[str, Any], **params) -> List[CodeContainer]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[CodeContainer]:
        return super().search_tags(tags, **params)
