from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config import settings


def chunk_text(text: str, doc_id: str) -> list[dict]:
    """Split text into chunks with metadata."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " "],
    )

    chunks = splitter.split_text(text)

    return [
        {
            "id": f"{doc_id}_chunk_{i}",
            "text": chunk,
            "metadata": {
                "doc_id": doc_id,
                "chunk_index": i,
            },
        }
        for i, chunk in enumerate(chunks)
    ]