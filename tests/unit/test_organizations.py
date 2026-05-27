"""Unit tests for the Organizations resource."""

from nexla_sdk.models.metrics.enums import ResourceType
from nexla_sdk.models.organizations.requests import (
    OrganizationCreate,
    OrgMemberActivateDeactivateRequest,
    OrgMemberDelete,
    OrgMemberList,
    OrgMemberUpdate,
)
from tests.utils.assertions import NexlaAssertions
from tests.utils.mock_builders import MockResponseBuilder


class TestOrganizationsResource:
    """Test cases for the Organizations resource."""

    def test_list_organizations(self, mock_client, assertions: NexlaAssertions):
        """Test listing organizations."""
        # Arrange
        mock_orgs = [
            MockResponseBuilder.organization(org_id=1, name="Org 1"),
            MockResponseBuilder.organization(org_id=2, name="Org 2"),
        ]
        mock_client.http_client.add_response("/orgs", mock_orgs)

        # Act
        orgs = mock_client.organizations.list()

        # Assert
        assert len(orgs) == 2
        assert orgs[0].id == 1
        assert orgs[0].name == "Org 1"
        assert orgs[1].id == 2
        assert orgs[1].name == "Org 2"

    def test_get_organization(self, mock_client, assertions: NexlaAssertions):
        """Test getting a single organization."""
        # Arrange
        org_id = 123
        mock_response = MockResponseBuilder.organization(org_id=org_id, name="Test Org")
        mock_client.http_client.add_response(f"/orgs/{org_id}", mock_response)

        # Act
        org = mock_client.organizations.get(org_id)

        # Assert
        assert org.id == org_id
        assert org.name == "Test Org"
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/orgs/{org_id}" in last_request["url"]

    def test_create_organization(self, mock_client, assertions: NexlaAssertions):
        """Test creating an organization."""
        # Arrange
        create_data = OrganizationCreate(
            name="New Test Org",
            owner={"full_name": "Test Owner", "email": "owner@test.com"},
            email_domain="test.com",
        )
        mock_response = MockResponseBuilder.organization(
            name="New Test Org", org_id=123
        )
        mock_client.http_client.add_response("/orgs", mock_response)

        # Act
        org = mock_client.organizations.create(create_data)

        # Assert
        assert org.name == "New Test Org"
        assert org.id == 123
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "POST"
        assert "/orgs" in last_request["url"]
        assert last_request["json"] == create_data.model_dump(exclude_none=True)

    def test_update_organization(self, mock_client, assertions: NexlaAssertions):
        """Test updating an organization."""
        # Arrange
        org_id = 123
        update_data = {"name": "Updated Org Name"}
        mock_response = MockResponseBuilder.organization(
            org_id=org_id, name="Updated Org Name"
        )
        mock_client.http_client.add_response(f"/orgs/{org_id}", mock_response)

        # Act
        org = mock_client.organizations.update(org_id, update_data)

        # Assert
        assert org.id == org_id
        assert org.name == "Updated Org Name"
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "PUT"
        assert f"/orgs/{org_id}" in last_request["url"]
        assert last_request["json"] == update_data

    def test_get_members(self, mock_client, assertions: NexlaAssertions):
        """Test getting organization members."""
        # Arrange
        org_id = 123
        mock_members = [
            MockResponseBuilder.org_member(member_id=1, email="member1@test.com"),
            MockResponseBuilder.org_member(member_id=2, email="member2@test.com"),
        ]
        mock_client.http_client.add_response(f"/orgs/{org_id}/members", mock_members)

        # Act
        members = mock_client.organizations.get_members(org_id)

        # Assert
        assert len(members) == 2
        for member, mock_member in zip(members, mock_members):
            assertions.assert_org_member_response(member, mock_member)
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/orgs/{org_id}/members" in last_request["url"]

    def test_update_members(self, mock_client, assertions: NexlaAssertions):
        """Test updating organization members."""
        # Arrange
        org_id = 123
        update_list = OrgMemberList(
            members=[
                OrgMemberUpdate(
                    email="new.member@test.com", full_name="New Member", admin=False
                ),
                OrgMemberUpdate(id=1, admin=True),
            ]
        )
        mock_response = [
            MockResponseBuilder.org_member(member_id=1, is_admin=True),
            MockResponseBuilder.org_member(
                member_id=3, email="new.member@test.com", is_admin=False
            ),
        ]
        mock_client.http_client.add_response(f"/orgs/{org_id}/members", mock_response)

        # Act
        members = mock_client.organizations.update_members(org_id, update_list)

        # Assert
        assert len(members) == 2
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "PUT"
        assert f"/orgs/{org_id}/members" in last_request["url"]
        assert last_request["json"] == update_list.model_dump(exclude_none=True)

    def test_delete_members(self, mock_client):
        """Test deleting organization members."""
        # Arrange
        org_id = 123
        delete_list = OrgMemberDelete(members=[{"email": "member1@test.com"}])
        mock_client.http_client.add_response(
            f"/orgs/{org_id}/members", {"status": "success"}
        )

        # Act
        response = mock_client.organizations.delete_members(org_id, delete_list)

        # Assert
        assert response == {"status": "success"}
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "DELETE"
        assert f"/orgs/{org_id}/members" in last_request["url"]
        assert last_request["json"] == delete_list.model_dump(exclude_none=True)

    def test_deactivate_members(self, mock_client, assertions: NexlaAssertions):
        """Test deactivating organization members."""
        # Arrange
        org_id = 123
        deactivate_list = OrgMemberActivateDeactivateRequest(
            members=[{"email": "member1@test.com"}]
        )
        mock_response = [
            MockResponseBuilder.org_member(
                member_id=1,
                email="member1@test.com",
                org_membership_status="DEACTIVATED",
            )
        ]
        mock_client.http_client.add_response(
            f"/orgs/{org_id}/members/deactivate", mock_response
        )

        # Act
        members = mock_client.organizations.deactivate_members(org_id, deactivate_list)

        # Assert
        assert members[0].org_membership_status == "DEACTIVATED"
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "PUT"
        assert f"/orgs/{org_id}/members/deactivate" in last_request["url"]
        assert last_request["json"] == deactivate_list.model_dump(exclude_none=True)

    def test_activate_members(self, mock_client, assertions: NexlaAssertions):
        """Test activating organization members."""
        # Arrange
        org_id = 123
        activate_list = OrgMemberActivateDeactivateRequest(
            members=[{"email": "member1@test.com"}]
        )
        mock_response = [
            MockResponseBuilder.org_member(
                member_id=1, email="member1@test.com", org_membership_status="ACTIVE"
            )
        ]
        mock_client.http_client.add_response(
            f"/orgs/{org_id}/members/activate", mock_response
        )

        # Act
        members = mock_client.organizations.activate_members(org_id, activate_list)

        # Assert
        assert members[0].org_membership_status == "ACTIVE"
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "PUT"
        assert f"/orgs/{org_id}/members/activate" in last_request["url"]
        assert last_request["json"] == activate_list.model_dump(exclude_none=True)

    def test_get_account_summary(self, mock_client):
        """Test getting the account summary for an organization."""
        # Arrange
        org_id = 123
        mock_summary = MockResponseBuilder.account_summary(org_id=org_id)
        mock_client.http_client.add_response(
            f"/orgs/{org_id}/account_summary", mock_summary
        )

        # Act
        summary = mock_client.organizations.get_account_summary(org_id)

        # Assert
        assert summary.org_id == org_id
        assert "data_sources" in summary.model_dump()
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/orgs/{org_id}/account_summary" in last_request["url"]

    def test_get_current_account_summary(self, mock_client):
        """Test getting the account summary for the current organization."""
        # Arrange
        mock_summary = MockResponseBuilder.account_summary(org_id=1)
        mock_client.http_client.add_response("/orgs/account_summary", mock_summary)

        # Act
        summary = mock_client.organizations.get_current_account_summary()

        # Assert
        assert "data_sources" in summary.model_dump()
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert "/orgs/account_summary" in last_request["url"]

    def test_get_audit_log(self, mock_client):
        """Test getting the audit log for an organization."""
        # Arrange
        org_id = 123
        mock_log = [
            MockResponseBuilder.audit_log_entry(),
            MockResponseBuilder.audit_log_entry(),
        ]
        mock_client.http_client.add_response(f"/orgs/{org_id}/audit_log", mock_log)

        # Act
        audit_log = mock_client.organizations.get_audit_log(org_id, per_page=10)

        # Assert
        assert len(audit_log) == 2
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/orgs/{org_id}/audit_log" in last_request["url"]
        assert last_request["params"] == {"per_page": 10}

    def test_get_resource_audit_log(self, mock_client):
        """Test getting audit logs for a canonical resource type."""
        org_id = 123
        mock_log = [MockResponseBuilder.audit_log_entry()]
        mock_client.http_client.add_response(
            f"/orgs/{org_id}/data_sources/audit_log", mock_log
        )

        audit_log = mock_client.organizations.get_resource_audit_log(
            org_id, ResourceType.DATA_SOURCES, per_page=10
        )

        assert len(audit_log) == 1
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/orgs/{org_id}/data_sources/audit_log" in last_request["url"]
        assert last_request["params"] == {"per_page": 10}

    def test_get_flow_status_metrics_defaults(self, mock_client):
        """Defaults send no query params and hit /orgs/<id>/flows/status_metrics."""
        org_id = 123
        mock_client.http_client.add_response(
            f"/orgs/{org_id}/flows/status_metrics", {"total": 0}
        )

        result = mock_client.organizations.get_flow_status_metrics(org_id)

        assert result == {"total": 0}
        last_request = mock_client.http_client.get_last_request()
        assert last_request["method"] == "GET"
        assert f"/orgs/{org_id}/flows/status_metrics" in last_request["url"]
        assert last_request["params"] == {}

    def test_get_flow_status_metrics_with_access_role_and_kwargs(self, mock_client):
        """access_role and **kwargs are forwarded as query params."""
        org_id = 123
        mock_client.http_client.add_response(
            f"/orgs/{org_id}/flows/status_metrics", {"total": 7}
        )

        result = mock_client.organizations.get_flow_status_metrics(
            org_id,
            from_date="2026-01-01",
            page=2,
            per_page=50,
            access_role="collaborator",
            owner_id=99,
        )

        assert result == {"total": 7}
        last_request = mock_client.http_client.get_last_request()
        assert last_request["params"] == {
            "from": "2026-01-01",
            "page": 2,
            "per_page": 50,
            "access_role": "collaborator",
            "owner_id": 99,
        }
