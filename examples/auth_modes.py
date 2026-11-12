"""Authenticate with one credential mode, then make one read call.

Set the variables for exactly one mode:

- NEXLA_SERVICE_KEY                  service key
- NEXLA_API_KEY                      API key
- NEXLA_ACCESS_TOKEN                 access token (the SDK does not refresh it)
- NEXLA_EMAIL and NEXLA_PASSWORD     password login; NEXLA_ORG_ID is optional

Optional for every mode:

- NEXLA_API_URL                      API base URL
- NEXLA_DATAPLANE                    dataplane UID, sent on /token calls only
- NEXLA_SWITCH_ORG_ID                switch the session to this org after login

Usage:
    python examples/auth_modes.py

Never write credentials into source files. Read them from the environment.
"""

import os
import sys

from nexla_sdk import NexlaClient, NexlaError


def client_from_env() -> NexlaClient:
    """Build a client from the first credential mode whose variables are set."""
    common = {
        "base_url": os.getenv("NEXLA_API_URL"),
        "dataplane": os.getenv("NEXLA_DATAPLANE"),
    }
    if os.getenv("NEXLA_SERVICE_KEY"):
        return NexlaClient(service_key=os.environ["NEXLA_SERVICE_KEY"], **common)
    if os.getenv("NEXLA_API_KEY"):
        return NexlaClient(api_key=os.environ["NEXLA_API_KEY"], **common)
    if os.getenv("NEXLA_ACCESS_TOKEN"):
        return NexlaClient(access_token=os.environ["NEXLA_ACCESS_TOKEN"], **common)
    if os.getenv("NEXLA_EMAIL") and os.getenv("NEXLA_PASSWORD"):
        org_id = os.getenv("NEXLA_ORG_ID")
        return NexlaClient(
            email=os.environ["NEXLA_EMAIL"],
            password=os.environ["NEXLA_PASSWORD"],
            org_id=int(org_id) if org_id else None,
            **common,
        )
    raise SystemExit(
        "No credential mode is set. See the docstring at the top of this file."
    )


def main() -> int:
    try:
        client = client_from_env()
        me = client.users.get_current()
        print(f"Authenticated as: {me.get('email', 'unknown')}")

        switch_to = os.getenv("NEXLA_SWITCH_ORG_ID")
        if switch_to:
            client.switch_org(int(switch_to))
            print(f"Switched session to org {switch_to}")
            me = client.users.get_current()
            print(f"Current user after switch: {me.get('email', 'unknown')}")
    except NexlaError as error:
        print(f"Authentication or request failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
