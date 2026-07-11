from groq import Groq

from ..config import settings

# Initialize Groq client
client = Groq(api_key=settings.groq_api_key)


def generate_answer(
    question: str,
    context_chunks: list,
    searched_in: str = "all documents",
) -> str:
    """
    Generate an answer using the retrieved document chunks.

    Args:
        question:
            User question.

        context_chunks:
            Retrieved chunks.
            Supports both:
                - list[dict] (recommended)
                - list[str]  (backward compatible)

        searched_in:
            Name of the searched document or
            "all documents".

    Returns:
        Generated answer.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    # -------------------------------------------------------
    # Build Context
    # -------------------------------------------------------

    context_parts = []

    for index, chunk in enumerate(context_chunks, start=1):

        if isinstance(chunk, dict):

            document_name = chunk.get(
                "document_name",
                "Unknown Document",
            )

            page_number = chunk.get(
                "page_number",
                "?",
            )

            text = chunk.get(
                "text",
                "",
            )

            context_parts.append(
                f"[Source {index}: {document_name}, Page {page_number}]\n{text}"
            )

        else:

            context_parts.append(
                f"[Source {index}]\n{chunk}"
            )

    if not context_parts:
        return (
            "I could not find any relevant information "
            "in the uploaded documents."
        )

    context = "\n\n-------------------------\n\n".join(
        context_parts
    )

    # -------------------------------------------------------
    # Search Scope
    # -------------------------------------------------------

    if searched_in == "all documents":
        scope = "Search scope: All uploaded documents."
    else:
        scope = f"Search scope: {searched_in}"

    # -------------------------------------------------------
    # Prompt
    # -------------------------------------------------------

    prompt = f"""
You are an intelligent document assistant.

{scope}

Use ONLY the information provided in the context below.

Rules:
1. Never use outside knowledge.
2. If the answer is fully available, answer completely.
3. If only part of the answer is available, answer only that part and state what is missing.
4. If the answer is not present in the context, reply:
   "The uploaded documents do not contain this information."
5. When information comes from multiple documents, combine it logically.
6. Mention document names naturally whenever they help the reader.
7. Do not hallucinate or guess.

Context:

{context}

Question:

{question}

Answer:
"""

    # -------------------------------------------------------
    # LLM Call
    # -------------------------------------------------------

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise document analysis assistant."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.1,
        max_tokens=1000,
    )

    answer = response.choices[0].message.content

    return answer.strip() if answer else "Unable to generate an answer."