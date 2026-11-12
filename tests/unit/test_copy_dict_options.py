"""copy() accepts copy options as a dict or as the options model."""

import pytest

from tests.utils.mock_builders import MockResponseBuilder

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("attr", "path", "build"),
    [
        ("sources", "/data_sources", lambda: MockResponseBuilder.source(source_id=6)),
        (
            "destinations",
            "/data_sinks",
            lambda: MockResponseBuilder.destination({"id": 6}),
        ),
        ("nexsets", "/data_sets", lambda: MockResponseBuilder.nexset({"id": 6})),
    ],
)
def test_copy_accepts_dict_options(mock_client, attr, path, build):
    mock_client.http_client.add_response(f"{path}/5/copy", build())

    getattr(mock_client, attr).copy(5, {"reuse_data_credentials": True})

    last = mock_client.http_client.get_last_request()
    assert last["method"] == "POST"
    assert f"{path}/5/copy" in last["url"]
    assert last["json"] == {"reuse_data_credentials": True}
