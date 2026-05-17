"""
Nexla API client
"""

import logging
import os
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from pydantic import ValidationError as PydanticValidationError

from . import telemetry
from .auth import TokenAuthHandler
from .exceptions import (
    AuthenticationError,
    NexlaError,
    NotFoundError,
    ServerError,
    ValidationError,
)
from .http_client import HttpClientError, HttpClientInterface, RequestsHttpClient
from .raw_operations import RawOperationsClient
from .resources.api_keys import ApiKeysResource
from .resources.approval_requests import ApprovalRequestsResource
from .resources.async_tasks import AsyncTasksResource
from .resources.attribute_transforms import AttributeTransformsResource
from .resources.auth_parameters import AuthParametersResource
from .resources.auth_templates import AuthTemplatesResource
from .resources.catalog_configs import CatalogConfigsResource
from .resources.cluster_endpoints import ClusterEndpointsResource
from .resources.clusters import ClustersResource
from .resources.code_containers import CodeContainersResource
from .resources.connectors import ConnectorsResource
from .resources.credentials import CredentialsResource
from .resources.cubejs import CubeJsResource
from .resources.custom_data_flows import CustomDataFlowsResource
from .resources.dashboard_transforms import DashboardTransformsResource
from .resources.data_credentials_groups import DataCredentialsGroupsResource
from .resources.data_flows import DataFlowsResource
from .resources.data_schemas import DataSchemasResource
from .resources.destinations import DestinationsResource
from .resources.doc_containers import DocContainersResource
from .resources.flow_nodes import FlowNodesResource
from .resources.flow_triggers import FlowTriggersResource
from .resources.flows import FlowsResource
from .resources.genai import GenAIResource
from .resources.lookups import LookupsResource
from .resources.marketplace import MarketplaceResource
from .resources.metrics import MetricsResource
from .resources.nexsets import NexsetsResource
from .resources.notification_channel_settings import NotificationChannelSettingsResource
from .resources.notification_settings import NotificationSettingsResource
from .resources.notification_types import NotificationTypesResource
from .resources.notifications import NotificationsResource
from .resources.org_auth_configs import OrgAuthConfigsResource
from .resources.org_tiers import OrgTiersResource
from .resources.organizations import OrganizationsResource
from .resources.projects import ProjectsResource
from .resources.quarantine_settings import QuarantineSettingsResource
from .resources.resource_parameters import ResourceParametersResource
from .resources.runtimes import RuntimesResource
from .resources.search_health import SearchHealthResource
from .resources.self_signup import SelfSignupResource
from .resources.self_signup_blocked_domains import SelfSignupBlockedDomainsResource
from .resources.service_keys import ServiceKeysResource
from .resources.sources import SourcesResource
from .resources.teams import TeamsResource
from .resources.tokens import TokensResource
from .resources.transforms import TransformsResource
from .resources.user_settings import UserSettingsResource
from .resources.user_tiers import UserTiersResource
from .resources.users import UsersResource
from .resources.validators import ValidatorsResource
from .resources.vendor_endpoints import VendorEndpointsResource
from .resources.vendors import VendorsResource
from .resources.webhooks import WebhooksResource

logger = logging.getLogger(__name__)

T = TypeVar("T")


class NexlaClient:
    """
    Client for the Nexla API

    The Nexla API supports two authentication methods:

    1. **Service Key Authentication** (recommended):
       Service keys are long-lived credentials created in the Nexla UI. The SDK
       obtains session tokens using the service key on demand and re-obtains a new
       token as needed. No refresh endpoint is used.

    2. **Direct Access Token Authentication**:
       Use a pre-obtained access token directly. These tokens are not refreshed by the SDK.

    Examples:
        # Method 1: Using service key (recommended for automation)
        client = NexlaClient(service_key="your-service-key")

        # Method 2: Using access token directly (manual/short-term use)
        client = NexlaClient(access_token="your-access-token")

        # Using the client (same regardless of authentication method)
        flows = client.flows.list()

    Note:
        - Service keys should be treated as highly sensitive credentials
        - Only provide either service_key OR access_token, not both
        - When using direct access tokens, ensure they have sufficient lifetime
          for your operations as they cannot be automatically refreshed
    """

    def __init__(
        self,
        service_key: Optional[str] = None,
        access_token: Optional[str] = None,
        base_url: Optional[str] = None,
        api_version: str = "v1",
        token_refresh_margin: int = 3600,
        http_client: Optional[HttpClientInterface] = None,
        trace_enabled: Optional[bool] = None,
    ):
        """
        Initialize the Nexla client

        Args:
            service_key: Nexla service key for authentication (mutually exclusive with access_token)
            access_token: Nexla access token for direct authentication (mutually exclusive with service_key)
            base_url: Nexla API base URL (defaults to environment variable or standard URL)
            api_version: API version to use
            token_refresh_margin: Seconds before token expiry to trigger refresh (default: 1 hour)
            http_client: HTTP client implementation (defaults to RequestsHttpClient)
            trace_enabled: Explicitly enable/disable OpenTelemetry tracing. If None,
                           tracing auto-enables when a global OTEL config is detected.

        Raises:
            NexlaError: If neither or both authentication methods are provided

        Environment Variables:
            NEXLA_SERVICE_KEY: Service key (used if no authentication parameters are provided)
            NEXLA_ACCESS_TOKEN: Access token (used if no authentication parameters are provided and NEXLA_SERVICE_KEY is not set)
            NEXLA_API_URL: Base URL for the Nexla API (used if base_url parameter is not provided)
        """
        # Check environment variables only if neither parameter is provided
        if not service_key and not access_token:
            # First check for service_key in environment
            service_key = os.getenv("NEXLA_SERVICE_KEY")
            # Only check for access_token if service_key is not available
            if not service_key:
                access_token = os.getenv("NEXLA_ACCESS_TOKEN")

        # Check for base_url in environment if not provided as parameter
        if not base_url:
            base_url = os.getenv("NEXLA_API_URL")
            if not base_url:
                base_url = "https://dataops.nexla.io/nexla-api"

        # Validate authentication parameters
        if not service_key and not access_token:
            raise NexlaError(
                "Either service_key or access_token must be provided either as parameters "
                "or via NEXLA_SERVICE_KEY/NEXLA_ACCESS_TOKEN environment variables"
            )
        if service_key and access_token:
            raise NexlaError(
                "Cannot provide both service_key and access_token. Choose one authentication method."
            )

        self.api_url = base_url.rstrip("/")
        self.api_version = api_version

        # Determine if tracing should be active and get a tracer
        self._trace_enabled = False
        if trace_enabled is True:
            self._trace_enabled = True
        elif trace_enabled is None and telemetry.is_tracing_configured():
            logger.debug(
                "Global OpenTelemetry configuration detected. Enabling tracing for Nexla SDK."
            )
            self._trace_enabled = True

        self.tracer = telemetry.get_tracer(self._trace_enabled)

        # Initialize HTTP client (instrumented if tracer provided)
        self.http_client = http_client or RequestsHttpClient(tracer=self.tracer)

        # Initialize authentication handler
        self.auth_handler = TokenAuthHandler(
            service_key=service_key,
            access_token=access_token,
            base_url=base_url,
            api_version=api_version,
            token_refresh_margin=token_refresh_margin,
            http_client=self.http_client,
        )

        # Full operation-level API access (OpenAPI operation_id based)
        self.raw: RawOperationsClient = RawOperationsClient(self)

        # Initialize API endpoints
        self.flows = FlowsResource(self)
        self.flow_nodes = FlowNodesResource(self)
        self.data_flows = DataFlowsResource(self)
        self.sources = SourcesResource(self)
        self.destinations = DestinationsResource(self)
        self.credentials = CredentialsResource(self)
        self.custom_data_flows = CustomDataFlowsResource(self)
        self.data_credentials_groups = DataCredentialsGroupsResource(self)
        self.lookups = LookupsResource(self)
        self.nexsets = NexsetsResource(self)
        self.users = UsersResource(self)
        self.user_settings = UserSettingsResource(self)
        self.user_tiers = UserTiersResource(self)
        self.organizations = OrganizationsResource(self)
        self.teams = TeamsResource(self)
        self.projects = ProjectsResource(self)
        self.notifications = NotificationsResource(self)
        self.notification_settings = NotificationSettingsResource(self)
        self.notification_channel_settings = NotificationChannelSettingsResource(self)
        self.notification_types = NotificationTypesResource(self)
        self.quarantine_settings = QuarantineSettingsResource(self)
        self.dashboard_transforms = DashboardTransformsResource(self)
        self.metrics = MetricsResource(self)
        self.code_containers = CodeContainersResource(self)
        self.transforms = TransformsResource(self)
        self.attribute_transforms = AttributeTransformsResource(self)
        self.async_tasks = AsyncTasksResource(self)
        self.approval_requests = ApprovalRequestsResource(self)
        self.runtimes = RuntimesResource(self)
        self.marketplace = MarketplaceResource(self)
        self.org_auth_configs = OrgAuthConfigsResource(self)
        self.org_tiers = OrgTiersResource(self)
        self.auth_parameters = AuthParametersResource(self)
        self.resource_parameters = ResourceParametersResource(self)
        self.catalog_configs = CatalogConfigsResource(self)
        self.vendor_endpoints = VendorEndpointsResource(self)
        self.genai = GenAIResource(self)
        self.self_signup = SelfSignupResource(self)
        self.self_signup_blocked_domains = SelfSignupBlockedDomainsResource(self)
        self.doc_containers = DocContainersResource(self)
        self.data_schemas = DataSchemasResource(self)
        self.tokens = TokensResource(self)
        self.search_health = SearchHealthResource(self)
        self.cubejs = CubeJsResource(self)

        # Phase 1 resources
        self.validators = ValidatorsResource(self)
        self.service_keys = ServiceKeysResource(self)
        self.flow_triggers = FlowTriggersResource(self)

        # Phase 3 resources
        self.clusters = ClustersResource(self)
        self.cluster_endpoints = ClusterEndpointsResource(self)

        # Phase 4 resources
        self.api_keys = ApiKeysResource(self)
        self.connectors = ConnectorsResource(self)
        self.vendors = VendorsResource(self)
        self.auth_templates = AuthTemplatesResource(self)

    def get_access_token(self) -> str:
        """
        Get a valid access token.

        For service keys, the SDK obtains tokens as needed and re-obtains a new
        one if the current token is near expiry. Direct access tokens are used as-is.

        Returns:
            A valid access token string

        Raises:
            AuthenticationError: If no valid token is available or refresh fails

        Examples:
            # Get a valid access token
            token = client.get_access_token()

            # Use the token for external API calls
            headers = {"Authorization": f"Bearer {token}"}
        """
        return self.auth_handler.ensure_valid_token()

    def refresh_access_token(self) -> str:
        """
        Obtain a fresh token and return it.

        For service keys, this obtains a new token. Direct access tokens cannot
        be refreshed and will raise an AuthenticationError.

        Returns:
            Refreshed access token string

        Raises:
            AuthenticationError: If token refresh fails

        Examples:
            # Force refresh and get new token
            new_token = client.refresh_access_token()
        """
        self.auth_handler.refresh_session_token()
        return self.auth_handler.get_access_token()

    def logout(self) -> None:
        """
        Logout current session and invalidate token.

        Calls POST /token/logout and clears internal token state when successful.
        """
        self.auth_handler.logout()

    def create_webhook_client(self, api_key: str) -> WebhooksResource:
        """
        Create a webhook client for sending data to Nexla webhooks.

        Webhooks use API key authentication instead of session tokens.
        The API key and webhook URL are provided when you create a webhook
        source in the Nexla UI.

        Args:
            api_key: Nexla API key for webhook authentication.

        Returns:
            WebhooksResource instance for sending webhook data.

        Examples:
            # Create a webhook client
            webhooks = client.create_webhook_client(api_key="your-api-key")

            # Send a single record
            response = webhooks.send_one_record(
                webhook_url="https://api.nexla.com/webhook/abc123",
                record={"event": "page_view", "user_id": 123}
            )

            # Send multiple records
            response = webhooks.send_many_records(
                webhook_url="https://api.nexla.com/webhook/abc123",
                records=[{"id": 1}, {"id": 2}]
            )

        Note:
            You can also create a WebhooksResource directly without a NexlaClient:

            from nexla_sdk.resources.webhooks import WebhooksResource
            webhooks = WebhooksResource(api_key="your-api-key")
        """
        return WebhooksResource(api_key=api_key, http_client=self.http_client)

    def _convert_to_model(
        self, data: Union[Dict[str, Any], List[Dict[str, Any]]], model_class: Type[T]
    ) -> Union[T, List[T]]:
        """
        Convert API response data to a Pydantic model

        Args:
            data: API response data, either a dict or a list of dicts
            model_class: Pydantic model class to convert to

        Returns:
            Pydantic model instance or list of instances

        Raises:
            ValidationError: If validation fails
        """
        try:
            logger.debug(f"Converting data to model: {model_class.__name__}")
            logger.debug(f"Data to convert: {data}")

            if isinstance(data, list):
                result = [model_class.model_validate(item) for item in data]
                logger.debug(f"Converted list result: {result}")
                return result

            result = model_class.model_validate(data)
            logger.debug(f"Converted single result: {result}")
            return result
        except PydanticValidationError as e:
            # Log the validation error details
            logger.error(f"Validation error converting to {model_class.__name__}: {e}")
            raise ValidationError(
                f"Failed to convert API response to {model_class.__name__}: {e}"
            )

    def request(self, method: str, path: str, **kwargs) -> Union[Dict[str, Any], None]:
        """
        Send a request to the Nexla API

        Args:
            method: HTTP method
            path: API path
            **kwargs: Additional arguments to pass to HTTP client

        Returns:
            API response as a dictionary or None for 204 No Content responses

        Raises:
            AuthenticationError: If authentication fails
            ServerError: If the API returns an error
        """
        url = f"{self.api_url}{path}"
        headers = {
            "Accept": f"application/vnd.nexla.api.{self.api_version}+json",
            "Content-Type": "application/json",
        }

        # If custom headers are provided, merge them with the default headers
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            # Let auth handler manage getting a valid token and handling auth retries
            return self.auth_handler.execute_authenticated_request(
                method=method, url=url, headers=headers, **kwargs
            )
        except HttpClientError as e:
            # Map HTTP client errors to appropriate Nexla exceptions
            self._handle_http_error(e, method, path, url, kwargs)
        except NexlaError:
            # Preserve explicit NexlaError subclasses (e.g., AuthenticationError)
            raise
        except Exception as e:
            raise NexlaError(
                message=f"Request failed: {e}",
                operation=f"{method.lower()}_request",
                context={
                    "method": method,
                    "path": path,
                    "url": url,
                    "kwargs": {
                        k: v for k, v in kwargs.items() if k not in ["json", "data"]
                    },
                },
                original_error=e,
            ) from e

    def _handle_http_error(
        self, error: HttpClientError, method: str, path: str, url: str, kwargs: dict
    ):
        """
        Handle HTTP client errors by mapping them to appropriate Nexla exceptions

        Args:
            error: The HTTP client error
            method: HTTP method that failed
            path: API path that failed
            url: Full URL that failed
            kwargs: Request parameters

        Raises:
            AuthenticationError: If authentication fails (401)
            NotFoundError: If resource not found (404)
            ServerError: For other API errors
        """
        status_code = getattr(error, "status_code", None)
        error_data = getattr(error, "response", {})

        error_msg = f"API request failed: {error}"

        if error_data:
            if "message" in error_data:
                error_msg = f"API error: {error_data['message']}"
            elif "error" in error_data:
                error_msg = f"API error: {error_data['error']}"

        # Extract resource information (prefer server-provided fields, fallback to path)
        resource_type = None
        resource_id = None
        if isinstance(error_data, dict):
            resource_type = error_data.get("resource_type") or None
            resource_id = error_data.get("resource_id") or None
        if not resource_type or not resource_id:
            # Fallback to parsing the path
            if path:
                path_parts = path.strip("/").split("/")
                if not resource_type and len(path_parts) >= 1:
                    resource_type = path_parts[0]
                if not resource_id and len(path_parts) >= 2 and path_parts[1].isdigit():
                    resource_id = path_parts[1]
        # Final defaults
        if not resource_type:
            resource_type = "unknown"

        # Build context
        context = {
            "method": method,
            "path": path,
            "url": url,
            "status_code": status_code,
            "api_response": error_data,
            "request_params": {
                k: v for k, v in kwargs.items() if k not in ["json", "data"]
            },
        }

        # Map status codes to specific exceptions
        if status_code in (400, 422):
            raise ValidationError(
                error_msg,
                status_code=status_code,
                response=error_data,
                operation=f"{method.lower()}_request",
                resource_type=resource_type,
                resource_id=resource_id,
                context=context,
                original_error=error,
            ) from error
        elif status_code == 401:
            raise AuthenticationError(
                "Authentication failed. Check your service key.",
                operation=f"{method.lower()}_request",
                resource_type=resource_type,
                resource_id=resource_id,
                context=context,
                original_error=error,
            ) from error
        elif status_code == 403:
            from .exceptions import AuthorizationError

            raise AuthorizationError(
                error_msg,
                status_code=status_code,
                response=error_data,
                operation=f"{method.lower()}_request",
                resource_type=resource_type,
                resource_id=resource_id,
                context=context,
                original_error=error,
            ) from error
        elif status_code == 404:
            raise NotFoundError(
                f"Resource not found: {resource_type}/{resource_id or 'unknown'}",
                resource_type=resource_type,
                resource_id=resource_id,
                operation=f"{method.lower()}_request",
                context=context,
                original_error=error,
            ) from error
        elif status_code == 409:
            from .exceptions import ResourceConflictError

            raise ResourceConflictError(
                error_msg,
                status_code=status_code,
                response=error_data,
                operation=f"{method.lower()}_request",
                resource_type=resource_type,
                resource_id=resource_id,
                context=context,
                original_error=error,
            ) from error
        elif status_code == 429:
            from .exceptions import RateLimitError

            retry_after = None
            # Try to parse retry-after from headers or body
            headers = getattr(error, "headers", {}) or {}
            if headers:
                retry_after_hdr = headers.get("Retry-After") or headers.get(
                    "retry-after"
                )
                if retry_after_hdr:
                    try:
                        retry_after = int(retry_after_hdr)
                    except Exception:
                        retry_after = None
            if not retry_after and isinstance(error_data, dict):
                retry_after = error_data.get("retry_after")
            raise RateLimitError(
                error_msg,
                retry_after=retry_after,
                status_code=status_code,
                response=error_data,
                operation=f"{method.lower()}_request",
                resource_type=resource_type,
                resource_id=resource_id,
                context=context,
                original_error=error,
            ) from error
        else:
            raise ServerError(
                error_msg,
                status_code=status_code,
                response=error_data,
                operation=f"{method.lower()}_request",
                resource_type=resource_type,
                resource_id=resource_id,
                context=context,
                original_error=error,
            ) from error
