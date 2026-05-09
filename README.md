# Nexla Python SDK

A Python SDK for interacting with the Nexla API.

## Installation

```bash
pip install nexla-sdk
```

## Authentication

The Nexla SDK requires a Service Key for authentication. You can create a service key from the Nexla UI:

1. Go to your Nexla UI instance (e.g., `https://dataops.nexla.io`)
2. Navigate to the **Authentication** screen in the **Settings** section
3. Click the **Create Service Key** button
4. Store the service key securely - it should be treated as highly sensitive since it is equivalent to your account password

## Quick Start

```python
from nexla_sdk import NexlaClient

# Initialize the client with your service key
client = NexlaClient(service_key="your_nexla_service_key")

# List flows — returns a list with one FlowResponse that contains flow nodes
flow_responses = client.flows.list()
for flow_response in flow_responses:
    for flow in flow_response.flows:
        print(f"Flow node: {flow.name}, ID: {flow.id}")

# List sources - returns a list of Source objects
sources = client.sources.list()
for source in sources:
    print(f"Source name: {source.name}, ID: {source.id}")

# Get a specific source - returns a Source object
source = client.sources.get(source_id)
print(f"Source details: {source.name}, type: {source.source_type}")

# Create a credential
credential_data = {
    "name": "My S3 Credential",
    "credentials_type": "s3",
    "credentials": {
        "access_key_id": "your_access_key",
        "secret_access_key": "your_secret_key", 
        "region": "us-east-1"
    }
}
credential = client.credentials.create(credential_data)
print(f"Created credential: {credential.id}")

# Create a data source
source_data = {
    "name": "My New Source",
    "description": "Created via SDK",
    "source_type": "s3",
    "data_credentials_id": credential.id,
    "source_config": {
        "path": "bucket/path/",
        "file_format": "json"
    }
}
new_source = client.sources.create(source_data)
print(f"Created source: {new_source.id}, name: {new_source.name}")
```

## Authentication Methods

The SDK supports two authentication methods:

### 1. Service Key Authentication (Recommended)

Service keys are long-lived credentials that obtain session tokens on demand (no refresh endpoint is used):

```python
client = NexlaClient(service_key="your_service_key")

# Or use environment variables
# export NEXLA_SERVICE_KEY="your_service_key"
# Optional: export NEXLA_API_URL="https://your-nexla-instance.com/nexla-api"
client = NexlaClient()
```

### 2. Direct Access Token Authentication

For temporary access using pre-obtained tokens (no refresh available):

```python
client = NexlaClient(access_token="your_access_token")

# Or use environment variables
# export NEXLA_ACCESS_TOKEN="your_access_token"
# Optional: export NEXLA_API_URL="https://your-nexla-instance.com/nexla-api"
client = NexlaClient()
```

## Core Resources

### Credentials

```python
# Create a credential
credential_data = {
    "name": "My S3 Credential",
    "credentials_type": "s3",
    "credentials": {
        "access_key_id": "xxx",
        "secret_access_key": "xxx",
        "region": "us-east-1"
    }
}
credential = client.credentials.create(credential_data)

# Test credential
probe_result = client.credentials.probe(credential.id)
print(f"Credential valid: {probe_result.get('status') in ('ok', 'success')}")

# Get credential tree structure
from nexla_sdk.models.credentials.requests import ProbeTreeRequest
tree_request = ProbeTreeRequest(depth=1, path="/")
tree = client.credentials.probe_tree(credential.id, tree_request)

# Get sample data
from nexla_sdk.models.credentials.requests import ProbeSampleRequest
sample_request = ProbeSampleRequest(path="/data/file.json")
sample = client.credentials.probe_sample(credential.id, sample_request)
```

### Sources

```python
# Create a source
source_data = {
    "name": "My Data Source",
    "source_type": "s3",
    "data_credentials_id": credential.id,
    "source_config": {
        "path": "bucket/path/",
        "file_format": "json"
    }
}
source = client.sources.create(source_data)

# Activate source
activated_source = client.sources.activate(source.id)

# Copy source
from nexla_sdk.models.sources.requests import SourceCopyOptions
copy_options = SourceCopyOptions(copy_access_controls=True)
copied_source = client.sources.copy(source.id, copy_options)
```

### Nexsets (Data Sets)

```python
# List nexsets
nexsets = client.nexsets.list()

# Get samples from a nexset
if nexsets:
    samples = client.nexsets.get_samples(
        set_id=nexsets[0].id,
        count=10,
        include_metadata=True
    )

# Create a transformed nexset
nexset_data = {
    "name": "Transformed Data",
    "parent_data_set_id": parent_nexset.id,
    "has_custom_transform": True,
    "transform": {
        "version": 1,
        "operations": [...]
    }
}
transformed = client.nexsets.create(nexset_data)
```

### Destinations

```python
# Create a destination
destination_data = {
    "name": "My Output",
    "sink_type": "s3",
    "data_credentials_id": credential.id,
    "data_set_id": nexset.id,
    "sink_config": {
        "path": "output/path/",
        "file_format": "parquet"
    }
}
destination = client.destinations.create(destination_data)

# Activate destination
activated_destination = client.destinations.activate(destination.id)
```

### Flows

```python
# Get flow by resource
flow = client.flows.get_by_resource(
    resource_type="data_sources",
    resource_id=source.id
)

# Activate entire flow
client.flows.activate(flow.flows[0].id, all=True)

# Pause flow
client.flows.pause(flow.flows[0].id, all=True)

# Copy flow
from nexla_sdk.models.flows.requests import FlowCopyOptions
copy_options = FlowCopyOptions(copy_access_controls=True)
copied_flow = client.flows.copy(flow.flows[0].id, copy_options)
```

## Pagination

The SDK provides built-in pagination support:

```python
# Get a paginator
paginator = client.sources.paginate(per_page=20)

# Iterate through all items
for source in paginator:
    print(source.name)

# Or iterate by pages
for page in paginator.iter_pages():
    print(f"Page {page.page_info.current_page}")
    for source in page:
        print(f"  - {source.name}")
```

## Observability: OpenTelemetry Tracing (Optional)

You can instrument the Nexla SDK with OpenTelemetry to emit spans for each outgoing API request. Tracing is optional and a no‑op unless enabled.

- Install optional tracing extras in your application environment:

```bash
pip install "nexla-sdk[tracing]"
# or install explicitly
pip install opentelemetry-distro opentelemetry-exporter-otlp
```

- Auto‑detection: If your app configures a global tracer provider, `NexlaClient` auto‑enables tracing. To control explicitly, use `trace_enabled=True|False`.

Example setup with console exporter:

```python
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

trace.set_tracer_provider(TracerProvider(resource=Resource({"service.name": "my-nexla-app"})))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

from nexla_sdk import NexlaClient

client = NexlaClient(service_key="<YOUR_SERVICE_KEY>")  # auto‑detects tracing
# or force: NexlaClient(service_key=..., trace_enabled=True)

flows = client.flows.list(page=1, per_page=1)  # emits a span
```

Notes:
- Tracing is a no‑op unless OpenTelemetry is installed and enabled.
- Spans include attributes like `http.method`, `url.full`, `server.address`, and `http.status_code`.
```

## Access Control

Manage access to resources:

```python
# Get current access rules
accessors = client.sources.get_accessors(source.id)

# Add user access
new_accessors = [{
    "type": "USER",
    "email": "user@example.com", 
    "access_roles": ["collaborator"]
}]
client.sources.add_accessors(source.id, new_accessors)

# Add team access
team_accessor = [{
    "type": "TEAM",
    "id": team_id,
    "access_roles": ["operator"]
}]
client.sources.add_accessors(source.id, team_accessor)

# Replace all accessors
client.sources.replace_accessors(source.id, new_accessors)
```

## Organizations and Teams

```python
# List organizations
orgs = client.organizations.list()

# Get organization members
members = client.organizations.get_members(org.id)

# Update organization members
from nexla_sdk.models.organizations.requests import OrgMemberList
member_list = OrgMemberList(members=[
    {"email": "new@example.com", "access_role": "admin"}
])
client.organizations.update_members(org.id, member_list)

# Create a team
team_data = {
    "name": "Data Team",
    "description": "Team for data operations"
}
team = client.teams.create(team_data)

# Add team members
from nexla_sdk.models.teams.requests import TeamMemberList
team_members = TeamMemberList(members=[
    {"email": "lead@example.com", "admin": True},
    {"email": "member@example.com", "admin": False}
])
client.teams.add_members(team.id, team_members)
```

## Projects

```python
# Create a project
project_data = {
    "name": "My Project",
    "description": "Data integration project"
}
project = client.projects.create(project_data)

# Add flows to project
from nexla_sdk.models.projects.requests import ProjectFlowList

# Option 1: Provide flow node IDs directly
flow_list = ProjectFlowList(flows=[flow_id])  # replace with actual flow node IDs
client.projects.add_flows(project.id, flow_list)

# Option 2: Provide resource identifiers (data flow edges)
# from nexla_sdk.models.projects.requests import ProjectFlowIdentifier
# flow_list = ProjectFlowList(data_flows=[ProjectFlowIdentifier(data_set_id=nexset.id)])
# client.projects.add_flows(project.id, flow_list)

# Get project flows
project_flows = client.projects.get_flows(project.id)
```

## Notifications

```python
# List unread notifications
notifications = client.notifications.list(read=0)

# Mark notification as read
client.notifications.mark_read([notification.id])

# Mark all notifications as read
client.notifications.mark_read("all")

# Get notification types
notification_types = client.notifications.get_types()

# Create notification setting
setting_data = {
    "notification_type_id": notification_type.id,
    "notification_channel_setting_id": channel_setting.id,
    "status": "ACTIVE"
}
setting = client.notifications.create_setting(setting_data)
```

## Metrics and Monitoring

```python
# Get daily metrics for a resource
metrics = client.metrics.get_resource_daily_metrics(
    resource_type="data_sources",
    resource_id=source.id,
    from_date="2024-01-01",
    to_date="2024-01-31"
)

# Get metrics by run
run_metrics = client.metrics.get_resource_metrics_by_run(
    resource_type="data_sources",
    resource_id=source.id,
    groupby="runId"
)

# Get rate limits
limits = client.metrics.get_rate_limits()
print(f"Rate limit: {limits}")
```

## Advanced Features

### Lookups (Data Maps)

```python
# Create a lookup table
lookup_data = {
    "name": "Product Mapping",
    "data_type": "string",
    "map_primary_key": "sku",
    "data_map": [
        {"sku": "ABC123", "name": "Product A", "price": 99.99},
        {"sku": "XYZ789", "name": "Product B", "price": 149.99}
    ]
}
lookup = client.lookups.create(lookup_data)

# Get lookup entries
entries = client.lookups.get_entries(lookup.id, "ABC*")

# Upsert lookup entries
new_entries = [
    {"sku": "DEF456", "name": "Product C", "price": 199.99}
]
client.lookups.upsert_entries(lookup.id, new_entries)
```

### User Management

```python
# Get user settings for the current authenticated user
settings = client.users.get_settings()

# Get user dashboard metrics
dashboard_metrics = client.users.get_dashboard_metrics(user_id)  # replace with a valid user_id (int)

# Update quarantine settings for a user
quarantine_config = {
    "cron_schedule": "0 0 * * *",
    "path": "/quarantine/exports/"
}
client.users.create_quarantine_settings(
    user_id=user_id,  # replace with a valid user_id (int)
    data_credentials_id=credential.id,
    config=quarantine_config
)
```

## Additional Example Features

The SDK examples cover advanced operations such as:

- Audit logging and compliance tracking
- User and team permissions management
- Data transformation and schema handling
- Metrics collection and monitoring
- Notification systems integration
- Quarantine settings for data validation

See the `examples/api/` directory for detailed examples of these operations.

## New Resources and Usage

The SDK includes additional helpers beyond core flows/sources/sinks:

### Code Containers, Transforms, Attribute Transforms

```python
# List code containers
containers = client.code_containers.list()

# Create a reusable record transform (aliased via /transforms)
from nexla_sdk.models.transforms import TransformCreate, TransformCodeOp
create_payload = TransformCreate(
    name="Uppercase Names",
    output_type="record",
    reusable=True,
    code_type="jolt_custom",
    code_encoding="none",
    code=[TransformCodeOp(operation="nexla.custom", spec={
        "language": "python",
        "encoding": "base64",
        "script": "ZGVmIHRyYW5zZm9ybShpbnB1dCwgbWV0YWRhdGEsIGFyZ3MpOiByZXR1cm4gaW5wdXQ=",
    })],
)
transform = client.transforms.create(create_payload)

# Attribute transforms
attr_transforms = client.attribute_transforms.list()
```

### Async Tasks

```python
from nexla_sdk.models.async_tasks import AsyncTaskCreate

# Start an async task
task = client.async_tasks.create(AsyncTaskCreate(type="EXPORT_DATA", args={"data_set_id": 123}))

# Poll status
status = client.async_tasks.get(task.id)

# Fetch result (if available)
result = client.async_tasks.result(task.id)

# Download artifact link (may return str or DownloadLink)
link = client.async_tasks.download_link(task.id)
```

### Approval Requests

```python
pending = client.approval_requests.list_pending()
if pending:
    approved = client.approval_requests.approve(pending[0].id)
```

### Runtimes

```python
from nexla_sdk.models.runtimes import RuntimeCreate

rt = client.runtimes.create(RuntimeCreate(name="python-3-11", language="python", version="3.11"))
client.runtimes.activate(rt.id)
client.runtimes.pause(rt.id)
```

### Marketplace

```python
domains = client.marketplace.list_domains()
if domains:
    items = client.marketplace.list_domain_items(domains[0].id)
```

### Org Auth Configs

```python
auth_configs = client.org_auth_configs.list()
if auth_configs:
    cfg = client.org_auth_configs.get(auth_configs[0].id)
```

### GenAI

```python
configs = client.genai.list_configs()
active = client.genai.show_active_config(gen_ai_usage="rag")
```

### Self Signup (Admin)

```python
requests = client.self_signup.list_requests()
blocked = client.self_signup.list_blocked_domains()
```

### Doc Containers and Data Schemas

```python
doc_audit = client.doc_containers.get_audit_log(doc_container_id=1001)
schema_audit = client.data_schemas.get_audit_log(schema_id=5001)
```

### Raw Operation-Level Access

```python
# List available OpenAPI operation ids
ops = client.raw.list_operations()

# Call by operation id with typed path/query/body slots
project_flows = client.raw.call(
    "get_project_flows",
    path_params={"project_id": 123},
)

# Direct raw HTTP helpers are also available
limits = client.raw.get("/limits")

# Backend-only or non-spec route access
approved = client.raw.request("POST", "/self_signup_requests/42/approve")
```

## Coverage Matrix

Mapping of major OpenAPI areas to SDK resources. All requests set `Accept: application/vnd.nexla.api.v1+json` and default base URL `https://dataops.nexla.io/nexla-api`.

- Session Management
  - Login/Logout: handled by client auth; `NexlaClient.logout()` ends session
- Flows: `client.flows` — list/get/get_by_resource/activate/pause/copy/delete; docs_recommendation; get_logs; get_metrics
- Sources: `client.sources` — CRUD/activate/pause/copy
- Destinations (Data Sinks): `client.destinations` — CRUD/activate/pause/copy
- Nexsets (Data Sets): `client.nexsets` — CRUD/activate/pause/samples/copy/docs_recommendation
- Credentials: `client.credentials` — CRUD/probe/probe_tree/probe_sample (async/request_id)
- Data Maps (Lookups): `client.lookups` — CRUD; entries get/upsert/delete
- Users: `client.users` — CRUD/settings/quarantine/metrics/audit_log/transfer
- Organizations: `client.organizations` — CRUD/members/account metrics/audit log/auth settings/custodians
- Teams: `client.teams` — CRUD/members
- Projects: `client.projects` — CRUD/flows add/replace/remove/search/get
- Notifications: `client.notifications` — list/delete/count/mark read/unread; channel/settings CRUD
- Metrics: `client.metrics` — resource daily/by-run; flow logs/metrics; rate limits
- Code Containers: `client.code_containers` — CRUD/copy/public list (accessors/audit via BaseResource)
- Transforms: `client.transforms` — CRUD/copy/public list
- Attribute Transforms: `client.attribute_transforms` — CRUD/public list
- Async Tasks: `client.async_tasks` — list/create/get/delete/rerun/result/download_link/types/explain_arguments
- Approval Requests: `client.approval_requests` — list_pending/list_requested/approve/reject
- Runtimes: `client.runtimes` — CRUD/activate/pause
- Marketplace: `client.marketplace` — domains CRUD; items list/create; custodians add/update/remove
- Org Auth Configs: `client.org_auth_configs` — list/all/get/create/update/delete
- GenAI Configurations/Org Settings: `client.genai` — configs CRUD; org settings CRUD; active_config
- Doc Containers: `client.doc_containers` — audit_log; (access control via BaseResource helpers)
- Data Schemas: `client.data_schemas` — audit_log; (access control via BaseResource helpers)
- Webhooks: `client.create_webhook_client(api_key=...)` for API-key authenticated webhook sends
- Full OpenAPI operation-level access: `client.raw.call(operation_id, ...)`

## Error Handling

The SDK provides specific exception types:

```python
from nexla_sdk.exceptions import (
    NexlaError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError
)

try:
    source = client.sources.get(999999)
except NotFoundError as e:
    print(f"Source not found: {e}")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except RateLimitError as e:
    print(f"Rate limited: {e}")
```

## Resource Path Mappings

The SDK uses the following API path mappings:
- **Credentials** → `/data_credentials`
- **Sources** → `/data_sources`
- **Destinations** → `/data_sinks`
- **Nexsets** → `/data_sets`
- **Lookups** → `/data_maps`
- **Flows** → `/flows`
- **Users** → `/users`
- **Organizations** → `/orgs`
- **Teams** → `/teams`
- **Projects** → `/projects`
- **Notifications** → `/notifications`
- **Metrics** → Various endpoints

## Common Resource Methods

All resources support these base methods:

- `list()` - List all resources
- `get(id)` - Get specific resource by ID
- `create(data)` - Create new resource
- `update(id, data)` - Update existing resource
- `delete(id)` - Delete resource
- `activate(id)` - Activate resource
- `pause(id)` - Pause resource
- `copy(id, options)` - Copy resource
- `paginate()` - Get paginated results
- `get_accessors(id)` - Get access control rules
- `add_accessors(id, accessors)` - Add access control rules
- `get_audit_log(id)` - Get audit log entries
 - `replace_accessors(id, accessors)` - Replace access control rules
 - `delete_accessors(id, accessors=None)` - Delete some or all access control rules

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/

# Run integration tests (requires API credentials)
export NEXLA_SERVICE_KEY="your_service_key"
export NEXLA_API_URL="https://your-nexla-instance.com/nexla-api"
pytest tests/integration/
```

### Parity Tooling

```bash
# Generate operation map for client.raw
python scripts/parity/generate_operation_map.py

# Build OpenAPI/admin-routes/SDK parity matrices
python scripts/parity/build_matrices.py \
  --admin-routes /Users/sakshammittal/Documents/GitHub/admin-api/config/routes.rb
```

### Setting Up Environment

```bash
# Create .env file
cat > .env << EOF
NEXLA_SERVICE_KEY=your_service_key
NEXLA_API_URL=https://dataops.nexla.io/nexla-api
EOF
```

## License

This project is licensed under the terms of the MIT license.

## Support

For API documentation and support:
- Visit: https://docs.nexla.com
- Email: support@nexla.com 
