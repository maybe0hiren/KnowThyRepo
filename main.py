from pathlib import Path

from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import loadData, search
from llmInteraction import llmInteraction


def main():
    print("Project QA Assistant")

    projectPath = input("Enter project folder path: ").strip()

    projectRoot = Path(projectPath).expanduser().resolve()

    if not projectRoot.exists() or not projectRoot.is_dir():
        print(f"Invalid project path: {projectRoot}")
        return

    print(f"\nIndexing project: {projectRoot}")
    print("Type 'exit' to quit\n")

    scanned = projectScanner(str(projectRoot))
    chunks = chunker(scanned)
    embedder(chunks)

    index, metadata = loadData()

    idToContent = {c["chunkID"]: c["content"] for c in chunks}
    while True:
        question = input(">> ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        retrieved = search(question, index, metadata, top_k=6)

        contextChunk = []
        for r in retrieved:
            cid = r["chunkID"]
            r["content"] = idToContent.get(cid, "")
            contextChunk.append(r)

        if not contextChunk:
            print("\nNo relevant context found.\n")
            continue

        answer = llmInteraction(question, contextChunk)

        print("\n--- Answer ---")
        print(answer)
        print("--------------\n")


if __name__ == "__main__":
    main()
