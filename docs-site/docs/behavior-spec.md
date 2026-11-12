---
id: behavior-spec
title: Behavior spec
description: Behavior rules shared by the Python and TypeScript SDKs.
slug: /behavior-spec
---

Both SDKs implement this contract. Source of truth: `admin-api-python` (FastAPI). Each rule cites the
backend file that drives it. A deliberate difference between the SDKs is listed in section 10.

## 1. Base URL and versioning
- Option `base_url` / `baseUrl`. Env `NEXLA_API_URL`. Default `https://dataops.nexla.io/nexla-api`.
- Versioning is path-only. The SDK does not depend on a vendor `Accept` type. It sends `Accept: application/json`.
- `User-Agent`: `nexla-sdk-python/<version>` and `nexla-sdk-js/<version>` (JS: only where the runtime allows it).

## 2. Authentication
Exactly one credential source. Precedence: explicit option > env var.

| Mode | Options | Env | Wire |
|---|---|---|---|
| Service key | `service_key` / `serviceKey` | `NEXLA_SERVICE_KEY` | `POST /token`, `Authorization: Basic <service_key>` (sent as is) |
| API key | `api_key` / `apiKey` | `NEXLA_API_KEY` | `POST /token`, `Authorization: Basic <api_key>` (sent as is) |
| Password | `email`, `password`, optional `org_id` / `orgId` | none | `POST /token`, `Authorization: Basic base64("email:password[:org_id]")` |
| Access token | `access_token` / `accessToken` | `NEXLA_ACCESS_TOKEN` | `Authorization: Bearer <token>`; no refresh |

- Optional `dataplane` option: sent as the `X-Nexla-Dataplane` request header on `/token` calls only.
  Unknown uid returns 400 `Dataplane not present: <uid>` (`token/module/_token_ops.py:143-153`).
- Token response model: `access_token`, `token_type`, `expires_in`, optional `sdk_application_id`, `user`, `org`,
  `org_membership` (`token/schema.py:233-275`). Unknown fields are kept.
- Session lifetime: `expires_in` from the response (backend default 86400 s). Refresh 3600 s before expiry
  (existing default and option name in each SDK kept).
- Concurrent callers that need a new token share one in-flight `/token` request.
- On 401 with a refreshable mode (service key, API key, password): obtain a new token once and retry the request once.
- Org switch: `switch_org(org_id)` / `switchOrg(orgId)` calls `POST /token/refresh?org_id=<id>` with the
  current Bearer token and replaces the session token. A token with no org gets 400
  `{"message":"Org context is not set"}` on every route except `/token/logout`.
- `logout()`: `POST /token/logout`.
- Token calls are never retried on 5xx (they are POSTs) but are retried on 429 and connect errors.

## 3. Timeouts and cancellation
- Python: `timeout=(connect, read)`; default `(10, 60)` seconds. A float sets both.
- JS: `timeoutMs`, default `60000`, implemented with `AbortController`. Every call also accepts `signal`.
- A timeout raises `NexlaTimeoutError`. A connection failure raises `NexlaConnectionError`.

## 4. Retries
Defaults: `max_retries = 3`. Backoff before attempt n (n = 1..3): `min(8, 0.5 * 2^(n-1))` seconds plus 0-100 ms jitter.

| Condition | Methods retried |
|---|---|
| Connect error (request not sent) | all |
| Read timeout / connection reset after send | idempotent only: GET, HEAD, OPTIONS, PUT, DELETE |
| 502, 503, 504 | idempotent only |
| 429 | all (rate limiter rejects before the route runs, `middleware/_rate_limiting.py`) |
| other status | none |

- The idempotent set is configurable: `retry_methods` / `retryMethods`. `retry_on_status` / `retryOn` stays configurable.
- 429 wait time, first match wins: body `error.retry_after` (seconds; the backend sends no header),
  then `Retry-After` header as seconds, then `Retry-After` as an HTTP date, then backoff.
  If the wait is over 60 s, do not retry; raise `RateLimitError` with `retry_after`.
- The request body is resent unchanged on retry.

## 5. Errors
Base class `NexlaError` with: `status_code`/`status`, `message`, `error_code` (or `undefined`),
`body` (parsed JSON, or text, or `None`), `request_id` (`X-Request-Id` response header), `method`, `url`.

| Status | Class |
|---|---|
| 400, 422 | `ValidationError` (body validation is 400 `{"message"}`, `main.py:341-389`; 422 only for pagination range and password expiry) |
| 401 | `AuthenticationError` |
| 403 | `AuthorizationError` |
| 404 | `NotFoundError` |
| 409 | `ResourceConflictError` |
| 423 | `AccountLockedError` (subclass of `AuthenticationError`) |
| 429 | `RateLimitError` (`retry_after` seconds) |
| 5xx and any other non-2xx | `ServerError` |
| timeout | `NexlaTimeoutError` (Python: subclass of `ServerError` for compatibility) |
| connection failure | `NexlaConnectionError` (Python: subclass of `ServerError` for compatibility) |

Body shapes and message extraction, first match wins:
1. `{"message", "error_code"?}` -> `message`, `error_code`.
2. `{"message", "detail"}` -> `message`; `detail` kept in `body`.
3. `{"error": {"type", "detail", "retry_after"}}` (429) -> message = `error.detail`, `error_code` = `error.type`.
4. `{"error": "<string>"}` -> message = that string.
5. `{"detail": "<string>"}` -> message = that string.
6. Non-JSON text (for example 429 `text/plain` `Retry later`) -> message = trimmed text.
7. Empty body (possible on 401, 403, 404, 423) -> message = `"<status> <reason>"`; never an empty string.
An empty or non-JSON error body still raises. It never returns `None`/`undefined`.

## 6. Pagination
- Wire: `page` and `per_page`. Pagination is on if either is > 0. With neither, the backend returns all rows.
  Default `per_page` on the backend is 10 (`data_sources/routes/_list.py:110-114`).
- Lists are bare JSON arrays.
- Headers: `X-Total-Count` (always when a pagination context exists); `X-Current-Page`, `X-Page-Count`,
  `X-Total-Page-Count`, `Link` with `rel="Previous"` / `rel="Next"` (capitalized) only when paginating.
- Iterator: Python `resource.paginate(...)` / `iter_pages()` and `iter_items()`; JS `client.paginate(...)`
  async iterator. Each sends an explicit `per_page` (default 100). Next page rules, first match wins:
  1. `X-Current-Page` and `X-Total-Page-Count` present -> stop when current >= total.
  2. `Link` header present -> continue only if it has `rel="Next"` (case-insensitive).
  3. Otherwise stop when the page has fewer than `per_page` items.
  Always stop on an empty page. Each page exposes `items`, `page`, `per_page`, `total_count`, `total_pages`.
- Do not follow the `Link` URL itself. Its host comes from `X-Forwarded-*` and it drops `/api/v1`.
  Increment `page` on the configured base URL instead.

## 7. Query parameters
Typed common params (names on the wire): `page`, `per_page`, `expand`, `sort_by`, `sort_order`
(`asc`|`desc`), `status`, `tags` (list joined with `,`), `name`, `access_role`, `from`, `to`, `org_id`.
- Python keyword names `from_date`/`to_date` map to wire `from`/`to`.
- `AccessRole` values: `admin`, `admin_only`, `all`, `collaborator`, `collaborator_only`, `member`, `operator`,
  `owner`, `owner_only`, `sharer`, `sharer_only` (`shared/schemas.py:49-72`). Upper case also accepted by the backend.
- Do not add params that are not in `tests_config/rails_query_parameters.json` for that route.

## 8. Method and naming rules
- Resource attribute names stay as they are today in each SDK. New resources use the backend folder name.
- Python methods: `snake_case`. JS generated methods: the spec `operationId` (snake_case), plus the existing
  short aliases (`list`, `get`, `create`, `update`, `delete`).
- HTTP method per operation must equal the backend route. Known fixes:
  `orgs/{id}/custodians` and `marketplace/domains/{id}/custodians`: GET list, PUT add, POST reset (replace all),
  DELETE remove. `approval_requests/{id}/reject`: PUT.

## 9. Webhooks (JS only)
- Default auth stays `query` (`?api_key=`), because the webhook host is not part of admin-api and header
  support cannot be confirmed from the backend. `authMethod: "header"` is documented as the safer choice when
  the host supports it. Keys in URLs can appear in proxy and server logs.

## 10. Deliberate differences
| Topic | Python | JS | Reason |
|---|---|---|---|
| Timeout | separate connect and read | one overall timeout | `fetch` has no connect timeout |
| Async | `AsyncNexlaClient` (httpx, extra `nexla-sdk[async]`) | native async | language |
| Network error classes | subclass `ServerError` | subclass `NexlaError` | keep existing Python `except ServerError` working |
