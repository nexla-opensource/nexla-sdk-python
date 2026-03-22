import pytest

from nexla_sdk import NexlaClient

pytestmark = pytest.mark.unit


@pytest.fixture
def client(mock_client: NexlaClient) -> NexlaClient:
    return mock_client


class TestApprovalRequestsResource:
    def test_lists_and_actions(self, client, mock_http_client):
        mock_http_client.add_response("/approval_requests/pending", [{"id": 1}])
        p = client.approval_requests.list_pending()
        assert p and p[0].id == 1

        mock_http_client.clear_responses()
        mock_http_client.add_response("/approval_requests/requested", [{"id": 2}])
        r = client.approval_requests.list_requested()
        assert r and r[0].id == 2

        mock_http_client.clear_responses()
        mock_http_client.add_response("/approval_requests/2/approve", {"id": 2})
        ap = client.approval_requests.approve(2)
        assert ap.id == 2

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/approval_requests/2/reject", {"id": 2, "status": "rejected"}
        )
        rj = client.approval_requests.reject(2, reason="not needed")
        assert rj.id == 2
        mock_http_client.assert_request_made("DELETE", "/approval_requests/2/reject")

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/approval_requests/2/cancel", {"id": 2, "status": "cancelled"}
        )
        cn = client.approval_requests.cancel(2)
        assert cn.id == 2
