import json
from typing import List, Dict

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer as ST
from tqdm import tqdm

modelName = "all-MiniLM-L6-v2"
indexFile = "data/index.faiss"
metadataFile = "data/metadata.json"

def embedder(chunks: List[Dict]) -> None:
    if not chunks:
        raise ValueError("No chunks provided")
    model = ST(modelName)
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(
        texts,
        batch_size = 32,
        show_progress_bar = True,
        convert_to_numpy = True,
        normalize_embeddings = True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)
    
    faiss.write_index(index, indexFile)
    
    metadata = []
    for i, chunk in enumerate(chunks):
        meta = chunk.copy()
        meta.pop("content")
        meta["vector_id"] = i
        metadata.append(meta)

    with open(metadataFile, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Stored {len(chunks)} embeddings")
    print(f"FAISS index: {indexFile}")
    print(f"Metadata: {metadataFile}")
    