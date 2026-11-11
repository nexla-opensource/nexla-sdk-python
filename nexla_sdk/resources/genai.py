from typing import Any, Dict, List

from nexla_sdk.models.genai.requests import (
    GenAiConfigCreatePayload,
    GenAiConfigPayload,
    GenAiOrgSettingPayload,
)
from nexla_sdk.models.genai.responses import (
    ActiveConfigView,
    GenAiConfig,
    GenAiOrgSetting,
)
from nexla_sdk.resources.base_resource import BaseResource


class GenAIResource(BaseResource):
    """Resource for GenAI configurations and org settings."""

    def __init__(self, client):
        super().__init__(client)
        self._path = ""
        self._model_class = None

    # Integration Configs
    def list_configs(self) -> List[GenAiConfig]:
        response = self._make_request("GET", "/gen_ai_integration_configs")
        return [GenAiConfig.model_validate(item) for item in (response or [])]

    def create_config(self, payload: GenAiConfigCreatePayload) -> GenAiConfig:
        data = self._serialize_data(payload)
        response = self._make_request("POST", "/gen_ai_integration_configs", json=data)
        return GenAiConfig.model_validate(response)

    def get_config(self, gen_ai_config_id: int) -> GenAiConfig:
        response = self._make_request(
            "GET", f"/gen_ai_integration_configs/{gen_ai_config_id}"
        )
        return GenAiConfig.model_validate(response)

    def update_config(
        self, gen_ai_config_id: int, payload: GenAiConfigPayload
    ) -> GenAiConfig:
        data = self._serialize_data(payload)
        response = self._make_request(
            "PUT", f"/gen_ai_integration_configs/{gen_ai_config_id}", json=data
        )
        return GenAiConfig.model_validate(response)

    def delete_config(self, gen_ai_config_id: int) -> Dict[str, Any]:
        return self._make_request(
            "DELETE", f"/gen_ai_integration_configs/{gen_ai_config_id}"
        )

    # Org Settings
    def list_org_settings(
        self, org_id: int = None, all: bool = False
    ) -> List[GenAiOrgSetting]:
        params = {}
        if org_id is not None:
            params["org_id"] = org_id
        if all:
            params["all"] = True
        response = self._make_request("GET", "/gen_ai_org_settings", params=params)
        return [GenAiOrgSetting.model_validate(item) for item in (response or [])]

    def create_org_setting(self, payload: GenAiOrgSettingPayload) -> GenAiOrgSetting:
        data = self._serialize_data(payload)
        response = self._make_request("POST", "/gen_ai_org_settings", json=data)
        return GenAiOrgSetting.model_validate(response)

    def get_org_setting(self, gen_ai_org_setting_id: int) -> GenAiOrgSetting:
        response = self._make_request(
            "GET", f"/gen_ai_org_settings/{gen_ai_org_setting_id}"
        )
        return GenAiOrgSetting.model_validate(response)

    def update_org_setting(
        self, gen_ai_org_setting_id: int, payload: GenAiOrgSettingPayload
    ) -> GenAiOrgSetting:
        data = self._serialize_data(payload)
        response = self._make_request(
            "PUT", f"/gen_ai_org_settings/{gen_ai_org_setting_id}", json=data
        )
        return GenAiOrgSetting.model_validate(response)

    def delete_org_setting(self, gen_ai_org_setting_id: int) -> Dict[str, Any]:
        return self._make_request(
            "DELETE", f"/gen_ai_org_settings/{gen_ai_org_setting_id}"
        )

    def delete_org_settings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("DELETE", "/gen_ai_org_settings", json=payload)

    def show_active_config(self, gen_ai_usage: str) -> ActiveConfigView:
        response = self._make_request(
            "GET",
            "/gen_ai_org_settings/active_config",
            params={"gen_ai_usage": gen_ai_usage},
        )
        return ActiveConfigView.model_validate(response)
