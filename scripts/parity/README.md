# Parity Tooling

This folder contains local tooling for validating Python SDK parity against:

- `plugin-redoc-0.yaml` (OpenAPI spec; not committed, place it at the repo root for local runs)
- `config/routes.rb` from the admin API checkout
- `nexla_sdk/resources/*.py` request surfaces

## Commands

Generate operation map used by `NexlaClient.raw`:

```bash
python scripts/parity/generate_operation_map.py
```

Build parity matrices and diffs:

```bash
python scripts/parity/build_matrices.py \
  --admin-routes <admin-api-checkout>/config/routes.rb
```

Outputs are written under `artifacts/parity/`.

## Operation drift check

`extract_sdk_operations.py` reads `nexla_sdk/resources/*.py` with the `ast` module. It lists every HTTP operation the SDK sends (`METHOD /path`) and the methods that send it. The list is committed as `sdk_operations.json`.

`check_operation_map_sync.py` runs in CI. It compares the current SDK with the manifest and fails on any added, removed, or re-owned operation.

### Update the manifest

Run this after you add, remove, or rename an SDK route, then commit the manifest:

```bash
python scripts/parity/extract_sdk_operations.py
```

The extractor fails, and writes nothing, when a `_make_request` call cannot be resolved. Make the method or path a literal, or extend `extract_sdk_operations.py` to read the pattern.

### Check against the backend spec (optional)

Set `NEXLA_PUBLIC_SPEC` to a public backend spec JSON. Build the file with `nexla-sdk-js/scripts/backend-spec/build_public_spec.py`, which runs in the backend checkout.

```bash
NEXLA_PUBLIC_SPEC=/path/to/nexla-api.public.json python scripts/parity/check_operation_map_sync.py
```

| Result | Effect |
|---|---|
| SDK operation missing from the backend spec | Fails (exit 1) |
| Backend operation missing from the SDK | Reported. Does not fail. |
| `NEXLA_PUBLIC_SPEC` points to a missing file | Setup error (exit 2) |

The backend check needs the public spec, so CI does not run it. Run it locally before a release.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Pass |
| 1 | Drift, or an SDK operation missing from the backend spec |
| 2 | Setup error: missing manifest, missing spec file, or unresolved call |

### Operation map (local only)

`check_operation_map_sync.py` also compares `nexla_sdk/generated/operation_map.py` with `plugin-redoc-0.yaml` when that file is at the repo root. The file is not committed. Without it, the script prints a skip line.
