from typing import List, Dict

import numpy as np
from sentence_transformers import SentenceTransformer

from qdrant_client import QdrantClient


model = SentenceTransformer("all-MiniLM-L6-v2")


def search(
    query: str,
    repoName: str,
    qdrantUrl: str,
    top_k: int = 6
) -> List[Dict]:

    queryVector = model.encode(
        query,
        convert_to_numpy=True
    ).astype("float32").tolist()

    qdrant = QdrantClient(url=qdrantUrl)

    results = qdrant.query_points(
        collection_name=repoName,
        query=queryVector,
        limit=top_k
    ).points

    chunks = []

    for result in results:
        payload = result.payload
        payload["score"] = result.score
        chunks.append(payload)

    return chunks
