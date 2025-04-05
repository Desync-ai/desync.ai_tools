# parsers/html_parser.py

"""
html_parser.py

Utility to parse raw HTML into structured content blocks.

Extracts:
- Paragraphs
- Headings (h1–h6)
- Lists (ul, ol)
- Tables (basic row extraction)
- Links (href + anchor text)
- Images (src + alt)

Intended to help downstream tasks like:
- Section-level analysis
- Chunked NLP
- Contact/link extraction
- Summarization

Author: Jackson-Ballow
License: MIT
"""

from typing import List, Dict

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("BeautifulSoup4 is required. Install it with: pip install beautifulsoup4")

from desync_search import DesyncClient


def parse_html_blocks(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    blocks = []

    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        blocks.append({"type": "heading", "tag": tag.name, "content": tag.get_text(strip=True)})

    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if text:
            blocks.append({"type": "paragraph", "content": text})

    for ul in soup.find_all(["ul", "ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        if items:
            blocks.append({"type": "list", "ordered": ul.name == "ol", "items": items})

    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            row = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if row:
                rows.append(row)
        if rows:
            blocks.append({"type": "table", "rows": rows})

    for a in soup.find_all("a", href=True):
        blocks.append({"type": "link", "href": a["href"], "text": a.get_text(strip=True)})

    for img in soup.find_all("img"):
        if img.get("src"):
            blocks.append({"type": "image", "src": img.get("src"), "alt": img.get("alt", "")})

    return blocks


if __name__ == "__main__":
    client = DesyncClient()

    urls = [
        "https://www.137ventures.com/team/justin-fishner-wolfson",
        "https://www.137ventures.com/team/sarah-mitchell"
    ]

    bulk_info = client.bulk_search(target_list=urls, extract_html=True)

    pages = client.collect_results(
        bulk_search_id=bulk_info["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=1.0
    )

    if not pages:
        print("No results returned from bulk search.")
        exit()

    first_page = pages[0]
    print(f"\nParsed blocks from: {first_page.url}")

    if not first_page.html_content:
        print("No HTML content retrieved.")
    else:
        blocks = parse_html_blocks(first_page.html_content)

        print("\n=== Parsed HTML Blocks For the First Search ===")
        for block in blocks:
            print(block)
