from typing import TYPE_CHECKING, Any, Dict, List, Union, cast

from nexla_sdk.models.transforms.requests import TransformCreate, TransformUpdate
from nexla_sdk.models.transforms.responses import Transform
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class TransformsResource(BaseResource[Transform]):
    """Resource for reusable record transforms (aliased to code containers)."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/transforms"
        self._model_class = Transform

    def list(self, **kwargs: Any) -> List[Transform]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        """
        List transforms with optional filters.

        Args:
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of transforms

        Examples:
            client.transforms.list(page=1, per_page=25)
        """
        return super().list(**kwargs)

    def get(self, transform_id: int, expand: bool = False) -> Transform:
        """Get a transform by ID."""
        return super().get(transform_id, expand)

    def create(self, data: Union[TransformCreate, Dict[str, Any]]) -> Transform:
        """Create a new transform."""
        return super().create(data)

    def update(
        self, transform_id: int, data: Union[TransformUpdate, Dict[str, Any]]
    ) -> Transform:
        """Update an existing transform."""
        return super().update(transform_id, data)

    def delete(self, transform_id: int) -> Dict[str, Any]:
        """Delete a transform by ID."""
        return super().delete(transform_id)

    def copy(self, transform_id: int) -> Transform:  # type: ignore[override]  # keeps public copy() signature; base copy() also takes options
        """Copy a transform by ID."""
        return super().copy(transform_id)

    def list_public(self) -> List[Transform]:  # type: ignore[override]  # keeps public list_public() signature; base also takes positional page
        """List publicly shared transforms."""
        path = f"{self._path}/public"
        response = self._make_request("GET", path)
        return cast(List[Transform], self._parse_response(response))

    def search(self, filters: Dict[str, Any], **params: Any) -> List[Transform]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params: Any) -> List[Transform]:
        return super().search_tags(tags, **params)

    def transform(self, transform_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{transform_id}/transform"
        return cast(Dict[str, Any], self._make_request("POST", path, json=payload))

    def transform_features(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], self._make_request("GET", "/transform/features"))

    def transform_accessible_resources(self) -> List[Dict[str, Any]]:
        """
        List transforms accessible to the current user with their role.

        Returns:
            Accessible transform entries
        """
        return cast(
            List[Dict[str, Any]], self._make_request("GET", "/transform/accessible")
        )

    def transform_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return cast(
            Dict[str, Any], self._make_request("POST", "/transform", json=payload)
        )
