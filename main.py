from pathlib import Path

from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import loadData, search
from llmInteraction import llmInteraction
from repoCloner import repoCloner


def main(apiKey: str, repoLink: str, question: str) -> str:
    projectPath = repoCloner(repoLink)
    projectRoot = Path(projectPath).resolve()

    if not projectRoot.exists():
        return "Invalid repo path."

    repoName = projectRoot.name

    repoDataFolder = Path("data") / repoName
    indexFile = repoDataFolder / "index.faiss"

    # Build embeddings only once
    if not indexFile.exists():
        scanned = projectScanner(str(projectRoot))
        chunks = chunker(scanned)
        embedder(chunks, repoName)

    # ✅ Load index + metadata + chunks.json
    index, metadata, chunks = loadData(repoName)

    # Search
    retrieved = search(question, index, metadata)

    if not retrieved:
        return "No relevant context found."

    idToChunk = {c["chunkID"]: c for c in chunks}

    contextChunks = []
    for r in retrieved:
        cid = r["chunkID"]
        chunkData = idToChunk.get(cid)

        if chunkData:
            contextChunks.append(chunkData)

    return llmInteraction(question, contextChunks, apiKey)
