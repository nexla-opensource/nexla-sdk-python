---
name: "nexla-data-flows-operator"
description: "Build, deploy, monitor, and troubleshoot production Nexla data pipelines via Python SDK or REST API. Use for flow setup, data transformation pipelines, schema management, access control, credential rotation, batch operations, error recovery, monitoring, CI/CD integration, and operational troubleshooting."
---

**Requirements**: Python >= 3.8, nexla_sdk >= 2.0.0 | **License**: MIT

## What this skill is for
- Build or modify Nexla pipelines end-to-end: credential → source → nexset → destination → flow.
- Operate and troubleshoot active data flows with repeatable checks and safe retries.

## When to use this skill
- **Build flows**: Create credential → source → nexset → destination → flow pipelines
- **Transform pipelines**: Create reusable transforms, apply to nexsets, validate output
- **Access control**: Grant team/user access, manage permissions, audit changes
- **Production automation**: CI/CD deployment, batch updates, scheduled operations
- **Error recovery**: Retry strategies, circuit breakers, transient failure handling
- **Monitoring**: Health checks, metrics tracking, alerting, SLA monitoring
- **Advanced workflows**: Credential rotation, schema migration, data quality checks
- **Troubleshooting**: Debug flow failures, analyze logs/metrics, recover from errors
- **Webhooks**: Push data to Nexla via webhook sources
- **Async tasks**: Manage background jobs, exports, imports
- **AI integration**: Configure GenAI for documentation suggestions

## Quick start
1) Set env vars (see `.env` template in `EXAMPLES.md`).
2) Run `python scripts/nexla_quickstart.py` to validate auth and list resources.
3) Use the step-by-step recipes in `EXAMPLES.md`.

## Available scripts
- `scripts/list_resources.py`: List/filter resources by type or name.
  - `python scripts/list_resources.py --type sources --name "orders" --limit 5`
- `scripts/deploy_flow.py`: Deploy flow config with validation and rollback.
  - `python scripts/deploy_flow.py --print-schema`
- `scripts/get_resource_logs.py`: Fetch flow logs for a resource run.
  - `python scripts/get_resource_logs.py --resource-type data_sets --resource-id 123`
- `scripts/manage_access.py`: Manage access control for resources.
  - `python scripts/manage_access.py --operation grant --resource-type sources --resource-id 123 --accessor-type TEAM --accessor-id 42 --role operator`

## Decision framework: REST vs SDK vs Scripts

| Scenario | Best Choice | Rationale |
|----------|-------------|-----------|
| One-time setup | **REST** (cURL) | Quick ad-hoc commands, no dependencies |
| Repeatable workflows | **Python SDK** | Type safety, retries, pagination, error handling |
| Production deployment | **Scripts** (in this skill) | Tested patterns, error recovery, idempotency |
| CI/CD integration | **Scripts** + SDK | Automated deployment, validation, rollback |
| Monitoring/health checks | **Scripts** + SDK | Scheduled polling, alerting, SLA tracking |
| Debugging/troubleshooting | **REST** + Scripts | Quick diagnostics + systematic debugging |

## Production readiness checklist
Before deploying flows to production, ensure:
- [ ] Credentials validated via `probe()` before use
- [ ] Idempotency: search by name/tag before create operations
- [ ] Error handling: wrap all operations in try/except with retry logic
- [ ] Flow isolation: pause flows before structural changes, activate after validation
- [ ] Monitoring: set up health checks, metric polling, alerting
- [ ] Access control: configure accessors, verify permissions
- [ ] Audit trail: enable logging, track resource changes
- [ ] Rollback plan: test flow pause/copy/delete procedures
- [ ] Rate limiting: implement backoff, respect retry-after headers
- [ ] Secrets management: use env vars, never commit credentials

## Error resilience patterns
- **Transient failures** (429, 5xx): Use exponential backoff retry (see `scripts/retry_helpers.py`)
- **Credential errors**: Probe before use, implement rotation workflow
- **Transform failures**: Validate on samples, test incrementally
- **Flow activation failures**: Check upstream dependencies, verify access
- **Rate limits**: Respect `retry_after`, use circuit breakers for sustained errors
- **Partial failures**: Implement checkpoint/resume patterns for batch operations

See `REFERENCE.md` → Error Handling Deep Dive for implementation patterns.

## Monitoring strategy
- **Health checks**: Poll flow status, check last run timestamp (see `scripts/health_check.py`)
- **Metrics tracking**: Daily aggregates, run-level summaries, error rates
- **Alerting**: Detect failures, SLA breaches, credential expiry
- **Debugging**: Analyze run logs, compare successful vs failed runs
- **SLA tracking**: Monitor latency, throughput, success rate

See `REFERENCE.md` → Monitoring & Observability for detailed patterns.

## Where to go deeper
- **Technical deep dives**: `REFERENCE.md` (error handling, retry strategies, monitoring, advanced workflows, webhooks, async tasks, GenAI)
- **Transform & schema patterns**: `TRANSFORMS.md` (reusable transforms, attribute transforms, schema validation)
- **Access control patterns**: `ACCESS_CONTROL.md` (team access, permission management, audit)
- **Copy-paste recipes**: `EXAMPLES.md` (18 recipes covering build, deploy, transform, access, monitor, webhooks, async tasks, GenAI)
- **Production scripts**: `scripts/` directory (deployment, health checks, batch operations, access management)
- **Quick validation**: Run `python scripts/nexla_quickstart.py` to verify auth and connectivity
