from typing import Any, Dict, List, Optional

from nexla_sdk.models.common import LogEntry
from nexla_sdk.models.teams.requests import TeamCreate, TeamMemberList, TeamUpdate
from nexla_sdk.models.teams.responses import Team, TeamMember
from nexla_sdk.resources.base_resource import BaseResource


class TeamsResource(BaseResource):
    """Resource for managing teams."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/teams"
        self._model_class = Team

    def list(self, **kwargs) -> List[Team]:
        """
        List teams with optional filters.

        Args:
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of teams

        Examples:
            client.teams.list(page=2, per_page=50)
        """
        return super().list(**kwargs)

    def get(self, team_id: int, expand: bool = False) -> Team:
        """
        Get single team by ID.

        Args:
            team_id: Team ID
            expand: Include expanded references

        Returns:
            Team instance

        Examples:
            client.teams.get(101)
        """
        return super().get(team_id, expand)

    def create(self, data: TeamCreate) -> Team:
        """
        Create new team.

        Args:
            data: Team creation data

        Returns:
            Created team

        Examples:
            team = client.teams.create(TeamCreate(name="Data Ops"))
        """
        return super().create(data)

    def update(self, team_id: int, data: TeamUpdate) -> Team:
        """
        Update team.

        Args:
            team_id: Team ID
            data: Updated team data

        Returns:
            Updated team
        """
        return super().update(team_id, data)

    def delete(self, team_id: int) -> Dict[str, Any]:
        """
        Delete team.

        Args:
            team_id: Team ID

        Returns:
            Response with status
        """
        return super().delete(team_id)

    def get_members(self, team_id: int) -> List[TeamMember]:
        """
        Get team members.

        Args:
            team_id: Team ID

        Returns:
            List of team members
        """
        path = f"{self._path}/{team_id}/members"
        response = self._make_request("GET", path)
        return [TeamMember(**member) for member in response]

    def add_members(self, team_id: int, members: TeamMemberList) -> List[TeamMember]:
        """
        Add members to team.

        Args:
            team_id: Team ID
            members: Members to add

        Returns:
            Updated member list
        """
        path = f"{self._path}/{team_id}/members"
        response = self._make_request("PUT", path, json=members.to_dict())
        return [TeamMember(**member) for member in response]

    def replace_members(
        self, team_id: int, members: TeamMemberList
    ) -> List[TeamMember]:
        """
        Replace all team members.

        Args:
            team_id: Team ID
            members: New member list

        Returns:
            New member list
        """
        path = f"{self._path}/{team_id}/members"
        response = self._make_request("POST", path, json=members.to_dict())
        return [TeamMember(**member) for member in response]

    def remove_members(
        self, team_id: int, members: Optional[TeamMemberList] = None
    ) -> List[TeamMember]:
        """
        Remove members from team.

        Args:
            team_id: Team ID
            members: Members to remove (None = remove all)

        Returns:
            Remaining members
        """
        path = f"{self._path}/{team_id}/members"
        data = members.to_dict() if members else None
        response = self._make_request("DELETE", path, json=data)
        return [TeamMember(**member) for member in response]

    def get_audit_log(self, team_id: int, **params) -> List[LogEntry]:
        path = f"{self._path}/{team_id}/audit_log"
        response = self._make_request("GET", path, params=params)
        return [LogEntry.model_validate(item) for item in (response or [])]
