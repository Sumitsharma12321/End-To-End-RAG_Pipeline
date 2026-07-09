import argparse
import os
import sys
import time
import uuid

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "backend")
    ),
)

from app.services.document_processor import extract_text
from app.services.chunker import chunk_text
from app.services.embedder import embed_texts
from app.db.vector_store import store_chunks


def ingest_file(file_path: str, verbose: bool = True) -> dict:
    """
    Process a single PDF or TXT file and store its embeddings in ChromaDB.

    Args:
        file_path: Path to the PDF or TXT file.
        verbose: Whether to print progress messages.

    Returns:
        Dictionary containing document metadata.
    """

    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Validate file extension
    allowed_extensions = {".pdf", ".txt"}
    extension = os.path.splitext(file_path)[1].lower()

    if extension not in allowed_extensions:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            "Only PDF and TXT files are supported."
        )

    start_time = time.time()
    doc_id = str(uuid.uuid4())
    filename = os.path.basename(file_path)

    if verbose:
        print(f"\nProcessing: {filename}")
        print(f"Doc ID : {doc_id}")
        print(f"Path   : {file_path}")

    # Step 1: Extract text
    if verbose:
        print("\nStep 1: Extracting text...")

    text = extract_text(file_path)

    if verbose:
        print(f"   {len(text)} characters extracted")

    if not text.strip():
        raise ValueError(f"No text found in file: {file_path}")

    # Step 2: Create chunks
    if verbose:
        print("\nStep 2: Creating chunks...")

    chunks = chunk_text(text, doc_id)

    if verbose:
        print(f"   {len(chunks)} chunks created")

    # Step 3: Generate embeddings
    if verbose:
        print("\nStep 3: Generating embeddings...")

    embeddings = embed_texts([chunk["text"] for chunk in chunks])

    if verbose:
        print(f"   {len(embeddings)} vectors generated")

    # Step 4: Store in ChromaDB
    if verbose:
        print("\nStep 4: Storing in ChromaDB...")

    store_chunks(chunks, embeddings)

    elapsed = round(time.time() - start_time, 2)

    if verbose:
        print("\nIngestion completed successfully.")
        print(f"Document ID     : {doc_id}")
        print(f"Chunks Stored   : {len(chunks)}")
        print(f"Processing Time : {elapsed} seconds")
        print("-" * 50)

    return {
        "doc_id": doc_id,
        "filename": filename,
        "chunks_created": len(chunks),
        "characters": len(text),
        "time_taken": elapsed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest a single document into ChromaDB."
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Path to the PDF or TXT file.",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output.",
    )

    args = parser.parse_args()

    try:
        result = ingest_file(
            args.file,
            verbose=not args.quiet,
        )

        if args.quiet:
            print(
                f"Done: {result['chunks_created']} chunks "
                f"from {result['filename']}"
            )

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)