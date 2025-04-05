# result_cleaning/html_cleaning/remove_boilerplate_html.py

"""
remove_boilerplate_html.py

This utility removes common boilerplate HTML blocks from crawled pages — including headers, navbars,
footers, scripts, and styles — leaving behind only content-rich elements (e.g., paragraphs, headings, links).
Useful for preprocessing HTML for NLP, summarization, or content-focused indexing.

Input:
    - List of DesyncClient PageData objects with `.html_content` filled.

Side Effects:
    - Mutates each PageData’s `.html_content` to contain only cleaned HTML.

Author: Jackson-Ballow
"""

from typing import List
from desync_search import DesyncClient
from desync_search.data_structures import PageData

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("BeautifulSoup4 is required. Install it with: pip install beautifulsoup4")


def remove_boilerplate_html(pages: List[PageData], tags_to_remove=None, text_threshold=30) -> None:
    """
    Mutates the .html_content of each PageData to remove boilerplate tags (nav, header, etc.)

    Args:
        pages (List[PageData]): Desync search results with .html_content populated.
        tags_to_remove (List[str], optional): HTML tags to filter out entirely.
        text_threshold (int): Minimum text length to keep a block.
    """
    tags_to_remove = tags_to_remove or ["header", "nav", "footer", "script", "style"]

    for page in pages:
        soup = BeautifulSoup(page.html_content or "", "html.parser")

        # Remove tags entirely
        for tag in tags_to_remove:
            for match in soup.find_all(tag):
                match.decompose()

        # Filter out short content
        for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "a", "div"]):
            if len(tag.get_text(strip=True)) < text_threshold:
                tag.decompose()

        # Update PageData HTML content in-place
        page.html_content = str(soup)


# Example Usage
if __name__ == "__main__":
    client = DesyncClient()

    urls = [
        "https://www.137ventures.com/team/justin-fishner-wolfson",
        "https://www.137ventures.com/team/sarah-mitchell"
    ]

    print("Starting bulk search...")
    bulk_info = client.bulk_search(target_list=urls, extract_html=True)

    print("Collecting results...")
    pages = client.collect_results(
        bulk_search_id=bulk_info["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=1.0,
    )

    if not pages:
        print("No pages retrieved.")
        exit()

    # Results before boilerplate cleaning
    first_page = pages[0]
    print(f"\n=== Length of Raw HTML Content for {first_page.url} ===")
    print(f"Length: {len(first_page.html_content or '')} characters")


    # Check out the results after the boilerplate cleaning
    remove_boilerplate_html([first_page])

    print(f"\n=== Length of Cleaned HTML Content for {first_page.url} ===")
    print(f"Length: {len(first_page.html_content or '')} characters")