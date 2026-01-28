#KnowThyRepo

An AI-powered repository assistant that can clone any
GitHub project, index its codebase, and answer natural-language
questions about it using a Retrieval-Augmented Generation (RAG)
pipeline.

------------------------------------------------------------------------

## Introduction

KnowThyRepo helps developers, recruiters, and learners quickly
understand any codebase by allowing them to ask questions such as:

-   What does this project do?
-   Which files handle authentication?
-   How is the backend structured?
-   What are the key modules in this repository?

Instead of giving generic AI responses, KnowThyRepo retrieves the most
relevant parts of the repository and uses them as context before
generating an answer.

------------------------------------------------------------------------

## Architecture

KnowThyRepo follows a Retrieval-Augmented Generation (RAG) architecture:

1. Repository Cloning

-   Accepts a GitHub repo link
-   Clones it locally (cached if already cloned)

2. Project Scanning

-   Recursively scans source code and documentation files
-   Ignores unnecessary folders (node_modules, .git, venv, etc.)

3. Chunking

-   Splits files into meaningful chunks:
    -   Functions and classes for code
    -   Headings for markdown
    -   Full config blocks for JSON/YAML

4. Embedding + Vector Indexing

-   Converts chunks into embeddings using Sentence Transformers
-   Stores embeddings in a FAISS vector index

5. Repo-Specific Storage

Each repository gets its own persistent index:

    data/<repoName>/
       index.faiss
       metadata.json
       chunks.json

6. Retrieval + Answer Generation

-   User question → vector search retrieves relevant chunks
-   Gemini LLM generates a short, grounded answer based only on
    retrieved context

------------------------------------------------------------------------

## Tech Stack

Core Language

-   Python 3.10+

Vector Search + Embeddings

-   FAISS
-   SentenceTransformers (all-MiniLM-L6-v2)

LLM Provider

-   Google Gemini API (google-genai)

Backend API

-   Flask (REST API endpoint)

------------------------------------------------------------------------

## Python Packages Required

    flask
    faiss-cpu
    sentence-transformers
    python-dotenv
    google-genai

------------------------------------------------------------------------

## Running the Backend

Start the Flask server:

    python app.py

The backend will run at:

    http://localhost:8000

------------------------------------------------------------------------

## API Usage

Send a POST request:

    curl -X POST http://localhost:8000/knowThyRepo \
      -H "Content-Type: application/json" \
      -d '{
        "repoLink": "https://github.com/user/repo",
        "question": "What does this project do?",
        "apiKey": "YOUR_GEMINI_API_KEY"
      }'

Response:

    {
      "answer": "This repository implements..."
    }

------------------------------------------------------------------------

## Project Scope

-   Integrate into a portfolio website so recruiters can interact
    directly
-   Add conversation memory for multi-turn context
-   Detect repo updates and re-index only changed files
-   Support multiple repos seamlessly
