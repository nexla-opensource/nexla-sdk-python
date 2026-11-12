"""Async client for the Nexla API.

Install the extra: ``pip install "nexla-sdk[async]"``.

AsyncNexlaClient has the resource attributes, method names and parameters of
NexlaClient. Resource methods are coroutines. Authentication, retries, timeouts
and errors follow the same spec as the sync client.

The resource wiring in ``__init__`` is copied from ``NexlaClient.__init__``.
``tests/unit/test_aio_surface.py`` fails when the two differ.
"""

from __future__ import annotations

import logging
from contextvars import ContextVar
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, Union

from nexla_sdk import telemetry
from nexla_sdk.aio.auth import TokenAuthHandler
from nexla_sdk.aio.http_client import AsyncHttpClientInterface, AsyncHttpxClient
from nexla_sdk.aio.raw_operations import RawOperationsClient
from nexla_sdk.aio.resources.api_keys import ApiKeysResource
from nexla_sdk.aio.resources.approval_requests import ApprovalRequestsResource
from nexla_sdk.aio.resources.async_tasks import AsyncTasksResource
from nexla_sdk.aio.resources.attribute_transforms import AttributeTransformsResource
from nexla_sdk.aio.resources.auth_parameters import AuthParametersResource
from nexla_sdk.aio.resources.auth_templates import AuthTemplatesResource
from nexla_sdk.aio.resources.catalog_configs import CatalogConfigsResource
from nexla_sdk.aio.resources.cluster_endpoints import ClusterEndpointsResource
from nexla_sdk.aio.resources.clusters import ClustersResource
from nexla_sdk.aio.resources.code_containers import CodeContainersResource
from nexla_sdk.aio.resources.connectors import ConnectorsResource
from nexla_sdk.aio.resources.credentials import CredentialsResource
from nexla_sdk.aio.resources.cubejs import CubeJsResource
from nexla_sdk.aio.resources.custom_data_flows import CustomDataFlowsResource
from nexla_sdk.aio.resources.dashboard_transforms import DashboardTransformsResource
from nexla_sdk.aio.resources.data_credentials_groups import (
    DataCredentialsGroupsResource,
)
from nexla_sdk.aio.resources.data_flows import DataFlowsResource
from nexla_sdk.aio.resources.data_schemas import DataSchemasResource
from nexla_sdk.aio.resources.destinations import DestinationsResource
from nexla_sdk.aio.resources.doc_containers import DocContainersResource
from nexla_sdk.aio.resources.flow_nodes import FlowNodesResource
from nexla_sdk.aio.resources.flow_triggers import FlowTriggersResource
from nexla_sdk.aio.resources.flows import FlowsResource
from nexla_sdk.aio.resources.genai import GenAIResource
from nexla_sdk.aio.resources.lookups import LookupsResource
from nexla_sdk.aio.resources.marketplace import MarketplaceResource
from nexla_sdk.aio.resources.mcp_sessions import McpSessionsResource
from nexla_sdk.aio.resources.metrics import MetricsResource
from nexla_sdk.aio.resources.nexsets import NexsetsResource
from nexla_sdk.aio.resources.notification_channel_settings import (
    NotificationChannelSettingsResource,
)
from nexla_sdk.aio.resources.notification_settings import NotificationSettingsResource
from nexla_sdk.aio.resources.notification_types import NotificationTypesResource
from nexla_sdk.aio.resources.notifications import NotificationsResource
from nexla_sdk.aio.resources.oauth import OAuthResource
from nexla_sdk.aio.resources.org_auth_configs import OrgAuthConfigsResource
from nexla_sdk.aio.resources.org_tiers import OrgTiersResource
from nexla_sdk.aio.resources.organizations import OrganizationsResource
from nexla_sdk.aio.resources.projects import ProjectsResource
from nexla_sdk.aio.resources.quarantine_settings import QuarantineSettingsResource
from nexla_sdk.aio.resources.resource_parameters import ResourceParametersResource
from nexla_sdk.aio.resources.runtimes import RuntimesResource
from nexla_sdk.aio.resources.sdk_applications import SdkApplicationsResource
from nexla_sdk.aio.resources.search_health import SearchHealthResource
from nexla_sdk.aio.resources.self_signup import SelfSignupResource
from nexla_sdk.aio.resources.self_signup_blocked_domains import (
    SelfSignupBlockedDomainsResource,
)
from nexla_sdk.aio.resources.service_keys import ServiceKeysResource
from nexla_sdk.aio.resources.sources import SourcesResource
from nexla_sdk.aio.resources.teams import TeamsResource
from nexla_sdk.aio.resources.tokens import TokensResource
from nexla_sdk.aio.resources.tool_sets import ToolSetsResource
from nexla_sdk.aio.resources.tools import ToolsResource
from nexla_sdk.aio.resources.transforms import TransformsResource
from nexla_sdk.aio.resources.user_settings import UserSettingsResource
from nexla_sdk.aio.resources.user_tiers import UserTiersResource
from nexla_sdk.aio.resources.users import UsersResource
from nexla_sdk.aio.resources.validators import ValidatorsResource
from nexla_sdk.aio.resources.vendor_endpoints import VendorEndpointsResource
from nexla_sdk.aio.resources.vendors import VendorsResource
from nexla_sdk.aio.resources.webhooks import WebhooksResource
from nexla_sdk.exceptions import NexlaError
from nexla_sdk.models.tokens.responses import TokenResponse
from nexla_sdk.transport_core import (
    HttpClientError,
    map_http_error,
    resolve_base_url,
    resolve_credentials,
    unexpected_request_error,
)

logger = logging.getLogger(__name__)


class AsyncNexlaClient:
    """Async client for the Nexla API.

    Use it as an async context manager, or call ``aclose()`` when finished.
    Authentication modes are the same as NexlaClient: service key, API key,
    email and password, or access token.

    Examples:
        async with AsyncNexlaClient(service_key="your-service-key") as client:
            sources = await client.sources.list()
            async for source in client.sources.paginate(per_page=50).iter_items():
                print(source.name)

    Note:
        Resource methods are coroutines. ``paginate()`` returns an AsyncPaginator
        that you iterate with ``async for``.
    """

    def __init__(
        self,
        service_key: Optional[str] = None,
        access_token: Optional[str] = None,
        base_url: Optional[str] = None,
        api_version: str = "v1",
        token_refresh_margin: int = 3600,
        http_client: Optional[AsyncHttpClientInterface] = None,
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
    ) -> None:
        """
        Initialize the async Nexla client. The arguments match NexlaClient.

        Args:
            service_key: Service key (mutually exclusive with the other credentials).
            access_token: Access token used as is. It is not refreshed.
            base_url: API base URL. Defaults to NEXLA_API_URL, then the production URL.
            api_version: API version.
            token_refresh_margin: Seconds before token expiry to obtain a new token.
            http_client: Async HTTP client. Defaults to AsyncHttpxClient. When given,
                timeout and retry arguments are ignored.
            trace_enabled: Enable or disable OpenTelemetry tracing. None means auto.
            timeout: Seconds as (connect, read), or one number for both.
            max_retries: Maximum retries per request.
            retry_methods: Methods retried on read errors and 502/503/504.
            retry_on_status: Status codes retried for retry_methods.
            api_key: API key (Basic, sent as is).
            email: Login email for password mode.
            password: Login password for password mode.
            org_id: Org for password mode.
            dataplane: Dataplane uid, sent as X-Nexla-Dataplane on /token calls.
        """
        service_key, api_key, access_token = resolve_credentials(
            service_key, api_key, access_token, email, password
        )
        base_url = resolve_base_url(base_url)

        self.api_url = base_url.rstrip("/")
        self.api_version = api_version

        self._trace_enabled = False
        if trace_enabled is True:
            self._trace_enabled = True
        elif trace_enabled is None and telemetry.is_tracing_configured():
            logger.debug(
                "Global OpenTelemetry configuration detected. Enabling tracing for Nexla SDK."
            )
            self._trace_enabled = True

        self.tracer = telemetry.get_tracer(self._trace_enabled)
        # Per task: each concurrent task sees the headers of its own last request.
        self._response_headers: ContextVar[Optional[Mapping[str, Any]]] = ContextVar(
            f"nexla_sdk_response_headers_{id(self)}", default=None
        )

        self.http_client: AsyncHttpClientInterface = http_client or AsyncHttpxClient(
            timeout=timeout,
            max_retries=max_retries,
            retry_methods=retry_methods,
            retry_on_status=retry_on_status,
            tracer=self.tracer,
        )

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
        self.raw = RawOperationsClient(self)

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
        self.validators = ValidatorsResource(self)
        self.service_keys = ServiceKeysResource(self)
        self.flow_triggers = FlowTriggersResource(self)
        self.clusters = ClustersResource(self)
        self.cluster_endpoints = ClusterEndpointsResource(self)
        self.api_keys = ApiKeysResource(self)
        self.connectors = ConnectorsResource(self)
        self.vendors = VendorsResource(self)
        self.auth_templates = AuthTemplatesResource(self)

    async def get_access_token(self) -> str:
        """Return a valid access token. Service keys obtain one when needed.

        Returns:
            A valid access token string.

        Raises:
            AuthenticationError: If no valid token is available or refresh fails.
        """
        return await self.auth_handler.ensure_valid_token()

    async def refresh_access_token(self) -> str:
        """Obtain a fresh token and return it. Access tokens cannot be refreshed.

        Raises:
            AuthenticationError: If token refresh fails.
        """
        await self.auth_handler.refresh_session_token()
        return self.auth_handler.get_access_token()

    async def switch_org(self, org_id: int) -> TokenResponse:
        """Switch the session to another org (POST /token/refresh?org_id=).

        Args:
            org_id: Org ID to switch to.

        Returns:
            The new token response.
        """
        return await self.auth_handler.switch_org(org_id)

    async def logout(self) -> None:
        """End the session. Calls POST /token/logout and clears the local token."""
        await self.auth_handler.logout()

    def create_webhook_client(self, api_key: str) -> WebhooksResource:
        """Create an async webhook client that uses this client's HTTP transport.

        Args:
            api_key: Nexla API key for webhook authentication.

        Returns:
            WebhooksResource. Its send methods are coroutines.
        """
        return WebhooksResource(api_key=api_key, http_client=self.http_client)

    @property
    def last_response_headers(self) -> Mapping[str, Any]:
        """Headers of the last response in the current task. Empty before any request.

        paginate() reads this after each list() call.
        """
        return self._response_headers.get() or {}

    async def request(
        self, method: str, path: str, **kwargs: Any
    ) -> Union[Dict[str, Any], None]:
        """Send a request to the Nexla API. Return the body, or None for 204.

        Raises:
            AuthenticationError: If authentication fails.
            ServerError: If the API returns an error.
        """
        body, _ = await self.request_with_headers(method, path, **kwargs)
        return body

    async def request_with_headers(
        self, method: str, path: str, **kwargs: Any
    ) -> Tuple[Union[Dict[str, Any], None], Any]:
        """Send a request to the Nexla API. Return (body, response headers).

        Raises:
            AuthenticationError: If authentication fails.
            ServerError: If the API returns an error.
        """
        self._response_headers.set({})
        url = f"{self.api_url}{path}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # If custom headers are provided, merge them with the default headers
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            (
                body,
                response_headers,
            ) = await self.auth_handler.execute_authenticated_request_with_headers(
                method=method, url=url, headers=headers, **kwargs
            )
            self._response_headers.set(response_headers)
            return body, response_headers
        except HttpClientError as e:
            raise map_http_error(e, method, path, url, kwargs) from e
        except NexlaError:
            # Preserve explicit NexlaError subclasses (e.g., AuthenticationError)
            raise
        except Exception as e:
            raise unexpected_request_error(e, method, path, url, kwargs) from e

    async def aclose(self) -> None:
        """Close the HTTP transport. Call this when the client is no longer needed."""
        await self.http_client.aclose()

    async def __aenter__(self) -> AsyncNexlaClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()
