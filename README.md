# 📌 KnowThyRepo

KnowThyRepo is an AI-powered repository assistant that can **clone any
GitHub project, index its codebase, and answer natural-language
questions about it** using a Retrieval-Augmented Generation (RAG)
pipeline.

------------------------------------------------------------------------

## 🚀 Introduction

KnowThyRepo helps developers, recruiters, and learners quickly
understand any codebase by allowing them to ask questions such as:

-   *What does this project do?*
-   *Which file handles authentication?*
-   *How is the backend structured?*
-   *What are the key modules in this repository?*

Instead of giving generic AI responses, KnowThyRepo retrieves the most
relevant parts of the repository and uses them as context before
generating an answer.

------------------------------------------------------------------------

## 🧠 Architecture

KnowThyRepo follows a **Retrieval-Augmented Generation (RAG)**
architecture:

### 1. Repository Cloning

-   Accepts a GitHub repository link
-   Clones it locally (cached if already cloned)

### 2. Project Scanning

-   Recursively scans code + documentation files
-   Ignores unnecessary folders (`node_modules`, `.git`, `venv`, etc.)

### 3. Chunking

Splits repository files into meaningful chunks: - Functions/classes for
code - Headings for markdown - Full blocks for config files

### 4. Embedding + Vector Indexing

-   Converts chunks into embeddings using Sentence Transformers
-   Stores embeddings inside a FAISS vector database
-   Using Gemini's embeddings for public hosting

### 5. Repo-Specific Persistent Storage

Each repository gets its own dedicated index:

    data/<repoName>/
       index.faiss
       metadata.json
       chunks.json

This prevents overwriting and allows multi-repo support.

### 6. Retrieval + Answer Generation

-   User question → FAISS similarity search retrieves top chunks
-   Gemini generates an answer using ONLY retrieved context

------------------------------------------------------------------------

## 🔑 BYOK Support (Bring Your Own Gemini Key)

KnowThyRepo uses a secure **BYOK model**, meaning: - Users submit their
own Gemini API key - The key is used only for that request - Keys are
never stored on the server

This ensures public usability without consuming the developer's quota.

------------------------------------------------------------------------

## 🛡️ Public Safety Features

To make KnowThyRepo safe for public deployment, the backend includes:

-   ✅ Rate limiting to prevent spam
-   ✅ Repository size limits (max file count + size)
-   ✅ Index caching (embeddings built only once per repo)
-   ✅ Automatic cleanup of old cloned repos

------------------------------------------------------------------------

## 🛠 Tech Stack

-   **Python 3.10+**
-   **Flask**
-   **FAISS**
-   **SentenceTransformers**
-   **Google Gemini API (`google-genai`)**
-   **Gunicorn**

------------------------------------------------------------------------

## 📦 Python Packages Required

Install dependencies:

``` bash
pip install flask
pip install faiss-cpu
pip install sentence-transformers
pip install python-dotenv
pip install google-genai
pip install gunicorn
```

------------------------------------------------------------------------

## 🔥 API Usage

Generate your Gemini's API key from https://developers.google.com/

Send a POST request:

``` bash
curl -X POST http://https://knowthyrepo.onrender.com/knowThyRepo \
  -H "Authorization: Bearer YOUR_GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "repoLink": "https://github.com/user/repo",
    "question": "What does this project do?"
  }'
```

Response:

``` json
{
  "answer": "This repository implements..."
}
```

------------------------------------------------------------------------

## 🌟 Project Scope

-   Integrate into a portfolio website
-   Add multi-turn chat memory
-   Detect repo updates and re-index only changed files
-   Add user authentication + quotas

