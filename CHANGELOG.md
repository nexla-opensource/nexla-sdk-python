# Changelog

All notable changes to the Python SDK (`nexla-sdk`) are listed here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Each release is a Git tag in the form `v<major>.<minor>.<patch>`. The package
version comes from the tag through `setuptools_scm`. Tags that start with
`ts-sdk-` belong to the TypeScript SDK and are not listed here.

## [Unreleased]

### Added

- Resources: `tools`, `tool_sets`, `mcp_sessions`, and `sdk_applications`.
- Missing API routes for data sources, destinations, data sets, credentials,
  credential groups, custom data flows, flows, notifications, organizations,
  lookups, validators, code containers, cluster endpoints, OAuth, and GenAI
  configs.
- Credential modes: API key (`api_key`), password login (`email`, `password`,
  optional `org_id`), and the `dataplane` option. Explicit options take
  precedence over environment variables.
- `NexlaClient.switch_org(org_id)` to change the org of the session.
- Typed errors for every response body shape: `AccountLockedError` (HTTP 423),
  `NexlaTimeoutError`, and `NexlaConnectionError`. `NexlaError` exposes
  `error_code`, `body`, `request_id`, `method`, and `url`.
- Header-driven pagination. The paginator reads `X-*` headers and `Link`
  `rel="Next"`. `Page` exposes `total_count`, `total_pages`, and `has_next`.
- Typed common list parameters (`expand`, `sort_by`, `sort_order`, `status`,
  `tags`, `name`, `access_role`, `from_date`, `to_date`, `org_id`) and the full
  `AccessRole` set.
- Retry and timeout options: `timeout`, `max_retries`, `retry_methods`, and
  `retry_on_status`.
- Deprecation helper (`nexla_sdk/utils/deprecation.py`). Deprecated methods keep
  their request and emit `DeprecationWarning`.
- Contract tests. 21 shared fixtures replay through the real client.
- Quality gates: Ruff lint (E, F, W, I, B, UP) and format checks, mypy strict on
  the core package and models, and an 85% unit coverage floor in CI.
- Repository files: MIT `LICENSE`, `CHANGELOG.md`, examples for auth modes,
  pagination, and error handling, the behavior spec, and the operation drift
  check.
- `scripts/build_skill.py` builds `nexla.skill` from `skills/nexla/`. CI fails
  when the committed archive is stale.

### Changed

- HTTP retries. POST and PATCH requests are no longer retried on 502, 503, or
  504, because a retried create can run twice. Read errors and 502, 503, and
  504 retry only for idempotent methods (GET, HEAD, OPTIONS, PUT, DELETE).
  Connect errors and 429 responses retry for all methods.
- HTTP 429 handling. The wait comes from `error.retry_after` in the body, then
  from the `Retry-After` header. A wait longer than 60 seconds raises
  `RateLimitError` and is not retried. Backoff before retry `n` is
  `min(8, 0.5 * 2^(n-1))` seconds plus up to 100 ms of jitter.
- Timeouts default to `(connect 10 s, read 60 s)`. The read timeout was 10 s.
- Error messages come from the response body. The status code selects the
  class. An empty body gives a message such as `401 Unauthorized`.
- `paginate()` default `per_page` is 100. It was 20. Each request sends
  `per_page`.
- A token response without `access_token` raises `AuthenticationError`. It
  previously stored `None` and sent `Bearer None`.
- `Source.source_type` is optional and defaults to `None`.
- `AccessRole` adds `owner_only`, `admin_only`, `collaborator_only`, `sharer`,
  `sharer_only`, `member`, and `all`. Existing members are unchanged.
- `approval_requests.reject()` and `cancel()` return `None`, as the API does.
  `approve()` still returns the request.
- `BaseResource` is generic over the model type. Type annotations changed in
  several modules. Runtime behavior is unchanged.
- The release workflow runs unit tests before it builds the package. It fails
  if the sdist or wheel does not contain `LICENSE`.
- `CONTRIBUTING.md` and the docs site point to this file. The docs-site
  changelog page is a pointer.

### Fixed

- HTTP methods and paths now match the backend routes:
  - `organizations.add_custodians` and `marketplace.add_domain_custodians`
    send PUT (add). They sent POST.
  - `approval_requests.reject` sends PUT. It sent DELETE.
  - `notifications.delete_all` sends DELETE to `/notifications`.
  - `org_auth_configs.list_all` calls `/api_auth_configs`.
  - `organizations.activate_rate_limited_sources` sends PUT `/orgs/{id}` with
    an `action` field.
  - `flows.get_flow_logs` sends `level`. The `severity` argument is an alias.
- `get_accessors`, `add_accessors`, `replace_accessors`, and `delete_accessors`
  no longer raise `AttributeError` on a non-empty response.
- A refused connection or DNS failure raises `NexlaConnectionError`. It raised
  `NexlaTimeoutError`.
- `pytest -m unit` runs every unit test in `tests/unit/`. About 110 tests
  without an explicit marker were skipped.
- Coverage and pytest settings in `pyproject.toml` apply. The old settings in
  `pytest.ini` were ignored.
- The `delete_org_settings` warning names `delete_org_setting`, the method that
  calls an existing route.

### Deprecated

- `organizations.update_custodians`: alias of `add_custodians`. The old method
  sent PUT, which adds custodians.
- `marketplace.update_domain_custodians`: alias of `add_domain_custodians`.
- `flows.get_flow_logs(severity=...)`: use `level=`.
- Methods whose route does not exist on the API. Each keeps its request and
  emits `DeprecationWarning`: `genai.delete_org_settings`,
  `projects.{get,add,replace,remove}_data_flows_legacy`,
  `data_flows.{list,create}_{data_source,data_sink}_flow(s)`,
  `data_flows.get_{data_source,data_sink}_audit_log`, `cubejs.query`,
  `sources.validate_config`, `destinations.validate_config`,
  `nexsets.catalog_add`, and `organizations.{get,update}_auth_setting(s)`.

### Removed

- `nexsets.list_catalog_refs_for_set`. The route is super-user only. The method
  was added and removed before a release.

## [1.0.8] - 2026-05-27

- Added an optional `access_role` query parameter to `status_metrics`.
- Fixed tests.

## [1.0.7] - 2026-05-14

- Fixed the `active_flows_metrics` path and the `LogEntry.impersonator_id` type.

## [1.0.6] - 2026-05-11

- Fixed flow-log endpoints and added `/health/*` primitives.
- Added release process documentation.

## [1.0.5] - 2026-05-08

- Added `list_docs`, `update_docs`, and `copy_docs` on `NexsetsResource`.

## [1.0.4] - 2026-05-07

- Fixed flow run status, flow log models, and resource type paths.
- Added `copy_and_replace_credentials` on `FlowsResource`.

## [1.0.3] - 2026-03-03

- Added monitoring endpoint methods and explicit parameters for MCP integration.

## [1.0.2] - 2026-02-11

- Made `DataMapInfo.description` and `NotificationSetting.resource_id` optional.
- Fixed Sentry-reported validation errors.
- Added the Nexla skill documentation (`nexla.skill`).

## [1.0.1] - 2025-10-31

- Added new SDK resources, docs, and unit tests.

## [1.0.0] - 2025-09-25

- Released the Nexla SDK V2 line.
- Added `get_user_by_email` to the users resource.
- Refactored authentication and added `refresh_access_token`.
- Updated packaging to use `setuptools_scm` version management.

## [0.1.8] - 2025-06-19

- Added webhook delivery tracking, webhook test and retry endpoints, and schema
  template helpers.
- Added a test for `users.get_by_email`.

## [0.1.7] - 2025-06-18

- Improved token management in `TokenAuthHandler`. Added
  `NexlaClient.refresh_access_token()`.

## [0.1.6] - 2025-06-17

- Tagged on the same commit as 0.1.5. No code changes.

## [0.1.5] - 2025-06-17

- Adjusted `NexlaClient` for pagination and serialization edge cases.

## [0.1.4] - 2025-06-17

- Refactored authentication handling. Simplified service key handling.

## [0.1.3] - 2025-06-11

- Updated `pyproject.toml` metadata and the publishing workflow.

[Unreleased]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v1.0.8...HEAD
[1.0.8]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v1.0.7...v1.0.8
[1.0.7]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v1.0.6...v1.0.7
[1.0.6]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v1.0.5...v1.0.6
[1.0.5]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v1.0.4...v1.0.5
[1.0.4]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v0.1.8...v1.0.0
[0.1.8]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/nexla-opensource/nexla-sdk-python/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/nexla-opensource/nexla-sdk-python/tree/v0.1.3
