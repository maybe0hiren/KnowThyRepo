import os
from typing import List, Dict

from dotenv import load_dotenv
import google.generativeai as genai



load_dotenv()

LLM = os.getenv("GEMINI_KEY")
if not LLM:
    raise RuntimeError("API key not found in environment")

genai.configure(api_key=LLM)

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
                You are an expert software engineer analyzing a software project.

                Using ONLY the provided context, answer the question in detail.

                Your answer MUST:
                - Explain the purpose of the project
                - Describe how the project works at a high level
                - Mention key components or modules if present
                - Be written as a structured explanation (paragraphs or bullet points)
                Context:
                {contextText}
                Question:
                {question}
            """.strip()
    return prompt

def llmInteraction(question: str, chunks: List[Dict]) -> str:
    prompt = createPrompt(question, chunks)
    model = genai.GenerativeModel(modelName)
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 1024
        }
    )
    return response.text.strip()
