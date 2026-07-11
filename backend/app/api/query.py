from fastapi import APIRouter, HTTPException

from ..models.schemas import QueryRequest, QueryResponse
from ..services.embedder import embed_query
from ..db.vector_store import search, get_all_documents
from ..services.llm_service import generate_answer
from ..config import settings

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """
    Query uploaded documents.

    If doc_id is provided:
        Search only inside that document.

    If doc_id is None:
        Search across all uploaded documents.
    """

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        # ----------------------------------------------------
        # Create query embedding
        # ----------------------------------------------------

        query_vector = embed_query(request.question)

        # ----------------------------------------------------
        # Determine search scope
        # ----------------------------------------------------

        searched_in = "all documents"

        if request.doc_id:

            documents = get_all_documents()

            document = next(
                (
                    d
                    for d in documents
                    if d["doc_id"] == request.doc_id
                ),
                None,
            )

            if document:
                searched_in = document["document_name"]
            else:
                searched_in = "selected document"

        # ----------------------------------------------------
        # Retrieve relevant chunks
        # ----------------------------------------------------

        chunks = search(
            query_embedding=query_vector,
            top_k=settings.top_k,
            doc_id=request.doc_id,
        )

        if not chunks:

            return QueryResponse(
                answer=(
                    "No relevant information was found "
                    "in the selected document(s)."
                ),
                sources=[],
                searched_in=searched_in,
            )

        # ----------------------------------------------------
        # Generate answer
        # ----------------------------------------------------

        answer = generate_answer(
            question=request.question,
            context_chunks=chunks,
            searched_in=searched_in,
        )

        # ----------------------------------------------------
        # Build sources
        # ----------------------------------------------------

        sources = []
        seen = set()

        for chunk in chunks:

            document_name = chunk.get(
                "document_name",
                "Unknown",
            )

            page_number = chunk.get(
                "page_number",
                "?",
            )

            source = (
                f"{document_name} "
                f"(Page {page_number})"
            )

            if source not in seen:
                seen.add(source)
                sources.append(source)

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return QueryResponse(
            answer=answer,
            sources=sources,
            searched_in=searched_in,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )