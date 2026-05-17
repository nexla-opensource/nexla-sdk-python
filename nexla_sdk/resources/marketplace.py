from typing import Any, Dict, List

from nexla_sdk.models.marketplace.requests import (
    CustodiansPayload,
    MarketplaceDomainCreate,
    MarketplaceDomainsItemCreate,
)
from nexla_sdk.models.marketplace.responses import (
    MarketplaceDomain,
    MarketplaceDomainsItem,
)
from nexla_sdk.models.organizations.responses import CustodianUser
from nexla_sdk.resources.base_resource import BaseResource


class MarketplaceResource(BaseResource):
    """Resource for marketplace domains and items."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/marketplace"
        self._model_class = MarketplaceDomain

    # Domains
    def list_domains(self) -> List[MarketplaceDomain]:
        response = self._make_request("GET", f"{self._path}/domains")
        return self._parse_response(response, MarketplaceDomain)  # type: ignore[arg-type]

    def create_domains(self, data: MarketplaceDomainCreate) -> List[MarketplaceDomain]:
        payload = self._serialize_data(data)
        response = self._make_request("POST", f"{self._path}/domains", json=payload)
        return self._parse_response(response, MarketplaceDomain)  # type: ignore[arg-type]

    def get_domains_for_org(self, org_id: int) -> List[MarketplaceDomain]:
        response = self._make_request(
            "GET", f"{self._path}/domains/for_org", params={"org_id": org_id}
        )
        return self._parse_response(response, MarketplaceDomain)  # type: ignore[arg-type]

    def get_domain(self, domain_id: int) -> MarketplaceDomain:
        response = self._make_request("GET", f"{self._path}/domains/{domain_id}")
        return self._parse_response(response, MarketplaceDomain)  # type: ignore[arg-type]

    def update_domain(
        self, domain_id: int, data: MarketplaceDomainCreate
    ) -> MarketplaceDomain:
        payload = self._serialize_data(data)
        response = self._make_request(
            "PUT", f"{self._path}/domains/{domain_id}", json=payload
        )
        return self._parse_response(response, MarketplaceDomain)  # type: ignore[arg-type]

    def create_domain(self, data: MarketplaceDomainCreate) -> MarketplaceDomain:
        payload = self._serialize_data(data)
        response = self._make_request("POST", f"{self._path}/domains", json=payload)
        return self._parse_response(response, MarketplaceDomain)  # type: ignore[arg-type]

    def delete_domain(self, domain_id: int) -> Dict[str, Any]:
        return self._make_request("DELETE", f"{self._path}/domains/{domain_id}")

    def get_domain_audit_log(self, domain_id: int, **params) -> Dict[str, Any]:
        return self._make_request(
            "GET", f"{self._path}/domains/{domain_id}/audit_log", params=params
        )

    # Items
    def list_domain_items(self, domain_id: int) -> List[MarketplaceDomainsItem]:
        response = self._make_request("GET", f"{self._path}/domains/{domain_id}/items")
        return self._parse_response(response, MarketplaceDomainsItem)  # type: ignore[arg-type]

    def create_domain_item(
        self, domain_id: int, data: MarketplaceDomainsItemCreate
    ) -> List[MarketplaceDomainsItem]:
        payload = self._serialize_data(data)
        response = self._make_request(
            "POST", f"{self._path}/domains/{domain_id}/items", json=payload
        )
        return self._parse_response(response, MarketplaceDomainsItem)  # type: ignore[arg-type]

    def get_domain_item(self, domain_id: int, item_id: int) -> MarketplaceDomainsItem:
        response = self._make_request(
            "GET", f"{self._path}/domains/{domain_id}/items/{item_id}"
        )
        return self._parse_response(response, MarketplaceDomainsItem)  # type: ignore[arg-type]

    def search_domain_items(
        self, domain_id: int, payload: Dict[str, Any]
    ) -> List[MarketplaceDomainsItem]:
        response = self._make_request(
            "POST", f"{self._path}/domains/{domain_id}/items/search", json=payload
        )
        return self._parse_response(response, MarketplaceDomainsItem)  # type: ignore[arg-type]

    def delist_domain_item(self, domain_id: int, item_id: int) -> Dict[str, Any]:
        return self._make_request(
            "DELETE", f"{self._path}/domains/{domain_id}/items/{item_id}"
        )

    def request_item_access(self, domain_id: int, item_id: int) -> Dict[str, Any]:
        return self._make_request(
            "POST",
            f"{self._path}/domains/{domain_id}/items/{item_id}/request_access",
        )

    # Global items
    def list_items(self) -> List[MarketplaceDomainsItem]:
        response = self._make_request("GET", f"{self._path}/items")
        return self._parse_response(response, MarketplaceDomainsItem)  # type: ignore[arg-type]

    def get_item(self, item_id: int) -> MarketplaceDomainsItem:
        response = self._make_request("GET", f"{self._path}/items/{item_id}")
        return self._parse_response(response, MarketplaceDomainsItem)  # type: ignore[arg-type]

    def search_items(self, payload: Dict[str, Any]) -> List[MarketplaceDomainsItem]:
        response = self._make_request(
            "POST", f"{self._path}/items/search", json=payload
        )
        return self._parse_response(response, MarketplaceDomainsItem)  # type: ignore[arg-type]

    # Custodians
    def list_domain_custodians(self, domain_id: int) -> List[CustodianUser]:
        response = self._make_request(
            "GET", f"{self._path}/domains/{domain_id}/custodians"
        )
        return self._parse_response(response, CustodianUser)  # type: ignore[arg-type]

    def update_domain_custodians(
        self, domain_id: int, payload: CustodiansPayload
    ) -> List[CustodianUser]:
        data = self._serialize_data(payload)
        response = self._make_request(
            "PUT", f"{self._path}/domains/{domain_id}/custodians", json=data
        )
        return self._parse_response(response, CustodianUser)  # type: ignore[arg-type]

    def add_domain_custodians(
        self, domain_id: int, payload: CustodiansPayload
    ) -> List[CustodianUser]:
        data = self._serialize_data(payload)
        response = self._make_request(
            "POST", f"{self._path}/domains/{domain_id}/custodians", json=data
        )
        return self._parse_response(response, CustodianUser)  # type: ignore[arg-type]

    def remove_domain_custodians(
        self, domain_id: int, payload: CustodiansPayload
    ) -> Dict[str, Any]:
        data = self._serialize_data(payload)
        return self._make_request(
            "DELETE", f"{self._path}/domains/{domain_id}/custodians", json=data
        )
