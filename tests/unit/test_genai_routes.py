"""Request shape for the genai resource methods added for missing routes.

Each row names the method, the HTTP verb and path the call must send, the
expected query params, and the expected JSON body (None means not checked).
"""

import pytest

pytestmark = pytest.mark.unit

GENAI_ROUTE_CALLS = [
    pytest.param(
        lambda c: c.genai.gen_ai_integration_configs_update_gen_ai_config(
            7, {"name": "x"}
        ),
        "PATCH",
        "/gen_ai_integration_configs/7",
        {},
        {"name": "x"},
        id="genai.gen_ai_integration_configs_update_gen_ai_config",
    ),
]


@pytest.mark.parametrize("call, method, path, params, json_body", GENAI_ROUTE_CALLS)
def test_genai_route_sends_expected_request(
    mock_client, mock_http_client, call, method, path, params, json_body
):
    call(mock_client)

    last = mock_http_client.get_last_request()
    assert last["method"] == method
    assert last["url"].endswith(path)
    assert last["params"] == params
    if json_body is not None:
        assert last["json"] == json_body


def test_delete_org_settings_warning_names_working_replacement(
    mock_client, mock_http_client
):
    # DELETE /gen_ai_org_settings does not exist. The warning must name the
    # route-backed method that deletes one setting.
    mock_http_client.add_response("/gen_ai_org_settings", [])

    with pytest.warns(
        DeprecationWarning,
        match=r"Use delete_org_setting\(gen_ai_org_setting_id\) instead",
    ):
        mock_client.genai.delete_org_settings({"x": 1})
