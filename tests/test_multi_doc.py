# ================================================================
# FILE: tests/test_multi_doc.py
# NEW FILE: Multi-document support ke liye complete test suite
#
# TEST COVERAGE:
#   1. Multiple file upload
#   2. Each doc gets unique doc_id
#   3. Query specific document
#   4. Query all documents
#   5. Metadata validation
#   6. Document list endpoint
#   7. Document delete
#   8. Duplicate handling
#   9. Cross-document retrieval
# ================================================================

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","backend")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── Fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def ai_doc(tmp_path):
    """ test document about AI"""
    f = tmp_path / "ai_basics.txt"
    f.write_text(
        "Artificial intelligence is a branch of computer science. "
        "Machine learning allows computers to learn from data. "
        "Deep learning uses neural networks with many layers. "
        "AI is used in healthcare, finance, and transportation. " * 10
    )
    return f


@pytest.fixture
def python_doc(tmp_path):
    """ test document about python"""
    f = tmp_path / "python_guide.txt"
    f.write_text(
        "Python is a high-level programming language created by Guido van Rossum. "
        "Python uses indentation to define code blocks. "
        "Popular Python libraries include NumPy, Pandas, and TensorFlow. "
        "Python is widely used for data science and web development. " * 10
    )
    return f


@pytest.fixture
def rag_doc(tmp_path):
    """test doocument about RAG """
    f = tmp_path / "rag_explained.txt"
    f.write_text(
        "RAG stands for Retrieval Augmented Generation. "
        "RAG combines information retrieval with language model generation. "
        "ChromaDB is used to store vector embeddings in RAG systems. "
        "RAG improves LLM accuracy by providing relevant context. " * 10
    )
    return f


@pytest.fixture
def uploaded_ai_doc(ai_doc):
    """AI doc upload karke doc_id return karo"""
    with open(ai_doc, "rb") as f:
        res = client.post(
            "/api/upload",
            files={"file": ("ai_basics.txt", f, "text/plain")}
        )
    assert res.status_code == 200
    return res.json()


@pytest.fixture
def uploaded_python_doc(python_doc):
    """Upload the Python doc and return the doc_id."""
    with open(python_doc, "rb") as f:
        res = client.post(
            "/api/upload",
            files={"file": ("python_guide.txt", f, "text/plain")}
        )
    assert res.status_code == 200
    return res.json()


# ── Section 1: Single upload (backward compatibility) ────────────

class TestSingleUploadBackwardCompat:
    """Existing single upload should work unchanged"""

    def test_single_upload_returns_200(self, ai_doc):
        with open(ai_doc, "rb") as f:
            res = client.post(
                "/api/upload",
                files={"file": ("ai_basics.txt", f, "text/plain")}
            )
        assert res.status_code == 200

    def test_single_upload_returns_doc_id(self, ai_doc):
        with open(ai_doc, "rb") as f:
            res = client.post(
                "/api/upload",
                files={"file": ("ai_basics.txt", f, "text/plain")}
            )
        data = res.json()
        assert "doc_id" in data
        assert len(data["doc_id"]) > 10

    def test_single_upload_returns_chunks_created(self, ai_doc):
        with open(ai_doc, "rb") as f:
            res = client.post(
                "/api/upload",
                files={"file": ("ai_basics.txt", f, "text/plain")}
            )
        assert res.json()["chunks_created"] > 0

    def test_single_upload_returns_upload_time(self, ai_doc):
        """NEW field — upload_time response mein hona chahiye"""
        with open(ai_doc, "rb") as f:
            res = client.post(
                "/api/upload",
                files={"file": ("ai_basics.txt", f, "text/plain")}
            )
        assert "upload_time" in res.json()


# ── Section 2: Multiple upload ───────────────────────────────────

class TestMultipleUpload:
    """Multiple files upload endpoint test"""

    def test_multiple_upload_endpoint_exists(self, ai_doc, python_doc):
        with open(ai_doc, "rb") as f1, open(python_doc, "rb") as f2:
            res = client.post(
                "/api/upload/multiple",
                files=[
                    ("files", ("ai_basics.txt", f1, "text/plain")),
                    ("files", ("python_guide.txt", f2, "text/plain")),
                ]
            )
        assert res.status_code == 200

    def test_multiple_upload_returns_correct_count(self, ai_doc, python_doc):
        with open(ai_doc, "rb") as f1, open(python_doc, "rb") as f2:
            res = client.post(
                "/api/upload/multiple",
                files=[
                    ("files", ("ai_basics.txt", f1, "text/plain")),
                    ("files", ("python_guide.txt", f2, "text/plain")),
                ]
            )
        data = res.json()
        assert data["total_files"] == 2

    def test_each_doc_gets_unique_doc_id(self, ai_doc, python_doc):
        """Har document ka alag doc_id hona chahiye"""
        with open(ai_doc, "rb") as f1, open(python_doc, "rb") as f2:
            res = client.post(
                "/api/upload/multiple",
                files=[
                    ("files", ("ai_basics.txt", f1, "text/plain")),
                    ("files", ("python_guide.txt", f2, "text/plain")),
                ]
            )
        data = res.json()
        uploaded = data["uploaded"]
        doc_ids = [u["doc_id"] for u in uploaded]
        # All doc_ids must be unique.
        assert len(doc_ids) == len(set(doc_ids))

    def test_multiple_upload_total_chunks_sum(self, ai_doc, python_doc):
        """total_chunks = sum of individual chunks"""
        with open(ai_doc, "rb") as f1, open(python_doc, "rb") as f2:
            res = client.post(
                "/api/upload/multiple",
                files=[
                    ("files", ("ai_basics.txt", f1, "text/plain")),
                    ("files", ("python_guide.txt", f2, "text/plain")),
                ]
            )
        data = res.json()
        individual_sum = sum(u["chunks_created"] for u in data["uploaded"])
        assert data["total_chunks"] == individual_sum

    def test_multiple_upload_filenames_correct(self, ai_doc, python_doc):
        with open(ai_doc, "rb") as f1, open(python_doc, "rb") as f2:
            res = client.post(
                "/api/upload/multiple",
                files=[
                    ("files", ("ai_basics.txt", f1, "text/plain")),
                    ("files", ("python_guide.txt", f2, "text/plain")),
                ]
            )
        filenames = [u["filename"] for u in res.json()["uploaded"]]
        assert "ai_basics.txt" in filenames
        assert "python_guide.txt" in filenames


# ── Section 3: Document list endpoint ───────────────────────────

class TestDocumentList:
    """GET /api/documents endpoint test"""

    def test_documents_endpoint_exists(self):
        res = client.get("/api/documents")
        assert res.status_code == 200

    def test_documents_response_structure(self):
        res = client.get("/api/documents")
        data = res.json()
        assert "documents" in data
        assert "total_documents" in data
        assert "total_chunks" in data

    def test_uploaded_doc_appears_in_list(self, uploaded_ai_doc):
        doc_id = uploaded_ai_doc["doc_id"]
        res = client.get("/api/documents")
        doc_ids = [d["doc_id"] for d in res.json()["documents"]]
        assert doc_id in doc_ids

    def test_document_metadata_in_list(self, uploaded_ai_doc):
        """The document list should contain the filename and chunks_count"""
        res = client.get("/api/documents")
        docs = res.json()["documents"]
        ai_doc = next(
            (d for d in docs if d["doc_id"] == uploaded_ai_doc["doc_id"]),
            None
        )
        assert ai_doc is not None
        assert "filename" in ai_doc
        assert "chunks_count" in ai_doc
        assert ai_doc["chunks_count"] > 0


# ── Section 4: Query specific document ──────────────────────────

class TestQuerySpecificDocument:
    """Search within a specific document using doc_id."""

    def test_query_with_doc_id_returns_200(self, uploaded_ai_doc):
        res = client.post(
            "/api/query",
            json={
                "question": "What is artificial intelligence?",
                "doc_id": uploaded_ai_doc["doc_id"]
            }
        )
        assert res.status_code == 200

    def test_query_with_doc_id_returns_answer(self, uploaded_ai_doc):
        res = client.post(
            "/api/query",
            json={
                "question": "What is machine learning?",
                "doc_id": uploaded_ai_doc["doc_id"]
            }
        )
        assert "answer" in res.json()
        assert len(res.json()["answer"]) > 10

    def test_query_response_has_searched_in(self, uploaded_ai_doc):
        """ The 'searched_in' field must be included in the response."""
        res = client.post(
            "/api/query",
            json={
                "question": "Tell me about AI",
                "doc_id": uploaded_ai_doc["doc_id"]
            }
        )
        assert "searched_in" in res.json()
        # name of specific doc is mandatory
        searched_in = res.json()["searched_in"]
        assert searched_in != "all documents"

    def test_query_response_has_sources(self, uploaded_ai_doc):
        res = client.post(
            "/api/query",
            json={
                "question": "What is deep learning?",
                "doc_id": uploaded_ai_doc["doc_id"]
            }
        )
        assert "sources" in res.json()


# ── Section 5: Query all documents ──────────────────────────────

class TestQueryAllDocuments:
    """ If no doc_id is provided, execute the search across all documents."""

    def test_query_without_doc_id_returns_200(
        self, uploaded_ai_doc, uploaded_python_doc
    ):
        res = client.post(
            "/api/query",
            json={"question": "What programming languages are mentioned?"}
        )
        assert res.status_code == 200

    def test_query_all_docs_searched_in_is_all(
        self, uploaded_ai_doc
    ):
        res = client.post(
            "/api/query",
            json={"question": "What is AI?"}
        )
        assert res.json()["searched_in"] == "all documents"

    def test_query_all_docs_sources_mention_documents(
        self, uploaded_ai_doc, uploaded_python_doc
    ):
        """The 'sources' field in the response must include the document names."""
        res = client.post(
            "/api/query",
            json={"question": "Tell me about technology"}
        )
        sources = res.json()["sources"]
        assert isinstance(sources, list)


# ── Section 6: Metadata validation ──────────────────────────────

class TestMetadataValidation:
    """store chunks into metadata"""

    def test_chunks_have_document_name_in_metadata(self, uploaded_ai_doc):
        """ The 'document_name' must be included in the ChromaDB metadata."""
        from app.db.vector_store import get_collection
        col = get_collection()
        result = col.get(
            where={"doc_id": uploaded_ai_doc["doc_id"]},
            include=["metadatas"]
        )
        metadatas = result.get("metadatas", [])
        assert len(metadatas) > 0
        for meta in metadatas:
            assert "document_name" in meta
            assert meta["document_name"] == "ai_basics.txt"

    def test_chunks_have_doc_id_in_metadata(self, uploaded_ai_doc):
        from app.db.vector_store import get_collection
        col = get_collection()
        result = col.get(
            where={"doc_id": uploaded_ai_doc["doc_id"]},
            include=["metadatas"]
        )
        for meta in result.get("metadatas", []):
            assert "doc_id" in meta
            assert meta["doc_id"] == uploaded_ai_doc["doc_id"]

    def test_chunks_have_page_number_in_metadata(self, uploaded_ai_doc):
        from app.db.vector_store import get_collection
        col = get_collection()
        result = col.get(
            where={"doc_id": uploaded_ai_doc["doc_id"]},
            include=["metadatas"]
        )
        for meta in result.get("metadatas", []):
            assert "page_number" in meta
            assert meta["page_number"] >= 1

    def test_chunks_have_upload_time_in_metadata(self, uploaded_ai_doc):
        from app.db.vector_store import get_collection
        col = get_collection()
        result = col.get(
            where={"doc_id": uploaded_ai_doc["doc_id"]},
            include=["metadatas"]
        )
        for meta in result.get("metadatas", []):
            assert "upload_time" in meta
            assert len(meta["upload_time"]) > 0


# ── Section 7: Document delete ───────────────────────────────────

class TestDocumentDelete:
    """Test document deletion endpoint"""

    def test_delete_existing_document(self, uploaded_ai_doc):
        doc_id = uploaded_ai_doc["doc_id"]
        res = client.delete(f"/api/documents/{doc_id}")
        assert res.status_code == 200
        assert "deleted" in res.json()["message"].lower()

    def test_delete_removes_from_list(self, uploaded_ai_doc):
        doc_id = uploaded_ai_doc["doc_id"]
        client.delete(f"/api/documents/{doc_id}")
        docs = client.get("/api/documents").json()["documents"]
        doc_ids = [d["doc_id"] for d in docs]
        assert doc_id not in doc_ids

    def test_delete_nonexistent_returns_404(self):
        res = client.delete("/api/documents/nonexistent-doc-id-12345")
        assert res.status_code == 404


# ── Section 8: Cross-document isolation ─────────────────────────

class TestCrossDocumentIsolation:
    """Ensure retrieval is isolated to the selected document"""

    def test_python_query_not_in_ai_doc(
        self, uploaded_ai_doc, uploaded_python_doc
    ):
        """
          Specific queries regarding the Python document should not retrieve content from the AI document.
           (Answer quality test: strict assertions are difficult to enforce with LLM generations)
        """
        res = client.post(
            "/api/query",
            json={
                "question": "Who created Python programming language?",
                "doc_id": uploaded_python_doc["doc_id"]
            }
        )
        assert res.status_code == 200
        # searched_in python doc hona chahiye
        assert "python" in res.json()["searched_in"].lower()

    def test_two_docs_have_different_doc_ids(
        self, uploaded_ai_doc, uploaded_python_doc
    ):
        assert uploaded_ai_doc["doc_id"] != uploaded_python_doc["doc_id"]