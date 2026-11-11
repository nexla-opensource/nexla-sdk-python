from typing import Any, Dict, List

from nexla_sdk.models.self_signup.responses import BlockedDomain, SelfSignupRequest
from nexla_sdk.resources.base_resource import BaseResource


class SelfSignupResource(BaseResource):
    """Resource for self sign-up and admin endpoints."""

    def __init__(self, client):
        super().__init__(client)
        self._path = ""
        self._model_class = None

    # Public signup
    def signup(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/signup", json=payload)

    def verify_email(self, token: str) -> Dict[str, Any]:
        return self._make_request(
            "GET", "/signup/verify_email", params={"token": token}
        )

    # Admin APIs
    def list_requests(self) -> List[SelfSignupRequest]:
        response = self._make_request("GET", "/self_signup_requests")
        return [SelfSignupRequest.model_validate(item) for item in (response or [])]

    def approve_request(self, request_id: str) -> SelfSignupRequest:
        # Backend routes use POST; OpenAPI may advertise PUT in some versions.
        response = self._make_request(
            "POST", f"/self_signup_requests/{request_id}/approve"
        )
        return SelfSignupRequest.model_validate(response)

    def list_blocked_domains(self) -> List[BlockedDomain]:
        response = self._make_request("GET", "/self_signup_blocked_domains")
        return [BlockedDomain.model_validate(item) for item in (response or [])]

    def add_blocked_domain(self, domain: str) -> BlockedDomain:
        response = self._make_request(
            "POST", "/self_signup_blocked_domains", json={"domain": domain}
        )
        return BlockedDomain.model_validate(response)

    def update_blocked_domain(self, domain_id: str, domain: str) -> BlockedDomain:
        response = self._make_request(
            "PUT", f"/self_signup_blocked_domains/{domain_id}", json={"domain": domain}
        )
        return BlockedDomain.model_validate(response)

    def delete_blocked_domain(self, domain_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/self_signup_blocked_domains/{domain_id}")
