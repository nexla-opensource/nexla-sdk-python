from typing import TYPE_CHECKING, Any, Dict, List

from nexla_sdk.models.org_tiers.responses import OrgTier
from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class OrgTiersResource(BaseResource[OrgTier]):
    """Resource for organization tiers."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/org_tiers"
        self._model_class = OrgTier

    def list(self, **kwargs: Any) -> List[OrgTier]:  # type: ignore[override]  # keeps public list() signature; base list() also takes positional filters
        return super().list(**kwargs)

    def get(self, org_tier_id: int) -> OrgTier:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
        return super().get(org_tier_id)

    def create(self, data: Dict[str, Any]) -> OrgTier:
        return super().create(data)

    def update(self, org_tier_id: int, data: Dict[str, Any]) -> OrgTier:
        return super().update(org_tier_id, data)

    def delete(self, org_tier_id: int) -> Dict[str, Any]:
        return super().delete(org_tier_id)
