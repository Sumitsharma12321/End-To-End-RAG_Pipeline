import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import chromadb
from app.config import settings


def clear_index(force: bool = False) -> bool:
    """
    Delete the ChromaDB collection.

    Args:
        force: Skip confirmation prompt.

    Returns:
        True if the collection was deleted successfully,
        otherwise False.
    """

    client = chromadb.PersistentClient(path=settings.chroma_db_path)

    # Check whether the collection exists
    try:
        collection = client.get_collection("documents")
        count = collection.count()
        print(f"\nFound {count} chunks in the ChromaDB collection.")

    except Exception:
        print("\nThe ChromaDB collection is already empty.")
        return False

    # Ask for confirmation
    if not force:
        print("\nWarning: This action will permanently delete all stored documents.")

        confirm = input("Do you want to continue? (yes/no): ").strip().lower()

        if confirm != "yes":
            print("Operation cancelled.")
            return False

    # Delete collection
    try:
        client.delete_collection("documents")

        print("\nCollection deleted successfully.")
        print("The vector database has been cleared.")

        return True

    except Exception as e:
        print(f"\nError while deleting the collection: {e}")
        return False


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Clear the ChromaDB vector index."
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete the collection without confirmation."
    )

    args = parser.parse_args()

    clear_index(force=args.force)