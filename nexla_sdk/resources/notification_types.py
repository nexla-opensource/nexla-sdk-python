from typing import TYPE_CHECKING, List

from nexla_sdk.models.notification_types.responses import NotificationType
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class NotificationTypesResource(BaseResource):
    """Resource for listing notification types."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/notification_types"
        self._model_class = NotificationType

    def list(self) -> List[NotificationType]:
        response = self._make_request("GET", self._path)
        return self._parse_response(response)

    def list_all(self) -> List[NotificationType]:
        response = self._make_request("GET", f"{self._path}/list")
        return self._parse_response(response)
