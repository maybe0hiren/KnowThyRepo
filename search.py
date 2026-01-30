from typing import List, Dict

from google import genai
import numpy as np

from qdrant_client import QdrantClient


geminiEmbedder = "models/gemini-embedding-001"


def search(query: str, repoName: str, apiKey: str,
           qdrantUrl: str, qdrantKey: str,
           top_k: int = 6) -> List[Dict]:

    client = genai.Client(api_key=apiKey)

    response = client.models.embed_content(
        model=geminiEmbedder,
        contents=query
    )

    queryVector = np.array(
        response.embeddings[0].values,
        dtype="float32"
    ).tolist()

    qdrant = QdrantClient(url=qdrantUrl, api_key=qdrantKey)

    results = qdrant.query_points(
        collection_name=repoName,
        query=queryVector,
        limit=top_k
    ).points

    chunks = []
    for r in results:
        payload = r.payload
        payload["score"] = r.score
        chunks.append(payload)

    return chunks
