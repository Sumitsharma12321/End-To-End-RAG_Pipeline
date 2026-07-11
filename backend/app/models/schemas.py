"""
FILE: app/models/schemas.py

PURPOSE:
Defines all request and response models used by the FastAPI application.

FEATURES:
1. Supports single document upload.
2. Supports multiple document upload.
3. Supports querying a specific document or all documents.
4. Provides document list information.
5. Returns metadata required by the frontend.
"""

from typing import Optional
from pydantic import BaseModel


# ============================================================
# Upload Schemas
# ============================================================

class UploadResponse(BaseModel):
    """
    Response returned after uploading a single document.
    """

    doc_id: str
    filename: str
    chunks_created: int
    message: str
    upload_time: Optional[str] = None


class MultiUploadResponse(BaseModel):
    """
    Response returned after uploading multiple documents.
    """

    uploaded: list[UploadResponse]
    total_files: int
    total_chunks: int
    message: str


# ============================================================
# Query Schemas
# ============================================================

class QueryRequest(BaseModel):
    """
    Request model for asking questions.

    If doc_id is provided:
        Search only within that document.

    If doc_id is None:
        Search across all uploaded documents.
    """

    question: str
    doc_id: Optional[str] = None


class QueryResponse(BaseModel):
    """
    Response returned after querying the knowledge base.
    """

    answer: str
    sources: list[str]
    searched_in: str


# ============================================================
# Document Management Schemas
# ============================================================

class DocumentInfo(BaseModel):
    """
    Information about a single uploaded document.
    """

    doc_id: str
    filename: str
    chunks_count: int
    upload_time: str


class DocumentListResponse(BaseModel):
    """
    Response model for listing all uploaded documents.
    """

    documents: list[DocumentInfo]
    total_documents: int
    total_chunks: int