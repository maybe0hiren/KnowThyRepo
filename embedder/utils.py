from __future__ import annotations

from typing import List, Union
import numpy as np


def l2_normalize(vector: np.ndarray) -> np.ndarray:
    if vector.ndim == 1:
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector
    norms = np.linalg.norm(vector, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)   # avoid div-by-zero
    return vector / norms


def ndarray_to_float_list(vector: np.ndarray) -> List[float]:
    return [float(v) for v in vector.tolist()]


def sanitize_text(text: str, max_chars: int = 8_192) -> str:
    text = text.replace("\x00", " ").strip()
    if len(text) > max_chars:
        text = text[:max_chars]
    return text



def chunk_list(lst: list, size: int) -> list[list]:
    return [lst[i: i + size] for i in range(0, len(lst), size)]


def validate_batch_requests(requests: list) -> None:
    if not isinstance(requests, list):
        raise TypeError(f"Batch input must be a list, got {type(requests).__name__}")
    if len(requests) == 0:
        raise ValueError("Batch input must not be empty")
