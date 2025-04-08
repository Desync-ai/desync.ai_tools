# result_cleaning/duplicate_page_remover.py

"""
duplicate_page_remover.py

Detects near-duplicate pages using Jaccard similarity on normalized text.
Keeps only one representative URL per duplicate group.

Use cases:
- Remove repeated/paginated content
- Clean training data or spam listings
- Build similarity graphs

Author: Jackson-Ballow
"""

from typing import List, Tuple
from desync_search.data_structures import PageData


def jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two strings."""
    set_a, set_b = set(a.lower().split()), set(b.lower().split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def detect_duplicate_pages_dedup(
    pages: List[PageData],
    threshold: float = 0.9
) -> Tuple[List[Tuple[str, str, float]], List[PageData]]:
    """
    Detects duplicate page pairs and returns deduplicated set.

    Args:
        pages (List[PageData]): Input crawled pages.
        threshold (float): Jaccard threshold (default=0.9)

    Returns:
        (duplicate_pairs, deduplicated_pages)
    """
    duplicates = []
    kept_urls = set()
    deduped = []

    for i in range(len(pages)):
        if pages[i].url in kept_urls:
            continue
        current = pages[i]
        is_unique = True

        for j in range(i + 1, len(pages)):
            other = pages[j]
            if not current.text_content or not other.text_content:
                continue
            sim = jaccard_similarity(current.text_content, other.text_content)
            if sim >= threshold:
                duplicates.append((current.url, other.url, round(sim, 3)))
                kept_urls.add(other.url)

        deduped.append(current)
        kept_urls.add(current.url)

    return duplicates, deduped


# === Example Usage ===
if __name__ == "__main__":
    from desync_search import DesyncClient

    print("Crawling 137ventures homepage …")
    client = DesyncClient()
    pages = client.crawl(
        start_url="https://www.137ventures.com",
        max_depth=1,
        scrape_full_html=False
    )

    pages[0].url = "https://www.137ventures.com"

    print(f"\nRetrieved {len(pages)} pages.")
    print("\nOriginal URLs:")
    for page in pages:
        print(f" - {page.url}")

    print("\nChecking for duplicates …")
    duplicates, deduped = detect_duplicate_pages_dedup(pages)

    if not duplicates:
        print("\nNo near-duplicates found.")
    else:
        print(f"\nFound {len(duplicates)} duplicate pairs:\n")

        print(f"\nKeeping {len(deduped)} pages out of {len(pages)}.\n")

        print("Deduplicated URLs:")
        for page in deduped:
            print(f" - {page.url}")
