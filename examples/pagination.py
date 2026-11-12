"""List every data source by walking pages.

The SDK sends an explicit per_page on each request and reads the X-* headers
and the Link header to decide whether another page exists. You do not track
page numbers yourself.

Usage:
    NEXLA_SERVICE_KEY=... python examples/pagination.py
"""

import sys

from nexla_sdk import NexlaClient, NexlaError

PAGE_SIZE = 100


def print_pages(client: NexlaClient) -> int:
    """Print one line per page and return the item count."""
    total = 0
    for page in client.sources.paginate(per_page=PAGE_SIZE).iter_pages():
        total += len(page.items)
        print(
            f"page {page.page}: {len(page.items)} items "
            f"(per_page={page.per_page}, total_pages={page.total_pages}, "
            f"total_count={page.total_count})"
        )
    return total


def print_items(client: NexlaClient, limit: int = 5) -> None:
    """Print the first few items without handling page boundaries."""
    for index, source in enumerate(
        client.sources.paginate(per_page=PAGE_SIZE).iter_items()
    ):
        if index >= limit:
            break
        print(f"  {source.id}: {source.name}")


def main() -> int:
    try:
        client = NexlaClient()
        print("Pages:")
        total = print_pages(client)
        print(f"Total items across all pages: {total}")
        print("First items:")
        print_items(client)
    except NexlaError as error:
        print(f"Pagination failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
