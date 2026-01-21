import json
from typing import List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer as ST

modelName = "all-MiniLM-L6-v2"
indexFile = "data/index.faiss"
metadataFile = "data/metadata.json"

model = ST(modelName)


def loadData():
    index = faiss.read_index(indexFile)
    with open(metadataFile, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata

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
