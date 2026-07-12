from datetime import datetime
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..models.schemas import (
    UploadResponse,
    MultiUploadResponse,
    DocumentInfo,
    DocumentListResponse,
)
from ..utils.file_utils import save_upload
from ..services.document_processor import extract_text
from ..services.chunker import chunk_text
from ..services.embedder import embed_texts
from ..db.vector_store import (
    store_chunks,
    get_all_documents,
    delete_document,
    get_total_chunks,
)

router = APIRouter()




def process_single_file(file: UploadFile) -> UploadResponse:
    """
    Runs the complete ingestion pipeline for a single document.

    Steps:
    1. Save uploaded file
    2. Extract text
    3. Split into chunks
    4. Generate embeddings
    5. Store chunks in ChromaDB
    """

   

    # ----------------------------------------------------
    # Save file
    # ----------------------------------------------------
    doc_id, file_path = save_upload(file)

    # ----------------------------------------------------
    # Extract text
    # ----------------------------------------------------
    text = extract_text(file_path)

    if not text or not text.strip():
        raise ValueError(
            f"No text could be extracted from '{file.filename}'."
        )

    # ----------------------------------------------------
    # Create chunks
    # ----------------------------------------------------
    chunks = chunk_text(
        text=text,
        doc_id=doc_id,
        document_name=file.filename,
    )

    # ----------------------------------------------------
    # Generate embeddings
    # ----------------------------------------------------
    embeddings = embed_texts(
        [chunk["text"] for chunk in chunks]
    )

    # ----------------------------------------------------
    # Store chunks in ChromaDB
    # ----------------------------------------------------
    store_chunks(
        chunks,
        embeddings,
    )

    # ----------------------------------------------------
    # Return response
    # ----------------------------------------------------
    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        chunks_created=len(chunks),
        message=f"'{file.filename}' processed successfully.",
        upload_time=datetime.utcnow().isoformat(),
    )


@router.post(
    "/upload",
    response_model=UploadResponse,
)
async def upload_single_document(
    file: UploadFile = File(...),
):
    """
    Upload and process a single document.
    """

    try:
        return process_single_file(file)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}",
        )


@router.post(
    "/upload/multiple",
    response_model=MultiUploadResponse,
)
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
):
    """
    Upload and process multiple documents.
    """

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one file.",
        )

    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files can be uploaded at once.",
        )

    uploaded = []
    failed = []
    total_chunks = 0

    for file in files:

        try:
            result = process_single_file(file)
            uploaded.append(result)
            total_chunks += result.chunks_created

        except Exception as e:
            failed.append(
                f"{file.filename}: {str(e)}"
            )

    if not uploaded:
        raise HTTPException(
            status_code=500,
            detail="All uploaded files failed.",
        )

    message = (
        f"{len(uploaded)} file(s) processed successfully."
    )

    if failed:
        message += (
            f" {len(failed)} file(s) failed."
        )

    return MultiUploadResponse(
        uploaded=uploaded,
        total_files=len(uploaded),
        total_chunks=total_chunks,
        message=message,
    )


@router.get(
    "/documents",
    response_model=DocumentListResponse,
)
async def list_documents():
    """
    Returns all uploaded documents.
    """

    try:

        docs = get_all_documents()

        return DocumentListResponse(
            documents=[
                DocumentInfo(
                    doc_id=doc["doc_id"],
                    filename=doc["document_name"],
                    chunks_count=doc["chunks_count"],
                    upload_time=doc["upload_time"],
                )
                for doc in docs
            ],
            total_documents=len(docs),
            total_chunks=get_total_chunks(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch documents: {str(e)}",
        )


@router.delete(
    "/documents/{doc_id}",
)
async def delete_document_endpoint(
    doc_id: str,
):
    """
    Delete a document and all its chunks from ChromaDB.
    """

    try:

        deleted = delete_document(doc_id)

        return {
            "message": "Document deleted successfully.",
            "doc_id": doc_id,
            "chunks_deleted": deleted,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}",
        )