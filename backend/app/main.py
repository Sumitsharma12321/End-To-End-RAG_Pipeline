from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import upload, query

app = FastAPI(
    title="Smart Document Insights API",
    version="2.0.0",
    description="Multi-document RAG Pipeline using FastAPI, ChromaDB and Groq"
)

# -------------------------------------------------------
# CORS
# -------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# API Routers
# -------------------------------------------------------

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

# -------------------------------------------------------
# Root
# -------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Smart Document Insights API is running",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# -------------------------------------------------------
# Health Check
# -------------------------------------------------------

@app.get("/health")
def health():
    try:
        from .db.vector_store import get_collection, get_total_chunks

        get_collection()

        return {
            "status": "ok",
            "version": "2.0.0",
            "chromadb": "connected",
            "total_chunks": get_total_chunks()
        }

    except Exception as e:

        return {
            "status": "degraded",
            "error": str(e)
        }


# -------------------------------------------------------
# Startup
# -------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    try:
        from .db.vector_store import get_collection

        get_collection()

        print("ChromaDB connected successfully.")

    except Exception as e:

        print(f"ChromaDB connection failed: {e}")