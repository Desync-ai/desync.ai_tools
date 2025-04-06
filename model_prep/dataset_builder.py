# model_prep/dataset_builder.py

"""
dataset_builder.py

Turns tokenized chunks (from tokenizer_loader.py) into a Hugging Face Dataset.

Inputs:
    - List of dicts from chunk_text_blocks.py (each has 'url', 'chunk_id', 'text', etc.)
    - Tokenized output from tokenizer_loader.py (input_ids, attention_mask, etc.)

Output:
    - Hugging Face Dataset with fields:
        - input_ids
        - attention_mask
        - url
        - chunk_id
        - text

Author: Jackson-Ballow
"""

from typing import List, Dict
from datasets import Dataset
import torch


def build_hf_dataset(
    chunks: List[Dict],
    tokenized: Dict[str, torch.Tensor]
) -> Dataset:
    if len(chunks) != tokenized["input_ids"].shape[0]:
        raise ValueError("Mismatch between number of chunks and tokenized inputs!")

    dataset_dict = {
        "input_ids": tokenized["input_ids"].tolist(),
        "attention_mask": tokenized["attention_mask"].tolist(),
        "url": [chunk["url"] for chunk in chunks],
        "chunk_id": [chunk["chunk_id"] for chunk in chunks],
        "text": [chunk["text"] for chunk in chunks],
    }

    return Dataset.from_dict(dataset_dict)


# === Example Usage (chaining full pipeline) ===
if __name__ == "__main__":
    import os
    import sys

    # 🧼 Fix import paths for local tools
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "result_cleaning", "html_cleaning"))
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "model_prep"))

    from remove_boilerplate_html import remove_boilerplate_html
    from chunk_text_blocks import chunk_text_blocks
    from tokenizer_loader import load_tokenizer, tokenize_chunks

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

    print("\nChunking cleaned HTML into blocks...")
    chunks = chunk_text_blocks(pages, method="paragraph", max_tokens=100)
    print(f"Generated {len(chunks)} chunks.")

    print("\n🔍 Loading tokenizer...")
    tokenizer = load_tokenizer("bert-base-uncased")

    print("Tokenizing chunks...")
    texts = [chunk["text"] for chunk in chunks]
    tokenized = tokenize_chunks(texts, tokenizer, max_length=100)

    print("Building HF Dataset...")
    dataset = build_hf_dataset(chunks, tokenized)

    print(f"\nDataset created with {len(dataset)} examples.")
    print("🔍 Sample entry:\n", dataset[0])
