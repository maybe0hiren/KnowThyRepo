from __future__ import annotations

import logging
from typing import List, Optional

from .schema import parse_embed_request, extract_text, EmbedResponse, EmbeddingValues
from .model_loader import get_model, DEFAULT_MODEL_NAME
from .utils import l2_normalize, ndarray_to_float_list, sanitize_text, chunk_list, validate_batch_requests

logger = logging.getLogger(__name__)

def _embed_text(text: str, model_name: str = DEFAULT_MODEL_NAME) -> list[float]:
    text = sanitize_text(text)
    model = get_model(model_name)
    vector = model.encode(
        text,
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=False,
    )
    vector = l2_normalize(vector)
    return ndarray_to_float_list(vector)

def embed_content(request: dict, model_name: Optional[str] = None) -> dict:
    embed_request = parse_embed_request(request)
    text = extract_text(embed_request)

    # Prefer model from request payload, then kwarg, then default
    resolved_model = model_name or DEFAULT_MODEL_NAME
    values = _embed_text(text, resolved_model)

    response = EmbedResponse(embedding=EmbeddingValues(values=values))
    logger.debug("Embedded %d chars → %d-dim vector", len(text), len(values))
    return response.to_dict()

def embed_batch(
    requests: List[dict],
    model_name: Optional[str] = None,
    batch_size: int = 32,
) -> List[dict]:
    validate_batch_requests(requests)

    import numpy as np

    resolved_model = model_name or DEFAULT_MODEL_NAME
    model = get_model(resolved_model)
    parsed = [parse_embed_request(r) for r in requests]
    texts = [sanitize_text(extract_text(p)) for p in parsed]

    results: list[list[float]] = []
    for chunk in chunk_list(texts, batch_size):
        vectors = model.encode(
            chunk,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=False,
            batch_size=batch_size,
        )
        vectors = l2_normalize(vectors)
        results.extend(ndarray_to_float_list(v) for v in vectors)

    return [
        EmbedResponse(embedding=EmbeddingValues(values=v)).to_dict()
        for v in results
    ]
