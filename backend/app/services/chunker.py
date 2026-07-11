"""
FILE: app/services/chunker.py

PURPOSE:
Splits extracted document text into smaller chunks and attaches
metadata required for retrieval.

CHANGES:
1. Added `document_name` parameter.
2. Stores document_name in metadata.
3. Estimates page number for every chunk.
4. Adds character start position.
5. Added validation for empty text and empty chunks.

WHY?
These metadata fields help:
- Filter documents during retrieval.
- Display source information in the frontend.
- Improve debugging and traceability.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config import settings


def chunk_text(
    text: str,
    doc_id: str,
    document_name: str = "Unknown"
) -> list[dict]:
    """
    Split document text into chunks and attach metadata.

    Args:
        text:
            Extracted document text.

        doc_id:
            Unique document identifier.

        document_name:
            Original uploaded filename.

    Returns:
        List of chunk dictionaries.
    """

    # Validate input
    if not text or not text.strip():
        raise ValueError("Document contains no text.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ".",
            "!",
            "?",
            " ",
            "",
        ],
    )

    raw_chunks = splitter.split_text(text)

    if not raw_chunks:
        raise ValueError("No chunks were generated from the document.")

    # Approximate characters per page
    chars_per_page = 3000
    total_chars = len(text)

    chunks = []

    for i, chunk in enumerate(raw_chunks):

        # Estimate chunk position in original text
        position = text.find(chunk[:50])

        if position == -1:
            position = i * (
                total_chars // max(len(raw_chunks), 1)
            )

        estimated_page = max(
            1,
            (position // chars_per_page) + 1
        )

        chunks.append(
            {
                "id": f"{doc_id}_chunk_{i}",
                "text": chunk,
                "metadata": {
                    "doc_id": doc_id,
                    "document_name": document_name,
                    "chunk_index": i,
                    "page_number": estimated_page,
                    "char_start": position,
                },
            }
        )

    return chunks