# result_cleaning/text_cleaning/remove_boilerplate_text.py

"""
remove_boilerplate_text.py

This utility removes repeated text chunks (like navbars, footers, shared sections)
across multiple scraped web pages. Intended for preprocessing `PageData` objects
from bulk searches or crawls before NLP tasks or analysis.

Input:
    - A list of DesyncClient PageData objects (with `.text_content` populated)
    - Customizable chunking method (line, sentence, or paragraph)
    - Threshold for removing shared boilerplate (e.g., 0.5 means remove chunks seen on ≥ 50% of pages)

Side Effects:
    - Mutates each PageData object's `.text_content` in-place by removing shared boilerplate.

Author: Jackson-Ballow
"""

from collections import Counter
from typing import List
from desync_search.data_structures import PageData
from desync_search import DesyncClient
import re


def remove_boilerplate_text(
    pages: List[PageData],
    threshold: float = 0.5,
    chunk_method: str = "line"
) -> None:
    """
    Removes repeated text chunks (boilerplate) from each PageData's text_content.

    Args:
        pages (List[PageData]): List of PageData objects with text_content filled.
        threshold (float): Fraction of pages a chunk must appear on to be considered boilerplate.
                           Example: threshold=0.5 → removes chunks seen on ≥50% of pages.
        chunk_method (str): One of "line", "sentence", or "paragraph" for chunking strategy.

    Returns:
        None (modifies pages in-place)
    """
    if not pages:
        return

    def chunk_text(text: str) -> List[str]:
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

    for page in pages:
        chunks = chunk_text(page.text_content or "")
        page_chunks.append(chunks)
        chunk_counter.update(set(chunks))

    def is_boilerplate(chunk: str) -> bool:
        return chunk_counter[chunk] >= threshold * len(pages)

    for page, chunks in zip(pages, page_chunks):
        filtered = [chunk for chunk in chunks if not is_boilerplate(chunk)]
        page.text_content = "\n\n".join(filtered)

# Example usage
if __name__ == "__main__":
    client = DesyncClient()

    urls = [
        "https://www.137ventures.com/team/justin-fishner-wolfson",
        "https://www.137ventures.com/team/sarah-mitchell",
        "https://www.137ventures.com/team/sebastian-ferus",
    ]

    print("Starting bulk search...")
    bulk_info = client.bulk_search(target_list=urls, extract_html=False)

    print("Collecting results...")
    pages = client.collect_results(
        bulk_search_id=bulk_info["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=0.975,
    )

    if not pages:
        print("No pages retrieved.")
        exit()

    print(f"Retrieved {len(pages)} pages")

    # The results before removing the boilerplate text
    print(f"\n=== Length of Raw Text Content and Preview for {pages[0].url} ===")
    print("Length: ", len(pages[0].text_content))
    print(pages[0].text_content[:200], "...")  # Show the first 200 characters of the raw data


    # Apply in-place boilerplate removal
    remove_boilerplate_text(pages, threshold=0.5, chunk_method="line")

    print(f"\n=== Length of Cleaned Content and Preview for {pages[0].url} ===")
    print("Cleaned text length (first page):", len(pages[0].text_content))
    print(pages[0].text_content[:200], "...")  # show first 200 chars of cleaned content
