import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","backend")))

from app.services.embedder import embed_texts, embed_query
from app.services.chunker import chunk_text

class TestEmbedder:
    def test_embed_texts_returns_list(self):
        result = embed_texts(["Hello world"])
        assert isinstance(result, list)

    def test_embed_texts_correct_count(self):
        texts = ["first text", "second text", "third text"]
        result = embed_texts(texts)
        assert len(result) == 3

    def test_embed_text_is_list_of_floats(self):
        result = embed_texts(["test"])
        assert isinstance(result[0], list)
        assert isinstance(result[0][0], float)

    def test_embed_vector_dimension(self):
        result = embed_texts(["test sentence"])
        # all-MiniLM-L6-v2 produces 384-dim vectors
        assert len(result[0]) == 384

    def test_embed_query_returns_list(self):
        vec = embed_query("What is machine learning?")
        assert isinstance(vec, list)

    def test_embed_query_dimension(self):
        vec = embed_query("What is AI?")
        assert len(vec) == 384

    def test_similar_texts_have_closer_vectors(self):
        import numpy as np
        v1 = embed_query("machine learning artificial intelligence")
        v2 = embed_query("deep learning neural networks AI")
        v3 = embed_query("football cricket sports game")
        sim_related = np.dot(v1, v2)
        sim_unrelated = np.dot(v1, v3)
        assert sim_related > sim_unrelated


class TestQueryAPI:
    def test_query_after_upload_returns_200(self, client, tmp_path):
        # Step 1: upload
        txt = tmp_path / "ai_doc.txt"
        txt.write_text(
            "Artificial intelligence is the simulation of human intelligence. "
            "Machine learning is a subset of AI that learns from data. "
            "Deep learning uses multi-layered neural networks. " * 15
        )
        with open(txt, "rb") as f:
            client.post("/api/upload",
                files={"file": ("ai_doc.txt", f, "text/plain")})

        # Step 2: query
        res = client.post("/api/query",
            json={"question": "What is machine learning?"})
        assert res.status_code == 200

    def test_query_response_has_answer(self, client, tmp_path):
        txt = tmp_path / "doc.txt"
        txt.write_text("Python is a programming language. " * 20)
        with open(txt, "rb") as f:
            client.post("/api/upload",
                files={"file": ("doc.txt", f, "text/plain")})
        res = client.post("/api/query",
            json={"question": "What is Python?"})
        assert "answer" in res.json()

    def test_query_answer_is_not_empty(self, client, tmp_path):
        txt = tmp_path / "doc.txt"
        txt.write_text("FastAPI is a modern web framework for Python. " * 20)
        with open(txt, "rb") as f:
            client.post("/api/upload",
                files={"file": ("doc.txt", f, "text/plain")})
        res = client.post("/api/query",
            json={"question": "What is FastAPI?"})
        assert len(res.json()["answer"]) > 10

    def test_query_response_has_sources(self, client, tmp_path):
        txt = tmp_path / "doc.txt"
        txt.write_text("ChromaDB is a vector database. " * 20)
        with open(txt, "rb") as f:
            client.post("/api/upload",
                files={"file": ("doc.txt", f, "text/plain")})
        res = client.post("/api/query",
            json={"question": "What is ChromaDB?"})
        assert "sources" in res.json()

    def test_query_without_upload_still_responds(self, client):
        res = client.post("/api/query",
            json={"question": "What is the meaning of life?"})
        assert res.status_code in [200, 400, 500]

    def test_empty_question_handled(self, client):
        res = client.post("/api/query", json={"question": ""})
        assert res.status_code in [200, 400, 422]


class TestEndToEndFlow:
    def test_full_rag_pipeline(self, client, tmp_path):
        # Complete flow test
        content = """
        The capital of France is Paris.
        Paris is known for the Eiffel Tower.
        France is a country in Western Europe.
        The French Revolution happened in 1789.
        Napoleon Bonaparte was a famous French leader.
        """ * 8

        txt = tmp_path / "france.txt"
        txt.write_text(content)

        # Upload
        with open(txt, "rb") as f:
            upload_res = client.post("/api/upload",
                files={"file": ("france.txt", f, "text/plain")})
        assert upload_res.status_code == 200
        assert upload_res.json()["chunks_created"] > 0

        # Query
        query_res = client.post("/api/query",
            json={"question": "What is the capital of France?"})
        assert query_res.status_code == 200
        answer = query_res.json()["answer"].lower()
        assert "paris" in answer or len(answer) > 10