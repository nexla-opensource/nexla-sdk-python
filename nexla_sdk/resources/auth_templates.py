"""Resource for managing auth templates."""

from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.auth_templates.requests import (
    AuthTemplateCreate,
    AuthTemplateUpdate,
)
from nexla_sdk.models.auth_templates.responses import AuthTemplate
from nexla_sdk.resources.base_resource import BaseResource


class AuthTemplatesResource(BaseResource):
    """Resource for managing auth templates.

    Auth templates define authentication configurations for vendors.
    Write operations (create, update, delete) require super user access.

    Examples:
        # List all auth templates
        templates = client.auth_templates.list()

        # Get an auth template by ID
        template = client.auth_templates.get(123)

        # Get an auth template by name
        template = client.auth_templates.get_by_name("oauth2_standard")

        # Create an auth template (super user only)
        template = client.auth_templates.create(AuthTemplateCreate(
            name="new_template",
            vendor_id=456,
            display_name="New Auth Template"
        ))

        # Update an auth template (super user only)
        template = client.auth_templates.update(123, AuthTemplateUpdate(
            description="Updated description"
        ))

        # Delete an auth template (super user only)
        client.auth_templates.delete(123)
    """

    def __init__(self, client):
        """Initialize the auth templates resource.

        Args:
            client: Nexla client instance
        """
        super().__init__(client)
        self._path = "/auth_templates"
        self._model_class = AuthTemplate

    def list(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        access_role: Optional[str] = None,
        **kwargs,
    ) -> List[AuthTemplate]:
        """List auth templates.

        Args:
            page: Page number (1-based)
            per_page: Items per page
            access_role: Filter by access role (owner, collaborator, operator, admin)

        Returns:
            List of auth templates
        """
        return super().list(
            page=page, per_page=per_page, access_role=access_role, **kwargs
        )

    def get(self, auth_template_id: int, expand: bool = False) -> AuthTemplate:
        """Get auth template by ID.

        Args:
            auth_template_id: Auth template ID
            expand: Include expanded references (where supported)

        Returns:
            AuthTemplate instance
        """
        return super().get(auth_template_id, expand=expand)

    def get_by_name(self, auth_template_name: str) -> AuthTemplate:
        """Get auth template by name.

        Args:
            auth_template_name: Auth template name

        Returns:
            AuthTemplate instance
        """
        params = {"auth_template_name": auth_template_name}
        response = self._make_request("GET", self._path, params=params)
        return self._parse_response(response)

    def create(self, data: Union[AuthTemplateCreate, Dict[str, Any]]) -> AuthTemplate:
        """Create a new auth template (super user only).

        Args:
            data: Auth template creation data

        Returns:
            Created auth template
        """
        return super().create(data)

    def update(
        self, auth_template_id: int, data: Union[AuthTemplateUpdate, Dict[str, Any]]
    ) -> AuthTemplate:
        """Update an auth template (super user only).

        Args:
            auth_template_id: Auth template ID
            data: Updated auth template data

        Returns:
            Updated auth template
        """
        return super().update(auth_template_id, data)

    def update_by_name(
        self, auth_template_name: str, data: Union[AuthTemplateUpdate, Dict[str, Any]]
    ) -> AuthTemplate:
        """Update an auth template by name (super user only).

        Args:
            auth_template_name: Auth template name
            data: Updated auth template data

        Returns:
            Updated auth template
        """
        params = {"auth_template_name": auth_template_name}
        serialized_data = self._serialize_data(data)
        response = self._make_request(
            "PUT", self._path, json=serialized_data, params=params
        )
        return self._parse_response(response)

    def delete(self, auth_template_id: int) -> Dict[str, Any]:
        """Delete an auth template (super user only).

        Args:
            auth_template_id: Auth template ID

        Returns:
            Response with status
        """
        return super().delete(auth_template_id)

    def delete_by_name(self, auth_template_name: str) -> Dict[str, Any]:
        """Delete an auth template by name (super user only).

        Args:
            auth_template_name: Auth template name

        Returns:
            Response with status
        """
        params = {"auth_template_name": auth_template_name}
        return self._make_request("DELETE", self._path, params=params)

    def update_all(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update auth templates via collection endpoint."""
        return self._make_request("PUT", self._path, json=payload)

    def delete_all(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delete auth templates via collection endpoint."""
        return self._make_request("DELETE", self._path, json=payload or {})
