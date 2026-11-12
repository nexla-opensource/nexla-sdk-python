"""Use the async client: concurrent reads, paging with async for, and cleanup.

Install the async extra first:
    pip install "nexla-sdk[async]"

Usage:
    NEXLA_SERVICE_KEY=... python examples/async_usage.py
"""

import asyncio
import os
import sys

from nexla_sdk import NexlaError
from nexla_sdk.aio import AsyncNexlaClient


async def list_sources_concurrently(client: AsyncNexlaClient) -> None:
    """Fetch the first page of sources and one flow's details at the same time."""
    sources, flows = await asyncio.gather(
        client.sources.list(per_page=10),
        client.flows.list(per_page=10),
    )
    print(f"{len(sources)} sources and {len(flows)} flows fetched concurrently")


async def print_all_sources(client: AsyncNexlaClient) -> int:
    """Walk every page of sources with async for. Return the item count."""
    total = 0
    async for source in client.sources.paginate(per_page=100).iter_items():
        total += 1
        print(f"source {source.id}: {source.name}")
    return total


async def main() -> int:
    # The client is an async context manager. Leaving the block closes the HTTP
    # transport. Credentials and the base URL come from NEXLA_SERVICE_KEY and
    # NEXLA_API_URL, as with the sync client.
    async with AsyncNexlaClient(
        service_key=os.getenv("NEXLA_SERVICE_KEY"),
        base_url=os.getenv("NEXLA_API_URL", "https://dataops.nexla.io/nexla-api"),
    ) as client:
        await list_sources_concurrently(client)
        count = await print_all_sources(client)
        print(f"total sources: {count}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except NexlaError as exc:
        print(f"Nexla error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
