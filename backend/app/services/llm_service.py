# ================================================================
# FILE: app/services/llm_service.py
# FIX: Answer quality restore kiya — pehle wala simple prompt wapas
#
# PROBLEM: Naye prompt mein:
#   1. "cite sources" force kiya — model sources pe focus karta tha
#   2. Context format change tha [Source 1: file.pdf, Page ~3]
#      model formatting pe zyada dhyan deta tha, answer pe kam
#   3. system prompt restrict tha — "always cite document" se
#      model darr ke chhota answer deta tha
#
# FIX:
#   1. Simple clean prompt wapas — pehle jaisa
#   2. Context plain text format — no source labels
#   3. System prompt simple — just be helpful
#   4. Multi-doc support bhi rakha — backward compatible
# ================================================================

from groq import Groq
from ..config import settings

# Module level pe load karo — har call pe nahi
client = Groq(api_key=settings.groq_api_key)


def generate_answer(
    question: str,
    context_chunks: list,
    searched_in: str = "all documents"
) -> str:
    """
    RAG prompt banao aur Groq se answer lo.

    Args:
        question: user ka sawaal
        context_chunks: list of dicts ya list of strings (dono support)
        searched_in: scope info (response mein use hota hai)

    Returns:
        str: detailed, helpful answer
    """
    if not question or not question.strip():
        raise ValueError("Question empty nahi ho sakta.")

    # Context build karo — SIMPLE format, no source labels
    # Ye pehle wala approach tha jo better answers deta tha
    context_texts = []
    for chunk in context_chunks:
        if isinstance(chunk, dict):
            # dict format se sirf text nikalo — metadata ignore karo
            text = chunk.get("text", "")
            if text:
                context_texts.append(text)
        else:
            # plain string — directly use karo
            if chunk:
                context_texts.append(str(chunk))

    if not context_texts:
        return (
            "I could not find relevant information in the uploaded documents. "
            "Please try rephrasing your question or upload a relevant document."
        )

    # Plain context — separator se join karo
    context = "\n\n---\n\n".join(context_texts)

    # SIMPLE PROMPT — pehle jaisa jo badiya tha
    prompt = f"""You are a helpful document assistant.
Use the context below to answer the question in detail.
If the answer is partially in the context, give what you can.
If the answer is not in the context, say "This information is not found in the document."
Do not make up information. Give a complete, detailed, and helpful answer.

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful and knowledgeable document assistant. "
                    "Give detailed, complete, and accurate answers based on the provided context. "
                    "Do not just quote lines — explain concepts properly."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,        # thoda higher — better explanation
        max_tokens=1500         # zyada tokens = zyada detailed answer
    )

    answer = response.choices[0].message.content
    return answer.strip() if answer else "Unable to generate answer."