KnowThyRepo
=====================

An AI-powered repository assistant that can clone any GitHub
project, index its codebase, and answer natural-language questions about it
using a Retrieval-Augmented Generation (RAG) pipeline.

------------------------------------------------------------
INTRODUCTION
------------------------------------------------------------

KnowThyRepo helps developers, recruiters, and learners quickly understand
any codebase by asking questions such as:

- What does this project do?
- Which file handles authentication?
- How is the backend structured?
- What are the key modules in this repository?

Instead of generic AI answers, KnowThyRepo retrieves the most relevant
parts of the repository and uses them as context before generating a response.

------------------------------------------------------------
ARCHITECTURE
------------------------------------------------------------

KnowThyRepo follows a Retrieval-Augmented Generation (RAG) workflow:

1. Repository Cloning
   - Accepts a GitHub repository link
   - Clones it locally (cached if already cloned)

2. Project Scanning
   - Recursively scans code + documentation files
   - Ignores unnecessary folders (node_modules, .git, venv, etc.)

3. Chunking
   - Splits files into meaningful chunks:
     * Functions/classes for code
     * Headings for markdown
     * Full blocks for config files

4. Embedding + Vector Indexing
   - Converts chunks into embeddings using Gemini Embedding Models
   - SentenceTransformers support exists, but Gemini embeddings are used
     for lightweight public hosting.

5. Persistent Storage with Qdrant Cloud
   - Embeddings are stored permanently in Qdrant Cloud instead of local disk.
   - Each repository becomes its own Qdrant collection:

       Collection Name: KnowThyRepo
         - vectors (embeddings)
         - payload (chunk metadata + content)

   - This prevents re-indexing on every server restart and enables scalability.

6. Retrieval + Answer Generation
   - User question is embedded using Gemini
   - Qdrant similarity search retrieves top relevant chunks
   - Gemini generates an answer using ONLY retrieved context

------------------------------------------------------------
BYOK SUPPORT (Bring Your Own Gemini Key)
------------------------------------------------------------

KnowThyRepo uses a secure BYOK model:

- Users submit their own Gemini API key
- The key is used only for that request
- Keys are never stored on the server

------------------------------------------------------------
PUBLIC SAFETY FEATURES
------------------------------------------------------------

To ensure safe public deployment, KnowThyRepo includes:

- Rate limiting to prevent spam
- Repository size limits (max file count + size)
- Persistent indexing (embeddings built only once per repo)
- Automatic cleanup of cloned repositories

------------------------------------------------------------
TECH STACK
------------------------------------------------------------

- Python 3.10+
- Flask
- Google Gemini API (google-genai)
- Gemini Embedding Models
- Qdrant Cloud Vector Database
- Gunicorn
- Render Deployment

------------------------------------------------------------
PYTHON PACKAGES REQUIRED
------------------------------------------------------------

Install dependencies:

pip install flask
pip install google-genai
pip install qdrant-client
pip install python-dotenv
pip install gunicorn
pip install numpy

------------------------------------------------------------
ENVIRONMENT VARIABLES
------------------------------------------------------------

Create a .env file with your Qdrant credentials:

QDRANT_URL=https://xxxx.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

Gemini API key is provided by users via Authorization header.

------------------------------------------------------------
API USAGE
------------------------------------------------------------

Live API endpoint:

https://knowthyrepo.onrender.com/knowThyRepo

Example curl request:

curl -X POST https://knowthyrepo.onrender.com/knowThyRepo \
  -H "Authorization: Bearer YOUR_GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "repoLink": "https://github.com/user/repo",
    "question": "What does this project do?"
  }'

Response:

{
  "answer": "This repository implements..."
}

------------------------------------------------------------
FUTURE SCOPE
------------------------------------------------------------

- Integrate into a portfolio website for recruiter interaction
- Add multi-turn chat memory
- Detect repo updates and re-index only changed files
- Add user authentication + quotas
- Improve indexing speed with batch embeddings

------------------------------------------------------------
LIVE DEPLOYMENT
------------------------------------------------------------

KnowThyRepo is publicly accessible at:

https://knowthyrepo.onrender.com
