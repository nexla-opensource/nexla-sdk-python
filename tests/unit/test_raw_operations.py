"""Unit tests for operation-level raw client access."""

import pytest

from nexla_sdk.exceptions import ValidationError


@pytest.mark.unit
class TestRawOperationsClient:
    def test_list_operations_includes_known_operation(self, mock_client):
        operations = mock_client.raw.list_operations()
        assert "get_project_flows" in operations
        assert "get_data_sources" in operations

    def test_call_operation_renders_path_and_uses_method(self, mock_client):
        mock_client.http_client.add_response(
            "/projects/123/flows", {"data": [{"flow_id": 123}]}
        )

        response = mock_client.raw.call(
            "get_project_flows", path_params={"project_id": 123}
        )

        assert response == {"data": [{"flow_id": 123}]}
        mock_client.http_client.assert_request_made("GET", "/projects/123/flows")

    def test_call_operation_with_query_and_body(self, mock_client):
        mock_client.http_client.add_response("/notifications", {"status": "ok"})

        response = mock_client.raw.call(
            "get_notifications",
            query={"page": 2, "per_page": 10},
            body={"read": True},
        )

        assert response == {"status": "ok"}
        request = mock_client.http_client.get_last_request()
        assert request["params"] == {"page": 2, "per_page": 10}
        assert request["json"] == {"read": True}
        assert request["method"] == "GET"

    def test_call_operation_missing_path_param_raises_validation_error(
        self, mock_client
    ):
        with pytest.raises(ValidationError):
            mock_client.raw.call("get_project_flows")

    def test_call_unknown_operation_raises_validation_error(self, mock_client):
        with pytest.raises(ValidationError):
            mock_client.raw.call("not_a_real_operation")

    def test_direct_helpers(self, mock_client):
        mock_client.http_client.add_response("/limits", {"second": {"common": {}}})
        response = mock_client.raw.get("/limits")
        assert "second" in response
        mock_client.http_client.assert_request_made("GET", "/limits")

    def test_generic_request_supports_backend_only_routes(self, mock_client):
        mock_client.http_client.add_response(
            "/self_signup_requests/1/approve", {"id": 1}
        )
        response = mock_client.raw.request("post", "/self_signup_requests/1/approve")
        assert response["id"] == 1
        mock_client.http_client.assert_request_made(
            "POST", "/self_signup_requests/1/approve"
        )
