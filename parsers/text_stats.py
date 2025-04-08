# /parsers/text_stats.py

"""
text_stats.py

Computes basic text statistics from DesyncClient PageData objects.

For each page:
    - Word count
    - Sentence count
    - Unique word ratio
    - Link density
    - Boilerplate ratio (optional, if original_html exists)

Use cases:
    - Filter low-content or spam pages
    - Estimate richness of information
    - Rank or score pages before NLP processing

Author: Jackson-Ballow
"""

import re
from typing import List, Dict
from desync_search.data_structures import PageData

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependency: bs4 (BeautifulSoup). Run `pip install beautifulsoup4`.")
    exit(1)


def compute_text_stats(page: PageData) -> Dict:
    """
    Computes basic stats on visible text and link structure from a PageData object.
    """
    text = page.text_content or ''
    html = page.html_content or ''

    word_list = re.findall(r'\b\w+\b', text.lower())
    word_count = len(word_list)
    sentence_count = len(re.findall(r'[.!?]', text))
    unique_words = set(word_list)
    unique_word_ratio = len(unique_words) / word_count if word_count else 0

    # Link density: words inside <a> tags relative to full text
    soup = BeautifulSoup(html, "html.parser")
    link_text = ' '.join(a.get_text() for a in soup.find_all('a'))
    link_word_count = len(re.findall(r'\b\w+\b', link_text))
    link_density = link_word_count / word_count if word_count else 0

    return {
        "url": page.url,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "unique_word_ratio": round(unique_word_ratio, 3),
        "link_density": round(link_density, 3),
    }



# === Example Usage ===
if __name__ == "__main__":
    from desync_search import DesyncClient

    try:
        import pandas as pd
    except ImportError:
        print(" dependency: pandas. Run `pip install pandas`.")
        exit(1)

    print("Running bulk search...")
    urls = [
        "https://www.137ventures.com/team/justin-fishner-wolfson",
        "https://www.137ventures.com/team/sarah-mitchell",
    ]
    client = DesyncClient()

    bulk = client.bulk_search(target_list=urls, extract_html=True)

    print("Waiting for HTML results...")
    pages = client.collect_results(
        bulk_search_id=bulk["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=1.0
    )

    print(f"Retrieved {len(pages)} pages. Computing text statistics…")
    stats = [compute_text_stats(page) for page in pages]

    df = pd.DataFrame(stats)
    print("\nText Statistics Summary:")
    print(df.head(10).to_string(index=False))
