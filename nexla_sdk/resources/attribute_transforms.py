from typing import Any, Dict, List

from nexla_sdk.models.attribute_transforms.requests import (
    AttributeTransformCreate,
    AttributeTransformUpdate,
)
from nexla_sdk.models.attribute_transforms.responses import AttributeTransform
from nexla_sdk.resources.base_resource import BaseResource


class AttributeTransformsResource(BaseResource):
    """Resource for reusable attribute transforms (aliased to code containers)."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/attribute_transforms"
        self._model_class = AttributeTransform

    def list(self, **kwargs) -> List[AttributeTransform]:
        """
        List attribute transforms with optional filters.

        Args:
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of attribute transforms

        Examples:
            client.attribute_transforms.list(page=1, per_page=25)
        """
        return super().list(**kwargs)

    def get(
        self, attribute_transform_id: int, expand: bool = False
    ) -> AttributeTransform:
        """Get an attribute transform by ID."""
        return super().get(attribute_transform_id, expand)

    def create(self, data: AttributeTransformCreate) -> AttributeTransform:
        """Create a new attribute transform."""
        return super().create(data)

    def update(
        self, attribute_transform_id: int, data: AttributeTransformUpdate
    ) -> AttributeTransform:
        """Update an attribute transform by ID."""
        return super().update(attribute_transform_id, data)

    def delete(self, attribute_transform_id: int) -> Dict[str, Any]:
        """Delete an attribute transform by ID."""
        return super().delete(attribute_transform_id)

    def list_public(self) -> List[AttributeTransform]:
        """List publicly shared attribute transforms."""
        path = f"{self._path}/public"
        response = self._make_request("GET", path)
        return self._parse_response(response)

    def copy(self, attribute_transform_id: int) -> AttributeTransform:
        """Copy an attribute transform."""
        return super().copy(attribute_transform_id)

    def search(self, filters: Dict[str, Any], **params) -> List[AttributeTransform]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[AttributeTransform]:
        return super().search_tags(tags, **params)
