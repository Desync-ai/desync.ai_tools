"""
crawl_remove_duplicate_text.py

This script helps users clean their scraped web data by identifying text snippets
that appear repeatedly across multiple pages — like navbars, footers, or repeated templates.

Use case:
    - Crawl a site with the DesyncClient and extract the unique, page-specific content by removing boilerplate.

Author: Jackson-Ballow
"""

from desync_search import DesyncClient
from collections import Counter
import re

def crawl_and_clean(
    start_url: str,
    max_depth: int = 3,
    threshold: float = 1.0,
    chunk_method: str = "line"
) -> list:
    """
    Crawls a website and removes repeated text chunks (e.g., navbars/footers).

    Args:
        start_url (str): The URL to begin crawling from.
        max_depth (int): How deep to crawl. 
                         Depth 0 = just the start_url gets scraped, 
                         Depth 1 = homepage + its internal links, and so on.
        threshold (float): Fraction of pages a chunk must appear on to be considered boilerplate.
                           Lower values (e.g., 0.3) remove more aggressively.
                           Example: threshold=0.5 → removes any chunk seen on ≥50% of pages.
        chunk_method (str): How to split the page content:
                            - 'line' (default): splits on every line. Best for nav items or structured layouts.
                            - 'sentence': splits on end punctuation (good for prose).
                            - 'paragraph': splits on double newlines (good for long-form blocks).

    Returns:
        cleaned_pages (List[str]): The cleaned text content from each page.
        pages (List[PageData]): Original Desync PageData objects (if you want metadata, links, etc.).
    """
    client = DesyncClient()
    pages = client.crawl(
        start_url=start_url,
        max_depth=max_depth,
        scrape_full_html=False,
        remove_link_duplicates=True
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

    # Remove boilerplate from each page
    cleaned_pages = []
    for chunks in page_chunks:
        filtered = [chunk for chunk in chunks if not is_boilerplate(chunk)]
        cleaned_pages.append("\n\n".join(filtered))

    return cleaned_pages, pages

if __name__ == "__main__":
    # Example usage:
    # - Try lowering threshold to 0.3 for more aggressive removal
    # - Switch to chunk_method="paragraph" or "sentence" for other use cases
    cleaned, original = crawl_and_clean(
        "https://www.137ventures.com/team",
        threshold=0.5,
        chunk_method="line",
        max_depth=1,
    )

    idx = 1  # Change to view a different page from the crawl
    print("=== ORIGINAL TEXT ===")
    print("Length of result: ", len(original[idx].text_content))
    print(original[idx].text_content, "\n")

    print("=== CLEANED TEXT ===")
    print("Length of result: ", len(cleaned[idx]))
    print(cleaned[idx])
