#!/usr/bin/env python3
"""Deploy Nexla flow with validation and rollback."""

import argparse
import json
import sys
import time
from typing import Any, Dict, List, Tuple

try:
    from nexla_sdk import CredentialError, FlowError, NexlaClient
except ImportError:
    print("Error: nexla_sdk not installed. Run: pip install nexla-sdk", file=sys.stderr)
    sys.exit(1)


def get_config_schema() -> Dict[str, Any]:
    """Return the expected deployment config schema."""
    return {
        "type": "object",
        "required": ["credential_id", "source", "destination"],
        "properties": {
            "credential_id": {
                "type": "integer",
                "description": "Credential ID to validate before deploying",
            },
            "source": {
                "type": "object",
                "required": [
                    "name",
                    "source_type",
                    "data_credentials_id",
                    "source_config",
                ],
                "properties": {
                    "name": {"type": "string"},
                    "source_type": {"type": "string"},
                    "data_credentials_id": {"type": "integer"},
                    "source_config": {"type": "object"},
                },
            },
            "destination": {
                "type": "object",
                "required": ["name", "sink_type", "data_credentials_id", "sink_config"],
                "properties": {
                    "name": {"type": "string"},
                    "sink_type": {"type": "string"},
                    "data_credentials_id": {"type": "integer"},
                    "sink_config": {"type": "object"},
                },
            },
        },
    }


def deploy_flow(
    client: NexlaClient, config: Dict[str, Any], dry_run: bool = False
) -> Dict[str, Any]:
    """
    Deploy flow with validation and rollback on failure.

    Args:
        client: NexlaClient instance
        config: Deployment configuration dict
        dry_run: If True, validate without creating resources

    Returns:
        Deployment result dict with status and details

    Config structure:
        {
          "credential_id": 123,
          "source": {
            "name": "my-source",
            "source_type": "s3",
            ...
          },
          "destination": {
            "name": "my-destination",
            "sink_type": "snowflake",
            "data_credentials_id": 456,
            ...
          }
        }
    """
    steps = []
    rollback_ids: List[Tuple[str, int]] = []

    try:
        # Step 1: Validate credential
        print("[1/5] Validating credential...")
        try:
            probe = client.credentials.probe(config["credential_id"])
            if probe.get("status") != "success":
                raise CredentialError("Credential probe failed")
            steps.append("credential_validated")
            print("✓ Credential validated")
        except Exception as e:
            raise CredentialError(f"Credential validation failed: {e}") from e

        if dry_run:
            print("\nDRY RUN: Would create source/destination/flow")
            print(f"Source: {config['source']['name']}")
            print(f"Destination: {config['destination']['name']}")
            return {"status": "dry_run_success", "steps": steps}

        # Step 2: Create source
        print("[2/5] Creating source...")
        from nexla_sdk.models.sources.requests import SourceCreate

        source = client.sources.create(SourceCreate(**config["source"]))
        rollback_ids.append(("source", source.id))
        steps.append(f"source_created:{source.id}")
        print(f"✓ Source created (ID: {source.id})")

        # Step 3: Wait for discovery
        print("[3/5] Waiting for nexset discovery...")
        max_wait = 60
        waited = 0
        poll_interval = 5

        while waited < max_wait:
            source = client.sources.get(source.id, expand=True)
            if source.data_sets:
                print(f"✓ Discovered {len(source.data_sets)} nexset(s)")
                break
            time.sleep(poll_interval)
            waited += poll_interval
            print(f"  Waiting... ({waited}s / {max_wait}s)")

        if not source.data_sets:
            raise FlowError("No nexsets discovered from source after 60s")

        steps.append(f"nexsets_discovered:{len(source.data_sets)}")

        # Step 4: Create destination
        print("[4/5] Creating destination...")
        from nexla_sdk.models.destinations.requests import DestinationCreate

        # Use first discovered nexset
        dest_config = config["destination"].copy()
        dest_config["data_set_id"] = source.data_sets[0]

        destination = client.destinations.create(DestinationCreate(**dest_config))
        rollback_ids.append(("destination", destination.id))
        steps.append(f"destination_created:{destination.id}")
        print(f"✓ Destination created (ID: {destination.id})")

        # Step 5: Activate flow
        print("[5/5] Activating flow...")
        flow = client.flows.get_by_resource("data_sinks", destination.id)

        if not flow.flows:
            raise FlowError("No flow node found for destination")

        flow_id = flow.flows[0].id
        client.flows.activate(flow_id)
        steps.append(f"flow_activated:{flow_id}")
        print(f"✓ Flow activated (ID: {flow_id})")

        print("\n" + "=" * 60)
        print("✓ Deployment successful!")
        print("=" * 60)

        return {
            "status": "success",
            "steps": steps,
            "source_id": source.id,
            "destination_id": destination.id,
            "flow_id": flow_id,
            "nexset_ids": source.data_sets,
        }

    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"❌ Deployment failed: {e}")
        print(f"{'=' * 60}")

        if rollback_ids:
            print("\nRolling back...")

            # Rollback in reverse order
            for resource_type, resource_id in reversed(rollback_ids):
                try:
                    if resource_type == "source":
                        client.sources.delete(resource_id)
                        print(f"✓ Deleted source {resource_id}")
                    elif resource_type == "destination":
                        client.destinations.delete(resource_id)
                        print(f"✓ Deleted destination {resource_id}")
                except Exception as rollback_error:
                    print(f"❌ Rollback error: {rollback_error}", file=sys.stderr)

        return {
            "status": "failed",
            "error": str(e),
            "steps": steps,
            "rollback_performed": bool(rollback_ids),
        }


def main():
    """Main entry point for deployment script."""
    parser = argparse.ArgumentParser(
        description="Deploy Nexla flow with validation and rollback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example config file (flow_config.json):
{
  "credential_id": 123,
  "source": {
    "name": "production-orders",
    "source_type": "s3",
    "data_credentials_id": 123,
    "source_config": {
      "path": "s3://bucket/orders/",
      "file_format": "parquet"
    }
  },
  "destination": {
    "name": "warehouse-orders",
    "sink_type": "snowflake",
    "data_credentials_id": 456,
    "sink_config": {
      "database": "analytics",
      "schema": "raw",
      "table": "orders"
    }
  }
}

Example usage:
  python deploy_flow.py --config flow_config.json --dry-run
  python deploy_flow.py --config flow_config.json
  python deploy_flow.py --config flow_config.json --output deployment_result.json
        """,
    )
    parser.add_argument("--config", help="Flow configuration file (JSON)")
    parser.add_argument(
        "--print-schema",
        action="store_true",
        help="Print expected config schema and exit",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without creating resources"
    )
    parser.add_argument("--output", help="Output file for deployment result (JSON)")
    args = parser.parse_args()

    if args.print_schema:
        print(json.dumps(get_config_schema(), indent=2))
        sys.exit(0)

    if not args.config:
        print(
            "Error: --config is required unless --print-schema is used", file=sys.stderr
        )
        sys.exit(1)

    # Load configuration
    try:
        with open(args.config) as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate config structure
    required_fields = ["credential_id", "source", "destination"]
    for field in required_fields:
        if field not in config:
            print(f"Error: config missing required field: {field}", file=sys.stderr)
            sys.exit(1)

    # Initialize client
    try:
        client = NexlaClient()
    except Exception as e:
        print(f"Error initializing NexlaClient: {e}", file=sys.stderr)
        print(
            "Ensure NEXLA_SERVICE_KEY or NEXLA_ACCESS_TOKEN is set and valid",
            file=sys.stderr,
        )
        sys.exit(1)

    # Deploy flow
    result = deploy_flow(client, config, dry_run=args.dry_run)

    # Save result if requested
    if args.output:
        try:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\nDeployment result saved to {args.output}")
        except Exception as e:
            print(f"Error saving result: {e}", file=sys.stderr)

    # Print result
    print("\nDeployment result:")
    print(json.dumps(result, indent=2))

    # Exit with appropriate status code
    sys.exit(0 if result["status"] in ["success", "dry_run_success"] else 1)


if __name__ == "__main__":
    main()
