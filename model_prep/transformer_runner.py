"""
transformer_runner.py
---------------------
Light‑weight wrapper around any Hugging Face sentence / encoder model that
returns a NumPy matrix of embeddings for a list of input texts.

Typical usage
>>> from transformer_runner import embed_texts
>>> vecs = embed_texts(["Hello world", "Another sentence"],
...                    model_name="all-MiniLM-L6-v2")
>>> vecs.shape
(2, 384)

The helper automatically:
• downloads / caches the model & tokenizer
• runs batching on GPU if available (or CPU otherwise)
• applies mean‑pooling over the last hidden states
• normalises the output vectors to unit length (cosine‑friendly)

Author: Jackson‑Ballow
"""

from __future__ import annotations

import math
from typing import List, Union, Optional

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel, AutoConfig

 # ---------------------------------------------------------------------------
 # Core helper
 # ---------------------------------------------------------------------------

def _mean_pool(last_hidden: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """Mean‑pooling that ignores padded tokens."""
    mask = attention_mask.unsqueeze(-1).type_as(last_hidden)
    summed = (last_hidden * mask).sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return summed / counts


def embed_texts(
    texts: List[str],
    model_name: str = "all-MiniLM-L6-v2",
    batch_size: int = 32,
    device: Optional[str] = None,
    max_length: int = 256,
) -> np.ndarray:
    """Embed *texts* using the specified encoder.

    Parameters
    ----------
    texts       : List[str]
        Sentences / paragraphs to encode.
    model_name  : str
        Hugging Face model repo or local path. Defaults to `all-MiniLM-L6-v2`.
    batch_size  : int
        How many texts to encode per forward pass.
    device      : str | None
        "cuda", "cpu", or None to auto‑select.
    max_length  : int
        Truncation length passed to the tokenizer.

    Returns
    -------
    np.ndarray  shape = (len(texts), hidden_size)
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, config=config)
    model.to(device)
    model.eval()

    embeddings: List[np.ndarray] = []

    with torch.inference_mode():
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            encoded = tokenizer(
                batch_texts,
                padding="longest",
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            ).to(device)

            outputs = model(**encoded)
            pooled = _mean_pool(outputs.last_hidden_state, encoded["attention_mask"])  # (B, H)
            # Convert to CPU numpy and L2‑normalise for cosine similarity
            vecs = pooled.cpu().numpy()
            norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
            vecs = vecs / norms
            embeddings.append(vecs)

    return np.vstack(embeddings)

# Example Usage
if __name__ == "__main__":
    import argparse, textwrap

    parser = argparse.ArgumentParser(
        description="Embed a list of sentences and print the shape.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent(
            """Example:
    python transformer_runner.py "Hello" "Who are the managing directors at 137 Ventures?"
            """
        ),
    )
    parser.add_argument("sentences", nargs="+", help="Sentences to embed")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2", help="HF model name")
    args = parser.parse_args()

    vecs = embed_texts(args.sentences, model_name=args.model)
    print("Embedded", len(args.sentences), "sentences →", vecs.shape)