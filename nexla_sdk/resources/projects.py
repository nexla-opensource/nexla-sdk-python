from typing import Any, Dict, List, Optional

from nexla_sdk.models.flows.responses import FlowResponse
from nexla_sdk.models.projects.requests import (
    ProjectCreate,
    ProjectFlowList,
    ProjectUpdate,
)
from nexla_sdk.models.projects.responses import Project, ProjectDataFlow
from nexla_sdk.resources.base_resource import BaseResource


class ProjectsResource(BaseResource):
    """Resource for managing projects."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/projects"
        self._model_class = Project

    def list(self, expand: bool = False, **kwargs) -> List[Project]:
        """
        List projects with optional filters.

        Args:
            expand: Include flows in the response
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of projects

        Examples:
            client.projects.list(page=1, per_page=10)
            client.projects.list(expand=True)
        """
        if expand:
            kwargs["expand"] = "true"
        return super().list(**kwargs)

    def get(self, project_id: int, expand: bool = False) -> Project:
        """
        Get single project by ID.

        Args:
            project_id: Project ID
            expand: Include expanded references

        Returns:
            Project instance

        Examples:
            client.projects.get(12)
        """
        return super().get(project_id, expand)

    def create(self, data: ProjectCreate) -> Project:
        """
        Create new project.

        Args:
            data: Project creation data

        Returns:
            Created project

        Examples:
            client.projects.create(ProjectCreate(name="My Project"))
        """
        return super().create(data)

    def update(self, project_id: int, data: ProjectUpdate) -> Project:
        """
        Update project.

        Args:
            project_id: Project ID
            data: Updated project data

        Returns:
            Updated project
        """
        return super().update(project_id, data)

    def delete(self, project_id: int) -> Dict[str, Any]:
        """
        Delete project.

        Args:
            project_id: Project ID

        Returns:
            Response with status
        """
        return super().delete(project_id)

    def copy(
        self, project_id: int, payload: Optional[Dict[str, Any]] = None
    ) -> Project:
        return super().copy(project_id, payload)

    def search(self, filters: Dict[str, Any], **params) -> List[Project]:
        return super().search(filters, **params)

    def search_tags(self, tags: List[str], **params) -> List[Project]:
        return super().search_tags(tags, **params)

    def get_resources_access(self, project_id: int) -> Dict[str, Any]:
        return self._make_request("GET", f"{self._path}/{project_id}/resources_access")

    def get_flows(self, project_id: int) -> FlowResponse:
        """
        Get flows in project.

        Args:
            project_id: Project ID

        Returns:
            Flow response
        """
        path = f"{self._path}/{project_id}/flows"
        response = self._make_request("GET", path)
        return FlowResponse.model_validate(response)

    def add_flows(
        self, project_id: int, flows: ProjectFlowList
    ) -> List[ProjectDataFlow]:
        """
        Add flows to project.

        Args:
            project_id: Project ID
            flows: Flows to add

        Returns:
            List of added project flows
        """
        path = f"{self._path}/{project_id}/flows"
        payload = self._serialize_data(flows)
        response = self._make_request("PUT", path, json=payload)
        # API returns a list of project data flows for add operation
        return [ProjectDataFlow.model_validate(item) for item in response]

    def replace_flows(
        self, project_id: int, flows: ProjectFlowList
    ) -> List[ProjectDataFlow]:
        """
        Replace all flows in project.

        Args:
            project_id: Project ID
            flows: New flow list

        Returns:
            List of project flows after replacement
        """
        path = f"{self._path}/{project_id}/flows"
        payload = self._serialize_data(flows)
        response = self._make_request("POST", path, json=payload)
        # API returns a list of project data flows for replace operation
        return [ProjectDataFlow.model_validate(item) for item in response]

    def remove_flows(
        self, project_id: int, flows: Optional[ProjectFlowList] = None
    ) -> List[ProjectDataFlow]:
        """
        Remove flows from project.

        Args:
            project_id: Project ID
            flows: Flows to remove (None = remove all)

        Returns:
            Remaining project flows
        """
        path = f"{self._path}/{project_id}/flows"
        data = self._serialize_data(flows) if flows else None
        response = self._make_request("DELETE", path, json=data)
        # API returns remaining flows list
        return [ProjectDataFlow.model_validate(item) for item in response]

    def add_data_flows(
        self, project_id: int, flows: ProjectFlowList
    ) -> List[ProjectDataFlow]:
        """
        Backward-compatible alias for adding flows to a project.

        Uses the updated endpoint '/flows'.
        """
        return self.add_flows(project_id, flows)

    def get_data_flows_legacy(self, project_id: int) -> List[ProjectDataFlow]:
        """
        Legacy project flow listing endpoint.

        This calls '/projects/{id}/data_flows', which the backend still supports
        for backward compatibility.
        """
        path = f"{self._path}/{project_id}/data_flows"
        response = self._make_request("GET", path)
        return [ProjectDataFlow.model_validate(item) for item in response]

    def replace_data_flows(
        self, project_id: int, flows: ProjectFlowList
    ) -> List[ProjectDataFlow]:
        """
        Backward-compatible alias for replacing all flows in a project.

        Uses the updated endpoint '/flows'.
        """
        return self.replace_flows(project_id, flows)

    def add_data_flows_legacy(
        self, project_id: int, flows: ProjectFlowList
    ) -> List[ProjectDataFlow]:
        """Legacy add endpoint: '/projects/{id}/data_flows'."""
        path = f"{self._path}/{project_id}/data_flows"
        payload = self._serialize_data(flows)
        response = self._make_request("PUT", path, json=payload)
        return [ProjectDataFlow.model_validate(item) for item in response]

    def replace_data_flows_legacy(
        self, project_id: int, flows: ProjectFlowList
    ) -> List[ProjectDataFlow]:
        """Legacy replace endpoint: '/projects/{id}/data_flows'."""
        path = f"{self._path}/{project_id}/data_flows"
        payload = self._serialize_data(flows)
        response = self._make_request("POST", path, json=payload)
        return [ProjectDataFlow.model_validate(item) for item in response]

    def remove_data_flows(
        self, project_id: int, flows: Optional[ProjectFlowList] = None
    ) -> List[ProjectDataFlow]:
        """
        Backward-compatible alias for removing flows from a project.

        Uses the updated endpoint '/flows'.
        """
        return self.remove_flows(project_id, flows)

    def remove_data_flows_legacy(
        self, project_id: int, flows: Optional[ProjectFlowList] = None
    ) -> List[ProjectDataFlow]:
        """Legacy remove endpoint: '/projects/{id}/data_flows'."""
        path = f"{self._path}/{project_id}/data_flows"
        data = self._serialize_data(flows) if flows else None
        response = self._make_request("DELETE", path, json=data)
        return [ProjectDataFlow.model_validate(item) for item in response]

    def search_flows(
        self, project_id: int, filters: List[Dict[str, Any]]
    ) -> FlowResponse:
        """
        Search flows in a project using filter criteria.

        Args:
            project_id: Project ID
            filters: List of filter dicts

        Returns:
            Flow response matching the search criteria
        """
        path = f"{self._path}/{project_id}/flows/search"
        payload = {"filters": filters}
        response = self._make_request("POST", path, json=payload)
        return FlowResponse.model_validate(response)
