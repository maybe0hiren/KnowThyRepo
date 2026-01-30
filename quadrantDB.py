import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

def getClient():
    return QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

def createCollection(repoName: str, dim: int):
    client = getClient()

    if repoName not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
            collection_name=repoName,
            vectors_config=VectorParams(
                size=dim,
                distance=Distance.COSINE
            )
        )
