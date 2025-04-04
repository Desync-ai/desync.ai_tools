"""
json_storage.py

This utility helps users export DesyncClient search results (PageData objects)
into a structured JSON file — perfect for backups, flexible processing, or structured logging.

Use case:
    - Perform a crawl or bulk search with DesyncClient.
    - Save the structured results to a JSON file for downstream tasks.

Author: Jackson-Ballow
"""

import json
from pathlib import Path
from typing import List
from desync_search import DesyncClient
from desync_search.data_structures import PageData


def save_to_json(pages: List[PageData], filepath: str, mode: str = "w"):
    """
    Saves a list of PageData objects to a JSON file.

    Args:
        pages (List[PageData]): List of DesyncClient results (crawl, search, or bulk).
        filepath (str): Destination path for the JSON file.
        mode (str): File mode. Use "w" to overwrite or "a" to append. Defaults to "w".
    """
    if mode not in {"w", "a"}:
        raise ValueError("mode must be 'w' (overwrite) or 'a' (append)")

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    # Convert PageData objects to serializable dictionaries
    new_data = []
    for page in pages:
        new_data.append({
            "url": page.url,
            "domain": getattr(page, "domain", ""),
            "timestamp": getattr(page, "timestamp", ""),
            "bulk_search_id": getattr(page, "bulk_search_id", ""),
            "search_type": getattr(page, "search_type", ""),
            "latency_ms": getattr(page, "latency_ms", ""),
            "depth": getattr(page, "depth", ""),
            "text_content": page.text_content.strip()
        })

    # Write to file
    if mode == "w" or not Path(filepath).exists():
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
    else:
        with open(filepath, "r+", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    raise ValueError("Existing JSON must be a list.")
            except json.JSONDecodeError:
                existing_data = []

            combined = existing_data + new_data
            f.seek(0)
            json.dump(combined, f, ensure_ascii=False, indent=2)
            f.truncate()


if __name__ == "__main__":
    client = DesyncClient()

    # Crawl example
    crawl_pages = client.crawl(
        start_url="https://www.137ventures.com/team",
        max_depth=1,
        scrape_full_html=False,
        remove_link_duplicates=True
    )
    save_to_json(crawl_pages, "output/crawl_results.json", mode="w")
    print(f"Saved {len(crawl_pages)} crawled pages to output/crawl_results.json")

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
    save_to_json(bulk_pages, "output/bulk_results.json", mode="w")
    print(f"Saved {len(bulk_pages)} bulk search pages to output/bulk_results.json")
