from typing import Any, Dict, List

from nexla_sdk.models.org_auth_configs.requests import AuthConfigPayload
from nexla_sdk.models.org_auth_configs.responses import AuthConfig
from nexla_sdk.resources.base_resource import BaseResource


class OrgAuthConfigsResource(BaseResource):
    """Resource for organization authentication configurations (/api_auth_configs)."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/api_auth_configs"
        self._model_class = AuthConfig

    def list(self) -> List[AuthConfig]:
        """List authentication configurations for the current organization."""
        response = self._make_request("GET", self._path)
        return self._parse_response(response)

    def list_all(self) -> List[AuthConfig]:
        """List all authentication configurations (admin only)."""
        response = self._make_request("GET", f"{self._path}/all")
        return self._parse_response(response)

    def list_sign_on_options(self) -> Dict[str, Any]:
        """List sign-on options (public)."""
        return self._make_request("GET", "/sign_on_options")

    def client_config(self) -> Dict[str, Any]:
        """Get client config for API auth."""
        return self._make_request("GET", f"{self._path}/client_config")

    def info(self) -> Dict[str, Any]:
        """Get API auth info."""
        return self._make_request("GET", f"{self._path}/info")

    def get(self, auth_config_id: int) -> AuthConfig:
        """Get a specific authentication configuration by ID."""
        response = self._make_request("GET", f"{self._path}/{auth_config_id}")
        return self._parse_response(response)

    def create(self, payload: AuthConfigPayload) -> AuthConfig:
        """Create a new authentication configuration."""
        data = self._serialize_data(payload)
        response = self._make_request("POST", self._path, json=data)
        return self._parse_response(response)

    def update(self, auth_config_id: int, payload: AuthConfigPayload) -> AuthConfig:
        """Update an existing authentication configuration."""
        data = self._serialize_data(payload)
        response = self._make_request(
            "PUT", f"{self._path}/{auth_config_id}", json=data
        )
        return self._parse_response(response)

    def delete(self, auth_config_id: int) -> Dict[str, Any]:
        """Delete an authentication configuration by ID."""
        return self._make_request("DELETE", f"{self._path}/{auth_config_id}")
