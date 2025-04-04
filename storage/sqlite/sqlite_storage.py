"""
sqlite_storage.py

This utility helps users export DesyncClient search results (PageData objects)
into an SQLite database — ideal for querying, archiving, or integrating with other tools.

Use case:
    - Perform a crawl or bulk search with DesyncClient.
    - Save results to a local SQLite database for inspection or downstream analysis.

Author: Mark Evgenev and Jackson-Ballow
"""

import sqlite3
from pathlib import Path
from typing import List
from desync_search import DesyncClient
from desync_search.data_structures import PageData


def save_to_sqlite(pages: List[PageData], db_path: str, table_name: str = "pages", append: bool = True):
    """
    Saves a list of PageData objects into an SQLite database.

    Args:
        pages (List[PageData]): List of DesyncClient results (crawl, search, or bulk).
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to write into. Default is "pages".
        append (bool): If False, the table will be dropped and recreated. Default is True.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    if not append:
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            url TEXT PRIMARY KEY,
            domain TEXT,
            timestamp INTEGER,
            bulk_search_id TEXT,
            search_type TEXT,
            latency_ms INTEGER,
            depth INTEGER,
            text_content TEXT
        )
    """)

    for page in pages:
        cur.execute(f"""
            INSERT OR REPLACE INTO {table_name} (
                url, domain, timestamp, bulk_search_id,
                search_type, latency_ms, depth, text_content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            page.url,
            getattr(page, "domain", ""),
            getattr(page, "timestamp", None),
            getattr(page, "bulk_search_id", ""),
            getattr(page, "search_type", ""),
            getattr(page, "latency_ms", None),
            getattr(page, "depth", None),
            page.text_content.strip()
        ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    client = DesyncClient()

    # Crawl example
    crawl_pages = client.crawl(
        start_url="https://www.137ventures.com/team",
        max_depth=1,
        scrape_full_html=False,
        remove_link_duplicates=True
    )
    save_to_sqlite(crawl_pages, "output/desync_pages.db", table_name="crawl_results", append=False)
    print(f"Saved {len(crawl_pages)} crawled pages to desync_pages.db (table: crawl_results)")

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
    save_to_sqlite(bulk_pages, "output/desync_pages.db", table_name="bulk_results", append=False)
    print(f"Saved {len(bulk_pages)} bulk search pages to desync_pages.db (table: bulk_results)")
