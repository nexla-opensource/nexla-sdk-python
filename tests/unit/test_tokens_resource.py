"""Unit tests for token resource."""

import pytest

from nexla_sdk import NexlaClient

pytestmark = pytest.mark.unit


@pytest.fixture
def client(mock_client: NexlaClient) -> NexlaClient:
    return mock_client


class TestTokensResource:
    def test_logout(self, client, mock_http_client):
        mock_http_client.add_response("/token/logout", {"status": "ok"})

        response = client.tokens.logout()

        assert isinstance(response, dict)
        mock_http_client.assert_request_made("POST", "/token/logout")

    def test_create_google_token(self, client, mock_http_client):
        mock_http_client.add_response("/gtoken", {"access_token": "goog"})

        response = client.tokens.create_google_token({"id_token": "g123"})

        assert response["access_token"] == "goog"
        mock_http_client.assert_request_made("POST", "/gtoken")

    def test_metadata(self, client, mock_http_client):
        mock_http_client.add_response("/metadata", {"version": "1"})

        response = client.tokens.metadata()

        assert response["version"] == "1"
        mock_http_client.assert_request_made("GET", "/metadata")

    def test_metadata_with_uid(self, client, mock_http_client):
        mock_http_client.add_response("/metadata/uid1", {"version": "1"})

        response = client.tokens.metadata("uid1")

        assert response["version"] == "1"
        mock_http_client.assert_request_made("GET", "/metadata/uid1")

    def test_resource_authorize(self, client, mock_http_client):
        mock_http_client.add_response("/resource_authorize", {"authorized": True})

        response = client.tokens.resource_authorize({"resource_id": 1})

        assert response["authorized"] is True
        mock_http_client.assert_request_made("POST", "/resource_authorize")

    def test_removed_duplicate_methods(self, client):
        """Verify redundant methods were removed."""
        assert not hasattr(client.tokens, "logout_post")
        assert not hasattr(client.tokens, "logout_put")
        assert not hasattr(client.tokens, "refresh_token_put")
