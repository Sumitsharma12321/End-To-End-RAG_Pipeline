from groq import Groq
from ..config import settings

client = Groq(api_key=settings.groq_api_key)


def generate_answer(question: str, context_chunks: list[str]) -> str:
    """Generate answer using retrieved document chunks."""

    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a helpful document assistant.

Use the context below to answer the question.

If the answer is partially in the context, provide the information that is available and clearly mention what is not specified or unclear from the document.

Context:
{context}

Question:
{question}

Provide a clear, detailed answer:
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=800
    )

    return response.choices[0].message.content.strip()