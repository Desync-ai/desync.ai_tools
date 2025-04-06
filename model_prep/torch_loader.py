# model_prep/torch_loader.py

"""
torch_loader.py

Provides a helper function to load a Hugging Face Dataset
into a PyTorch DataLoader with a custom collate function.

- Stacks 'input_ids' and 'attention_mask' into batched tensors.
- Preserves other columns (e.g., 'url', 'chunk_id', 'text') in lists.

Author: Jackson-Ballow
"""

import torch
from torch.utils.data import DataLoader

def get_torch_dataloader(
    dataset,
    batch_size: int = 8,
    shuffle: bool = True,
    drop_last: bool = False,
):
    """
    Wraps the given Hugging Face Dataset in a DataLoader.

    Args:
        dataset (datasets.Dataset): The HF dataset, with at least 'input_ids' and 'attention_mask' columns.
        batch_size (int): Number of samples per batch.
        shuffle (bool): Shuffle data on each epoch.
        drop_last (bool): Whether to drop the last incomplete batch if dataset size % batch_size != 0.

    Returns:
        DataLoader: Yields dictionaries with:
            - 'input_ids': (batch_size, seq_len) torch.LongTensor
            - 'attention_mask': (batch_size, seq_len) torch.LongTensor
            - 'url', 'chunk_id', 'text': lists of strings
            - plus any other columns passed as strings
    """

    # Tell HF not to convert URL/text columns into tensors
    dataset.set_format(
        type="torch",
        columns=["input_ids", "attention_mask"],  # only these become PyTorch tensors
        output_all_columns=True,  # preserve the other columns in the returned batch
    )

    def collate_fn(batch):
        """
        Custom collate function:
          - Stacks 'input_ids' and 'attention_mask'
          - Leaves everything else as a list of Python objects
        """
        # The 'batch' is a list of dicts, one per example
        # e.g. batch[0].keys() -> ["input_ids", "attention_mask", "url", "chunk_id", "text", ...]

        input_ids = torch.stack([example["input_ids"] for example in batch])
        attention_mask = torch.stack([example["attention_mask"] for example in batch])

        # For everything else, just collect them in a list
        # (Assuming they're strings, or other non-tensor data)
        collated = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }
        # Grab all non-tensor fields dynamically
        for key in batch[0].keys():
            if key not in ("input_ids", "attention_mask"):
                collated[key] = [example[key] for example in batch]

        return collated

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=drop_last,
        collate_fn=collate_fn,
    )

if __name__ == "__main__":
    import os
    import sys

    from desync_search import DesyncClient

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "result_cleaning", "html_cleaning"))
    from remove_boilerplate_html import remove_boilerplate_html

    from chunk_text_blocks import chunk_text_blocks
    from tokenizer_loader import load_tokenizer, tokenize_chunks
    from dataset_builder import build_hf_dataset

    # 1) Scrape
    client = DesyncClient()
    urls = ["https://example.com", "https://another-example.com"]
    bulk_info = client.bulk_search(target_list=urls, extract_html=True)
    pages = client.collect_results(
        bulk_search_id=bulk_info["bulk_search_id"],
        target_links=urls
    )

    # 2) Clean HTML
    remove_boilerplate_html(pages)

    # 3) Chunk text
    chunks = chunk_text_blocks(pages, method="paragraph", max_tokens=100)
    raw_texts = [c["text"] for c in chunks]

    # 4) Tokenize
    tokenizer = load_tokenizer("bert-base-uncased")
    tokenized = tokenize_chunks(raw_texts, tokenizer, max_length=128)

    # 5) Build HF dataset
    dataset = build_hf_dataset(chunks, tokenized)

    # 6) Get a PyTorch DataLoader
    loader = get_torch_dataloader(dataset, batch_size=2)
    for batch in loader:
        print("BATCH keys:", batch.keys())
        print("BATCH input_ids shape:", batch["input_ids"].shape)
        print("URLs in this batch:", batch["url"])
        break  # just show the first batch for demo
