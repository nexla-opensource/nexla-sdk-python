from typing import Any, Dict, List, Optional, Union

from nexla_sdk.models.metrics.enums import UserMetricResourceType
from nexla_sdk.models.users.credits import UserCredit, UserCreditCreate
from nexla_sdk.models.users.requests import UserCreate, UserUpdate
from nexla_sdk.models.users.responses import User, UserExpanded, UserSettings
from nexla_sdk.resources.base_resource import BaseResource


class UsersResource(BaseResource):
    """Resource for managing users."""

    def __init__(self, client):
        super().__init__(client)
        self._path = "/users"
        self._model_class = User

    def list(self, expand: bool = False, **kwargs) -> List[User]:
        """
        List users with optional filters.

        Args:
            expand: Include expanded information
            page: Page number (via kwargs)
            per_page: Items per page (via kwargs)
            access_role: Filter by access role (via kwargs)
            **kwargs: Additional query parameters

        Returns:
            List of users

        Examples:
            client.users.list(page=1, per_page=50)
            client.users.list(expand=True)
        """
        if expand:
            response = self._make_request(
                "GET", f"{self._path}?expand=1", params=kwargs
            )
            return [UserExpanded(**item) for item in response]

        return super().list(**kwargs)

    def list_sso_options(self) -> Dict[str, Any]:
        return self._make_request("GET", "/users/sso_options")

    def get(self, user_id: int, expand: bool = False) -> User:
        """
        Get user by ID.

        Args:
            user_id: User ID
            expand: Include expanded information

        Returns:
            User object

        Examples:
            client.users.get(42)
            client.users.get(42, expand=True)
        """
        if expand:
            path = f"{self._path}/{user_id}?expand=1"
            response = self._make_request("GET", path)
            return UserExpanded(**response)

        return super().get(user_id, expand=False)

    def create(self, data: UserCreate) -> User:
        """
        Create new user.

        Args:
            data: User creation data

        Returns:
            Created user

        Examples:
            client.users.create(UserCreate(email="user@example.com", name="Jane"))
        """
        return super().create(data)

    def update(self, user_id: int, data: UserUpdate) -> User:
        """
        Update user.

        Args:
            user_id: User ID
            data: Updated user data

        Returns:
            Updated user
        """
        return super().update(user_id, data)

    def delete(self, user_id: int) -> Dict[str, Any]:
        """
        Delete user.

        Args:
            user_id: User ID

        Returns:
            Response with status
        """
        return super().delete(user_id)

    # Account summary methods
    def get_account_summary(self) -> Dict[str, Any]:
        """Get current user's account summary."""
        return self._make_request("GET", "/users/account_summary")

    def get_user_account_summary(self, user_id: int) -> Dict[str, Any]:
        """Get account summary for a specific user."""
        path = f"{self._path}/{user_id}/account_summary"
        return self._make_request("GET", path)

    # Password and authentication methods
    def reset_password(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/reset_password", json=payload)

    def set_password(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/set_password", json=payload)

    def password_entropy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/password_entropy", json=payload)

    def send_invite(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/users/send_invite", json=payload)

    def change_password(self, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/change_password"
        return self._make_request("PUT", path, json=payload)

    def get_sso_options(self, email: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if email:
            params["email"] = email
        return self._make_request("GET", "/users/sso_options", params=params)

    # User settings and current user
    def get_settings(self) -> List[UserSettings]:
        """
        Get current user's settings.

        Returns:
            List of user settings
        """
        path = "/user_settings"
        response = self._make_request("GET", path)
        return [UserSettings(**item) for item in response]

    def get_current(self) -> Dict[str, Any]:
        """Get info on current user (includes org memberships and current org info)."""
        path = "/users/current"
        return self._make_request("GET", path)

    # Audit and history methods
    def get_audit_history(self, user_id: int, **params) -> List[Dict[str, Any]]:
        path = f"{self._path}/{user_id}/audit_history"
        return self._make_request("GET", path, params=params) or []

    def get_login_history(self, user_id: int, **params) -> List[Dict[str, Any]]:
        path = f"{self._path}/{user_id}/login_history"
        return self._make_request("GET", path, params=params) or []

    def get_api_key_events(self, user_id: int, **params) -> List[Dict[str, Any]]:
        path = f"{self._path}/{user_id}/api_keys/events"
        return self._make_request("GET", path, params=params) or []

    def get_resource_audit_log(
        self, user_id: int, resource_type: str, **params
    ) -> List[Dict[str, Any]]:
        path = f"{self._path}/{user_id}/{resource_type}/audit_log"
        response = self._make_request("GET", path, params=params)
        return response or []

    # Metrics methods
    def get_metrics(
        self, user_id: int, metrics_name: Optional[str] = None, **params
    ) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/metrics"
        if metrics_name:
            path = f"{path}/{metrics_name}"
        return self._make_request("GET", path, params=params)

    def get_orgs(self, user_id: int, **params) -> List[Dict[str, Any]]:
        path = f"{self._path}/{user_id}/orgs"
        return self._make_request("GET", path, params=params) or []

    # Quarantine settings
    def get_quarantine_settings(self, user_id: int) -> Dict[str, Any]:
        """
        Get quarantine data export settings for user.

        Args:
            user_id: User ID

        Returns:
            Quarantine settings
        """
        path = f"{self._path}/{user_id}/quarantine_settings"
        return self._make_request("GET", path)

    def create_quarantine_settings(
        self, user_id: int, data_credentials_id: int, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create quarantine data export settings.

        Args:
            user_id: User ID
            data_credentials_id: Credential ID for export location
            config: Configuration including cron schedule and path

        Returns:
            Created settings
        """
        path = f"{self._path}/{user_id}/quarantine_settings"
        data = {"data_credentials_id": data_credentials_id, "config": config}
        return self._make_request("POST", path, json=data)

    def update_quarantine_settings(
        self, user_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update quarantine data export settings.

        Args:
            user_id: User ID
            data: Updated settings

        Returns:
            Updated settings
        """
        path = f"{self._path}/{user_id}/quarantine_settings"
        return self._make_request("PUT", path, json=data)

    def delete_quarantine_settings(self, user_id: int) -> Dict[str, Any]:
        """
        Delete quarantine data export settings.

        Args:
            user_id: User ID

        Returns:
            Response status
        """
        path = f"{self._path}/{user_id}/quarantine_settings"
        return self._make_request("DELETE", path)

    # Dashboard transforms
    def get_dashboard_transforms(self, user_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/dashboard_transforms"
        return self._make_request("GET", path)

    def get_audit_log(
        self,
        user_id: int,
        from_date: str = None,
        to_date: str = None,
        event_filter: str = None,
        change_filter: str = None,
        page: int = None,
        per_page: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Get audit log for a user.

        Args:
            user_id: User ID
            from_date: Start date filter (YYYY-MM-DD)
            to_date: End date filter (YYYY-MM-DD)
            event_filter: Filter by event type
            change_filter: Filter by change type
            page: Page number for pagination
            per_page: Items per page

        Returns:
            List of audit log entries
        """
        path = f"{self._path}/{user_id}/audit_log"
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
        if isinstance(response, list):
            return response
        return []

    def create_dashboard_transforms(
        self, user_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/dashboard_transforms"
        return self._make_request("POST", path, json=payload)

    def update_dashboard_transforms(
        self, user_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/dashboard_transforms"
        return self._make_request("PUT", path, json=payload)

    def delete_dashboard_transforms(self, user_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/dashboard_transforms"
        return self._make_request("DELETE", path)

    # Flows dashboard and metrics
    def get_flows_dashboard(self, user_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/flows/dashboard"
        return self._make_request("GET", path, params=params)

    def get_flows_status_metrics(self, user_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/flows/status_metrics"
        return self._make_request("GET", path, params=params)

    def get_flows_account_metrics(self, user_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/flows/account_metrics"
        return self._make_request("GET", path, params=params)

    # Account activation and locking
    def activate(self, user_id: int, activate: bool = True) -> Dict[str, Any]:
        action = "activate" if activate else "deactivate"
        path = f"{self._path}/{user_id}/{action}"
        return self._make_request("PUT", path)

    def lock_account(self, user_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/lock_account"
        return self._make_request("PUT", path)

    def unlock_account(self, user_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/unlock_account"
        return self._make_request("PUT", path)

    def activate_rate_limited_sources(
        self, user_id: int, status: Optional[str] = None, activate: bool = True
    ) -> Dict[str, Any]:
        action = "source_activate" if activate else "source_pause"
        path = f"{self._path}/{user_id}/{action}"
        if status:
            path = f"{path}/{status}"
        return self._make_request("PUT", path)

    def get_account_rate_limited(self, user_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/account_rate_limited"
        return self._make_request("GET", path)

    # Resource transfer
    def get_transferable_resources(self, user_id: int, org_id: int) -> Dict[str, Any]:
        """
        Get a list of resources owned by a user that can be transferred.

        Args:
            user_id: The ID of the user whose resources are being checked
            org_id: The ID of the organization context

        Returns:
            A dictionary of transferable resources by type
        """
        path = f"{self._path}/{user_id}/transferable"
        params = {"org_id": org_id}
        return self._make_request("GET", path, params=params)

    def transfer_resources(
        self, user_id: int, org_id: int, delegate_owner_id: int
    ) -> Dict[str, Any]:
        """
        Transfer a user's resources to another user within an organization.

        Args:
            user_id: The ID of the user whose resources are being transferred
            org_id: The ID of the organization context
            delegate_owner_id: The ID of the user to whom resources will be transferred

        Returns:
            A dictionary confirming the transfer details
        """
        path = f"{self._path}/{user_id}/transfer"
        data = {"org_id": org_id, "delegate_owner_id": delegate_owner_id}
        return self._make_request("PUT", path, json=data)

    # User credits
    def list_credits(self, user_id: int, **params) -> List[UserCredit]:
        path = f"{self._path}/{user_id}/credits"
        response = self._make_request("GET", path, params=params)
        return [UserCredit.model_validate(item) for item in (response or [])]

    def create_credit(self, user_id: int, payload: UserCreditCreate) -> UserCredit:
        path = f"{self._path}/{user_id}/credits"
        data = self._serialize_data(payload)
        response = self._make_request("POST", path, json=data)
        return UserCredit.model_validate(response)

    def get_credit(self, user_id: int, credit_id: int) -> UserCredit:
        path = f"{self._path}/{user_id}/credits/{credit_id}"
        response = self._make_request("GET", path)
        return UserCredit.model_validate(response)

    def use_credits(self, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/credits/use"
        return self._make_request("PUT", path, json=payload)

    def use_credit(self, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for use_credits."""
        return self.use_credits(user_id, payload)

    def refresh_credits(self, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/credits/refresh"
        return self._make_request("PUT", path, json=payload)

    def refresh_credit(self, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for refresh_credits."""
        return self.refresh_credits(user_id, payload)

    def expire_credit(self, user_id: int, credit_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/credits/{credit_id}/expire"
        return self._make_request("PUT", path)

    def delete_credit(self, user_id: int, credit_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/credits/{credit_id}"
        return self._make_request("DELETE", path)

    # API keys
    def list_api_keys(self, user_id: int, **params) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys"
        return self._make_request("GET", path, params=params)

    def search_api_keys(
        self, user_id: int, filters: Dict[str, Any], **params
    ) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys/search"
        return self._make_request("POST", path, json=filters, params=params)

    def get_api_key(self, user_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys/{api_key_id}"
        return self._make_request("GET", path)

    def create_api_key(self, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys"
        return self._make_request("POST", path, json=payload)

    def update_api_key(
        self, user_id: int, api_key_id: int, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys/{api_key_id}"
        return self._make_request("PUT", path, json=payload)

    def rotate_api_key(self, user_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys/{api_key_id}/rotate"
        return self._make_request("PUT", path)

    def activate_api_key(self, user_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys/{api_key_id}/activate"
        return self._make_request("PUT", path)

    def pause_api_key(self, user_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys/{api_key_id}/pause"
        return self._make_request("PUT", path)

    def pause_all_api_keys(self, user_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys/pause"
        return self._make_request("PUT", path)

    def delete_api_key(self, user_id: int, api_key_id: int) -> Dict[str, Any]:
        path = f"{self._path}/{user_id}/api_keys/{api_key_id}"
        return self._make_request("DELETE", path)

    # Extended metrics
    def get_account_metrics(
        self,
        user_id: int,
        from_date: str,
        to_date: Optional[str] = None,
        org_id: Optional[int] = None,
        aggregate: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get total account metrics for user.

        Args:
            user_id: User ID
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (optional)
            org_id: Organization ID (for users in multiple orgs)
            aggregate: Aggregation mode (optional)

        Returns:
            Account metrics
        """
        path = f"{self._path}/{user_id}/flows/account_metrics"
        params = {"from": from_date}
        if to_date:
            params["to"] = to_date
        if org_id:
            params["org_id"] = org_id
        if aggregate:
            params["aggregate"] = aggregate

        return self._make_request("GET", path, params=params)

    def get_flow_status_metrics(
        self,
        user_id: int,
        from_date: str = None,
        page: int = None,
        per_page: int = None,
    ) -> Dict[str, Any]:
        """
        Get flow status metrics for a user.

        Args:
            user_id: User ID
            from_date: Start date filter (YYYY-MM-DD)
            page: Page number for pagination
            per_page: Items per page

        Returns:
            Flow status metrics
        """
        path = f"{self._path}/{user_id}/flows/status_metrics"
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self._make_request("GET", path, params=params)

    def get_dashboard_metrics(
        self, user_id: int, access_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get 24 hour flow stats for user.

        Args:
            user_id: User ID
            access_role: Filter by access role

        Returns:
            Dashboard metrics
        """
        path = f"{self._path}/{user_id}/flows/dashboard"
        params = {}
        if access_role:
            params["access_role"] = access_role

        return self._make_request("GET", path, params=params)

    def get_daily_metrics(
        self,
        user_id: int,
        resource_type: Union[UserMetricResourceType, str],
        from_date: str,
        to_date: Optional[str] = None,
        org_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get daily data processing metrics for a user.

        Args:
            user_id: User ID
            resource_type: UserMetricResourceType or exact string value
                ("SOURCE", "SINK").
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (optional)
            org_id: Organization ID (optional)

        Returns:
            Daily metrics data
        """
        resource_type_value = self._resolve_enum_value(
            UserMetricResourceType, resource_type, "resource_type"
        )
        path = f"{self._path}/{user_id}/metrics"
        params = {
            "resource_type": resource_type_value,
            "from": from_date,
            "aggregate": 1,
        }
        if to_date:
            params["to"] = to_date
        if org_id:
            params["org_id"] = org_id

        return self._make_request("GET", path, params=params)
