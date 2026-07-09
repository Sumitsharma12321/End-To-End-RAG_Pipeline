import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","backend")))

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_text():
    return """
    Machine learning is a subset of artificial intelligence.
    It allows systems to learn from data and improve over time.
    Deep learning uses neural networks with many layers.
    Natural language processing helps computers understand human language.
    RAG stands for Retrieval Augmented Generation.
    Vector databases store embeddings for semantic search.
    ChromaDB is a popular open source vector database.
    FastAPI is a modern Python web framework for building APIs.
    """ * 10  # repeat to have enough content for chunking

@pytest.fixture
def sample_pdf_path(tmp_path):
    # Create a simple text file to simulate upload
    f = tmp_path / "sample.txt"
    f.write_text("""
    This is a test document about artificial intelligence.
    Machine learning models can process large amounts of data.
    The RAG pipeline retrieves relevant chunks before generating answers.
    Vector embeddings capture semantic meaning of text.
    ChromaDB stores and retrieves vector embeddings efficiently.
    """ * 5)
    return str(f)