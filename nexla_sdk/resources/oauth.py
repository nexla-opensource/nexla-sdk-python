from typing import TYPE_CHECKING

from nexla_sdk.models.oauth.requests import OauthStartRequest
from nexla_sdk.models.oauth.responses import OauthStartResponse
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class OAuthResource(BaseResource):
    """Resource for the server-side OAuth flow."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/oauth"
        self._model_class = None

    def start(self, data: OauthStartRequest) -> OauthStartResponse:
        """
        Start a server-side OAuth flow.

        The client opens the returned popup_url in a popup window. The popup
        completes the flow on the backend.

        Args:
            data: Vendor or auth template selection and form values

        Returns:
            Popup URL and session ID

        Examples:
            resp = client.oauth.start(OauthStartRequest(vendor_name="Salesforce"))
            print(resp.popup_url)
        """
        response = self._make_request(
            "POST", f"{self._path}/start", json=self._serialize_data(data)
        )
        return self._parse_response(response, OauthStartResponse)
