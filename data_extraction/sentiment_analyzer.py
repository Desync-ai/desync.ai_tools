# data_extraction/sentiment_analyzer.py

"""
sentiment_analyzer.py

Analyzes sentiment of each DesyncClient PageData object's text content using a transformer model.

Useful for:
- Flagging positive/negative bios or reviews
- Detecting tone in press/blog/testimonial pages
- Routing based on emotional polarity

Author: Jackson Ballow
"""

from typing import List, Dict
from desync_search.data_structures import PageData

try:
    from transformers import pipeline
except ImportError:
    print("Missing dependency: transformers. Run `pip install transformers`.")
    exit(1)


def analyze_sentiment(pages: List[PageData], device: int = -1) -> List[Dict]:
    """
    Runs sentiment analysis on page.text_content using HuggingFace pipeline.

    Args:
        pages (List[PageData]): List of pages with .text_content.
        device (int): -1 = CPU, 0 = GPU

    Returns:
        List[Dict]: List of {"url", "label", "score"} per page.
    """
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=device)

    results = []
    for page in pages:
        text = page.text_content.strip()
        if not text or len(text.split()) < 10:
            results.append({"url": page.url, "label": "neutral", "score": 0.0})
            continue

        try:
            result = classifier(text[:1000])[0]  # truncate long content
            results.append({
                "url": page.url,
                "label": result["label"],
                "score": round(result["score"], 3)
            })
        except Exception as e:
            results.append({"url": page.url, "label": f"error: {e}", "score": 0.0})

    return results


# === Example Usage ===
if __name__ == "__main__":
    from desync_search import DesyncClient

    print("Starting bulk search...")
    urls = [
        "https://www.trustpilot.com/review/www.robinhood.com",  # Negative
        "https://embedsocial.com/blog/positive-reviews-examples/",  # Positive
        "https://a16z.com/privacy-policy/", # Neutral
    ]

    client = DesyncClient()
    bulk = client.bulk_search(target_list=urls, extract_html=False)

    print("Collecting search results...")
    pages = client.collect_results(
        bulk_search_id=bulk["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=1.0
    )

    sentiments = analyze_sentiment(pages, device=-1)

    print("\nSentiment Results:")
    for s in sentiments:
        print(f"{s['url']}: {s['label']} ({s['score']})")
