import json
from typing import List, Dict
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer as ST


modelName = "all-MiniLM-L6-v2"


def embedder(chunks: List[Dict], repoName: str) -> None:
    if not chunks:
        raise ValueError("No chunks provided")

    repoFolder = Path("data") / repoName
    repoFolder.mkdir(parents=True, exist_ok=True)

    indexFile = repoFolder / "index.faiss"
    metadataFile = repoFolder / "metadata.json"
    chunksFile = repoFolder / "chunks.json"

    model = ST(modelName)
    texts = [chunk["content"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(indexFile))

    metadata = []
    for i, chunk in enumerate(chunks):
        meta = chunk.copy()
        meta.pop("content")
        meta["vector_id"] = i
        metadata.append(meta)

    with open(metadataFile, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(chunksFile, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"Stored embeddings + chunks for repo: {repoName}")
