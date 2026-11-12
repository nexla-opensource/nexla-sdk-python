# Repository Guidelines

## Project Structure & Module Organization
- `nexla_sdk/` — core SDK (client, resources, models).
- `tests/` — pytest suites: `unit/`, `integration/`, `property/`, `performance/` plus `run_tests.py` helper.
- `examples/` — runnable usage snippets.
- `docs-site/` — Docusaurus site and API doc generator.
- Root config: `pyproject.toml` (build, deps, pytest, coverage, ruff, mypy), `.pre-commit-config.yaml` (lint/format/type check).

## Build, Test, and Development Commands
- Setup dev env: `python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]`
- Lint/format (pre-commit): `pre-commit install && pre-commit run -a`
- Lint only: `ruff check nexla_sdk` • Format: `ruff format` (Black-compatible) • Format check: `ruff format --check .`
- Type check: `mypy` (strict, scope in `pyproject.toml` `[tool.mypy] files`)
- Unit tests: `pytest -m unit -q` or `python tests/run_tests.py`
- Coverage: `pytest --cov=nexla_sdk --cov-report=term-missing`. CI fails below 85%: add `--cov-fail-under=85`.
- Integration tests (require creds): `export NEXLA_SERVICE_KEY=... && pytest -m integration -vv`

## Coding Style & Naming Conventions
- Python 3.8+; 4‑space indent; type hints required for public APIs.
- Naming: modules/functions `snake_case`, classes `CapWords`, constants `UPPER_SNAKE_CASE`.
- Keep modules focused; colocate resource-specific helpers under the relevant subpackage.
- Enforce style with Ruff lint and Ruff format (via pre-commit). No unused imports or dead code.

## Testing Guidelines
- Frameworks: pytest, pytest-cov, Hypothesis (property tests), responses/freezegun for I/O/time.
- Test names: files `tests/**/test_*.py`; functions `test_*`; optional class groups `Test*`.
- Markers: `unit` (default), `integration`, `property`, `performance`, `slow` (see `[tool.pytest.ini_options]` in `pyproject.toml`).
- Run focused suites: `python tests/run_tests.py --unit|--integration --coverage`.
- Credentials for integration: use `.env` or `tests/.env` (see `.env.example`, `tests/env.template`). Never commit secrets.

## Commit & Pull Request Guidelines
- Commits: imperative, concise; prefer Conventional style: `feat:`, `fix:`, `docs:`, `refactor:`, `test:` (e.g., `feat: add webhook delivery history`).
- PRs: clear description, linked issues, test plan (commands/output), and docs/examples updates when behavior changes.
- CI must pass (lint + unit tests across supported Python versions). Include new/updated tests for any code changes.

## Security & Configuration Tips
- Do not hardcode tokens or URLs; read from env (`NEXLA_API_URL`, `NEXLA_SERVICE_KEY`).
- Use `.env.example` as a template; scrub credentials from logs and fixtures.

