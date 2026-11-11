"""Request shape for data credential routes served by CredentialsResource."""

import pytest

pytestmark = pytest.mark.unit

ROUTE_CALLS = [
    pytest.param(
        lambda c: c.credentials.data_credentials_update_credentials(
            1, {"name": "renamed"}
        ),
        "PATCH",
        "/data_credentials/1",
        {"json": {"name": "renamed"}},
        id="credentials.data_credentials_update_credentials",
    ),
    pytest.param(
        lambda c: c.credentials.iceberg_migration_status(1, "run-7"),
        "GET",
        "/data_credentials/1/migrate/iceberg/run-7/status",
        {},
        id="credentials.iceberg_migration_status",
    ),
    pytest.param(
        lambda c: c.credentials.data_credentials_probe_credentials_get(
            1, async_mode=True
        ),
        "GET",
        "/data_credentials/1/probe/authenticate",
        {"params": {"async": True}},
        id="credentials.data_credentials_probe_credentials_get",
    ),
    pytest.param(
        lambda c: c.credentials.data_credentials_probe_list_files_in_bucket_credentials(
            1, {"bucket": "b"}
        ),
        "PUT",
        "/data_credentials/1/probe/buckets",
        {"json": {"bucket": "b"}},
        id="credentials.data_credentials_probe_list_files_in_bucket_credentials",
    ),
    pytest.param(
        lambda c: c.credentials.probe_database_metadata_credentials(
            1, {"schema": "public"}
        ),
        "POST",
        "/data_credentials/1/probe/database/metadata",
        {"json": {"schema": "public"}},
        id="credentials.probe_database_metadata_credentials",
    ),
    pytest.param(
        lambda c: c.credentials.probe_database_query_usage_credentials(
            1, {"schema": "public"}
        ),
        "POST",
        "/data_credentials/1/probe/database/query-usage",
        {"json": {"schema": "public"}},
        id="credentials.probe_database_query_usage_credentials",
    ),
    pytest.param(
        lambda c: c.credentials.data_credentials_probe_file_download_credentials(
            1, {"path": "a.csv"}
        ),
        "PUT",
        "/data_credentials/1/probe/file/download",
        {"json": {"path": "a.csv"}},
        id="credentials.data_credentials_probe_file_download_credentials",
    ),
    pytest.param(
        lambda c: c.credentials.data_credentials_probe_read_file_credentials(
            1, {"path": "a.csv"}
        ),
        "PUT",
        "/data_credentials/1/probe/files",
        {"json": {"path": "a.csv"}},
        id="credentials.data_credentials_probe_read_file_credentials",
    ),
    pytest.param(
        lambda c: c.credentials.data_credentials_probe_detect_schemas_credentials(
            1, {"path": "a.csv"}
        ),
        "PUT",
        "/data_credentials/1/probe/schemas",
        {"json": {"path": "a.csv"}},
        id="credentials.data_credentials_probe_detect_schemas_credentials",
    ),
    pytest.param(
        lambda c: c.credentials.data_credentials_probe_search_path_credentials(
            1, {"path": "/"}, query="foo", keep_path=True
        ),
        "PUT",
        "/data_credentials/1/probe/search_path",
        {"params": {"query": "foo", "keep_path": True}, "json": {"path": "/"}},
        id="credentials.data_credentials_probe_search_path_credentials",
    ),
    # Already served by existing methods. Pinned here to lock the verb and path.
    pytest.param(
        lambda c: c.credentials.credentials_schema(),
        "GET",
        "/data_credentials/format",
        {},
        id="credentials.credentials_schema",
    ),
    pytest.param(
        lambda c: c.credentials.intent(1, {}, method="POST"),
        "POST",
        "/data_credentials/1/intent",
        {"json": {}},
        id="credentials.intent_post",
    ),
    pytest.param(
        lambda c: c.credentials.intent(1, {}),
        "PUT",
        "/data_credentials/1/intent",
        {"json": {}},
        id="credentials.intent_put",
    ),
]


@pytest.mark.parametrize("call, method, path, expected", ROUTE_CALLS)
def test_data_credential_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, expected
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    for key, value in expected.items():
        assert last[key] == value
