from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.common import LogEntry
from nexla_sdk.models.metrics.enums import ResourceType
from nexla_sdk.models.organizations.custodians import OrgCustodiansPayload
from nexla_sdk.models.organizations.requests import (
    OrganizationCreate,
    OrganizationUpdate,
    OrgMemberActivateDeactivateRequest,
    OrgMemberDelete,
    OrgMemberList,
)
from nexla_sdk.models.organizations.responses import (
    AccountSummary,
    CustodianUser,
    Organization,
    OrgMember,
)
from nexla_sdk.resources.base_resource import BaseResource


class OrganizationsResource(BaseResource):
    """Resource for managing organizations."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/orgs"
        self._model_class = Organization

    def list(self, **kwargs) -> List[Organization]:
        """
        List organizations with optional filters.

        Args:
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of organizations

        Examples:
            client.organizations.list(page=1, per_page=25)
        """
        return super().list(**kwargs)

    def list_all(self, **params) -> List[Organization]:
        response = self._make_request("GET", f"{self._path}/all", params=params)
        return self._parse_response(response)

    def get(self, org_id: int, expand: bool = False) -> Organization:
        """
        Get single organization by ID.

        Args:
            org_id: Organization ID
            expand: Include expanded references

        Returns:
            Organization instance
        """
        return super().get(org_id, expand)

    def create(self, data: OrganizationCreate) -> Organization:
        """
        Create a new organization. Note: This is an admin-only operation.

        Args:
            data: Organization creation data

        Returns:
            Created organization
        """
        return super().create(data)

    def update(self, org_id: int, data: OrganizationUpdate) -> Organization:
        """
        Update organization.

        Args:
            org_id: Organization ID
            data: Updated organization data

        Returns:
            Updated organization
        """
        return super().update(org_id, data)

    def delete(self, org_id: int) -> Dict[str, Any]:
        """
        Delete organization.

        Args:
            org_id: Organization ID

        Returns:
            Response with status
        """
        return super().delete(org_id)

    def get_login_history(self, org_id: int, **params) -> List[Dict[str, Any]]:
        path = f"{self._path}/{org_id}/login_history"
        response = self._make_request("GET", path, params=params)
        return response or []

    def get_metrics(
        self, org_id: int, metrics_name: Optional[str] = None, **params
    ) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/metrics"
        if metrics_name:
            path = f"{path}/{metrics_name}"
        return self._make_request("GET", path, params=params)

    def get_members(self, org_id: int) -> List[OrgMember]:
        """
        Get all members in organization.

        Args:
            org_id: Organization ID

        Returns:
            List of organization members
        """
        path = f"{self._path}/{org_id}/members"
        response = self._make_request("GET", path)
        return [OrgMember(**member) for member in response]

    def update_members(self, org_id: int, members: OrgMemberList) -> List[OrgMember]:
        """
        Add or update members in organization.

        Args:
            org_id: Organization ID
            members: Members to add/update

        Returns:
            Updated member list
        """
        path = f"{self._path}/{org_id}/members"
        response = self._make_request("PUT", path, json=members.to_dict())
        return [OrgMember(**member) for member in response]

    def replace_members(self, org_id: int, members: OrgMemberList) -> List[OrgMember]:
        """
        Replace all members in organization.

        Args:
            org_id: Organization ID
            members: New member list

        Returns:
            New member list
        """
        path = f"{self._path}/{org_id}/members"
        response = self._make_request("POST", path, json=members.to_dict())
        return [OrgMember(**member) for member in response]

    def delete_members(self, org_id: int, members: OrgMemberDelete) -> Dict[str, Any]:
        """
        Remove members from organization.

        Args:
            org_id: Organization ID
            members: Members to remove

        Returns:
            Response status
        """
        path = f"{self._path}/{org_id}/members"
        return self._make_request("DELETE", path, json=members.to_dict())

    def deactivate_members(
        self, org_id: int, members: OrgMemberActivateDeactivateRequest
    ) -> List[OrgMember]:
        """
        Deactivate members in an organization.

        Args:
            org_id: Organization ID
            members: Members to deactivate

        Returns:
            Updated list of members
        """
        path = f"{self._path}/{org_id}/members/deactivate"
        response = self._make_request("PUT", path, json=members.to_dict())
        return [OrgMember(**member) for member in response]

    def activate_members(
        self, org_id: int, members: OrgMemberActivateDeactivateRequest
    ) -> List[OrgMember]:
        """
        Activate members in an organization.

        Args:
            org_id: Organization ID
            members: Members to activate

        Returns:
            Updated list of members
        """
        path = f"{self._path}/{org_id}/members/activate"
        response = self._make_request("PUT", path, json=members.to_dict())
        return [OrgMember(**member) for member in response]

    def get_account_summary(self, org_id: int) -> AccountSummary:
        """
        Get account summary statistics for an organization.

        Args:
            org_id: Organization ID

        Returns:
            Account summary
        """
        path = f"{self._path}/{org_id}/account_summary"
        response = self._make_request("GET", path)
        return AccountSummary.model_validate(response)

    def get_current_account_summary(self) -> AccountSummary:
        """
        Get account summary for the current organization based on auth token.

        Returns:
            Account summary
        """
        path = f"{self._path}/account_summary"
        response = self._make_request("GET", path)
        return AccountSummary.model_validate(response)

    def get_account_rate_limited(self, org_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/account_rate_limited"
        return self._make_request("GET", path)

    def activate_rate_limited_sources(
        self, org_id: int, status: Optional[str] = None, activate: bool = True
    ) -> Dict[str, Any]:
        action = "source_activate" if activate else "source_pause"
        path = f"{self._path}/{org_id}/{action}"
        if status:
            path = f"{path}/{status}"
        return self._make_request("PUT", path)

    def activate_org(self, org_id: int, activate: bool = True) -> Dict[str, Any]:
        path = (
            f"{self._path}/{org_id}/activate"
            if activate
            else f"{self._path}/{org_id}/deactivate"
        )
        return self._make_request("PUT", path)

    def set_rate_limits(self, org_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/rate_limits"
        return self._make_request("PUT", path, json=payload)

    def throttle(self, org_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/throttle"
        return self._make_request("PUT", path, json=payload)

    def get_flows_report(self, org_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/flows_report"
        return self._make_request("GET", path, params=params)

    def get_clusters(self, org_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/clusters"
        return self._make_request("GET", path, params=params)

    def update_cluster(self, org_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/cluster"
        return self._make_request("PUT", path, json=payload)

    def activate_cluster(self, org_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/cluster/activate"
        return self._make_request("PUT", path)

    def revert_cluster(self, org_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/cluster/revert"
        return self._make_request("PUT", path)

    def list_notification_settings(self, org_id: int, **params) -> List[Dict[str, Any]]:
        path = f"{self._path}/{org_id}/notification_settings"
        return self._make_request("GET", path, params=params) or []

    def create_notification_settings(self, org_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/notification_settings"
        return self._make_request("POST", path, json=payload)

    def update_notification_settings(
        self, org_id: int, notification_settings_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/notification_settings/{notification_settings_id}"
        return self._make_request("PUT", path, json=payload)

    def delete_notification_settings(self, org_id: int, notification_settings_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/notification_settings/{notification_settings_id}"
        return self._make_request("DELETE", path)

    def list_data_sets_catalog_configs(self, org_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/data_sets_catalog_configs"
        return self._make_request("GET", path, params=params)

    def get_data_sets_catalog_config(self, config_id: int) -> Dict[str, Any]:
        path = f"{self._path}/data_sets_catalog_configs/{config_id}"
        return self._make_request("GET", path)

    def enable_feature(self, org_id: int, feature_name: str) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/features/{feature_name}/enable"
        return self._make_request("PUT", path)

    def disable_feature(self, org_id: int, feature_name: str) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/features/{feature_name}/disable"
        return self._make_request("PUT", path)

    def get_org_flow_account_metrics(
        self, org_id: int, from_date: str, to_date: str = None, aggregate: str = None
    ) -> Dict[str, Any]:
        """Get total account metrics for an organization (flows)."""
        path = f"{self._path}/{org_id}/flows/account_metrics"
        params = {"from": from_date}
        if to_date:
            params["to"] = to_date
        if aggregate:
            params["aggregate"] = aggregate
        return self._make_request("GET", path, params=params)

    def get_dashboard_transforms(self, org_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/dashboard_transforms"
        return self._make_request("GET", path)

    def create_dashboard_transforms(self, org_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/dashboard_transforms"
        return self._make_request("POST", path, json=payload)

    def update_dashboard_transforms(self, org_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/dashboard_transforms"
        return self._make_request("PUT", path, json=payload)

    def delete_dashboard_transforms(self, org_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/dashboard_transforms"
        return self._make_request("DELETE", path)

    def get_flows_dashboard(self, org_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/flows/dashboard"
        return self._make_request("GET", path, params=params)

    def get_flows_status_metrics(self, org_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/flows/status_metrics"
        return self._make_request("GET", path, params=params)

    def get_flows_account_metrics(self, org_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/flows/account_metrics"
        return self._make_request("GET", path, params=params)

    def get_audit_log(
        self,
        org_id: int,
        from_date: str = None,
        to_date: str = None,
        event_filter: str = None,
        change_filter: str = None,
        page: int = None,
        per_page: int = None,
    ) -> List[LogEntry]:
        """
        Get audit log for an organization.

        Args:
            org_id: Organization ID
            from_date: Start date filter (YYYY-MM-DD)
            to_date: End date filter (YYYY-MM-DD)
            event_filter: Filter by event type
            change_filter: Filter by change type
            page: Page number for pagination
            per_page: Items per page

        Returns:
            List of audit log entries
        """
        path = f"{self._path}/{org_id}/audit_log"
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        if event_filter is not None:
            params["event_filter"] = event_filter
        if change_filter is not None:
            params["change_filter"] = change_filter
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        response = self._make_request("GET", path, params=params)
        return [LogEntry.model_validate(item) for item in response]

    def get_flow_status_metrics(
        self, org_id: int, from_date: str = None, page: int = None, per_page: int = None
    ) -> Dict[str, Any]:
        """
        Get flow status metrics for an organization.

        Args:
            org_id: Organization ID
            from_date: Start date filter (YYYY-MM-DD)
            page: Page number for pagination
            per_page: Items per page

        Returns:
            Flow status metrics
        """
        path = f"{self._path}/{org_id}/flows/status_metrics"
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self._make_request("GET", path, params=params)

    def get_resource_audit_log(
        self, org_id: int, resource_type: Union[ResourceType, str], **params
    ) -> List[LogEntry]:
        """
        Get audit log for a specific resource type within an organization.

        Args:
            org_id: Organization ID
            resource_type: ResourceType or exact string value
                ("data_sources", "data_sets", "data_sinks").
            **params: Additional query parameters

        Returns:
            List of audit log entries
        """
        resource_type_value = self._resolve_enum_value(
            ResourceType, resource_type, "resource_type"
        )
        path = f"{self._path}/{org_id}/{resource_type_value}/audit_log"
        response = self._make_request("GET", path, params=params)
        return [LogEntry.model_validate(item) for item in response]

    def get_auth_settings(self, org_id: int) -> List[Dict[str, Any]]:
        """
        Get authentication settings for organization.

        Args:
            org_id: Organization ID

        Returns:
            List of auth settings
        """
        path = f"{self._path}/{org_id}/auth_settings"
        return self._make_request("GET", path)

    def update_auth_setting(
        self, org_id: int, auth_setting_id: int, enabled: bool
    ) -> Dict[str, Any]:
        """
        Enable/disable authentication configuration.

        Args:
            org_id: Organization ID
            auth_setting_id: Auth setting ID
            enabled: Whether to enable

        Returns:
            Updated auth setting
        """
        path = f"{self._path}/{org_id}/auth_settings/{auth_setting_id}"
        data = {"enabled": enabled}
        return self._make_request("PUT", path, json=data)

    # Org custodians
    def get_custodians(self, org_id: int) -> List[CustodianUser]:
        path = f"{self._path}/{org_id}/custodians"
        response = self._make_request("GET", path)
        if isinstance(response, list):
            return [CustodianUser.model_validate(item) for item in response]
        return []

    def update_custodians(
        self, org_id: int, payload: OrgCustodiansPayload
    ) -> List[CustodianUser]:
        path = f"{self._path}/{org_id}/custodians"
        data = self._serialize_data(payload)
        response = self._make_request("PUT", path, json=data)
        if isinstance(response, list):
            return [CustodianUser.model_validate(item) for item in response]
        return []

    def add_custodians(
        self, org_id: int, payload: OrgCustodiansPayload
    ) -> List[CustodianUser]:
        path = f"{self._path}/{org_id}/custodians"
        data = self._serialize_data(payload)
        response = self._make_request("PUT", path, json=data)
        if isinstance(response, list):
            return [CustodianUser.model_validate(item) for item in response]
        return []

    def reset_custodians(
        self, org_id: int, payload: OrgCustodiansPayload
    ) -> List[CustodianUser]:
        path = f"{self._path}/{org_id}/custodians"
        data = self._serialize_data(payload)
        response = self._make_request("POST", path, json=data)
        if isinstance(response, list):
            return [CustodianUser.model_validate(item) for item in response]
        return []

    def remove_custodians(
        self, org_id: int, payload: OrgCustodiansPayload
    ) -> Dict[str, Any]:
        path = f"{self._path}/{org_id}/custodians"
        data = self._serialize_data(payload)
        return self._make_request("DELETE", path, json=data)
