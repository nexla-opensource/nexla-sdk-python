Contributing to nexla-sdk
=========================

Thanks for your interest in contributing!

Setup
- Python 3.8+ is required.
- Install dev deps: `pip install -e .[dev]`
- Run unit tests: `pytest -m unit`
- CI fails when unit coverage of `nexla_sdk` drops below 85%.
- Run the CI gates before you push:
  ```bash
  ruff check . && ruff format --check .
  mypy
  pytest -m unit --cov=nexla_sdk --cov-fail-under=85
  ```

Coding standards
- Pydantic v2 models.
- Keep public API stable; deprecate before breaking.
- Run pre-commit: `pre-commit install` then commit.
- Add a line under `## [Unreleased]` in `CHANGELOG.md` for each user-facing change.
- HTTP methods, retries, timeouts, error classes, and pagination must match `docs-site/docs/behavior-spec.md`.

Testing
- Prefer unit tests with mocks.
- Avoid network in unit tests.
- Add integration tests only when necessary.

Skill bundle (`nexla.skill`)
- `skills/nexla/` is the only source. Do not edit `nexla.skill` by hand.
- After you change `skills/nexla/`, run `python scripts/build_skill.py` and commit `nexla.skill`.
- The `skill-bundle` CI job runs `python scripts/build_skill.py --check`. It fails when the committed archive is stale.

Operation drift check
- `scripts/parity/sdk_operations.json` lists every HTTP operation the SDK sends. CI fails when the code and the list differ.
- After you add, remove, or rename a route, run `python scripts/parity/extract_sdk_operations.py` and commit the manifest.
- To compare with the backend, set `NEXLA_PUBLIC_SPEC` to a public spec JSON and run `python scripts/parity/check_operation_map_sync.py`. The check fails on SDK operations that the spec does not define. See `scripts/parity/README.md`.

Release
------

Versions are derived from Git tags by `setuptools_scm` (no manual version bumps). Tag format: `v<major>.<minor>.<patch>` (e.g. `v1.1.0`).

**Prerequisites:**
- Write access to the GitHub repository (to create releases).
- The `release` GitHub environment must be configured with PyPI trusted publishing enabled.

**Pre-release checklist:**
1. Ensure CI passes on `main` (ruff lint + unit tests across Python 3.8–3.12).
2. Move the entries under `## [Unreleased]` in `CHANGELOG.md` to a new `## [<version>] - <date>` heading. Add the compare link at the bottom of the file. The docs-site changelog page points to `CHANGELOG.md` and needs no edit.
3. Verify the version `setuptools_scm` will produce matches the tag you intend to create:
   ```bash
   pip install setuptools_scm && python -c "import setuptools_scm; print(setuptools_scm.get_version())"
   ```

**Creating a release (recommended — GitHub Releases UI):**
1. Go to **Releases → Draft a new release** on GitHub.
2. Create a new tag: `v<version>` (e.g. `v1.1.0`) targeting `main`.
3. Set the release title to the tag name.
4. Add release notes summarizing changes.
5. Click **Publish release**.

Alternatively, via the CLI:
```bash
git tag v1.1.0
git push origin v1.1.0
gh release create v1.1.0 --title v1.1.0 --notes "Summary of changes"
```

**What happens automatically (`.github/workflows/release.yml`):**
1. Triggered on GitHub Release `published` event.
2. Full git checkout (needed for `setuptools_scm` tag-based versioning).
3. Verifies version via `setuptools_scm.get_version()`.
4. Builds sdist and wheel with `python -m build`.
5. Publishes to PyPI via trusted publishing (`pypa/gh-action-pypi-publish`).
6. Posts a deployment summary with version, tag, commit, and package name.

**Post-release:**
- Confirm the package appears on PyPI: `pip install nexla-sdk==<version>`.
- Docs site builds on every pull request and on pushes to `main` (via `.github/workflows/docs.yml`). It deploys only on pushes to `main`, and only when Pages is enabled (see "GitHub Pages" below).

GitHub Pages
- The build job runs on every pull request. It does not need Pages.
- The deploy job is skipped unless the repository variable `PAGES_ENABLED` is `true`. A skipped job does not fail the workflow.
- To enable deployment:
  1. Go to **Settings → Pages**. Under **Build and deployment**, set **Source** to **GitHub Actions**.
  2. Go to **Settings → Secrets and variables → Actions → Variables**. Add a repository variable `PAGES_ENABLED` with the value `true`.
  3. Optional: add the variable `SITE_URL` with the public URL of the site. The build uses `https://example.com` when it is unset.
  4. Push to `main`, or re-run the **Docs Site** workflow on `main`.

**Version scheme notes:**
- `setuptools_scm` config: `version_scheme = "no-guess-dev"`, `local_scheme = "no-local-version"`.
- On a tagged commit, the version is the tag (e.g. `1.1.0`).
- Between tags, dev versions look like `1.1.1.dev1` (no dirty/local suffix).

**Troubleshooting:**
- **Version mismatch**: Ensure the tag points to the exact commit on `main` and that the tag name starts with `v`.
- **Publishing fails**: Check that the `release` GitHub environment exists and has PyPI trusted publisher configured (no API token needed).
- **Tag already exists**: Delete the remote tag and GitHub release, then recreate. Do not re-use a tag name for a different commit.

