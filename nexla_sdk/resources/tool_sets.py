from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class ToolSetsResource(BaseResource[Any]):
    """Resource for tool sets, their exports, revisions, and tools."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/tool_sets"
        self._model_class = None

    def get(self, tool_set_id: str) -> Dict[str, Any]:  # type: ignore[override]  # keeps public get() signature; base get() also takes expand
        """
        Get a tool set by ID or key.

        Args:
            tool_set_id: Tool set ID or key

        Returns:
            Tool set as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "GET",
                f"{self._path}/{tool_set_id}",
                resource_id=str(tool_set_id),
                operation="get_resource",
            ),
        )

    def update(
        self, tool_set_id: Union[int, str, Dict[str, Any]], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Replace the fields of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            data: Fields to update

        Returns:
            Updated tool set as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT",
                f"{self._path}/{tool_set_id}",
                resource_id=str(tool_set_id),
                operation="update_resource",
                json=data,
            ),
        )

    def delete(self, tool_set_id: Union[int, str]) -> Optional[Dict[str, Any]]:  # type: ignore[override]  # returns None for an empty body; base delete() returns a Dict
        """
        Delete a tool set.

        Args:
            tool_set_id: Tool set ID or key

        Returns:
            Response body, or None when the response is empty
        """
        return cast(
            Optional[Dict[str, Any]],
            self._make_request(
                "DELETE",
                f"{self._path}/{tool_set_id}",
                resource_id=str(tool_set_id),
                operation="delete_resource",
            ),
        )

    def tool_sets_update_tool_set(
        self, tool_set_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Partially update a tool set.

        Args:
            tool_set_id: Tool set ID or key
            data: Fields to update

        Returns:
            Updated tool set as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request("PATCH", f"{self._path}/{tool_set_id}", json=data),
        )

    def tool_set_audit_log(self, tool_set_id: str) -> List[Dict[str, Any]]:
        """
        Get the audit log of a tool set.

        The backend route currently returns an empty list.

        Args:
            tool_set_id: Tool set ID or key

        Returns:
            List of audit log entries
        """
        return cast(
            List[Dict[str, Any]],
            self._make_request("GET", f"{self._path}/{tool_set_id}/audit_log"),
        )

    def index_exports(
        self,
        tool_set_id: str,
        tool_set_revision_id: Optional[int] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List exports of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            tool_set_revision_id: Filter by tool set revision ID
            page: Page number
            per_page: Items per page

        Returns:
            List of exports
        """
        params = {
            "tool_set_revision_id": tool_set_revision_id,
            "page": page,
            "per_page": per_page,
        }
        return cast(
            List[Dict[str, Any]],
            self._make_request(
                "GET",
                f"{self._path}/{tool_set_id}/exports",
                params={k: v for k, v in params.items() if v is not None},
            ),
        )

    def create_export(self, tool_set_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an export of a tool set revision.

        Args:
            tool_set_id: Tool set ID or key
            data: Export fields, including tool_set_revision_id

        Returns:
            Created export as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "POST", f"{self._path}/{tool_set_id}/exports", json=data
            ),
        )

    def show_export(self, tool_set_id: str, export_id: str) -> Dict[str, Any]:
        """
        Get an export of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            export_id: Export ID or server key

        Returns:
            Export as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "GET", f"{self._path}/{tool_set_id}/exports/{export_id}"
            ),
        )

    def update_export(
        self, tool_set_id: str, export_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an export of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            export_id: Export ID or server key
            data: Fields to update

        Returns:
            Updated export as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT",
                f"{self._path}/{tool_set_id}/exports/{export_id}",
                json=data,
            ),
        )

    def delete_export(
        self, tool_set_id: str, export_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Delete an export of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            export_id: Export ID or server key

        Returns:
            Response body, or None when the response is empty
        """
        return cast(
            Optional[Dict[str, Any]],
            self._make_request(
                "DELETE", f"{self._path}/{tool_set_id}/exports/{export_id}"
            ),
        )

    def activate_export(self, tool_set_id: str, export_id: str) -> Dict[str, Any]:
        """
        Set an export of a tool set to active.

        Args:
            tool_set_id: Tool set ID or key
            export_id: Export ID or server key

        Returns:
            Updated export as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT", f"{self._path}/{tool_set_id}/exports/{export_id}/activate"
            ),
        )

    def pause_export(self, tool_set_id: str, export_id: str) -> Dict[str, Any]:
        """
        Set an export of a tool set to paused.

        Args:
            tool_set_id: Tool set ID or key
            export_id: Export ID or server key

        Returns:
            Updated export as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT", f"{self._path}/{tool_set_id}/exports/{export_id}/pause"
            ),
        )

    def retire_export(self, tool_set_id: str, export_id: str) -> Dict[str, Any]:
        """
        Set an export of a tool set to retired.

        Args:
            tool_set_id: Tool set ID or key
            export_id: Export ID or server key

        Returns:
            Updated export as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT", f"{self._path}/{tool_set_id}/exports/{export_id}/retire"
            ),
        )

    def index_revisions(
        self,
        tool_set_id: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List revisions of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            page: Page number
            per_page: Items per page

        Returns:
            List of revisions
        """
        params = {"page": page, "per_page": per_page}
        return cast(
            List[Dict[str, Any]],
            self._make_request(
                "GET",
                f"{self._path}/{tool_set_id}/revisions",
                params={k: v for k, v in params.items() if v is not None},
            ),
        )

    def create_revision(self, tool_set_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a revision of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            data: Revision fields

        Returns:
            Created revision as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "POST", f"{self._path}/{tool_set_id}/revisions", json=data
            ),
        )

    def show_revision(self, tool_set_id: str, revision_id: str) -> Dict[str, Any]:
        """
        Get a revision of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            revision_id: Revision ID or semantic version

        Returns:
            Revision as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "GET", f"{self._path}/{tool_set_id}/revisions/{revision_id}"
            ),
        )

    def delete_revision(
        self, tool_set_id: str, revision_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Delete a revision of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            revision_id: Revision ID or semantic version

        Returns:
            Response body, or None when the response is empty
        """
        return cast(
            Optional[Dict[str, Any]],
            self._make_request(
                "DELETE", f"{self._path}/{tool_set_id}/revisions/{revision_id}"
            ),
        )

    def publish_revision(self, tool_set_id: str, revision_id: str) -> Dict[str, Any]:
        """
        Set a revision of a tool set to published.

        Args:
            tool_set_id: Tool set ID or key
            revision_id: Revision ID or semantic version

        Returns:
            Updated revision as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT", f"{self._path}/{tool_set_id}/revisions/{revision_id}/publish"
            ),
        )

    def draft_revision(self, tool_set_id: str, revision_id: str) -> Dict[str, Any]:
        """
        Set a revision of a tool set to draft.

        Args:
            tool_set_id: Tool set ID or key
            revision_id: Revision ID or semantic version

        Returns:
            Updated revision as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT", f"{self._path}/{tool_set_id}/revisions/{revision_id}/draft"
            ),
        )

    def deprecate_revision(self, tool_set_id: str, revision_id: str) -> Dict[str, Any]:
        """
        Set a revision of a tool set to deprecated.

        Args:
            tool_set_id: Tool set ID or key
            revision_id: Revision ID or semantic version

        Returns:
            Updated revision as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT", f"{self._path}/{tool_set_id}/revisions/{revision_id}/deprecate"
            ),
        )

    def retire_revision(self, tool_set_id: str, revision_id: str) -> Dict[str, Any]:
        """
        Set a revision of a tool set to retired.

        Args:
            tool_set_id: Tool set ID or key
            revision_id: Revision ID or semantic version

        Returns:
            Updated revision as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request(
                "PUT", f"{self._path}/{tool_set_id}/revisions/{revision_id}/retire"
            ),
        )

    def tool_sets_index_tools(self, tool_set_id: str) -> List[Dict[str, Any]]:
        """
        List the tools of the latest revision of a tool set.

        Args:
            tool_set_id: Tool set ID or key

        Returns:
            List of tools
        """
        return cast(
            List[Dict[str, Any]],
            self._make_request("GET", f"{self._path}/{tool_set_id}/tools"),
        )

    def add_tools(self, tool_set_id: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Add tools to a tool set.

        Args:
            tool_set_id: Tool set ID or key
            data: Body with a "tools" list

        Returns:
            List of tools after the change
        """
        return cast(
            List[Dict[str, Any]],
            self._make_request("PUT", f"{self._path}/{tool_set_id}/tools", json=data),
        )

    def reset_tools(
        self, tool_set_id: str, data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Replace the tools of a tool set.

        Args:
            tool_set_id: Tool set ID or key
            data: Body with a "tools" list

        Returns:
            List of tools after the change
        """
        return cast(
            List[Dict[str, Any]],
            self._make_request("POST", f"{self._path}/{tool_set_id}/tools", json=data),
        )

    def remove_tools(
        self, tool_set_id: str, data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Remove tools from a tool set.

        Args:
            tool_set_id: Tool set ID or key
            data: Body with a "tools" list

        Returns:
            List of tools after the change
        """
        return cast(
            List[Dict[str, Any]],
            self._make_request(
                "DELETE", f"{self._path}/{tool_set_id}/tools", json=data
            ),
        )
