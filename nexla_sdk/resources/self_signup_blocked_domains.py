from typing import Any, Dict, List

from nexla_sdk.resources.base_resource import BaseResource


class SelfSignupBlockedDomainsResource(BaseResource):
    """Resource for self-signup blocked domains."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/self_signup_blocked_domains"
        self._model_class = None

    def list(self, **kwargs) -> List[Dict[str, Any]]:
        return self._make_request("GET", self._path, params=kwargs) or []

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", self._path, json=payload)

    def update(self, domain_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", f"{self._path}/{domain_id}", json=payload)

    def delete(self, domain_id: int) -> Dict[str, Any]:
        return self._make_request("DELETE", f"{self._path}/{domain_id}")
