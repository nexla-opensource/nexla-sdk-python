import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.models.marketplace.requests import (
    CustodiansPayload,
    MarketplaceDomainCreate,
    MarketplaceDomainsItemCreate,
)
from nexla_sdk.models.marketplace.responses import (
    MarketplaceDomain,
    MarketplaceDomainsItem,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def client(mock_client: NexlaClient) -> NexlaClient:
    return mock_client


class TestMarketplaceResource:
    def test_domains_items_and_custodians(self, client, mock_http_client):
        mock_http_client.add_response(
            "/marketplace/domains", [{"id": 1, "name": "Dom"}]
        )
        doms = client.marketplace.list_domains()
        assert isinstance(doms[0], MarketplaceDomain)

        mock_http_client.clear_responses()
        payload = MarketplaceDomainCreate(name="New")
        mock_http_client.add_response(
            "/marketplace/domains", [{"id": 2, "name": "New"}]
        )
        doms_created = client.marketplace.create_domains(payload)
        assert isinstance(doms_created[0], MarketplaceDomain)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/marketplace/domains/for_org", [{"id": 1, "name": "Dom"}]
        )
        by_org = client.marketplace.get_domains_for_org(5)
        assert isinstance(by_org[0], MarketplaceDomain)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/marketplace/domains/2", {"id": 2, "name": "New"}
        )
        got = client.marketplace.get_domain(2)
        assert isinstance(got, MarketplaceDomain)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/marketplace/domains/2", {"id": 2, "name": "Upd"}
        )
        upd = client.marketplace.update_domain(2, payload)
        assert isinstance(upd, MarketplaceDomain)

        mock_http_client.clear_responses()
        mock_http_client.add_response("/marketplace/domains/2", {"status": "deleted"})
        d = client.marketplace.delete_domain(2)
        assert d.get("status") == "deleted"

        mock_http_client.clear_responses()
        mock_http_client.add_response("/marketplace/domains/1/items", [{"id": 10}])
        items = client.marketplace.list_domain_items(1)
        assert isinstance(items[0], MarketplaceDomainsItem)

        mock_http_client.clear_responses()
        item_payload = MarketplaceDomainsItemCreate(name="Item", data_set_id=999)
        mock_http_client.add_response("/marketplace/domains/1/items", [{"id": 11}])
        created_items = client.marketplace.create_domain_item(1, item_payload)
        assert isinstance(created_items[0], MarketplaceDomainsItem)

        mock_http_client.clear_responses()
        mock_http_client.add_response("/marketplace/domains/1/custodians", [])
        cust = client.marketplace.list_domain_custodians(1)
        assert isinstance(cust, list)

        mock_http_client.clear_responses()
        cust_payload = CustodiansPayload(custodians=[])
        mock_http_client.add_response("/marketplace/domains/1/custodians", [])
        upd_c = client.marketplace.update_domain_custodians(1, cust_payload)
        assert isinstance(upd_c, list)

        mock_http_client.clear_responses()
        mock_http_client.add_response("/marketplace/domains/1/custodians", [])
        add_c = client.marketplace.add_domain_custodians(1, cust_payload)
        assert isinstance(add_c, list)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/marketplace/domains/1/custodians", {"status": "ok"}
        )
        rem_c = client.marketplace.remove_domain_custodians(1, cust_payload)
        assert rem_c.get("status") == "ok"

    def test_domain_custodian_methods_match_backend_verbs(
        self, client, mock_http_client
    ):
        """Backend (marketplace/routes/_core.py:1565-1576): PUT adds, POST resets."""
        payload = CustodiansPayload(custodians=[])
        url = "/marketplace/domains/1/custodians"

        mock_http_client.add_response(url, [])
        client.marketplace.add_domain_custodians(1, payload)
        mock_http_client.assert_request_made("PUT", url)

        mock_http_client.clear_requests()
        client.marketplace.reset_domain_custodians(1, payload)
        mock_http_client.assert_request_made("POST", url)

        mock_http_client.clear_requests()
        with pytest.warns(DeprecationWarning, match="add_domain_custodians"):
            client.marketplace.update_domain_custodians(1, payload)
        mock_http_client.assert_request_made("PUT", url)
