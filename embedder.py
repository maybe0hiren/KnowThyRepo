from typing import List, Dict
import numpy as np

from sentence_transformers import SentenceTransformer

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


model = SentenceTransformer("all-MiniLM-L6-v2")


def embedder(chunks: List[Dict], repoName: str,
             qdrantUrl: str, qdrantKey: str):

    if not chunks:
        raise ValueError("No chunks provided")

    texts = [c["content"] for c in chunks]

    embeddings = model.encode(texts, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")

    dim = embeddings.shape[1]

    qdrant = QdrantClient(url=qdrantUrl, api_key=qdrantKey)

    existing = [c.name for c in qdrant.get_collections().collections]

    if repoName not in existing:
        qdrant.create_collection(
            collection_name=repoName,
            vectors_config=VectorParams(
                size=dim,
                distance=Distance.COSINE
            )
        )

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

    print(f"Stored embeddings in Qdrant for repo: {repoName}")
