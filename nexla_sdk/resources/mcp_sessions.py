from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from nexla_sdk.resources.base_resource import BaseResource

if TYPE_CHECKING:
    from nexla_sdk.client import NexlaClient


class McpSessionsResource(BaseResource[Any]):
    """Resource for MCP sessions."""

    def __init__(self, client: "NexlaClient") -> None:
        super().__init__(client)
        self._path = "/mcp_sessions"
        self._model_class = None

    def index_mcp_sessions(
        self,
        org_id: Optional[int] = None,
        tool_set_revision_id: Optional[int] = None,
        mcp_session_id: Optional[str] = None,
        initialized: Optional[bool] = None,
        terminated: Optional[bool] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List MCP sessions.

        Args:
            org_id: Filter by org ID
            tool_set_revision_id: Filter by tool set revision ID
            mcp_session_id: Filter by MCP session ID
            initialized: Filter by initialized state
            terminated: Filter by terminated state
            page: Page number
            per_page: Items per page

        Returns:
            List of MCP sessions
        """
        params = {
            "org_id": org_id,
            "tool_set_revision_id": tool_set_revision_id,
            "mcp_session_id": mcp_session_id,
            "initialized": None if initialized is None else str(initialized).lower(),
            "terminated": None if terminated is None else str(terminated).lower(),
            "page": page,
            "per_page": per_page,
        }
        return cast(
            List[Dict[str, Any]],
            self._make_request(
                "GET",
                self._path,
                params={k: v for k, v in params.items() if v is not None},
            ),
        )

    def create_mcp_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an MCP session.

        Args:
            data: Session fields

        Returns:
            Created MCP session as a dict
        """
        return cast(Dict[str, Any], self._make_request("POST", self._path, json=data))

    def show_mcp_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get an MCP session by ID or MCP session ID.

        Args:
            session_id: Session ID or MCP session ID

        Returns:
            MCP session as a dict
        """
        return cast(
            Dict[str, Any], self._make_request("GET", f"{self._path}/{session_id}")
        )

    def mcp_sessions_update_mcp_session(
        self, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Partially update an MCP session.

        Args:
            session_id: Session ID or MCP session ID
            data: Fields to update

        Returns:
            Updated MCP session as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request("PATCH", f"{self._path}/{session_id}", json=data),
        )

    def mcp_sessions_update_mcp_session_put(
        self, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an MCP session.

        Args:
            session_id: Session ID or MCP session ID
            data: Fields to update

        Returns:
            Updated MCP session as a dict
        """
        return cast(
            Dict[str, Any],
            self._make_request("PUT", f"{self._path}/{session_id}", json=data),
        )

    def delete_mcp_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Delete an MCP session.

        Args:
            session_id: Session ID or MCP session ID

        Returns:
            Response body, or None when the response is empty
        """
        return cast(
            Optional[Dict[str, Any]],
            self._make_request("DELETE", f"{self._path}/{session_id}"),
        )
