"""
csv_storage.py

This utility helps users export DesyncClient search results (PageData objects)
into a structured CSV file — perfect for analysis, backups, or downstream tasks.

Use case:
    - Perform a crawl or bulk search with DesyncClient.
    - Save the structured results to a CSV for offline analysis.

Author: Jackson-Ballow
"""

import csv
from pathlib import Path
from typing import List
from desync_search import DesyncClient
from desync_search.data_structures import PageData


def save_to_csv(pages: List[PageData], filepath: str, mode: str = "w"):
    """
    Saves a list of PageData objects to a CSV file.

    Args:
        pages (List[PageData]): List of DesyncClient results (crawl, search, or bulk).
        filepath (str): Destination path for the CSV file.
        mode (str): File mode. Use "w" to overwrite or "a" to append. Defaults to "w".
    """
    if mode not in {"w", "a"}:
        raise ValueError("mode must be 'w' (overwrite) or 'a' (append)")

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    file_exists = Path(filepath).exists()

    with open(filepath, mode=mode, newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Only write header if file doesn't exist or we're overwriting
        if mode == "w" or not file_exists:
            writer.writerow([
                "url",
                "domain",
                "timestamp",
                "bulk_search_id",
                "search_type",
                "latency_ms",
                "depth",
                "text_content"
            ])

        for page in pages:
            writer.writerow([
                page.url,
                getattr(page, "domain", ""),
                getattr(page, "timestamp", ""),
                getattr(page, "bulk_search_id", ""),
                getattr(page, "search_type", ""),
                getattr(page, "latency_ms", ""),
                getattr(page, "depth", ""),
                page.text_content.replace("\n", " ").strip()
            ])


if __name__ == "__main__":
    client = DesyncClient()

    # Crawl example
    crawl_pages = client.crawl(
        start_url="https://www.137ventures.com/team",
        max_depth=1,
        scrape_full_html=False,
        remove_link_duplicates=True
    )
    save_to_csv(crawl_pages, "output/crawl_results.csv", mode="w")
    print(f"Saved {len(crawl_pages)} crawled pages to output/crawl_results.csv")

    # Bulk search example
    urls = [
        "https://www.137ventures.com/team/sarah-mitchell",
        "https://www.137ventures.com/team/sebastian-ferus",
        "https://www.137ventures.com/team/justin-fishner-wolfson"
    ]
    bulk_info = client.bulk_search(target_list=urls, extract_html=False)
    bulk_pages = client.collect_results(
        bulk_search_id=bulk_info["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=0.975,
    )
    save_to_csv(bulk_pages, "output/bulk_results.csv", mode="w")
    print(f"Saved {len(bulk_pages)} bulk search pages to output/bulk_results.csv")
