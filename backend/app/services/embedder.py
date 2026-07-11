from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Convert text chunks into embeddings."""

    embeddings = model.encode(
        texts,
        batch_size=64,              # Added
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Convert user query into embedding."""

    embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embedding.tolist()