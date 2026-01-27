import os
from typing import List, Dict

from dotenv import load_dotenv
from google import genai



load_dotenv()

LLM = os.getenv("GEMINI_KEY")
if not LLM:
    raise RuntimeError("API key not found in environment")

client = genai.Client(api_key=LLM)

modelName = "models/gemini-2.5-flash"

def createPrompt(question: str, chunks: List[Dict]) -> str:

    contextBlocks = []

    for chunk in chunks:
        block = (
            f"File: {chunk['path']} "
            f"(lines {chunk['startLine']}-{chunk['endLine']})\n"
            f"{chunk['content']}"
        )
        contextBlocks.append(block)

    contextText = "\n\n---\n\n".join(contextBlocks)

    prompt = f"""
                You are an expert software engineer chatbot analyzing a software project.
                Using ONLY the provided context, answer the question in detail.
                Althought you are an expert, you have to wrap up the content like a chatbit would, keep the import points but the answer should be short and crisp.
                The answers must look like a chat and not an essay, so keep it simple, no headings and titles.
                Wrap your answer in 3-4 sentences max.
                Context:
                {contextText}
                Question:
                {question}
            """.strip()
    return prompt

def llmInteraction(question: str, chunks: List[Dict]) -> str:
    prompt = createPrompt(question, chunks)
    response = client.models.generate_content(
        model=modelName,
        contents=prompt
    )
    return response.text.strip()
