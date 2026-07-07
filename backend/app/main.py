from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import upload, query

app = FastAPI(
    title="Smart Document Insights API",
    version="1.0.0",
    description="RAG-based Document Question Answering System"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # only URL in the production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(
    upload.router,
    prefix="/api",
    tags=["Upload"]
)

app.include_router(
    query.router,
    prefix="/api",
    tags=["Query"]
)

# Home Route
@app.get("/")
def root():
    return {
        "message": "Smart Document Insights API is running",
        "docs": "/docs",
        "health": "/health"
    }

# Health Check
@app.get("/health")
def health():
    return {
        "status": "ok"
    }
