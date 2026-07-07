from groq import Groq
from ..config import settings

client = Groq(api_key=settings.groq_api_key)


def generate_answer(question: str, context_chunks: list[str]) -> str:
    """Generate answer using retrieved document chunks."""

    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a helpful document assistant.

Answer the question using ONLY the context below.

If the answer is not present in the context, reply:
"I don't know based on the document."

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()