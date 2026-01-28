import json
from typing import List, Dict
from pathlib import Path

import faiss
# from sentence_transformers import SentenceTransformer as ST
from google import genai
import numpy as np


# modelName = "all-MiniLM-L6-v2"
geminiEmbedder = "models/gemini-embedding-001"


def embedder(chunks: List[Dict], repoName: str, apiKey: str) -> None:
    if not chunks:
        raise ValueError("No chunks provided")

    repoFolder = Path("data") / repoName
    repoFolder.mkdir(parents=True, exist_ok=True)

    indexFile = repoFolder / "index.faiss"
    metadataFile = repoFolder / "metadata.json"
    chunksFile = repoFolder / "chunks.json"

    # model = ST(modelName)
    texts = [chunk["content"] for chunk in chunks]

    client = genai.Client(api_key=apiKey)

    vectors = []
    for text in texts:
        response = client.models.embed_content(
            model=geminiEmbedder,
            contents=text
        )
        vectors.append(response.embeddings[0].values)

    embeddings = np.array(vectors).astype("float32")

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
