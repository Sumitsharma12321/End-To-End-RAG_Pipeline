from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str

    chroma_db_path: str = "./chroma_db"
    upload_dir: str = "./uploaded_docs"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5

    class Config:
        env_file = ".env"


settings = Settings()