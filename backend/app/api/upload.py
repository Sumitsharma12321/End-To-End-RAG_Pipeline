from fastapi import APIRouter, UploadFile, File, HTTPException

from ..models.schemas import UploadResponse
from ..utils.file_utils import save_upload
from ..services.document_processor import extract_text
from ..services.chunker import chunk_text
from ..services.embedder import embed_texts
from ..db.vector_store import store_chunks

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        # Save file
        doc_id, file_path = save_upload(file)

        # Extract text
        text = extract_text(file_path)

        # Split into chunks
        chunks = chunk_text(text, doc_id)

        # Create embeddings
        embeddings = embed_texts([chunk["text"] for chunk in chunks])

        # Store in ChromaDB
        store_chunks(chunks, embeddings)

        return UploadResponse(
            doc_id=doc_id,
            filename=file.filename,
            chunks_created=len(chunks),
            message="Document processed successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))