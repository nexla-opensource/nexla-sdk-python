"""
Nexla API client
"""

import logging
import os
import threading
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    NoReturn,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from . import telemetry
from .auth import TokenAuthHandler
from .exceptions import (
    NexlaConnectionError,
    NexlaError,
    NexlaTimeoutError,
    ValidationError,
    error_from_response,
)
from .http_client import (
    HttpClientError,
    HttpClientInterface,
    HttpConnectionError,
    HttpTimeoutError,
    RequestsHttpClient,
)
from .models.tokens.responses import TokenResponse
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
from .resources.mcp_sessions import McpSessionsResource
from .resources.metrics import MetricsResource
from .resources.nexsets import NexsetsResource
from .resources.notification_channel_settings import NotificationChannelSettingsResource
from .resources.notification_settings import NotificationSettingsResource
from .resources.notification_types import NotificationTypesResource
from .resources.notifications import NotificationsResource
from .resources.oauth import OAuthResource
from .resources.org_auth_configs import OrgAuthConfigsResource
from .resources.org_tiers import OrgTiersResource
from .resources.organizations import OrganizationsResource
from .resources.projects import ProjectsResource
from .resources.quarantine_settings import QuarantineSettingsResource
from .resources.resource_parameters import ResourceParametersResource
from .resources.runtimes import RuntimesResource
from .resources.sdk_applications import SdkApplicationsResource
from .resources.search_health import SearchHealthResource
from .resources.self_signup import SelfSignupResource
from .resources.self_signup_blocked_domains import SelfSignupBlockedDomainsResource
from .resources.service_keys import ServiceKeysResource
from .resources.sources import SourcesResource
from .resources.teams import TeamsResource
from .resources.tokens import TokensResource
from .resources.tool_sets import ToolSetsResource
from .resources.tools import ToolsResource
from .resources.transforms import TransformsResource
from .resources.user_settings import UserSettingsResource
from .resources.user_tiers import UserTiersResource
from .resources.users import UsersResource
from .resources.validators import ValidatorsResource
from .resources.vendor_endpoints import VendorEndpointsResource
from .resources.vendors import VendorsResource
from .resources.webhooks import WebhooksResource

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


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

    Other modes: ``api_key`` (Basic, sent as is) and ``email``/``password``
    (Basic ``email:password[:org_id]``). Both obtain session tokens with POST /token.
    Use ``switch_org(org_id)`` to change the org of the current session.

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
        timeout: Union[float, Tuple[float, float]] = (10.0, 60.0),
        max_retries: int = 3,
        retry_methods: Optional[Iterable[str]] = None,
        retry_on_status: Optional[Iterable[int]] = None,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        org_id: Optional[int] = None,
        dataplane: Optional[str] = None,
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
            timeout: Seconds as (connect, read), or one number for both. Default (10, 60).
                     Ignored when http_client is given.
            max_retries: Maximum retries per request. Default 3. Ignored when http_client is given.
            retry_methods: Methods retried on read errors and 502/503/504.
                           Default: GET, HEAD, OPTIONS, PUT, DELETE.
            retry_on_status: Status codes retried for retry_methods. Default: 502, 503, 504.

        Raises:
            NexlaError: If neither or both authentication methods are provided

        Environment Variables:
            NEXLA_SERVICE_KEY: Service key (used if no authentication parameters are provided)
            NEXLA_ACCESS_TOKEN: Access token (used if no authentication parameters are provided and NEXLA_SERVICE_KEY is not set)
            NEXLA_API_URL: Base URL for the Nexla API (used if base_url parameter is not provided)
        """
        # Credential modes: service key, API key, email/password, or access token.
        # Exactly one. Explicit options win; env vars are read only when none is passed.
        has_password = bool(email or password)
        if has_password and not (email and password):
            raise NexlaError("email and password must be provided together")
        explicit = [
            name
            for name, value in (
                ("service_key", service_key),
                ("api_key", api_key),
                ("access_token", access_token),
                ("email/password", has_password),
            )
            if value
        ]
        if len(explicit) > 1:
            raise NexlaError(
                "Cannot provide more than one of service_key, api_key, access_token, "
                "or email/password. Choose one authentication method."
            )
        if not explicit:
            service_key = os.getenv("NEXLA_SERVICE_KEY") or None
            if not service_key:
                api_key = os.getenv("NEXLA_API_KEY") or None
            if not service_key and not api_key:
                access_token = os.getenv("NEXLA_ACCESS_TOKEN") or None

        # Check for base_url in environment if not provided as parameter
        if not base_url:
            base_url = os.getenv("NEXLA_API_URL")
            if not base_url:
                base_url = "https://dataops.nexla.io/nexla-api"

        if not (service_key or api_key or access_token or has_password):
            raise NexlaError(
                "Either service_key, api_key, access_token, or email and password must be "
                "provided as parameters or via NEXLA_SERVICE_KEY, NEXLA_API_KEY, or "
                "NEXLA_ACCESS_TOKEN environment variables"
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
        self._response_state = threading.local()

        # Initialize HTTP client (instrumented if tracer provided)
        self.http_client = http_client or RequestsHttpClient(
            timeout=timeout,
            max_retries=max_retries,
            retry_methods=retry_methods,
            retry_on_status=retry_on_status,
            tracer=self.tracer,
        )

        # Initialize authentication handler
        self.auth_handler = TokenAuthHandler(
            service_key=service_key,
            access_token=access_token,
            base_url=base_url,
            api_version=api_version,
            token_refresh_margin=token_refresh_margin,
            http_client=self.http_client,
            api_key=api_key,
            email=email,
            password=password,
            org_id=org_id,
            dataplane=dataplane,
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
        self.oauth = OAuthResource(self)
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
        self.tools = ToolsResource(self)
        self.tool_sets = ToolSetsResource(self)
        self.sdk_applications = SdkApplicationsResource(self)
        self.mcp_sessions = McpSessionsResource(self)
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

    def switch_org(self, org_id: int) -> TokenResponse:
        """
        Switch the session to another org (POST /token/refresh?org_id=).

        The switch lasts until the SDK obtains a new token. When the SDK
        re-obtains a token (service key, API key, or password mode), the
        session returns to the credential's default org.

        Args:
            org_id: Org ID to switch to

        Returns:
            The new token response

        Examples:
            token = client.switch_org(42)
        """
        return self.auth_handler.switch_org(org_id)

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

            single = model_class.model_validate(data)
            logger.debug(f"Converted single result: {single}")
            return single
        except PydanticValidationError as e:
            # Log the validation error details
            logger.error(f"Validation error converting to {model_class.__name__}: {e}")
            raise ValidationError(
                f"Failed to convert API response to {model_class.__name__}: {e}"
            ) from e

    @property
    def last_response_headers(self) -> Mapping[str, Any]:
        """
        Headers of the last response received on the calling thread.

        paginate() reads this after each list() call. Empty before any request.
        """
        return getattr(self._response_state, "headers", None) or {}

    def request(
        self, method: str, path: str, **kwargs: Any
    ) -> Union[Dict[str, Any], None]:
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
        body, _ = self.request_with_headers(method, path, **kwargs)
        return body

    def request_with_headers(
        self, method: str, path: str, **kwargs: Any
    ) -> Tuple[Union[Dict[str, Any], None], Any]:
        """
        Send a request to the Nexla API and return (body, response headers).

        The headers are also stored for last_response_headers.

        Raises:
            AuthenticationError: If authentication fails
            ServerError: If the API returns an error
        """
        self._response_state.headers = {}
        url = f"{self.api_url}{path}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # If custom headers are provided, merge them with the default headers
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            # Let auth handler manage getting a valid token and handling auth retries
            body, response_headers = (
                self.auth_handler.execute_authenticated_request_with_headers(
                    method=method, url=url, headers=headers, **kwargs
                )
            )
            self._response_state.headers = response_headers
            return body, response_headers
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
        self,
        error: HttpClientError,
        method: str,
        path: str,
        url: str,
        kwargs: Dict[str, Any],
    ) -> NoReturn:
        """
        Map an HTTP client error to a typed NexlaError.

        Status code and body shape choose the class (see exceptions.error_from_response).
        Timeouts map to NexlaTimeoutError and connection failures to NexlaConnectionError.

        Raises:
            NexlaTimeoutError: The request timed out
            NexlaConnectionError: The connection failed
            NexlaError: A typed subclass for the HTTP status
        """
        error_data = getattr(error, "response", {}) or {}

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
        if not resource_type:
            resource_type = "unknown"

        context = {
            "method": method,
            "path": path,
            "url": url,
            "status_code": getattr(error, "status_code", None),
            "api_response": error_data,
            "request_params": {
                k: v for k, v in kwargs.items() if k not in ["json", "data"]
            },
        }
        common: Dict[str, Any] = {
            "operation": f"{method.lower()}_request",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "context": context,
            "original_error": error,
        }

        if isinstance(error, HttpTimeoutError):
            raise NexlaTimeoutError(
                f"Request timed out: {error}", method=method, url=url, **common
            ) from error
        if isinstance(error, HttpConnectionError):
            raise NexlaConnectionError(
                f"Connection failed: {error}", method=method, url=url, **common
            ) from error

        body = error.body if error.body is not None else (error_data or None)
        raise error_from_response(
            getattr(error, "status_code", None),
            body,
            headers=getattr(error, "headers", {}),
            method=method,
            url=url,
            **common,
        ) from error
