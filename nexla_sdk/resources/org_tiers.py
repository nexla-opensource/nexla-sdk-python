from typing import Any, Dict, List

from nexla_sdk.models.org_tiers.responses import OrgTier
from nexla_sdk.resources.base_resource import BaseResource


class OrgTiersResource(BaseResource):
    """Resource for organization tiers."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/org_tiers"
        self._model_class = OrgTier

    def list(self, **kwargs) -> List[OrgTier]:
        return super().list(**kwargs)

    def get(self, org_tier_id: int) -> OrgTier:
        return super().get(org_tier_id)

    def create(self, data: Dict[str, Any]) -> OrgTier:
        return super().create(data)

    def update(self, org_tier_id: int, data: Dict[str, Any]) -> OrgTier:
        return super().update(org_tier_id, data)

    def delete(self, org_tier_id: int) -> Dict[str, Any]:
        return super().delete(org_tier_id)
