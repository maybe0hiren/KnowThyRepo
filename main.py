from pathlib import Path

from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import loadData, search
from llmInteraction import llmInteraction


def main(apiKey: str, projectPath: str, question: str) -> str:
    projectRoot = Path(projectPath).expanduser().resolve()
    if not projectRoot.exists() or not projectRoot.is_dir():
        print(f"Invalid project path: {projectRoot}")
        return

    scanned = projectScanner(str(projectRoot))
    chunks = chunker(scanned)
    embedder(chunks)

    index, metadata = loadData()

    idToContent = {c["chunkID"]: c["content"] for c in chunks}

    retrieved = search(question, index, metadata, top_k=6)

    contextChunk = []
    for r in retrieved:
        cid = r["chunkID"]
        r["content"] = idToContent.get(cid, "")
        contextChunk.append(r)
    if not contextChunk:
        return "No relevant context found"

    answer = llmInteraction(question, contextChunk, apiKey)
    return answer
