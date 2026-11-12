from typing import TYPE_CHECKING, Any, List, cast

from nexla_sdk.models.quarantine_settings.responses import QuarantineSetting
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class QuarantineSettingsResource(BaseResource[QuarantineSetting]):
    """Resource for listing quarantine settings (global endpoints)."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/quarantine_settings"
        self._model_class = QuarantineSetting

    def list(self, **kwargs: Any) -> List[QuarantineSetting]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        return super().list(**kwargs)

    def get(self, quarantine_setting_id: int) -> QuarantineSetting:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
        return super().get(quarantine_setting_id)

    def list_all(self, **params: Any) -> List[QuarantineSetting]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return cast(List[QuarantineSetting], self._parse_response(response))
