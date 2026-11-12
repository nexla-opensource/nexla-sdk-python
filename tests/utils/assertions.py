"""Custom assertions for testing."""

from typing import Any, Dict, List, Optional, Type

from pydantic import ValidationError

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.common import FlowNode
from nexla_sdk.models.destinations.responses import (
    DataMapInfo,
    DataSetInfo,
    Destination,
)
from nexla_sdk.models.flows.responses import FlowMetrics, FlowResponse
from nexla_sdk.models.lookups.responses import Lookup
from nexla_sdk.models.nexsets.responses import Nexset
from nexla_sdk.models.organizations.responses import Organization, OrgMember
from nexla_sdk.models.projects.responses import Project, ProjectDataFlow
from nexla_sdk.models.sources.responses import Source


def assert_api_call_made(mock_http_client, method: str, url_pattern: str, **kwargs):
    """Assert that a specific API call was made."""
    mock_http_client.assert_request_made(method, url_pattern, **kwargs)


def assert_model_valid(
    model_instance: BaseModel, expected_fields: Optional[Dict[str, Any]] = None
):
    """Assert that a model instance is valid and optionally check specific fields."""
    # Check that it's a valid model instance
    assert isinstance(model_instance, BaseModel), (
        f"Expected BaseModel instance, got {type(model_instance)}"
    )

    # Check that required fields are present and have expected values
    if expected_fields:
        for field_name, expected_value in expected_fields.items():
            actual_value = getattr(model_instance, field_name, None)
            assert actual_value == expected_value, (
                f"Expected {field_name}={expected_value}, got {actual_value}"
            )

    # Ensure the model can be serialized (no validation errors)
    try:
        model_instance.model_dump()
    except Exception as e:
        raise AssertionError(f"Model serialization failed: {e}")


def assert_model_list_valid(model_list: List[BaseModel], model_class: Type[BaseModel]):
    """Assert that a list contains valid model instances of the expected type."""
    assert isinstance(model_list, list), f"Expected list, got {type(model_list)}"

    for i, item in enumerate(model_list):
        assert isinstance(item, model_class), (
            f"Item {i} is not of type {model_class.__name__}: {type(item)}"
        )
        assert_model_valid(item)


def assert_validation_error(func, error_message_contains: Optional[str] = None):
    """Assert that calling func raises a ValidationError with optional message check."""
    try:
        func()
        raise AssertionError("Expected ValidationError to be raised")
    except ValidationError as e:
        if error_message_contains:
            assert error_message_contains in str(e), (
                f"Error message should contain '{error_message_contains}': {e}"
            )
    except Exception as e:
        raise AssertionError(f"Expected ValidationError, got {type(e).__name__}: {e}")


def assert_credential_structure(credential_data: Dict[str, Any]):
    """Assert that credential data has the expected structure from API documentation."""
    # Required fields
    required_fields = ["id", "name", "credentials_type", "owner", "org", "access_roles"]
    for field in required_fields:
        assert field in credential_data, f"Credential missing required field: {field}"

    # Check owner structure
    owner = credential_data["owner"]
    assert "id" in owner and "full_name" in owner, "Owner missing required fields"

    # Check org structure
    org = credential_data["org"]
    assert "id" in org and "name" in org, "Organization missing required fields"

    # Check access roles
    assert isinstance(credential_data["access_roles"], list), (
        "access_roles should be a list"
    )
    assert len(credential_data["access_roles"]) > 0, "access_roles should not be empty"


def assert_source_structure(source_data: Dict[str, Any]):
    """Assert that source data has the expected structure from API documentation."""
    # Required fields
    required_fields = ["id", "name", "status", "source_type", "access_roles"]
    for field in required_fields:
        assert field in source_data, f"Source missing required field: {field}"

    # Check valid status values
    valid_statuses = ["ACTIVE", "PAUSED", "DRAFT", "DELETED", "ERROR", "INIT"]
    assert source_data["status"] in valid_statuses, (
        f"Invalid status: {source_data['status']}"
    )

    # Check owner structure if present
    if "owner" in source_data and source_data["owner"]:
        owner = source_data["owner"]
        assert "id" in owner and "full_name" in owner, "Owner missing required fields"

    # Check org structure if present
    if "org" in source_data and source_data["org"]:
        org = source_data["org"]
        assert "id" in org and "name" in org, "Organization missing required fields"

    # Check access roles
    assert isinstance(source_data["access_roles"], list), (
        "access_roles should be a list"
    )

    # Check data_sets if present
    if "data_sets" in source_data and source_data["data_sets"]:
        assert isinstance(source_data["data_sets"], list), "data_sets should be a list"
        for dataset in source_data["data_sets"]:
            assert "id" in dataset, "Dataset missing required id field"

    # Check data_credentials if present
    if "data_credentials" in source_data and source_data["data_credentials"]:
        assert_credential_structure(source_data["data_credentials"])


def assert_destination_structure(destination_data: Dict[str, Any]):
    """Assert that destination data has the expected structure."""
    # Required fields
    required_fields = ["id", "name", "status", "sink_type", "access_roles"]
    for field in required_fields:
        assert field in destination_data, f"Destination missing required field: {field}"

    # Check valid status values
    valid_statuses = ["ACTIVE", "PAUSED", "DRAFT", "DELETED", "ERROR"]
    assert destination_data["status"] in valid_statuses, (
        f"Invalid status: {destination_data['status']}"
    )

    # Check owner structure if present
    if "owner" in destination_data and destination_data["owner"]:
        owner = destination_data["owner"]
        assert "id" in owner and "full_name" in owner, "Owner missing required fields"

    # Check org structure if present
    if "org" in destination_data and destination_data["org"]:
        org = destination_data["org"]
        assert "id" in org and "name" in org, "Organization missing required fields"


def assert_nexset_structure(nexset_data: Dict[str, Any]):
    """Assert that nexset data has the expected structure."""
    # Required fields
    required_fields = ["id", "access_roles"]
    for field in required_fields:
        assert field in nexset_data, f"Nexset missing required field: {field}"

    # Check owner structure if present
    if "owner" in nexset_data and nexset_data["owner"]:
        owner = nexset_data["owner"]
        assert "id" in owner and "full_name" in owner, "Owner missing required fields"

    # Check data_sinks if present
    if "data_sinks" in nexset_data and nexset_data["data_sinks"]:
        assert isinstance(nexset_data["data_sinks"], list), (
            "data_sinks should be a list"
        )


def assert_lookup_structure(lookup_data: Dict[str, Any]):
    """Assert that lookup data has the expected structure."""
    # Required fields
    required_fields = [
        "id",
        "name",
        "description",
        "map_primary_key",
        "owner",
        "org",
        "access_roles",
    ]
    for field in required_fields:
        assert field in lookup_data, f"Lookup missing required field: {field}"

    # Check owner structure
    owner = lookup_data["owner"]
    assert "id" in owner and "full_name" in owner, "Owner missing required fields"

    # Check org structure
    org = lookup_data["org"]
    assert "id" in org and "name" in org, "Organization missing required fields"


def assert_user_structure(user_data: Dict[str, Any]):
    """Assert that user data has the expected structure."""
    # Required fields
    required_fields = ["id", "email", "full_name", "default_org", "status"]
    for field in required_fields:
        assert field in user_data, f"User missing required field: {field}"

    # Check default_org structure
    default_org = user_data["default_org"]
    assert "id" in default_org and "name" in default_org, (
        "Default org missing required fields"
    )

    # Check org_memberships if present
    if "org_memberships" in user_data:
        assert isinstance(user_data["org_memberships"], list), (
            "org_memberships should be a list"
        )


def assert_organization_structure(org_data: Dict[str, Any]):
    """Assert that organization data has the expected structure."""
    # Required fields
    required_fields = ["id", "name", "email_domain", "access_roles", "owner", "status"]
    for field in required_fields:
        assert field in org_data, f"Organization missing required field: {field}"

    # Check owner structure
    owner = org_data["owner"]
    assert_user_structure(owner)


def assert_team_structure(team_data: Dict[str, Any]):
    """Assert that team data has the expected structure."""
    # Required fields
    required_fields = ["id", "name", "description", "owner", "org", "access_roles"]
    for field in required_fields:
        assert field in team_data, f"Team missing required field: {field}"

    # Check owner structure
    owner = team_data["owner"]
    assert "id" in owner and "full_name" in owner, "Owner missing required fields"

    # Check members if present
    if "members" in team_data:
        assert isinstance(team_data["members"], list), "members should be a list"


def assert_project_structure(project_data: Dict[str, Any]):
    """Assert that project data has the expected structure."""
    # Required fields
    required_fields = ["id", "owner", "org", "name", "description", "access_roles"]
    for field in required_fields:
        assert field in project_data, f"Project missing required field: {field}"

    # Check data_flows if present
    if "data_flows" in project_data:
        assert isinstance(project_data["data_flows"], list), (
            "data_flows should be a list"
        )

    # Check flows if present
    if "flows" in project_data:
        assert isinstance(project_data["flows"], list), "flows should be a list"


def assert_notification_structure(notification_data: Dict[str, Any]):
    """Assert that notification data has the expected structure."""
    # Required fields
    required_fields = [
        "id",
        "owner",
        "org",
        "access_roles",
        "level",
        "resource_id",
        "resource_type",
        "message",
    ]
    for field in required_fields:
        assert field in notification_data, (
            f"Notification missing required field: {field}"
        )

    # Check valid levels
    valid_levels = ["DEBUG", "INFO", "WARN", "ERROR", "RECOVERED", "RESOLVED"]
    assert notification_data["level"] in valid_levels, (
        f"Invalid level: {notification_data['level']}"
    )


def assert_probe_response_structure(probe_data: Dict[str, Any]):
    """Assert that probe response has the expected structure."""
    required_fields = ["status", "message", "connection_type"]
    for field in required_fields:
        assert field in probe_data, f"Probe response missing required field: {field}"

    assert probe_data["status"] in [
        "ok",
        "success",
        "error",
    ], f"Invalid probe status: {probe_data['status']}"


def assert_error_response_structure(error_data: Dict[str, Any]):
    """Assert that error response has the expected structure."""
    # Should have either 'error' or 'message' field
    assert "error" in error_data or "message" in error_data, (
        "Error response missing error/message field"
    )

    # Should have some indication of the error type or status
    if "status_code" in error_data:
        assert isinstance(error_data["status_code"], int), (
            "status_code should be an integer"
        )


def assert_paginated_response_structure(response_data: Dict[str, Any]):
    """Assert that paginated response has the expected structure."""
    if "meta" in response_data:
        meta = response_data["meta"]
        assert "currentPage" in meta, "Pagination meta missing currentPage"
        assert "totalCount" in meta, "Pagination meta missing totalCount"
        assert "pageCount" in meta, "Pagination meta missing pageCount"

    if "data" in response_data:
        assert isinstance(response_data["data"], list), (
            "Paginated data should be a list"
        )


def assert_metrics_response_structure(metrics_data: Dict[str, Any]):
    """Assert that metrics response has the expected structure."""
    assert "status" in metrics_data, "Metrics response missing status field"
    assert "metrics" in metrics_data, "Metrics response missing metrics field"

    if metrics_data["status"] == 200:
        metrics = metrics_data["metrics"]
        if isinstance(metrics, dict):
            # Single metrics object
            assert "records" in metrics or "size" in metrics, (
                "Metrics should have records or size"
            )
        elif isinstance(metrics, list):
            # List of metrics (e.g., daily metrics)
            for metric in metrics:
                assert isinstance(metric, dict), "Each metric should be a dictionary"


def assert_flow_response_structure(flow_data: Dict[str, Any]):
    """Assert that flow response has the expected structure."""
    assert "flows" in flow_data, "Flow response missing flows field"
    assert isinstance(flow_data["flows"], list), "flows should be a list"

    # Check optional elements
    optional_lists = ["data_sources", "data_sets", "data_sinks", "data_credentials"]
    for field in optional_lists:
        if field in flow_data:
            assert isinstance(flow_data[field], list), f"{field} should be a list"


def assert_datetime_field_valid(
    data: Dict[str, Any], field_name: str, required: bool = False
):
    """Assert that a datetime field is valid if present."""
    if field_name in data:
        datetime_value = data[field_name]
        if datetime_value is not None:
            # Should be a string in ISO format or None
            assert isinstance(datetime_value, str), f"{field_name} should be a string"
            # Basic check for ISO format (contains T and ends with Z or has timezone)
            assert "T" in datetime_value, f"{field_name} should be in ISO format"
    elif required:
        raise AssertionError(f"Required datetime field {field_name} is missing")


def assert_list_field_valid(
    data: Dict[str, Any], field_name: str, required: bool = False, min_length: int = 0
):
    """Assert that a list field is valid if present."""
    if field_name in data:
        list_value = data[field_name]
        if list_value is not None:
            assert isinstance(list_value, list), f"{field_name} should be a list"
            assert len(list_value) >= min_length, (
                f"{field_name} should have at least {min_length} items"
            )
    elif required:
        raise AssertionError(f"Required list field {field_name} is missing")


class NexlaAssertions:
    @staticmethod
    def assert_owner_response(actual, expected: Dict[str, Any]) -> None:
        """Assert owner response matches expected data."""
        assert actual.id == expected["id"]
        assert actual.full_name == expected["full_name"]
        assert actual.email == expected["email"]

    @staticmethod
    def assert_source_response(response: Source, expected_data: Dict[str, Any]):
        """Assert source response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.name == expected_data["name"]
        assert response.status == expected_data["status"]
        assert response.source_type == expected_data["source_type"]
        if "owner" in expected_data:
            assert response.owner.id == expected_data["owner"]["id"]
            assert response.owner.email == expected_data["owner"]["email"]
        if "org" in expected_data:
            assert response.org.id == expected_data["org"]["id"]
            assert response.org.name == expected_data["org"]["name"]

    @staticmethod
    def assert_credential_response(actual, expected: Dict[str, Any]) -> None:
        """Assert credential response matches expected data."""
        assert actual.id == expected["id"]
        assert actual.name == expected["name"]
        assert actual.credentials_type == expected["credentials_type"]

        if expected.get("owner"):
            NexlaAssertions.assert_owner_response(actual.owner, expected["owner"])

        if expected.get("org"):
            NexlaAssertions.assert_organization_response(actual.org, expected["org"])

    @staticmethod
    def assert_destination_response(
        response: Destination, expected_data: Dict[str, Any]
    ):
        """Assert destination response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.name == expected_data["name"]
        if "status" in expected_data:
            assert response.status == expected_data["status"]
        if "sink_type" in expected_data:
            assert response.sink_type == expected_data["sink_type"]
        if "owner" in expected_data:
            assert response.owner.id == expected_data["owner"]["id"]
            assert response.owner.email == expected_data["owner"]["email"]
        if "org" in expected_data:
            assert response.org.id == expected_data["org"]["id"]
            assert response.org.name == expected_data["org"]["name"]

    @staticmethod
    def assert_flow_node(actual: FlowNode, expected: Dict[str, Any]) -> None:
        """Assert flow node matches expected data."""
        assert actual.id == expected["id"]

        # Check parent/source relationships
        if "parent_node_id" in expected:
            assert actual.parent_node_id == expected.get("parent_node_id")
        if "data_source_id" in expected:
            assert actual.data_source_id == expected.get("data_source_id")
        if "data_set_id" in expected:
            assert actual.data_set_id == expected.get("data_set_id")
        if "data_sink_id" in expected:
            assert actual.data_sink_id == expected.get("data_sink_id")

        # Check optional fields
        if expected.get("status"):
            assert actual.status == expected["status"]
        if expected.get("name"):
            assert actual.name == expected["name"]
        if expected.get("description"):
            assert actual.description == expected["description"]

        # Recursively check children if present
        if expected.get("children") and actual.children:
            assert len(actual.children) == len(expected["children"])
            for actual_child, expected_child in zip(
                actual.children, expected["children"]
            ):
                NexlaAssertions.assert_flow_node(actual_child, expected_child)

    @staticmethod
    def assert_flow_response(actual: FlowResponse, expected: Dict[str, Any]) -> None:
        """Assert flow response matches expected data."""
        # Check flows array
        assert len(actual.flows) == len(expected["flows"])
        for actual_flow, expected_flow in zip(actual.flows, expected["flows"]):
            NexlaAssertions.assert_flow_node(actual_flow, expected_flow)

        # Check optional expanded elements
        if expected.get("data_sources") and actual.data_sources:
            assert len(actual.data_sources) == len(expected["data_sources"])
            for actual_src, expected_src in zip(
                actual.data_sources, expected["data_sources"]
            ):
                NexlaAssertions.assert_source_response(actual_src, expected_src)

        if expected.get("data_sets") and actual.data_sets:
            assert len(actual.data_sets) == len(expected["data_sets"])
            # Note: Would need assert_nexset_response method if checking details

        if expected.get("data_sinks") and actual.data_sinks:
            assert len(actual.data_sinks) == len(expected["data_sinks"])
            for actual_sink, expected_sink in zip(
                actual.data_sinks, expected["data_sinks"]
            ):
                NexlaAssertions.assert_destination_response(actual_sink, expected_sink)

        if expected.get("data_credentials") and actual.data_credentials:
            assert len(actual.data_credentials) == len(expected["data_credentials"])
            for actual_cred, expected_cred in zip(
                actual.data_credentials, expected["data_credentials"]
            ):
                NexlaAssertions.assert_credential_response(actual_cred, expected_cred)

    @staticmethod
    def assert_flow_metrics(actual: FlowMetrics, expected: Dict[str, Any]) -> None:
        """Assert flow metrics match expected data."""
        assert actual.origin_node_id == expected["origin_node_id"]
        assert actual.records == expected["records"]
        assert actual.size == expected["size"]
        assert actual.errors == expected["errors"]
        assert actual.run_id == expected["run_id"]

    @staticmethod
    def assert_lookup_response(response: Lookup, expected_data: Dict[str, Any]):
        """Assert lookup response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.name == expected_data["name"]
        if "description" in expected_data:
            assert response.description == expected_data["description"]
        if "map_primary_key" in expected_data:
            assert response.map_primary_key == expected_data["map_primary_key"]
        if "data_type" in expected_data:
            assert response.data_type == expected_data["data_type"]
        if "public" in expected_data:
            assert response.public == expected_data["public"]
        if "owner" in expected_data:
            assert response.owner.id == expected_data["owner"]["id"]
            assert response.owner.email == expected_data["owner"]["email"]
        if "org" in expected_data:
            assert response.org.id == expected_data["org"]["id"]
            assert response.org.name == expected_data["org"]["name"]

    @staticmethod
    def assert_lookup_entry(entry: Dict[str, Any], expected_data: Dict[str, Any]):
        """Assert lookup entry matches expected data."""
        for key, value in expected_data.items():
            assert entry[key] == value

    def assert_nexset_response(self, response: Nexset, expected_data: Dict[str, Any]):
        """Assert nexset response matches expected data."""
        assert response.id == expected_data["id"]
        if "name" in expected_data:
            assert response.name == expected_data["name"]
        if "description" in expected_data:
            assert response.description == expected_data["description"]
        if "status" in expected_data:
            assert response.status == expected_data["status"]
        if "owner" in expected_data:
            assert response.owner.id == expected_data["owner"]["id"]
            assert response.owner.email == expected_data["owner"]["email"]
        if "org" in expected_data:
            assert response.org.id == expected_data["org"]["id"]
            assert response.org.name == expected_data["org"]["name"]

    def assert_nexset_sample(self, sample):
        """Assert nexset sample has expected structure."""
        assert hasattr(sample, "raw_message"), "Sample should have raw_message"
        assert isinstance(sample.raw_message, dict), "Sample raw_message should be dict"

        # If metadata exists, validate it
        if hasattr(sample, "nexla_metadata") and sample.nexla_metadata:
            assert isinstance(sample.nexla_metadata, dict), (
                "Sample nexla_metadata should be dict"
            )

    def assert_data_set_info_response(
        self, response: DataSetInfo, expected_data: Dict[str, Any]
    ):
        """Assert data set info response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.name == expected_data["name"]
        if "description" in expected_data:
            assert response.description == expected_data["description"]
        if "status" in expected_data:
            assert response.status == expected_data["status"]

    def assert_data_map_info_response(
        self, response: DataMapInfo, expected_data: Dict[str, Any]
    ):
        """Assert data map info response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.name == expected_data["name"]
        assert response.description == expected_data["description"]
        assert response.public == expected_data["public"]
        assert response.owner_id == expected_data["owner_id"]
        assert response.org_id == expected_data["org_id"]

    @staticmethod
    def assert_project_response(response: Project, expected_data: Dict[str, Any]):
        """Assert project response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.name == expected_data["name"]
        assert response.description == expected_data["description"]
        if "owner" in expected_data:
            assert response.owner.id == expected_data["owner"]["id"]
            assert response.owner.email == expected_data["owner"]["email"]
        if "org" in expected_data:
            assert response.org.id == expected_data["org"]["id"]
            assert response.org.name == expected_data["org"]["name"]
        if "client_identifier" in expected_data:
            assert response.client_identifier == expected_data["client_identifier"]
        if "client_url" in expected_data:
            assert response.client_url == expected_data["client_url"]
        if "flows_count" in expected_data:
            assert response.flows_count == expected_data["flows_count"]
        if "access_roles" in expected_data:
            assert response.access_roles == expected_data["access_roles"]
        if "tags" in expected_data:
            assert response.tags == expected_data["tags"]

    @staticmethod
    def assert_user_response(response, expected_data: Dict[str, Any]):
        """Assert user response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.email == expected_data["email"]
        assert response.full_name == expected_data["full_name"]
        if "super_user" in expected_data:
            assert response.super_user == expected_data["super_user"]
        if "impersonated" in expected_data:
            assert response.impersonated == expected_data["impersonated"]
        if "default_org" in expected_data:
            assert response.default_org.id == expected_data["default_org"]["id"]
            assert response.default_org.name == expected_data["default_org"]["name"]
        if "user_tier" in expected_data:
            assert response.user_tier == expected_data["user_tier"]
        if "status" in expected_data:
            assert response.status == expected_data["status"]
        if "api_key" in expected_data:
            assert response.api_key == expected_data["api_key"]
        if "org_memberships" in expected_data:
            assert len(response.org_memberships) == len(
                expected_data["org_memberships"]
            )

    @staticmethod
    def assert_team_response(response, expected_data: Dict[str, Any]):
        """Assert team response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.name == expected_data["name"]
        if "description" in expected_data:
            assert response.description == expected_data["description"]
        if "owner" in expected_data:
            assert response.owner.id == expected_data["owner"]["id"]
            assert response.owner.email == expected_data["owner"]["email"]
        if "org" in expected_data:
            assert response.org.id == expected_data["org"]["id"]
            assert response.org.name == expected_data["org"]["name"]
        if "member" in expected_data:
            assert response.member == expected_data["member"]
        if "access_roles" in expected_data:
            assert response.access_roles == expected_data["access_roles"]
        if "members" in expected_data:
            assert len(response.members) == len(expected_data["members"])

    @staticmethod
    def assert_team_member_response(response, expected_data: Dict[str, Any]):
        """Assert team member response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.email == expected_data["email"]
        if "admin" in expected_data:
            assert response.admin == expected_data["admin"]

    @staticmethod
    def assert_project_data_flow_response(
        response: ProjectDataFlow, expected_data: Dict[str, Any]
    ):
        """Assert project data flow response matches expected data."""
        assert response.id == expected_data["id"]
        assert response.project_id == expected_data["project_id"]
        if "data_source_id" in expected_data:
            assert response.data_source_id == expected_data["data_source_id"]
        if "data_set_id" in expected_data:
            assert response.data_set_id == expected_data["data_set_id"]
        if "data_sink_id" in expected_data:
            assert response.data_sink_id == expected_data["data_sink_id"]
        if "name" in expected_data:
            assert response.name == expected_data["name"]
        if "description" in expected_data:
            assert response.description == expected_data["description"]

    @staticmethod
    def assert_organization_response(
        response: Organization, expected_data: Dict[str, Any]
    ):
        """Assert organization response matches expected data."""
        assert isinstance(response, Organization)
        for key, expected_value in expected_data.items():
            if key == "account_tier" and response.org_tier:
                # Special handling for nested model
                for k, v in expected_value.items():
                    assert getattr(response.org_tier, k) == v
            elif hasattr(response, key):
                assert getattr(response, key) == expected_value

    @staticmethod
    def assert_org_member_response(response: OrgMember, expected_data: Dict[str, Any]):
        """Assert org member response matches expected data."""
        assert isinstance(response, OrgMember)
        assert response.id == expected_data.get("id")
        assert response.email == expected_data.get("email")
        assert response.is_admin == expected_data.get("is_admin?")
