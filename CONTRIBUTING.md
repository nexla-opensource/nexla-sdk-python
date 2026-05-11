Contributing to nexla-sdk
=========================

Thanks for your interest in contributing!

Setup
- Python 3.8+ is required.
- Install dev deps: `pip install -e .[dev]`
- Run unit tests: `pytest -m unit`

Coding standards
- Pydantic v2 models.
- Keep public API stable; deprecate before breaking.
- Run pre-commit: `pre-commit install` then commit.

Testing
- Prefer unit tests with mocks.
- Avoid network in unit tests.
- Add integration tests only when necessary.

Release
------

Versions are derived from Git tags by `setuptools_scm` (no manual version bumps). Tag format: `v<major>.<minor>.<patch>` (e.g. `v1.1.0`).

**Prerequisites:**
- Write access to the GitHub repository (to create releases).
- The `release` GitHub environment must be configured with PyPI trusted publishing enabled.

**Pre-release checklist:**
1. Ensure CI passes on `main` (ruff lint + unit tests across Python 3.8–3.12).
2. Update `docs-site/docs/changelog.md` with user-facing changes under a new version heading.
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
- Docs site rebuilds automatically on pushes to `main` (via `.github/workflows/docs.yml`), not on tag pushes.

**Version scheme notes:**
- `setuptools_scm` config: `version_scheme = "no-guess-dev"`, `local_scheme = "no-local-version"`.
- On a tagged commit, the version is the tag (e.g. `1.1.0`).
- Between tags, dev versions look like `1.1.1.dev1` (no dirty/local suffix).

**Troubleshooting:**
- **Version mismatch**: Ensure the tag points to the exact commit on `main` and that the tag name starts with `v`.
- **Publishing fails**: Check that the `release` GitHub environment exists and has PyPI trusted publisher configured (no API token needed).
- **Tag already exists**: Delete the remote tag and GitHub release, then recreate. Do not re-use a tag name for a different commit.

