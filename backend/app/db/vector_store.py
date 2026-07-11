import chromadb
from datetime import datetime
from ..config import settings


# ---------------------------------------------------------------

_client = None
_collection = None


def get_collection():
    """
    Returns the ChromaDB collection using the Singleton pattern.
    """

    global _client, _collection

    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_db_path
        )

    if _collection is None:
        _collection = _client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

    return _collection


# ---------------------------------------------------------------
# Store Chunks
# ---------------------------------------------------------------

def store_chunks(
    chunks: list[dict],
    embeddings: list[list[float]]
) -> int:
    """
    Stores document chunks and their embeddings into ChromaDB.

    Args:
        chunks:
            List of chunk dictionaries.

            Each chunk should contain:
                id
                text
                metadata

            Metadata should include:
                doc_id
                document_name
                page_number
                chunk_index

        embeddings:
            Embedding vectors corresponding to each chunk.

    Returns:
        Number of chunks successfully stored.

    Notes:
        Automatically adds an upload timestamp
        to every chunk's metadata.
    """

    if not chunks or not embeddings:
        raise ValueError(
            "Chunks and embeddings cannot be empty."
        )

    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Mismatch between chunks ({len(chunks)}) "
            f"and embeddings ({len(embeddings)})."
        )

    collection = get_collection()

    upload_time = datetime.utcnow().isoformat()

    for chunk in chunks:

        if "metadata" not in chunk:
            chunk["metadata"] = {}

        chunk["metadata"]["upload_time"] = upload_time

    try:

        collection.add(
            ids=[c["id"] for c in chunks],
            embeddings=embeddings,
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks],
        )

        return len(chunks)

    except Exception as e:
      raise


# ---------------------------------------------------------------
# Search
# ---------------------------------------------------------------

def search(
    query_embedding: list[float],
    top_k: int = 5,
    doc_id: str = None
):
    """
    Performs semantic similarity search.

    Args:
        query_embedding:
            Query embedding vector.

        top_k:
            Number of chunks to retrieve.

        doc_id:
            Optional document identifier.

            If provided:
                Search only inside that document.

            If None:
                Search across every uploaded document.

    Returns:
        List of dictionaries containing:

            text
            doc_id
            document_name
            chunk_index
            similarity
    """

    collection = get_collection()

    total_chunks = collection.count()

    if total_chunks == 0:
        raise ValueError(
            "No documents have been uploaded yet."
        )

    actual_k = min(top_k, total_chunks)

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": actual_k,
        "include": [
            "documents",
            "metadatas",
            "distances",
        ],
    }

    if doc_id:
        query_params["where"] = {
            "doc_id": doc_id
        }

    results = collection.query(**query_params)

    chunks = []

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(
        docs,
        metas,
        distances,
    ):

        chunks.append(
            {
                "text": doc,
                "doc_id": meta.get("doc_id"),
                "document_name": meta.get(
                    "document_name"
                ),
                "page_number": meta.get(
                    "page_number",
                     1,
                ),
                "chunk_index": meta.get(
                    "chunk_index",
                    0,
                ),
                "similarity": round(
                    1 - dist,
                    3,
                ),
            }
        )

    # Remove duplicate chunks caused by overlapping text

    seen = set()
    unique = []

    for chunk in chunks:

        key = chunk["text"][:80]

        if key not in seen:
            seen.add(key)
            unique.append(chunk)

    return unique[:top_k]


# ---------------------------------------------------------------
# Document Management
# ---------------------------------------------------------------

def get_all_documents():
    """
    Returns all uploaded documents.

    Returns:
        List containing:

            doc_id
            document_name
            chunks_count
            upload_time
    """

    collection = get_collection()

    if collection.count() == 0:
        return []

    all_data = collection.get(
        include=["metadatas"]
    )

    metadatas = all_data.get(
        "metadatas",
        [],
    )

    document_map = {}

    for meta in metadatas:

        doc_id = meta.get("doc_id")

        if not doc_id:
            continue

        if doc_id not in document_map:

            document_map[doc_id] = {
                "doc_id": doc_id,
                "document_name": meta.get(
                    "document_name",
                    "Unknown",
                ),
                "chunks_count": 0,
                "upload_time": meta.get(
                    "upload_time",
                    "",
                ),
            }

        document_map[doc_id]["chunks_count"] += 1

    documents = list(document_map.values())

    documents.sort(
        key=lambda x: x["upload_time"],
        reverse=True,
    )

    return documents


def get_document_chunks_count(
    doc_id: str,
):
    """
    Returns the number of chunks
    stored for a document.
    """

    collection = get_collection()

    result = collection.get(
        where={"doc_id": doc_id},
        include=["metadatas"],
    )

    return len(
        result.get("metadatas", [])
    )


def document_exists(
    doc_id: str,
):
    """
    Checks whether a document
    already exists in ChromaDB.
    """

    return (
        get_document_chunks_count(doc_id)
        > 0
    )


def delete_document(
    doc_id: str,
):
    """
    Deletes all chunks belonging
    to a specific document.

    Returns:
        Number of deleted chunks.
    """

    collection = get_collection()

    result = collection.get(
        where={"doc_id": doc_id},
        include=["metadatas"],
    )

    ids_to_delete = result.get(
        "ids",
        [],
    )

    if not ids_to_delete:
        raise ValueError(
            f"Document '{doc_id}' not found."
        )

    collection.delete(
        ids=ids_to_delete
    )

    return len(ids_to_delete)


def get_total_chunks():
    """
    Returns the total number
    of indexed chunks.
    """

    return get_collection().count()