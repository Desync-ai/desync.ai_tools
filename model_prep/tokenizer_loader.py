# model_prep/tokenizer_loader.py

"""
tokenizer_loader.py

Loads a HuggingFace tokenizer and tokenizes a list of text chunks for transformer input.

Supports:
- Any model from HuggingFace (e.g., "bert-base-uncased", "distilbert-base-uncased")
- Custom padding, truncation, and max_length settings

Input:
    - List of strings (text chunks)
    - Model name (e.g., "bert-base-uncased")

Output:
    - Tokenizer object
    - Tokenized output as dict with input_ids, attention_mask, etc.

Author: Jackson-Ballow
"""

from typing import List, Tuple

try:
    from transformers import AutoTokenizer
except ImportError:
    raise ImportError("Transformers is required. Install it with: pip install transforms")


def load_tokenizer(model_name: str = "bert-base-uncased"):
    """
    Loads a HuggingFace tokenizer by model name.

    Args:
        model_name (str): HuggingFace model name (e.g., "bert-base-uncased")

    Returns:
        tokenizer: PreTrainedTokenizer instance
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return tokenizer


def tokenize_chunks(chunks: List[str], tokenizer, max_length: int = 512):
    """
    Tokenizes a list of text chunks using the provided tokenizer.

    Args:
        chunks (List[str]): List of input text strings.
        tokenizer: HuggingFace tokenizer object.
        max_length (int): Maximum number of tokens per sequence.

    Returns:
        Dict[str, List[List[int]]]: Tokenized outputs (input_ids, attention_mask, etc.)
    """
    tokenized = tokenizer(
        chunks,
        padding="max_length",
        truncation=True,
        max_length=max_length,
        return_tensors="pt"
    )
    return tokenized


# === Example Usage (chaining full pipeline) ===
if __name__ == "__main__":
    import sys
    import os

    # Fix import paths for local tools
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

    # Load tokenizer and tokenize
    print("\nLoading tokenizer...")
    tokenizer = load_tokenizer("bert-base-uncased")

    print("Tokenizing chunks...")
    texts = [chunk["text"] for chunk in chunks]
    encoded = tokenize_chunks(texts, tokenizer, max_length=100)

    print("\nTokenized Output (sample):")
    print("input_ids:\n", encoded["input_ids"][:2])
    print("attention_mask:\n", encoded["attention_mask"][:2])
