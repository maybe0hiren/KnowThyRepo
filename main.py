from pathlib import Path

from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import loadData, search
from llmInteraction import llmInteraction


def main():
    print("Project QA Assistant")

    project_path = input("Enter project folder path: ").strip()

    project_root = Path(project_path).expanduser().resolve()

    if not project_root.exists() or not project_root.is_dir():
        print(f"Invalid project path: {project_root}")
        return

    print(f"\nIndexing project: {project_root}")
    print("Type 'exit' to quit\n")

    scanned = projectScanner(str(project_root))
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
