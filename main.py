from pathlib import Path

from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import loadData, search
from llmInteraction import llmInteraction
from repoCloner import repoCloner

from cleanup import cleanup
from repoGuard import validateRepo


def main(apiKey: str, repoLink: str, question: str) -> str:
    cleanup()

    projectPath = repoCloner(repoLink)
    projectRoot = Path(projectPath).resolve()

    if not projectRoot.exists() or not projectRoot.is_dir():
        return "Repository could not be cloned or accessed."

    repoName = projectRoot.name

    try:
        validateRepo(str(projectRoot))
    except Exception as e:
        return f"Repo rejected: {str(e)}"

    repoDataFolder = Path("data") / repoName
    indexFile = repoDataFolder / "index.faiss"
    metadataFile = repoDataFolder / "metadata.json"
    chunksFile = repoDataFolder / "chunks.json"

    if indexFile.exists() and metadataFile.exists() and chunksFile.exists():
        print(f"Index already exists for '{repoName}', skipping embedding...")
    else:
        print(f"Indexing repo: {repoName}")

        scanned = projectScanner(str(projectRoot))
        chunks = chunker(scanned)

        embedder(chunks, repoName)

    try:
        index, metadata, chunks = loadData(repoName)
    except Exception:
        return "Failed to load index files. Try re-indexing."

    retrieved = search(question, index, metadata, top_k=6)

    if not retrieved:
        return "No relevant context found in this repository."

    idToChunk = {c["chunkID"]: c for c in chunks}

    contextChunks = []
    for r in retrieved:
        chunkData = idToChunk.get(r["chunkID"])
        if chunkData:
            contextChunks.append(chunkData)

    if not contextChunks:
        return "Relevant chunks were found, but content could not be loaded."

    try:
        answer = llmInteraction(question, contextChunks, apiKey)
        return answer
    except Exception as e:
        return f"LLM Error: {str(e)}"
