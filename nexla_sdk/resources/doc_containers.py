from typing import Any, Dict, List, Optional

from nexla_sdk.models.common import LogEntry
from nexla_sdk.models.doc_containers.responses import DocContainer
from nexla_sdk.resources.base_resource import BaseResource


class DocContainersResource(BaseResource):
    """Resource for document containers."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/doc_containers"
        self._model_class = DocContainer

    def list(self, **kwargs) -> List[DocContainer]:
        return super().list(**kwargs)

    def get(self, doc_container_id: int, expand: bool = False) -> DocContainer:
        return super().get(doc_container_id, expand)

    def create(self, data: Dict[str, Any]) -> DocContainer:
        return super().create(data)

    def update(self, doc_container_id: int, data: Dict[str, Any]) -> DocContainer:
        return super().update(doc_container_id, data)

    def delete(self, doc_container_id: int) -> Dict[str, Any]:
        return super().delete(doc_container_id)

    def copy(
        self, doc_container_id: int, payload: Optional[Dict[str, Any]] = None
    ) -> DocContainer:
        return super().copy(doc_container_id, payload)

    def search(self, filters: Dict[str, Any], **params) -> List[DocContainer]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[DocContainer]:
        return super().search_tags(tags, **params)

    def get_audit_log(self, doc_container_id: int, **params) -> List[LogEntry]:
        path = f"{self._path}/{doc_container_id}/audit_log"
        response = self._make_request("GET", path, params=params)
        return [LogEntry.model_validate(item) for item in (response or [])]

    # Accessors via BaseResource methods are compatible
    # get_accessors, add_accessors, replace_accessors, delete_accessors
