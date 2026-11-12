"""
Example: Fetch Resources from Nexla API

This example demonstrates how to list and get resources for all available
resource types in the Nexla SDK, including:
- Credentials (data_credentials)
- Sources (data_sources)
- Destinations (data_sinks)
- Nexsets (data_sets)
- Flows
- Lookups (data_maps)
- Users

Prerequisites:
- Set NEXLA_SERVICE_KEY or NEXLA_ACCESS_TOKEN environment variable
- Valid Nexla account with appropriate permissions

Usage:
python examples/fetch_resources.py
"""

import os

from nexla_sdk import NexlaClient
from nexla_sdk.exceptions import AuthenticationError, NexlaError


def initialize_client() -> NexlaClient:
    """Initialize Nexla client with authentication."""
    base_url = os.getenv("NEXLA_API_URL")
    # Option 1: Service key (recommended)
    service_key = os.getenv("NEXLA_SERVICE_KEY")
    if service_key:
        return NexlaClient(service_key=service_key, base_url=base_url)

    # Option 2: Access token
    access_token = os.getenv("NEXLA_ACCESS_TOKEN")
    if access_token:
        return NexlaClient(access_token=access_token, base_url=base_url)

    raise ValueError(
        "Please set NEXLA_SERVICE_KEY or NEXLA_ACCESS_TOKEN environment variable"
    )


def list_credentials(client: NexlaClient) -> None:
    """List all credentials and get details for the first one."""
    try:
        print("\n=== CREDENTIALS ===")
        credentials = client.credentials.list()
        print(f"Total credentials: {len(credentials)}")

        for cred in credentials[:3]:  # Show first 3
            print(
                "- ID: {}, Name: {}, Type: {}".format(
                    cred.id, cred.name, getattr(cred, "credentials_type", "N/A")
                )
            )

        # Get detailed info for first credential
        if credentials:
            first_cred = client.credentials.get(credentials[0].id)
            print("First credential details:")
            print(f"  Name: {first_cred.name}")
            print("  Created: {}".format(getattr(first_cred, "created_at", "N/A")))

    except NexlaError as e:
        print(f"Error fetching credentials: {e}")


def list_sources(client: NexlaClient) -> None:
    """List all sources and get details for the first one."""
    try:
        print("\n=== SOURCES ===")
        sources = client.sources.list()
        print(f"Total sources: {len(sources)}")

        for source in sources[:3]:  # Show first 3
            print(
                "- ID: {}, Name: {}, Status: {}".format(
                    source.id, source.name, getattr(source, "status", "N/A")
                )
            )

        # Get detailed info for first source
        if sources:
            first_source = client.sources.get(sources[0].id)
            print("First source details:")
            print(f"  Name: {first_source.name}")
            print("  Created: {}".format(getattr(first_source, "created_at", "N/A")))

    except NexlaError as e:
        print(f"Error fetching sources: {e}")


def list_destinations(client: NexlaClient) -> None:
    """List all destinations and get details for the first one."""
    try:
        print("\n=== DESTINATIONS ===")
        destinations = client.destinations.list()
        print(f"Total destinations: {len(destinations)}")

        for dest in destinations[:3]:  # Show first 3
            print(
                "- ID: {}, Name: {}, Status: {}".format(
                    dest.id, dest.name, getattr(dest, "status", "N/A")
                )
            )

        # Get detailed info for first destination
        if destinations:
            first_dest = client.destinations.get(destinations[0].id)
            print("First destination details:")
            print(f"  Name: {first_dest.name}")
            print("  Created: {}".format(getattr(first_dest, "created_at", "N/A")))

    except NexlaError as e:
        print(f"Error fetching destinations: {e}")


def list_nexsets(client: NexlaClient) -> None:
    """List all nexsets and get details for the first one."""
    try:
        print("\n=== NEXSETS ===")
        nexsets = client.nexsets.list()
        print(f"Total nexsets: {len(nexsets)}")

        for nexset in nexsets[:3]:  # Show first 3
            print(
                "- ID: {}, Name: {}, Records: {}".format(
                    nexset.id, nexset.name, getattr(nexset, "total_records", "N/A")
                )
            )

        # Get detailed info for first nexset
        if nexsets:
            first_nexset = client.nexsets.get(nexsets[0].id)
            print("First nexset details:")
            print(f"  Name: {first_nexset.name}")
            print("  Schema: {}".format(getattr(first_nexset, "schema", "N/A")))

    except NexlaError as e:
        print(f"Error fetching nexsets: {e}")


def list_flows(client: NexlaClient) -> None:
    """List all flows and get details for the first one."""
    try:
        print("\n=== FLOWS ===")
        flows = client.flows.list()
        print(f"Total flows: {len(flows)}")

        for flow in flows[:3]:  # Show first 3
            print(
                "- ID: {}, Name: {}, Status: {}".format(
                    getattr(flow, "id", "N/A"),
                    getattr(flow, "name", "N/A"),
                    getattr(flow, "status", "N/A"),
                )
            )

        # Get detailed info for first flow
        if flows and hasattr(flows[0], "id"):
            first_flow = client.flows.get(flows[0].id)
            print("First flow details:")
            print("  Name: {}".format(getattr(first_flow, "name", "N/A")))
            print("  Created: {}".format(getattr(first_flow, "created_at", "N/A")))

    except NexlaError as e:
        print(f"Error fetching flows: {e}")


def list_lookups(client: NexlaClient) -> None:
    """List all lookups and get details for the first one."""
    try:
        print("\n=== LOOKUPS ===")
        lookups = client.lookups.list()
        print(f"Total lookups: {len(lookups)}")

        for lookup in lookups[:3]:  # Show first 3
            print(
                "- ID: {}, Name: {}, Type: {}".format(
                    lookup.id, lookup.name, getattr(lookup, "data_map_type", "N/A")
                )
            )

        # Get detailed info for first lookup
        if lookups:
            first_lookup = client.lookups.get(lookups[0].id)
            print("First lookup details:")
            print(f"  Name: {first_lookup.name}")
            print("  Created: {}".format(getattr(first_lookup, "created_at", "N/A")))

    except NexlaError as e:
        print(f"Error fetching lookups: {e}")


def list_users(client: NexlaClient) -> None:
    """List all users and get details for the first one."""
    try:
        print("\n=== USERS ===")
        users = client.users.list()
        print(f"Total users: {len(users)}")

        for user in users[:3]:  # Show first 3
            print(
                "- ID: {}, Name: {}, Email: {}".format(
                    user.id,
                    getattr(user, "full_name", "N/A"),
                    getattr(user, "email", "N/A"),
                )
            )

        # Get detailed info for first user
        if users:
            first_user = client.users.get(users[0].id)
            print("First user details:")
            print("  Name: {}".format(getattr(first_user, "name", "N/A")))
            print("  Email: {}".format(getattr(first_user, "email", "N/A")))

    except NexlaError as e:
        print(f"Error fetching users: {e}")


def demonstrate_pagination(client: NexlaClient) -> None:
    """Demonstrate pagination with sources."""
    try:
        print("\n=== PAGINATION EXAMPLE ===")

        # Get paginated results
        paginator = client.sources.paginate(per_page=5)

        page_count = 0
        total_items = 0

        for page in paginator.iter_pages():
            page_count += 1
            page_items = len(page.items)
            total_items += page_items

            print(f"Page {page_count}: {page_items} items")

            # Show first item from each page
            if page.items:
                first_item = page.items[0]
                print(f"  First item: ID={first_item.id}, Name={first_item.name}")

            # Only show first 3 pages for demo
            if page_count >= 3:
                break

        print(f"Total pages processed: {page_count}")
        print(f"Total items processed: {total_items}")

    except NexlaError as e:
        print(f"Error with pagination: {e}")


def main():
    """Main function to demonstrate all resource operations."""
    try:
        # Initialize client
        client = initialize_client()
        print("Successfully initialized Nexla client")

        # List and get resources for each type
        list_credentials(client)
        list_sources(client)
        list_destinations(client)
        list_nexsets(client)
        list_flows(client)
        list_lookups(client)
        list_users(client)

        # Demonstrate pagination
        demonstrate_pagination(client)

        print("\n=== SUMMARY ===")
        print("Successfully demonstrated listing and getting resources for all types!")

    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Please check your NEXLA_SERVICE_KEY or NEXLA_ACCESS_TOKEN")
    except NexlaError as e:
        print(f"Client configuration error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
