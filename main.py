import os
from pathlib import Path
import subprocess

from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import search
from llmInteraction import llmInteraction
from repoCloner import repoCloner
from repoGuard import validateRepo

from qdrant_client import QdrantClient

import sqlDB
import quadrantDB


def checkRepoStatus(repoLink: str):
    if sqlDB.repoExists(repoLink):
        
        result = subprocess.run(
            ["git", "ls-remote", repoLink, "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        repoHash = result.stdout.split()[0]

        return [hashMatches(repoLink, repoHash), repoHash]
    return [False, NULL]

def index(repoLink: str, newHash: str):

    projectPath = repoCloner(repoLink)
    projectRoot = Path(projectPath).resolve()
    if not projectRoot.exists():
        raise RuntimeError("Repo clone failed")
    repoName = projectRoot.name

    quadrantDB.createCollection(repoName)
    updateHash(repoLink, newHash)

    qdrantUrl = os.getenv("QDRANT_URL")
    qdrantKey = os.getenv("QDRANT_KEY")
    validateRepo(str(projectRoot))
    qdrant = QdrantClient(url=qdrantUrl, api_key=qdrantKey)
    existing = [c.name for c in qdrant.get_collections().collections]
    if repoName in existing:
        return "Repository already indexed"
    scanned = projectScanner(str(projectRoot))
    chunks = chunker(scanned)
    embedder(chunks, repoName, qdrantUrl, qdrantKey)

    result = subprocess.run(
            ["rm", "-rf", projectRoot],
            capture_output=True,
            text=True,
            check=True
        )
    return 0;


def ask(repoLink: str, question: str, apiKey: str):

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


def main(repoLink: str, question: str, apiKey: str):
    [status, repoHash] = checkRepoStatus(repoLink)
    if status:
        return ask(repoLink, question, apiKey)
    else:
        if index(repoLink) == 0:
            return ask(repoLink, question, apiKey)

