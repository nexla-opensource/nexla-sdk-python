import pytest

from nexla_sdk import NexlaClient
from nexla_sdk.models.code_containers.requests import (
    CodeContainerCreate,
    CodeContainerUpdate,
)
from nexla_sdk.models.code_containers.responses import CodeContainer, CodeOperation

pytestmark = pytest.mark.unit


@pytest.fixture
def client(mock_client: NexlaClient) -> NexlaClient:
    return mock_client


class TestCodeContainersResource:
    def test_list_public_get_crud_copy(self, client, mock_http_client):
        mock_http_client.add_response("/code_containers", [{"id": 1, "name": "cc"}])
        out = client.code_containers.list()
        assert isinstance(out[0], CodeContainer)

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/code_containers/public", [{"id": 2, "name": "pub"}]
        )
        pub = client.code_containers.list_public()
        assert isinstance(pub[0], CodeContainer)

        mock_http_client.clear_responses()
        mock_http_client.add_response("/code_containers/1", {"id": 1, "name": "cc"})
        got = client.code_containers.get(1)
        assert isinstance(got, CodeContainer)

        mock_http_client.clear_responses()
        create = CodeContainerCreate(
            name="cc",
            output_type="json",
            code_type="python",
            code_encoding="utf-8",
            code=[CodeOperation(operation="map", spec={})],
        )
        mock_http_client.add_response("/code_containers", {"id": 3, "name": "cc"})
        created = client.code_containers.create(create)
        assert isinstance(created, CodeContainer)

        mock_http_client.clear_responses()
        mock_http_client.add_response("/code_containers/3", {"id": 3, "name": "cc2"})
        upd = client.code_containers.update(3, CodeContainerUpdate(name="cc2"))
        assert upd.name == "cc2"

        mock_http_client.clear_responses()
        mock_http_client.add_response(
            "/code_containers/3/copy", {"id": 4, "name": "cc-copy"}
        )
        cp = client.code_containers.copy(3)
        assert isinstance(cp, CodeContainer)

        mock_http_client.clear_responses()
        mock_http_client.add_response("/code_containers/4", {"status": "deleted"})
        res = client.code_containers.delete(4)
        assert res.get("status") == "deleted"


@pytest.mark.unit
def test_get_schema_sends_method_query(mock_client, mock_http_client):
    mock_client.code_containers.get_schema(method="get")

    last = mock_http_client.get_last_request()
    assert last["method"] == "GET"
    assert last["url"].endswith("/code_containers/schema")
    assert last["params"] == {"method": "get"}


@pytest.mark.unit
def test_get_schema_without_method_sends_no_query(mock_client, mock_http_client):
    mock_client.code_containers.get_schema()

    last = mock_http_client.get_last_request()
    assert last["url"].endswith("/code_containers/schema")
    assert last["params"] == {}
