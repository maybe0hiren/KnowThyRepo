from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class Part:
    text: str

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError(f"Part.text must be a str, got {type(self.text).__name__}")


@dataclass
class Content:
    parts: List[Part]

    def __post_init__(self) -> None:
        if not isinstance(self.parts, list) or len(self.parts) == 0:
            raise ValueError("Content.parts must be a non-empty list")
        self.parts = [
            Part(**p) if isinstance(p, dict) else p
            for p in self.parts
        ]


@dataclass
class EmbedRequest:
    model: str
    content: Content
    task_type: Optional[str] = field(default=None)

    def __post_init__(self) -> None:
        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("EmbedRequest.model must be a non-empty string")
        if isinstance(self.content, dict):
            self.content = Content(**self.content)
        if not isinstance(self.content, Content):
            raise TypeError("EmbedRequest.content must be a Content object or dict")


@dataclass
class EmbeddingValues:
    values: List[float]


@dataclass
class EmbedResponse:
    embedding: EmbeddingValues

    def to_dict(self) -> dict:
        return {"embedding": {"values": self.embedding.values}}

def parse_embed_request(raw: dict) -> EmbedRequest:
    if not isinstance(raw, dict):
        raise TypeError(f"Request must be a dict, got {type(raw).__name__}")

    missing = [k for k in ("model", "content") if k not in raw]
    if missing:
        raise ValueError(f"Missing required field(s): {missing}")

    return EmbedRequest(
        model=raw["model"],
        content=raw["content"],
        task_type=raw.get("task_type"),
    )


def extract_text(request: EmbedRequest) -> str:
    texts = [part.text for part in request.content.parts]
    combined = " ".join(t.strip() for t in texts if t.strip())
    if not combined:
        raise ValueError("All parts are empty — nothing to embed")
    return combined
