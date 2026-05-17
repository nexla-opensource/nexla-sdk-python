from typing import Any, Dict, Optional

from nexla_sdk.resources.base_resource import BaseResource


class TokensResource(BaseResource):
    """Resource for auth/token endpoints."""

    def __init__(self, client):
        super().__init__(client)
        self._path = ""
        self._model_class = None

    def create_token(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/token", json=payload)

    def update_token(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", "/token", json=payload)

    def create_google_token(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/gtoken", json=payload)

    def refresh_token(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/token/refresh", json=payload)

    def logout(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._make_request("POST", "/token/logout", json=payload or {})

    def create_idp_token(
        self, uid: Optional[str], payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = "/token" if uid is None else f"/token/{uid}"
        return self._make_request("POST", path, json=payload)

    def metadata(self, uid: Optional[str] = None) -> Dict[str, Any]:
        path = "/metadata" if uid is None else f"/metadata/{uid}"
        return self._make_request("GET", path)

    def aws_marketplace_token(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/aws_marketplace_token", json=payload)

    def resource_authorize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/resource_authorize", json=payload)
