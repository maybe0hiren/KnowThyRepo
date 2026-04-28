
from .embedder import embed_content, embed_batch
from .model_loader import DEFAULT_MODEL_NAME, get_embedding_dim
from .schema import parse_embed_request, extract_text, EmbedRequest, EmbedResponse

__all__ = [
    "embed_content",
    "embed_batch",
    "DEFAULT_MODEL_NAME",
    "get_embedding_dim",
    "parse_embed_request",
    "extract_text",
    "EmbedRequest",
    "EmbedResponse",
]

__version__ = "1.0.0"
