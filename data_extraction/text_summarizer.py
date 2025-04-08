# data_extraction/text_summarizer.py

"""
text_summarizer.py

Summarizes DesyncClient PageData content using a transformer model (CPU or GPU).
Useful for quickly skimming long bios or overviews.

Author: Jackson Ballow
"""

from typing import List, Dict
from desync_search.data_structures import PageData

try:
    from transformers import pipeline
except ImportError:
    print("Missing dependency: transformers. Run `pip install transformers`.")
    exit(1)


def summarize_pages(
    pages: List[PageData],
    max_length_chars: int = 400,
    device: int = -1  # -1 for CPU
) -> List[Dict]:
    from transformers import pipeline

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=device)

    summaries = []
    for page in pages:
        text = page.text_content.strip()

        # Skip pages with insufficient text content
        if not text or len(text.split()) < 30:
            continue

        # Prevent input from exceeding model max length (BART = 1024 tokens ≈ 4000 characters)
        max_input_chars = 4000
        if len(text) > max_input_chars:
            text = text[:max_input_chars]

        # Convert the desired max_length_chars to a token length approximation (1 token ≈ 4 chars)
        token_limit = min(1024, max(20, max_length_chars // 4))
        
        # Adjust min_length based on text size.
        # For very short texts the minimum summary length requirement might be too high.
        min_length_value = 20 if len(text.split()) >= 50 else 5

        try:
            output = summarizer(
                text, max_length=token_limit, min_length=min_length_value, do_sample=False
            )
            # Check if the output list is not empty and contains the expected key:
            if output and isinstance(output, list) and "summary_text" in output[0]:
                summary = output[0]["summary_text"]
            else:
                summary = "[No summary produced]"
        except Exception as e:
            summary = f"[Error during summarization: {e}]"

        summaries.append({
            "url": page.url,
            "summary": summary
        })

    return summaries


# === Example Usage ===
if __name__ == "__main__":
    from desync_search import DesyncClient
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "result_cleaning", "text_content_cleaning"))

    try:
        from remove_boilerplate_text import remove_boilerplate_text
    except:
        print("Missing boilerplate remover. Install or fix import.")
        exit(1)

    print("Starting bulk search...")

    urls = [
        "https://a16z.com/author/ben-horowitz/",
        "https://a16z.com/author/marc-andreessen/",
        "https://a16z.com/author/kimberly-tan/",
    ]

    client = DesyncClient()

    bulk_info = client.bulk_search(target_list=urls, extract_html=False)

    pages = client.collect_results(
        bulk_search_id=bulk_info["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=0.975,
    )

    remove_boilerplate_text(pages, threshold=0.5, chunk_method="line")

    print(f"Retrieved {len(pages)} pages. Generating summaries for the URLs...")
    summaries = summarize_pages(pages, max_length_chars=200, device=-1)

    import time
    time.sleep(4)

    print("\nSummaries:")
    for item in summaries:
        print(f"\nURL: {item['url']}\nSummary: {item['summary']}\n")
