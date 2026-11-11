import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.models.self_signup.responses import BlockedDomain, SelfSignupRequest

pytestmark = pytest.mark.unit


@pytest.fixture
def client(mock_client: NexlaClient) -> NexlaClient:
    return mock_client


class TestSelfSignupResource:
    def test_signup_and_verify(self, client, mock_http_client):
        mock_http_client.add_response("/signup", {"status": "ok"})
        res = client.self_signup.signup({"email": "a@b.com", "full_name": "A B"})
        assert res.get("status") == "ok"

        mock_http_client.clear_responses()
        mock_http_client.add_response("/signup/verify_email", {"status": "verified"})
        res2 = client.self_signup.verify_email("tkn")
        assert res2.get("status") == "verified"

    def test_admin_endpoints(self, client, mock_http_client):
        mock_http_client.add_response(
            "/self_signup_requests", [{"id": 1, "email": "x@y.com"}]
        )
        reqs = client.self_signup.list_requests()
        assert isinstance(reqs[0], SelfSignupRequest)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/self_signup_requests/1/approve", {"id": 1, "status": "approved"}
        )
        approved = client.self_signup.approve_request("1")
        assert isinstance(approved, SelfSignupRequest) and approved.id == 1
        # The backend routes self-signup approve via POST. The OpenAPI spec
        # advertises PUT in some versions; the SDK locks the POST contract
        # here so future drift is caught.
        last_request = mock_http_client.get_last_request()
        assert last_request["method"] == "POST"
        assert "/self_signup_requests/1/approve" in last_request["url"]

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/self_signup_blocked_domains", [{"id": 1, "domain": "example.com"}]
        )
        domains = client.self_signup.list_blocked_domains()
        assert isinstance(domains[0], BlockedDomain)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/self_signup_blocked_domains", {"id": 2, "domain": "bad.com"}
        )
        added = client.self_signup.add_blocked_domain("bad.com")
        assert isinstance(added, BlockedDomain) and added.id == 2

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/self_signup_blocked_domains/2", {"id": 2, "domain": "worse.com"}
        )
        updated = client.self_signup.update_blocked_domain("2", "worse.com")
        assert isinstance(updated, BlockedDomain) and updated.domain == "worse.com"

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/self_signup_blocked_domains/2", {"status": "deleted"}
        )
        deleted = client.self_signup.delete_blocked_domain("2")
        assert deleted.get("status") == "deleted"
