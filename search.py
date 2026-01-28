import json
from typing import List, Dict
from pathlib import Path

import faiss
# from sentence_transformers import SentenceTransformer as ST
from google import genai
import numpy as np


# modelName = "all-MiniLM-L6-v2"
embedModel = "models/text-embedding-004"

# model = ST(modelName)


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


def search(query: str, index, metadata: List[Dict], apiKey: str, top_k: int = 6) -> List[Dict]:
    client = genai.Client(api_key=apiKey)

    # queryVector = model.encode(
    #     [query],
    #     convert_to_numpy=True,
    #     normalize_embeddings=True
    # )

    response = client.models.embed_content(
        model=embedModel,
        contents=query
    )

    queryVector = np.array(
        response.embeddings[0].values,
        dtype="float32"
    ).reshape(1, -1)

    scores, indices = index.search(queryVector, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        chunkMeta = metadata[idx].copy()
        chunkMeta["score"] = float(score)
        results.append(chunkMeta)

    return results
