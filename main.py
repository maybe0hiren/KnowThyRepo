import sys
from pathlib import Path

from scanner import project_scanner
from chunker import chunker
from embedder import embedder
from search import load_data, search
from llmInteraction import llmInteraction


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <project_path>")
        sys.exit(1)

    project_root = Path(sys.argv[1]).resolve()

    if not project_root.exists() or not project_root.is_dir():
        print(f"Invalid project path: {project_root}")
        sys.exit(1)

    print("Project QA Assistant")
    print(f"Project: {project_root}")
    print("Type 'exit' to quit\n")

    scanned = project_scanner(str(project_root))
    chunks = chunker(scanned)
    embedder(chunks)

    index, metadata = load_data()

    idToContent = {c["chunkID"]: c["content"] for c in chunks}

    while True:
        question = input(">> ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        retrieved = search(question, index, metadata, top_k=6)

        context = []
        for r in retrieved:
            cid = r["chunkID"]
            r["content"] = idToContent.get(cid, "")
            context.append(r)

        if not context:
            print("\nNo relevant context found.\n")
            continue

        answer = llmInteraction(question, context)

        print("\n--- Answer ---")
        print(answer)
        print("--------------\n")


if __name__ == "__main__":
    main()
