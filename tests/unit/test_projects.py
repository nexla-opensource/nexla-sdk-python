"""Unit tests for projects resource."""

import pytest
from pydantic import ValidationError

from nexla_sdk.exceptions import NotFoundError, ServerError
from nexla_sdk.http_client import HttpClientError
from nexla_sdk.models.flows.responses import FlowResponse
from nexla_sdk.models.projects.requests import (
    ProjectCreate,
    ProjectFlowIdentifier,
    ProjectFlowList,
    ProjectUpdate,
)
from nexla_sdk.models.projects.responses import Project, ProjectDataFlow
from tests.utils.mock_builders import MockDataFactory, MockResponseBuilder


@pytest.mark.unit
class TestProjectsResource:
    """Test cases for ProjectsResource."""

    def test_list_projects(self, mock_client):
        """Test listing projects."""
        # Arrange
        mock_data = [MockResponseBuilder.project() for _ in range(2)]
        mock_client.http_client.add_response("/projects", mock_data)

        # Act
        projects = mock_client.projects.list()

        # Assert
        assert len(projects) == 2
        assert all(isinstance(project, Project) for project in projects)
        mock_client.http_client.assert_request_made("GET", "/projects")

    def test_list_projects_with_parameters(self, mock_client):
        """Test listing projects with query parameters."""
        # Arrange
        mock_data = [MockResponseBuilder.project()]
        mock_client.http_client.add_response("/projects", mock_data)

        # Act
        projects = mock_client.projects.list(
            page=2, per_page=10, access_role="collaborator"
        )

        # Assert
        assert len(projects) == 1
        mock_client.http_client.assert_request_made("GET", "/projects")

        # Verify the parameters
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("page") == 2
        assert request["params"].get("per_page") == 10
        assert request["params"].get("access_role") == "collaborator"

    def test_list_projects_with_expand(self, mock_client):
        """Test listing projects with expand parameter."""
        # Arrange
        factory = MockDataFactory()
        project_data = factory.create_mock_project()
        project_data["data_flows"] = [
            factory.create_mock_project_data_flow() for _ in range(2)
        ]
        project_data["flows"] = [
            factory.create_mock_project_data_flow() for _ in range(2)
        ]
        mock_client.http_client.add_response("/projects", [project_data])

        # Act
        projects = mock_client.projects.list(expand=True)

        # Assert
        assert len(projects) == 1
        assert len(projects[0].data_flows) == 2
        assert len(projects[0].flows) == 2
        mock_client.http_client.assert_request_made("GET", "/projects")

        # Verify expand parameter was sent
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("expand") == "true"

    def test_get_project(self, mock_client):
        """Test getting a single project."""
        # Arrange
        project_id = 123
        mock_data = MockResponseBuilder.project(project_id=project_id)
        mock_client.http_client.add_response(f"/projects/{project_id}", mock_data)

        # Act
        project = mock_client.projects.get(project_id)

        # Assert
        assert isinstance(project, Project)
        assert project.id == project_id
        mock_client.http_client.assert_request_made("GET", f"/projects/{project_id}")

    def test_get_project_with_expand(self, mock_client):
        """Test getting project with expand parameter."""
        # Arrange
        project_id = 123
        mock_data = MockResponseBuilder.project(project_id=project_id)
        mock_client.http_client.add_response(f"/projects/{project_id}", mock_data)

        # Act
        project = mock_client.projects.get(project_id, expand=True)

        # Assert
        assert isinstance(project, Project)
        mock_client.http_client.assert_request_made("GET", f"/projects/{project_id}")

        # Verify expand parameter was sent
        request = mock_client.http_client.get_last_request()
        assert request["params"].get("expand") == 1

    def test_create_project(self, mock_client):
        """Test creating a project."""
        # Arrange
        mock_data = MockResponseBuilder.project()
        mock_client.http_client.add_response("/projects", mock_data)

        project_data = ProjectCreate(
            name="Test Project",
            description="Test project description",
            data_flows=[
                ProjectFlowIdentifier(data_source_id=123),
                ProjectFlowIdentifier(data_set_id=456),
            ],
        )

        # Act
        project = mock_client.projects.create(project_data)

        # Assert
        assert isinstance(project, Project)
        mock_client.http_client.assert_request_made("POST", "/projects")

        # Verify request body
        request = mock_client.http_client.get_last_request()
        assert request["json"]["name"] == "Test Project"

    def test_update_project(self, mock_client):
        """Test updating a project."""
        # Arrange
        project_id = 123
        mock_data = MockResponseBuilder.project(
            project_id=project_id, name="Updated Project"
        )
        mock_client.http_client.add_response(f"/projects/{project_id}", mock_data)

        update_data = ProjectUpdate(
            name="Updated Project", description="Updated description"
        )

        # Act
        project = mock_client.projects.update(project_id, update_data)

        # Assert
        assert isinstance(project, Project)
        assert project.name == "Updated Project"
        mock_client.http_client.assert_request_made("PUT", f"/projects/{project_id}")

    def test_delete_project(self, mock_client):
        """Test deleting a project."""
        # Arrange
        project_id = 123
        mock_client.http_client.add_response(
            f"/projects/{project_id}", {"status": "deleted"}
        )

        # Act
        result = mock_client.projects.delete(project_id)

        # Assert
        assert result == {"status": "deleted"}
        mock_client.http_client.assert_request_made("DELETE", f"/projects/{project_id}")

    def test_get_flows(self, mock_client):
        """Test getting flows in a project."""
        # Arrange
        project_id = 123
        mock_data = MockResponseBuilder.flow_response()
        mock_client.http_client.add_response(f"/projects/{project_id}/flows", mock_data)

        # Act
        flows = mock_client.projects.get_flows(project_id)

        # Assert
        assert isinstance(flows, FlowResponse)
        mock_client.http_client.assert_request_made(
            "GET", f"/projects/{project_id}/flows"
        )

    def test_search_flows(self, mock_client):
        """Test searching flows in a project."""
        # Arrange
        project_id = 123
        filters = [{"field": "name", "operator": "contains", "value": "test"}]
        mock_data = MockResponseBuilder.flow_response()
        mock_client.http_client.add_response(
            f"/projects/{project_id}/flows/search", mock_data
        )

        # Act
        flows = mock_client.projects.search_flows(project_id, filters)

        # Assert
        assert isinstance(flows, FlowResponse)
        mock_client.http_client.assert_request_made(
            "POST", f"/projects/{project_id}/flows/search"
        )

    def test_legacy_data_flows_endpoints(self, mock_client):
        """Test deprecated /data_flows project endpoints."""
        project_id = 123
        factory = MockDataFactory()
        mock_data = [factory.create_mock_project_data_flow() for _ in range(2)]
        mock_client.http_client.add_response(
            f"/projects/{project_id}/data_flows", mock_data
        )

        list_result = mock_client.projects.get_data_flows_legacy(project_id)
        assert len(list_result) == 2
        assert all(isinstance(flow, ProjectDataFlow) for flow in list_result)
        mock_client.http_client.assert_request_made(
            "GET", f"/projects/{project_id}/data_flows"
        )

        flows = ProjectFlowList(data_flows=[ProjectFlowIdentifier(data_source_id=456)])

        mock_client.http_client.clear_responses()
        mock_client.http_client.add_response(
            f"/projects/{project_id}/data_flows", mock_data
        )
        add_result = mock_client.projects.add_data_flows_legacy(project_id, flows)
        assert len(add_result) == 2
        mock_client.http_client.assert_request_made(
            "PUT", f"/projects/{project_id}/data_flows"
        )

        mock_client.http_client.clear_responses()
        mock_client.http_client.add_response(
            f"/projects/{project_id}/data_flows", mock_data
        )
        replace_result = mock_client.projects.replace_data_flows_legacy(
            project_id, flows
        )
        assert len(replace_result) == 2
        mock_client.http_client.assert_request_made(
            "POST", f"/projects/{project_id}/data_flows"
        )

        mock_client.http_client.clear_responses()
        mock_client.http_client.add_response(
            f"/projects/{project_id}/data_flows", mock_data
        )
        remove_result = mock_client.projects.remove_data_flows_legacy(project_id, flows)
        assert len(remove_result) == 2
        mock_client.http_client.assert_request_made(
            "DELETE", f"/projects/{project_id}/data_flows"
        )

    def test_add_data_flows(self, mock_client):
        """Test adding data flows to a project."""
        # Arrange
        project_id = 123
        factory = MockDataFactory()
        mock_data = [factory.create_mock_project_data_flow() for _ in range(2)]
        mock_client.http_client.add_response(f"/projects/{project_id}/flows", mock_data)

        flows = ProjectFlowList(
            data_flows=[
                ProjectFlowIdentifier(data_source_id=456),
                ProjectFlowIdentifier(data_set_id=789),
            ]
        )

        # Act
        result = mock_client.projects.add_data_flows(project_id, flows)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(flow, ProjectDataFlow) for flow in result)
        mock_client.http_client.assert_request_made(
            "PUT", f"/projects/{project_id}/flows"
        )

    def test_replace_data_flows(self, mock_client):
        """Test replacing data flows in a project."""
        # Arrange
        project_id = 123
        factory = MockDataFactory()
        mock_data = [factory.create_mock_project_data_flow()]
        mock_client.http_client.add_response(f"/projects/{project_id}/flows", mock_data)

        flows = ProjectFlowList(data_flows=[ProjectFlowIdentifier(data_source_id=999)])

        # Act
        result = mock_client.projects.replace_data_flows(project_id, flows)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        mock_client.http_client.assert_request_made(
            "POST", f"/projects/{project_id}/flows"
        )

    def test_remove_data_flows(self, mock_client):
        """Test removing data flows from a project."""
        # Arrange
        project_id = 123
        factory = MockDataFactory()
        mock_data = [factory.create_mock_project_data_flow()]
        mock_client.http_client.add_response(f"/projects/{project_id}/flows", mock_data)

        flows = ProjectFlowList(data_flows=[ProjectFlowIdentifier(data_source_id=456)])

        # Act
        result = mock_client.projects.remove_data_flows(project_id, flows)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        mock_client.http_client.assert_request_made(
            "DELETE", f"/projects/{project_id}/flows"
        )

    def test_remove_all_data_flows(self, mock_client):
        """Test removing all data flows from a project."""
        # Arrange
        project_id = 123
        mock_client.http_client.add_response(f"/projects/{project_id}/flows", [])

        # Act
        result = mock_client.projects.remove_data_flows(project_id)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0
        mock_client.http_client.assert_request_made(
            "DELETE", f"/projects/{project_id}/flows"
        )

    def test_backward_compatibility_add_flows(self, mock_client):
        """Test backward compatibility add_flows method."""
        # Arrange
        project_id = 123
        factory = MockDataFactory()
        mock_data = [factory.create_mock_project_data_flow()]
        mock_client.http_client.add_response(f"/projects/{project_id}/flows", mock_data)

        flows = ProjectFlowList(data_flows=[ProjectFlowIdentifier(data_source_id=123)])

        # Act
        result = mock_client.projects.add_flows(project_id, flows)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        mock_client.http_client.assert_request_made(
            "PUT", f"/projects/{project_id}/flows"
        )

    def test_backward_compatibility_replace_flows(self, mock_client):
        """Test backward compatibility replace_flows method."""
        # Arrange
        project_id = 123
        factory = MockDataFactory()
        mock_data = [factory.create_mock_project_data_flow()]
        mock_client.http_client.add_response(f"/projects/{project_id}/flows", mock_data)

        flows = ProjectFlowList(data_flows=[ProjectFlowIdentifier(data_source_id=123)])

        # Act
        result = mock_client.projects.replace_flows(project_id, flows)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        mock_client.http_client.assert_request_made(
            "POST", f"/projects/{project_id}/flows"
        )

    def test_backward_compatibility_remove_flows(self, mock_client):
        """Test backward compatibility remove_flows method."""
        # Arrange
        project_id = 123
        factory = MockDataFactory()
        mock_data = [factory.create_mock_project_data_flow()]
        mock_client.http_client.add_response(f"/projects/{project_id}/flows", mock_data)

        flows = ProjectFlowList(data_flows=[ProjectFlowIdentifier(data_source_id=123)])

        # Act
        result = mock_client.projects.remove_flows(project_id, flows)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        mock_client.http_client.assert_request_made(
            "DELETE", f"/projects/{project_id}/flows"
        )

    def test_http_error_handling(self, mock_client):
        """Test HTTP error handling."""
        # Arrange
        mock_client.http_client.add_error(
            "/projects",
            HttpClientError(
                "Server Error",
                status_code=500,
                response={"message": "Internal server error"},
            ),
        )

        # Act & Assert
        with pytest.raises(ServerError) as exc_info:
            mock_client.projects.list()

        assert exc_info.value.status_code == 500

    def test_not_found_error_handling(self, mock_client):
        """Test not found error handling."""
        # Arrange
        project_id = 999
        mock_client.http_client.add_error(
            f"/projects/{project_id}",
            HttpClientError(
                "Project not found",
                status_code=404,
                response={"message": "Project not found"},
            ),
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            mock_client.projects.get(project_id)

    def test_validation_error_handling(self):
        """Test validation error handling."""
        # Act & Assert - Pydantic will raise validation error
        with pytest.raises(ValidationError):
            # Missing required 'name' field will fail validation
            ProjectCreate(description="Test")

    def test_empty_list_response(self, mock_client):
        """Test empty list response."""
        # Arrange
        mock_client.http_client.add_response("/projects", [])

        # Act
        projects = mock_client.projects.list()

        # Assert
        assert isinstance(projects, list)
        assert len(projects) == 0
