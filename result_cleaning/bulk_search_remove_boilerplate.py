"""
bulk_remove_boilerplate.py

This script helps users clean their scraped web data by identifying text snippets
that appear repeatedly across multiple pages — like navbars, footers, or repeated templates.

Use case:
    - Perform a bulk search with the DesyncClient and extract the unique, page-specific content by removing boilerplate.

Author: Jackson-Ballow
"""

from desync_search import DesyncClient
from collections import Counter
from typing import List
import re

def bulk_and_clean(
    url_list: List[str],
    threshold: float = 0.5,
    chunk_method: str = "line"
) -> List:
    """
    Runs a bulk search and removes repeated text chunks (e.g., navbars/footers).

    Args:
        url_list (List[str]): A list of up to 1000 URLs to bulk search.
        threshold (float): Fraction of pages a chunk must appear on to be considered boilerplate.
                           Lower values (e.g., 0.3) remove more aggressively.
                           Example: threshold=0.5 → removes any chunk seen on ≥50% of pages.
        chunk_method (str): How to split the page content:
                            - 'line' (default): splits on every line. Best for nav items or structured layouts.
                            - 'sentence': splits on end punctuation (good for full paragraphs).
                            - 'paragraph': splits on double newlines (longer chunks).

    Returns:
        pages (List[PageData]): The original Desync PageData objects, but with .text_content cleaned.
    """
    if len(url_list) == 0 or len(url_list) > 1000:
        raise ValueError("url_list must contain between 1 and 1000 URLs.")

    client = DesyncClient()

    # Start bulk search
    bulk_info = client.bulk_search(target_list=url_list, extract_html=False)
    pages = client.collect_results(
        bulk_search_id=bulk_info["bulk_search_id"],
        target_links=url_list,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=0.975
    )

    # Helper: split text content into chunks
    def chunk_text(text):
        if chunk_method == "paragraph":
            return [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
        elif chunk_method == "sentence":
            return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 0]
        elif chunk_method == "line":
            return [line.strip() for line in text.splitlines() if len(line.strip()) > 0]
        else:
            raise ValueError("chunk_method must be 'line', 'sentence', or 'paragraph'")

    chunk_counter = Counter()
    page_chunks = []

    # Tokenize and count how many pages each chunk appears in
    for page in pages:
        chunks = chunk_text(page.text_content)
        page_chunks.append(chunks)
        unique_chunks = set(chunks)
        chunk_counter.update(unique_chunks)

    # Mark any chunk seen on ≥ threshold * total_pages as boilerplate
    def is_boilerplate(chunk):
        return chunk_counter[chunk] >= threshold * len(pages)

    # Clean each page in-place
    for page, chunks in zip(pages, page_chunks):
        filtered = [chunk for chunk in chunks if not is_boilerplate(chunk)]
        page.text_content = "\n\n".join(filtered)

    return pages

if __name__ == "__main__":
    urls = [
        "https://www.137ventures.com/team/koby-aliphios",
        "https://www.137ventures.com/team/sebastian-ferus",
        "https://www.137ventures.com/team/justin-fishner-wolfson",
        # Add up to 1000 URLs
    ]

    # Increase the threshold to remove less
    cleaned_pages = bulk_and_clean(
        url_list=urls,
        threshold=0.5,
        chunk_method="line"
    )

    idx = 0  # View results from the 1st URL in the list
    print("=== CLEANED PAGE ===")
    print("URL:", cleaned_pages[idx].url)
    print("Length of cleaned text:", len(cleaned_pages[idx].text_content))
    print(cleaned_pages[idx].text_content)
