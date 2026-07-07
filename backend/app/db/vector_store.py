import chromadb
from ..config import settings

client = chromadb.PersistentClient(path=settings.chroma_db_path)


def get_collection(name: str = "documents"):
    return client.get_or_create_collection(name=name)


def store_chunks(chunks: list[dict], embeddings: list[list[float]]):
    collection = get_collection()

    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )


def search(query_embedding: list[float], top_k: int = None):
    collection = get_collection()

    top_k = min(top_k, collection.count())

    results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k
)
    return results["documents"][0]