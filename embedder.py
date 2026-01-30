from typing import List, Dict

from google import genai
import numpy as np

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


geminiEmbedder = "models/gemini-embedding-001"


def embedder(chunks: List[Dict], repoName: str, apiKey: str,
             qdrantUrl: str, qdrantKey: str) -> None:

    if not chunks:
        raise ValueError("No chunks provided")

    client = genai.Client(api_key=apiKey)

    vectors = []
    for chunk in chunks:
        response = client.models.embed_content(
            model=geminiEmbedder,
            contents=chunk["content"]
        )
        vectors.append(response.embeddings[0].values)

    embeddings = np.array(vectors).astype("float32")
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
                payload={
                    "chunkID": chunk["chunkID"],
                    "path": chunk["path"],
                    "language": chunk["language"],
                    "chunkType": chunk["chunkType"],
                    "content": chunk["content"],
                    "startLine": chunk["startLine"],
                    "endLine": chunk["endLine"]
                }
            )
        )

    qdrant.upsert(
        collection_name=repoName,
        points=points
    )

    print(f"Stored embeddings in Qdrant for repo: {repoName}")
