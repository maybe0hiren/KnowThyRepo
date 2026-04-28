from __future__ import annotations

import os
import logging
import threading
from typing import Optional

os.environ.setdefault("PYTHONHASHSEED", "42")

logger = logging.getLogger(__name__)
try:
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer
    _DEPS_AVAILABLE = True
except ImportError as _import_err:
    _DEPS_AVAILABLE = False
    _IMPORT_ERR = _import_err

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
_SEED = 42


def _fix_seeds() -> None:
    import random
    import numpy as np
    import torch

    random.seed(_SEED)
    np.random.seed(_SEED)
    torch.manual_seed(_SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(_SEED)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


class _ModelRegistry:

    _lock = threading.Lock()
    _models: dict[str, "SentenceTransformer"] = {}

    @classmethod
    def get(cls, model_name: str = DEFAULT_MODEL_NAME) -> "SentenceTransformer":
        if not _DEPS_AVAILABLE:
            raise RuntimeError(
                f"Required packages are not installed: {_IMPORT_ERR}\n"
                "Run: pip install sentence-transformers torch"
            )

        if model_name not in cls._models:
            with cls._lock:
                if model_name not in cls._models:
                    _fix_seeds()
                    logger.info("Loading embedding model '%s' …", model_name)
                    model = SentenceTransformer(model_name)
                    model.eval()
                    cls._models[model_name] = model
                    logger.info("Model '%s' loaded (dim=%d).", model_name,
                                model.get_sentence_embedding_dimension())

        return cls._models[model_name]

    @classmethod
    def embedding_dim(cls, model_name: str = DEFAULT_MODEL_NAME) -> int:
        return cls.get(model_name).get_sentence_embedding_dimension()

    @classmethod
    def loaded_models(cls) -> list[str]:
        return list(cls._models.keys())



def get_model(model_name: Optional[str] = None) -> "SentenceTransformer":
    return _ModelRegistry.get(model_name or DEFAULT_MODEL_NAME)


def get_embedding_dim(model_name: Optional[str] = None) -> int:
    return _ModelRegistry.embedding_dim(model_name or DEFAULT_MODEL_NAME)
