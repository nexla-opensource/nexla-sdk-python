"""Unit tests for OAuthResource (POST /oauth/start)."""

import pytest
from pydantic import ValidationError

from nexla_sdk.models.oauth import OauthStartRequest, OauthStartResponse

pytestmark = pytest.mark.unit


def test_start_posts_body_and_parses_response(mock_client, mock_http_client):
    mock_http_client.add_response(
        "/oauth/start",
        {"popup_url": "https://dataops.example/oauth/redirect?sid=abc", "sid": "abc"},
    )

    resp = mock_client.oauth.start(
        OauthStartRequest(vendor_name="Salesforce", auto_create_credential=True)
    )

    assert isinstance(resp, OauthStartResponse)
    assert resp.sid == "abc"
    assert resp.popup_url.endswith("sid=abc")
    last = mock_http_client.get_last_request()
    assert last["method"] == "POST"
    assert last["url"].endswith("/oauth/start")
    assert last["json"] == {
        "vendor_name": "Salesforce",
        "auto_create_credential": True,
        "form_values": {},
    }


def test_start_omits_unset_optional_fields(mock_client, mock_http_client):
    mock_http_client.add_response("/oauth/start", {"popup_url": "u", "sid": "s"})

    mock_client.oauth.start(OauthStartRequest(auth_template_id=7))

    last = mock_http_client.get_last_request()
    assert "client_origin" not in last["json"]
    assert "vendor_id" not in last["json"]
    assert last["json"]["auth_template_id"] == 7


def test_request_rejects_unknown_credentials_type():
    with pytest.raises(ValidationError):
        OauthStartRequest(credentials_type="oauth")
