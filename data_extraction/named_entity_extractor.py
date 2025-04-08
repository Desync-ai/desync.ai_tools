# /data_extraction/named_entity_extractor.py

"""
named_entity_extractor.py

Extracts named entities (people, organizations, locations, dates) from text_content
using spaCy's small English model — fast and CPU-friendly.

Use cases:
    - Enrich team bios
    - Link entities across sites
    - Feed into structured knowledge bases

Author: Jackson-Ballow
"""

from typing import List, Dict
from desync_search.data_structures import PageData

try:
    import spacy
except ImportError:
    print("Missing dependency: spacy. Run `pip install spacy` and `python -m spacy download en_core_web_sm`.")
    exit(1)

try:
    import pandas as pd
except ImportError:
    print("Missing dependency: pandas. Run `pip install pandas`.")
    exit(1)


# Load lightweight English model (CPU-friendly)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    exit(1)


def extract_entities(page: PageData) -> Dict:
    text = page.text_content or ""
    doc = nlp(text)

    entities = {
        "url": page.url,
        "people": list({ent.text for ent in doc.ents if ent.label_ == "PERSON"}),
        "orgs": list({ent.text for ent in doc.ents if ent.label_ == "ORG"}),
        "locations": list({ent.text for ent in doc.ents if ent.label_ == "GPE"}),
        "dates": list({ent.text for ent in doc.ents if ent.label_ == "DATE"}),
    }

    return entities


# === Example Usage ===
if __name__ == "__main__":
    try:
        from desync_search import DesyncClient
    except ImportError:
        print("Missing dependency: desync_search. Make sure you're in the Desync Tools repo or installed the package.")
        exit(1)

    print("Running bulk search...")
    urls = [
        "https://www.137ventures.com/team/justin-fishner-wolfson",
        "https://www.137ventures.com/team/sarah-mitchell",
        "https://www.137ventures.com/team/james-pardee"
    ]

    client = DesyncClient()
    bulk = client.bulk_search(target_list=urls, extract_html=True)

    print("Waiting for results...")
    pages = client.collect_results(
        bulk_search_id=bulk["bulk_search_id"],
        target_links=urls,
        wait_time=30.0,
        poll_interval=2.0,
        completion_fraction=1.0
    )

    print(f"Retrieved {len(pages)} pages. Extracting named entities...")

    entity_data = [extract_entities(p) for p in pages]
    df = pd.DataFrame(entity_data)

    print("\nNamed Entity Summary:")
    print(df.to_string(index=False))
