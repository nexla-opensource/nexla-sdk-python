import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.models.org_auth_configs.requests import AuthConfigPayload
from nexla_sdk.models.org_auth_configs.responses import AuthConfig

pytestmark = pytest.mark.unit


@pytest.fixture
def client(mock_client: NexlaClient) -> NexlaClient:
    return mock_client


class TestOrgAuthConfigsResource:
    def test_list_get_list_all_and_crud(self, client, mock_http_client):
        resp = [{"id": 1, "name": "Okta", "protocol": "saml"}]
        mock_http_client.add_response("/api_auth_configs", resp)
        items = client.org_auth_configs.list()
        assert isinstance(items, list) and isinstance(items[0], AuthConfig)
        mock_http_client.assert_request_made("GET", "/api_auth_configs")

        mock_http_client.clear_responses()
        mock_http_client.add_response("/api_auth_configs", resp)
        all_items = client.org_auth_configs.list_all()
        assert isinstance(all_items, list) and isinstance(all_items[0], AuthConfig)
        # Backend has no /api_auth_configs/all route (api_auth_configs/routes/_crud.py:51)
        last = mock_http_client.get_last_request()
        assert last["method"] == "GET" and last["url"].endswith("/api_auth_configs")

        mock_http_client.clear_responses()
        mock_http_client.add_response("/api_auth_configs/1", resp[0])
        got = client.org_auth_configs.get(1)
        assert isinstance(got, AuthConfig) and got.id == 1
        mock_http_client.assert_request_made("GET", "/api_auth_configs/1")

        payload = AuthConfigPayload(name="Okta", protocol="saml")
        created = {"id": 2, "name": "Okta", "protocol": "saml"}
        mock_http_client.clear_responses()
        mock_http_client.add_response("/api_auth_configs", created)
        res = client.org_auth_configs.create(payload)
        assert isinstance(res, AuthConfig) and res.id == 2
        mock_http_client.assert_request_made(
            "POST", "/api_auth_configs", json=payload.model_dump(exclude_none=True)
        )

        mock_http_client.clear_responses()
        updated = {"id": 2, "name": "Okta-2", "protocol": "saml"}
        mock_http_client.add_response("/api_auth_configs/2", updated)
        res2 = client.org_auth_configs.update(2, payload)
        assert isinstance(res2, AuthConfig) and res2.name == "Okta-2"
        mock_http_client.assert_request_made("PUT", "/api_auth_configs/2")

        mock_http_client.clear_responses()
        mock_http_client.add_response("/api_auth_configs/2", {"status": "deleted"})
        del_res = client.org_auth_configs.delete(2)
        assert del_res.get("status") == "deleted"
        mock_http_client.assert_request_made("DELETE", "/api_auth_configs/2")
