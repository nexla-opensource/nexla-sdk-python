Generate shared contract fixtures. Each fixture = one SDK call against a scripted HTTP exchange.

Fields:
  name, description
  client:   options the runner passes to the client (auth, retries). Runners must make backoff sleep a no-op.
  call:     {"op": <op name>, "args": {...}}  -- each runner maps op -> SDK call
  exchanges: ordered list of {"request": {method, path, query?, headers?, body?}, "response": {status, headers?, body?, text?}}
             "request" lists what the SDK MUST send (subset match on query/headers/body).
  expect:   {"result": <value>} or {"error": {class, status, message?, error_code?, retry_after?, request_id?}}
Ops: get_source(id) | create_source(body) | list_sources_all(per_page) | add_custodians(org_id, custodians)
     | reset_custodians(org_id, custodians) | reject_approval(request_id) | login() (forces a token fetch, then get_source(1))

The same files live in nexla-sdk-python/tests/contract/fixtures and
nexla-sdk-js/packages/ts-sdk/tests/contract/fixtures. MANIFEST.sha256 must match in both repos.
