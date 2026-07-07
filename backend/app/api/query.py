from fastapi import APIRouter, HTTPException

from ..models.schemas import QueryRequest, QueryResponse
from ..services.embedder import embed_query
from ..db.vector_store import search
from ..services.llm_service import generate_answer
from ..config import settings

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    try:
        # Convert question to embedding
        query_vec = embed_query(request.question)

        # Retrieve relevant chunks
        chunks = search(query_vec, top_k=settings.top_k)

        # Generate answer
        answer = generate_answer(request.question, chunks)

        return QueryResponse(
            answer=answer,
            sources=[f"Chunk {i+1}" for i in range(len(chunks))]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))