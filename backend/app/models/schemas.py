from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    doc_id: str | None = None  # optional: filter by specific doc

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]  # page/chunk references

class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks_created: int
    message: str