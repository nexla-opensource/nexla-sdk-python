import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.models.common import LogEntry

pytestmark = pytest.mark.unit


@pytest.fixture
def client(mock_client: NexlaClient) -> NexlaClient:
    return mock_client


class TestDocContainersResource:
    def test_audit_log(self, client, mock_http_client):
        log = {
            "id": 1,
            "item_type": "DOC_CONTAINER",
            "item_id": 10,
            "event": "updated",
            "change_summary": ["updated"],
            "object_changes": {"name": ["old", "new"]},
            "request_ip": "127.0.0.1",
            "request_user_agent": "pytest",
            "request_url": "http://x",
            "user": {"id": 1},
            "org_id": 1,
            "owner_id": 1,
            "owner_email": "a@b.com",
            "created_at": "2023-01-01T00:00:00Z",
        }
        mock_http_client.add_response("/doc_containers/10/audit_log", [log])
        out = client.doc_containers.get_audit_log(10)
        assert isinstance(out[0], LogEntry)
        mock_http_client.assert_request_made("GET", "/doc_containers/10/audit_log")

    def test_audit_log_parses_integer_impersonator_id(
        self, client, mock_http_client
    ):
        """admin-api returns ``impersonator_id`` as the impersonating user's
        numeric id when impersonation is active. Earlier the SDK typed this
        as ``Optional[str]`` and validation failed on real responses."""
        log = {
            "id": 2,
            "item_type": "DOC_CONTAINER",
            "item_id": 10,
            "event": "updated",
            "change_summary": ["updated"],
            "object_changes": {"name": ["old", "new"]},
            "request_ip": "127.0.0.1",
            "request_user_agent": "pytest",
            "request_url": "http://x",
            "user": {"id": 1},
            "org_id": 1,
            "owner_id": 1,
            "owner_email": "a@b.com",
            "created_at": "2023-01-01T00:00:00Z",
            "impersonator_id": 5,  # numeric, not string
        }
        mock_http_client.add_response("/doc_containers/10/audit_log", [log])
        out = client.doc_containers.get_audit_log(10)
        assert out[0].impersonator_id == 5
