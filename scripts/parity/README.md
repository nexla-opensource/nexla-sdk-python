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
