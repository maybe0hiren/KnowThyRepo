from scanner import projectScanner
from chunker import chunker
from embedder import embedder
from search import loadData, search
from llmInteraction import llmInteraction


def main():
    print("Project QA Assistant")
    print("Type 'exit' to quit\n")

    scanned = project_scanner(".")
    chunks = chunker(scanned)

    embedder(chunks)

    index, metadata = load_data()

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
            print("No relevant context found.\n")
            continue

        answer = llmInteraction(question, contextChunk)

        print("\n--- Answer ---")
        print(answer)
        print("--------------\n")


if __name__ == "__main__":
    main()
