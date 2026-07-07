import os
import shutil
import subprocess
from pathlib import Path

from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import search
from llmInteraction import llmInteraction
from repoCloner import repoCloner
from repoGuard import validateRepo

import sqlDB
import quadrantDB

EMBEDDING_DIM = 384


def checkRepoStatus(repoLink: str):
    print("Checking repo status")

    # Get latest commit hash
    result = subprocess.run(
        ["git", "ls-remote", repoLink, "HEAD"],
        capture_output=True,
        text=True,
        check=True
    )

    repoHash = result.stdout.split()[0]

    # New repository
    if not sqlDB.repoExists(repoLink):
        return False, repoHash

    # Existing repository
    return sqlDB.hashMatches(repoLink, repoHash), repoHash


def index(repoLink: str, newHash: str):
    print("Cloning repository")

    projectPath = repoCloner(repoLink)
    projectRoot = Path(projectPath).resolve()

    if not projectRoot.exists():
        raise RuntimeError("Repository clone failed")

    repoName = projectRoot.name

    qdrantUrl = os.getenv("QDRANT_URL")
    qdrantKey = os.getenv("QDRANT_API_KEY")

    try:
        validateRepo(str(projectRoot))

        client = quadrantDB.getClient()

        existing = [
            collection.name
            for collection in client.get_collections().collections
        ]

        # Fresh collection every time we re-index
        if repoName in existing:
            print("Deleting old collection")
            quadrantDB.deleteCollection(repoName)

        print("Creating collection")
        quadrantDB.createCollection(
            repoName,
            EMBEDDING_DIM
        )

        print("Scanning")
        scanned = projectScanner(str(projectRoot))

        print("Chunking")
        chunks = chunker(scanned)

        print("Embedding")
        embedder(
            chunks,
            repoName,
            qdrantUrl,
            qdrantKey
        )

        # Only update SQLite AFTER successful indexing
        if sqlDB.repoExists(repoLink):
            sqlDB.updateHash(repoLink, newHash)
        else:
            sqlDB.insertRepo(repoLink, newHash)

        print("Index complete")
        return 0

    finally:
        if projectRoot.exists():
            print("Cleaning up cloned repository")
            shutil.rmtree(projectRoot, ignore_errors=True)


def ask(repoLink: str, question: str, apiKey: str):
    print("Asking LLM")

    repoName = repoLink.rstrip("/").split("/")[-1].replace(".git", "")

    retrievedChunks = search(
        question,
        repoName,
        os.getenv("QDRANT_URL"),
        os.getenv("QDRANT_API_KEY"),
        top_k=6
    )

    if not retrievedChunks:
        return "No relevant context found."

    return llmInteraction(
        question,
        retrievedChunks,
        apiKey
    )


def main(repoLink: str, question: str, apiKey: str):
    status, repoHash = checkRepoStatus(repoLink)

    if status:
        print("Repository is already indexed and up to date.")
    else:
        print("Repository requires indexing.")
        index(repoLink, repoHash)

    return ask(
        repoLink,
        question,
        apiKey
    )