from typing import List, Dict

from sentence_transformers import SentenceTransformer

import quadrantDB
from qdrant_client.models import PointStruct


model = SentenceTransformer("all-MiniLM-L6-v2")


def embedder(
    chunks: List[Dict],
    repoName: str,
    qdrantUrl: str,
    qdrantKey: str
):
    if not chunks:
        raise ValueError("No chunks provided")

    texts = [chunk["content"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    ).astype("float32")

    qdrant = quadrantDB.getClient()

    points = []

    for i, chunk in enumerate(chunks):
        points.append(
            PointStruct(
                id=i,
                vector=embeddings[i].tolist(),
                payload=chunk
            )
        )

    qdrant.upsert(
        collection_name=repoName,
        points=points
    )

    print(f"Stored {len(points)} embeddings in Qdrant for repo: {repoName}")