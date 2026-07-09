import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import chromadb
from app.config import settings
from app.services.embedder import embed_query


def check_index(show_samples: int = 3, test_query: str = None):
    """
    Display the current status of the ChromaDB index.

    Args:
        show_samples: Number of sample chunks to display.
        test_query: Optional query to test document retrieval.
    """

    client = chromadb.PersistentClient(path=settings.chroma_db_path)

    print("\nChromaDB Index Status")
    print("─────────────────────────────────────")

    # Check whether the collection exists
    try:
        collection = client.get_collection("documents")

    except Exception:
        print("No collection found.")
        print("No documents have been indexed yet.")
        print("\nUse ingest.py to add documents to the vector database.")
        return

    # Display collection statistics
    count = collection.count()

    print(f"Collection Name : documents")
    print(f"Database Path   : {settings.chroma_db_path}")
    print(f"Total Chunks    : {count}")

    if count == 0:
        print("\nThe collection is empty.")
        return

    # Display sample chunks
    print(f"\nSample Chunks (First {show_samples})")
    print("─────────────────────────────────────")

    samples = collection.peek(limit=show_samples)

    for i, (chunk_id, document, metadata) in enumerate(
        zip(
            samples["ids"],
            samples["documents"],
            samples["metadatas"]
        ),
        start=1,
    ):

        print(f"\nChunk {i}")
        print(f"  Chunk ID    : {chunk_id}")
        print(f"  Document ID : {metadata.get('doc_id', 'N/A')}")
        print(f"  Chunk Index : {metadata.get('chunk_index', 'N/A')}")
        print(f"  Preview     : {document[:120]}...")

    # Count unique documents
    all_metadata = collection.get(include=["metadatas"])["metadatas"]

    unique_documents = {
        metadata.get("doc_id", "")
        for metadata in all_metadata
    }

    print(f"\nUnique Documents        : {len(unique_documents)}")
    print(
        f"Average Chunks/Document : "
        f"{count // max(len(unique_documents), 1)}"
    )

    # Run an optional retrieval query
    if test_query:

        print(f"\nTest Query: \"{test_query}\"")
        print("─────────────────────────────────────")

        try:
            query_vector = embed_query(test_query)

            results = collection.query(
                query_embeddings=[query_vector],
                n_results=min(3, count),
            )

            for i, document in enumerate(results["documents"][0], start=1):
                print(f"\nTop Result {i}")
                print(f"  {document[:150]}...")

        except Exception as e:
            print(f"Query execution failed: {e}")

    print("\n─────────────────────────────────────")
    print("Status: The index is ready for querying.")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Check the status of the ChromaDB index."
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=3,
        help="Number of sample chunks to display (default: 3).",
    )

    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Run a test query and display the top matching results.",
    )

    args = parser.parse_args()

    check_index(
        show_samples=args.samples,
        test_query=args.query,
    )