from typing import List

from nexla_sdk.models.quarantine_settings.responses import QuarantineSetting
from nexla_sdk.resources.base_resource import BaseResource


class QuarantineSettingsResource(BaseResource):
    """Resource for listing quarantine settings (global endpoints)."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/quarantine_settings"
        self._model_class = QuarantineSetting

    def list(self, **kwargs) -> List[QuarantineSetting]:
        return super().list(**kwargs)

    def get(self, quarantine_setting_id: int) -> QuarantineSetting:
        return super().get(quarantine_setting_id)

    def list_all(self, **params) -> List[QuarantineSetting]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)
