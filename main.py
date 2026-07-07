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
    print("checking repo status")
    if sqlDB.repoExists(repoLink):
        
        result = subprocess.run(
            ["git", "ls-remote", repoLink, "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        repoHash = result.stdout.split()[0]

        return [sqlDB.hashMatches(repoLink, repoHash), repoHash]
    return [False, None]

def index(repoLink: str, newHash: str):
    print("cloning repo")
    projectPath = repoCloner(repoLink)
    projectRoot = Path(projectPath).resolve()
    if not projectRoot.exists():
        raise RuntimeError("Repo clone failed")
    repoName = projectRoot.name
    qdrantUrl = os.getenv("QDRANT_URL")
    qdrantKey = os.getenv("QDRANT_KEY")
    validateRepo(str(projectRoot))
    qdrant = QdrantClient(url=qdrantUrl, api_key=qdrantKey)
    existing = [c.name for c in qdrant.get_collections().collections]
    if repoName in existing:
        return "Repository already indexed"
    quadrantDB.createCollection(repoName, 3072)
    if sqlDB.repoExists(repoLink):
        sqlDB.updateHash(repoLink, newHash)
    else:
        sqlDB.insertRepo(repoLink, newHash)
    print("Scanning")
    scanned = projectScanner(str(projectRoot))
    print("chunking")
    chunks = chunker(scanned)
    print("Embedding")
    embedder(chunks, repoName, qdrantUrl, qdrantKey)

    result = subprocess.run(
            ["rm", "-rf", projectRoot],
            capture_output=True,
            text=True,
            check=True
        )
    return 0;


def ask(repoLink: str, question: str, apiKey: str):
    print("asking LLM")
    qdrantUrl = os.getenv("QDRANT_URL")
    qdrantKey = os.getenv("QDRANT_KEY")

    repoName = repoLink.rstrip("/").split("/")[-1].replace(".git", "")
    print("Getting chunks")
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
        if index(repoLink, repoHash) == 0:
            return ask(repoLink, question, apiKey)

