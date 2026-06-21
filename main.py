import os
from pathlib import Path

from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import search
from llmInteraction import llmInteraction
from repoCloner import repoCloner
from repoGuard import validateRepo

from qdrant_client import QdrantClient


def indexRepoMain(repoLink: str):

    qdrantUrl = os.getenv("QDRANT_URL")
    qdrantKey = os.getenv("QDRANT_KEY")

    projectPath = repoCloner(repoLink)
    projectRoot = Path(projectPath).resolve()

    if not projectRoot.exists():
        raise RuntimeError("Repo clone failed")

    repoName = projectRoot.name

    validateRepo(str(projectRoot))

    qdrant = QdrantClient(url=qdrantUrl, api_key=qdrantKey)

    existing = [c.name for c in qdrant.get_collections().collections]

    if repoName in existing:
        return "Repository already indexed"

    scanned = projectScanner(str(projectRoot))
    chunks = chunker(scanned)

    embedder(chunks, repoName, qdrantUrl, qdrantKey)

    return "Repository indexed successfully"


def askMain(repoLink: str, question: str, apiKey: str):

    qdrantUrl = os.getenv("QDRANT_URL")
    qdrantKey = os.getenv("QDRANT_KEY")

    repoName = repoLink.rstrip("/").split("/")[-1].replace(".git", "")

    retrievedChunks = search(
        question,
        repoName,
        qdrantUrl,
        qdrantKey,
        top_k=6
    )

    if not retrievedChunks:
        return "No relevant context found."

    answer = llmInteraction(question, retrievedChunks, apiKey)

    return answer

