import json
from typing import List, Dict
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer as ST


modelName = "all-MiniLM-L6-v2"
model = ST(modelName)


def loadData(repoName: str):
    repoFolder = Path("data") / repoName

    indexFile = repoFolder / "index.faiss"
    metadataFile = repoFolder / "metadata.json"
    chunksFile = repoFolder / "chunks.json"

    index = faiss.read_index(str(indexFile))

    with open(metadataFile, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    with open(chunksFile, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return index, metadata, chunks


def search(query: str, index, metadata: List[Dict], top_k: int = 6) -> List[Dict]:
    queryVector = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = index.search(queryVector, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        chunkMeta = metadata[idx].copy()
        chunkMeta["score"] = float(score)
        results.append(chunkMeta)

    return results
