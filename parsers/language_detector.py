# parsers/language_detector.py

"""
language_detector.py

Detects the language of each PageData object using `langdetect`.

Useful for:
- Filtering out non-English pages
- Segmenting multilingual corpora
- Redirecting language-specific pipelines

Author: Jackson Ballow
"""

from typing import List, Dict
from desync_search.data_structures import PageData

try:
    from langdetect import detect
except ImportError:
    print("Missing dependency: langdetect. Run `pip install langdetect`.")
    exit(1)


def detect_languages(pages: List[PageData]) -> List[Dict]:
    """
    Detects language for each page's text_content.

    Args:
        pages (List[PageData]): List of pages with .text_content.

    Returns:
        List[Dict]: List of {"url", "language"} per page.
    """
    results = []

    for page in pages:
        text = page.text_content.strip()
        if not text or len(text.split()) < 10:
            language = "unknown"
        else:
            try:
                language = detect(text)
            except Exception:
                language = "error"

        results.append({"url": page.url, "language": language})

    return results


# === Example Usage ===
if __name__ == "__main__":
    from desync_search import DesyncClient

    print("Running bulk search...")
    urls = [
        "https://www.137ventures.com/team",  # English
        "https://fr.wikipedia.org/wiki/France",   # French
        "https://es.wikipedia.org/wiki/Espa%C3%B1a",  # Spanish
    ]

    client = DesyncClient()
    bulk = client.bulk_search(target_list=urls, extract_html=False)

    pages = client.collect_results(
        bulk_search_id=bulk["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=1.0,
    )

    langs = detect_languages(pages)

    print("\nDetected Languages:")
    for item in langs:
        print(f"{item['url']}  →  {item['language']}")
