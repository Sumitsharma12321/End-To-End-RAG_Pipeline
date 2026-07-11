# ================================================================
# FILE: app/api/query.py
# FIX: Context chunks plain text format mein pass karo LLM ko
#
# PROBLEM: Naye query.py mein chunks dict format mein the
#   generate_answer() ko dict list milti thi aur
#   [Source 1: file.pdf, Page ~3] labels context mein aate the
#   Model in labels pe focus karta tha — answer chhota hota tha
#
# FIX:
#   1. Context chunks plain text extract karo pehle
#   2. generate_answer ko simple text list pass karo
#   3. Sources separately build karo — context mein nahi
#   4. doc_id filter rakha — multi-doc support intact
# ================================================================

from fastapi import APIRouter, HTTPException
from ..models.schemas import QueryRequest, QueryResponse
from ..services.embedder import embed_query
from ..db.vector_store import search, get_all_documents
from ..services.llm_service import generate_answer
from ..config import settings

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Document(s) se question ka answer lo.

    - doc_id diya: sirf us document mein search
    - doc_id nahi diya: sab documents mein search

    FIX: Context plain text format mein pass hota hai LLM ko
         Sources alag se build hote hain — context mein nahi
    """
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question empty nahi ho sakta."
        )

    try:
        # Step 1: Question embed karo
        query_vec = embed_query(request.question)

        # Step 2: searched_in determine karo
        searched_in = "all documents"
        if request.doc_id:
            all_docs = get_all_documents()
            doc_info = next(
                (d for d in all_docs if d["doc_id"] == request.doc_id),
                None
            )
            if doc_info:
                searched_in = doc_info["document_name"]
            else:
                searched_in = f"document ({request.doc_id[:8]}...)"

        # Step 3: Relevant chunks retrieve karo
        chunks = search(
            query_embedding=query_vec,
            top_k=settings.top_k,
            doc_id=request.doc_id
        )

        if not chunks:
            return QueryResponse(
                answer=(
                    "No relevant information found. "
                    "Try rephrasing your question."
                ),
                sources=[],
                searched_in=searched_in
            )

        # Step 4: FIX — Plain text list banao LLM ke liye
        # Dict se sirf text nikalo — metadata LLM ko confuse karta tha
        plain_texts = []
        for chunk in chunks:
            if isinstance(chunk, dict):
                text = chunk.get("text", "")
                if text:
                    plain_texts.append(text)
            else:
                plain_texts.append(str(chunk))

        # Step 5: LLM se answer lo — plain text pass karo
        answer = generate_answer(
            question=request.question,
            context_chunks=plain_texts,     # FIX: plain text, not dicts
            searched_in=searched_in
        )

        # Step 6: Sources build karo — answer ke liye nahi, display ke liye
        sources = []
        seen_sources = set()
        for chunk in chunks:
            if isinstance(chunk, dict):
                doc_name = chunk.get("document_name", "Unknown")
                page = chunk.get("page_number", "?")
                source_key = f"{doc_name}_p{page}"
                if source_key not in seen_sources:
                    sources.append(f"{doc_name} (Page ~{page})")
                    seen_sources.add(source_key)
            else:
                # Old format — generic source
                if "Document" not in sources:
                    sources.append("Document")

        return QueryResponse(
            answer=answer,
            sources=sources[:5],
            searched_in=searched_in
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )