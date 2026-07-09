import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","backend")))

from app.services.chunker import chunk_text
from app.services.document_processor import extract_text

class TestChunker:
    def test_chunking_returns_list(self, sample_text):
        chunks = chunk_text(sample_text, "doc-001")
        assert isinstance(chunks, list)

    def test_chunking_creates_multiple_chunks(self, sample_text):
        chunks = chunk_text(sample_text, "doc-001")
        assert len(chunks) > 1

    def test_each_chunk_has_required_keys(self, sample_text):
        chunks = chunk_text(sample_text, "doc-001")
        for chunk in chunks:
            assert "id" in chunk
            assert "text" in chunk
            assert "metadata" in chunk

    def test_chunk_id_contains_doc_id(self, sample_text):
        chunks = chunk_text(sample_text, "doc-xyz")
        for chunk in chunks:
            assert "doc-xyz" in chunk["id"]

    def test_chunk_text_not_empty(self, sample_text):
        chunks = chunk_text(sample_text, "doc-001")
        for chunk in chunks:
            assert len(chunk["text"].strip()) > 0

    def test_chunk_metadata_has_doc_id(self, sample_text):
        chunks = chunk_text(sample_text, "doc-001")
        for chunk in chunks:
            assert chunk["metadata"]["doc_id"] == "doc-001"

    def test_chunk_index_is_sequential(self, sample_text):
        chunks = chunk_text(sample_text, "doc-001")
        for i, chunk in enumerate(chunks):
            assert chunk["metadata"]["chunk_index"] == i


class TestDocumentProcessor:
    def test_extract_text_from_txt(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Hello world. This is a test document.")
        text = extract_text(str(txt_file))
        assert "Hello world" in text

    def test_extracted_text_is_string(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Test content here.")
        text = extract_text(str(txt_file))
        assert isinstance(text, str)

    def test_extracted_text_not_empty(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Some content to test.")
        text = extract_text(str(txt_file))
        assert len(text.strip()) > 0

    def test_unsupported_format_raises_error(self, tmp_path):
        bad_file = tmp_path / "test.xyz"
        bad_file.write_text("content")
        with pytest.raises(ValueError):
            extract_text(str(bad_file))


class TestUploadAPI:
    def test_upload_txt_returns_200(self, client, tmp_path):
        txt = tmp_path / "doc.txt"
        txt.write_text("Machine learning is a field of AI. " * 20)
        with open(txt, "rb") as f:
            res = client.post("/api/upload",
                files={"file": ("doc.txt", f, "text/plain")})
        assert res.status_code == 200

    def test_upload_response_has_doc_id(self, client, tmp_path):
        txt = tmp_path / "doc.txt"
        txt.write_text("Test document content. " * 20)
        with open(txt, "rb") as f:
            res = client.post("/api/upload",
                files={"file": ("doc.txt", f, "text/plain")})
        assert "doc_id" in res.json()

    def test_upload_response_has_chunks_created(self, client, tmp_path):
        txt = tmp_path / "doc.txt"
        txt.write_text("Test content for chunking. " * 20)
        with open(txt, "rb") as f:
            res = client.post("/api/upload",
                files={"file": ("doc.txt", f, "text/plain")})
        assert "chunks_created" in res.json()
        assert res.json()["chunks_created"] > 0

    def test_upload_response_has_filename(self, client, tmp_path):
        txt = tmp_path / "myfile.txt"
        txt.write_text("Document text here. " * 20)
        with open(txt, "rb") as f:
            res = client.post("/api/upload",
                files={"file": ("myfile.txt", f, "text/plain")})
        assert res.json()["filename"] == "myfile.txt"

    def test_upload_wrong_format_returns_error(self, client, tmp_path):
        bad = tmp_path / "test.exe"
        bad.write_text("binary content")
        with open(bad, "rb") as f:
            res = client.post("/api/upload",
                files={"file": ("test.exe", f, "application/exe")})
        assert res.status_code in [400, 422, 500]