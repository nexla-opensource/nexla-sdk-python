from typing import Any, Dict, List

from nexla_sdk.models.user_tiers.responses import UserTier
from nexla_sdk.resources.base_resource import BaseResource


class UserTiersResource(BaseResource):
    """Resource for user tiers."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/user_tiers"
        self._model_class = UserTier

    def list(self, **kwargs) -> List[UserTier]:
        return super().list(**kwargs)

    def get(self, user_tier_id: int) -> UserTier:
        return super().get(user_tier_id)

    def create(self, data: Dict[str, Any]) -> UserTier:
        return super().create(data)

    def update(self, user_tier_id: int, data: Dict[str, Any]) -> UserTier:
        return super().update(user_tier_id, data)

    def delete(self, user_tier_id: int) -> Dict[str, Any]:
        return super().delete(user_tier_id)
