# model_prep/chunk_text_blocks.py

"""
chunk_text_blocks.py

Utility to break down cleaned HTML content into manageable chunks
for transformer models (e.g., ~512 tokens).

The sample usage uses parse_html_blocks from /parsers/html_parser.py for semantic-aware chunking.

Author: Jackson-Ballow
"""

from typing import List, Literal

from desync_search.data_structures import PageData

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parsers"))

from html_parser import parse_html_blocks


def chunk_text_blocks(
    pages: List[PageData],
    method: Literal["paragraph", "sentence", "lines", "fixed"] = "paragraph",
    max_tokens: int = 512
) -> List[dict]:
    """
    Chunks cleaned HTML into model-friendly blocks.

    Args:
        pages (List[PageData]): PageData objects with cleaned .html_content.
        method (str): 'paragraph', 'sentence', 'lines', or 'fixed'
        max_tokens (int): Approximate max word count per chunk.

    Returns:
        List[dict]: One dict per chunk with {url, source, chunk_id, text}
    """
    chunks = []

    for page in pages:
        html_blocks = parse_html_blocks(page.html_content or "")
        # Include both <p> blocks and styled <div> paragraphs
        paragraphs = [
            b["content"] for b in html_blocks
            if b["type"] in ("paragraph", "paragraph-div")
        ]

        content = "\n\n".join(paragraphs)

        if method == "paragraph":
            raw_chunks = paragraphs
        elif method == "sentence":
            raw_chunks = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content) if s.strip()]
        elif method == "lines":
            raw_chunks = [l.strip() for l in content.splitlines() if l.strip()]
        elif method == "fixed":
            words = content.split()
            raw_chunks = [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]
        else:
            raise ValueError("Invalid method")

        for i, chunk in enumerate(raw_chunks):
            if len(chunk.split()) <= max_tokens:
                chunks.append({
                    "url": page.url,
                    "source": "html",
                    "chunk_id": f"{page.url}#chunk-{i}",
                    "text": chunk
                })

    return chunks


# === Example Usage ===
if __name__ == "__main__":
    import re
    import os
    import sys

    # Fix path so we can import from sibling directories
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parsers"))

    from remove_boilerplate_html import remove_boilerplate_html

    from desync_search import DesyncClient

    urls = [
        "https://www.137ventures.com/team/justin-fishner-wolfson",
        "https://www.137ventures.com/team/sarah-mitchell"
    ]

    print("Starting bulk search...")
    client = DesyncClient()
    bulk_info = client.bulk_search(target_list=urls, extract_html=True)

    print("Collecting results...")
    pages = client.collect_results(
        bulk_search_id=bulk_info["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=1.0
    )

    if not pages:
        print("No results returned.")
        exit()

    print(f"Retrieved {len(pages)} pages. Cleaning HTML...")
    remove_boilerplate_html(pages)

    print("Checking HTML content after cleaning...")
    for page in pages:
        print(f"\n--- {page.url} ---")
        print(f"HTML length: {len(page.html_content or '')}")
        if page.html_content:
            print("Preview:", page.html_content[:500])
        else:
            print("No HTML content")

    print("\nChunking cleaned HTML into blocks...")
    chunks = chunk_text_blocks(pages, method="paragraph", max_tokens=100)

    print(f"\nGenerated {len(chunks)} chunks. Sample output:\n")
    for chunk in chunks[:3]:
        print(f"- {chunk['chunk_id']} ({len(chunk['text'].split())} words)\n  {chunk['text']}\n")
