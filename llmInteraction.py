import os
from typing import List, Dict
from google import genai


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
                Using ONLY the provided context, answer the user's question in clear, simple, and accurate language. Focus on explaining how the project works, including its architecture, workflow, components, and relationships between files, modules, or services only and only whenever relevant to the question.
                Guidelines:
                Base your answer strictly on the provided context. Do not make assumptions or invent details.
                Explain technical concepts in an easy-to-understand way while preserving important implementation details.
                When relevant, describe the flow of data, control, or execution through the system.
                Highlight the purpose of key components and how they interact.
                If the context is insufficient to fully answer the question, clearly state what information is missing.
                Prefer practical explanations over theoretical ones.
                Response Style:
                Answer like a helpful chatbot, not a documentation page.
                Use natural conversational language.
                Keep the response concise but informative.
                Avoid headings, titles, greetings, and unnecessary introductions.
                Prioritize explaining "what", "how", and "why" in relation to the project's structure and workflow.
                Limit the response to approximately 4–8 sentences unless the question requires more detail.
                Context:
                {contextText}
                Question:
                {question}
            """.strip()
    return prompt

def llmInteraction(question: str, chunks: List[Dict], apiKey: str) -> str:
    if not apiKey:
        raise RuntimeError("API key invalid")
    client = genai.Client(api_key=apiKey)
    modelName = "models/gemini-2.5-flash"
    prompt = createPrompt(question, chunks)
    response = client.models.generate_content(
        model=modelName,
        contents=prompt
    )
    return response.text.strip()
