import os
from pathlib import Path

from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import search
from llmInteraction import llmInteraction
from repoCloner import repoCloner

from cleanup import cleanup
from repoGuard import validateRepo

from qdrant_client import QdrantClient


def main(apiKey: str, repoLink: str, question: str) -> str:
    cleanup()

    qdrantUrl = os.getenv("QDRANT_URL")
    qdrantKey = os.getenv("QDRANT_API_KEY")

    if not qdrantUrl or not qdrantKey:
        return "Qdrant credentials missing in environment."

    projectPath = repoCloner(repoLink)
    projectRoot = Path(projectPath).resolve()

    if not projectRoot.exists() or not projectRoot.is_dir():
        return "Repository could not be cloned or accessed."

    repoName = projectRoot.name

    try:
        validateRepo(str(projectRoot))
    except Exception as e:
        return f"Repo rejected: {str(e)}"

    qdrant = QdrantClient(url=qdrantUrl, api_key=qdrantKey)
    existing = [c.name for c in qdrant.get_collections().collections]

    if repoName in existing:
        print(f"Repo '{repoName}' already indexed in Qdrant, skipping embedding...")
    else:
        print(f"Indexing repo: {repoName}")

        scanned = projectScanner(str(projectRoot))
        chunks = chunker(scanned)

        embedder(chunks, repoName, apiKey, qdrantUrl, qdrantKey)

    retrievedChunks = search(
        question,
        repoName,
        apiKey,
        qdrantUrl,
        qdrantKey,
        top_k=6
    )

    if not retrievedChunks:
        return "No relevant context found in this repository."

    try:
        answer = llmInteraction(question, retrievedChunks, apiKey)
        return answer
    except Exception as e:
        return f"LLM Error: {str(e)}"
