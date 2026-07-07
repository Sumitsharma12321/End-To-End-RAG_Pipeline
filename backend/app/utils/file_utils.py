import os, uuid
from fastapi import UploadFile
from ..config import settings

ALLOWED_TYPES = ["application/pdf",
                 "text/plain",
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                 ]

def save_upload(file: UploadFile) -> tuple[str, str]:
    """Save uploaded file, return (doc_id, file_path)"""
    if file.content_type not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type: {file.content_type}")

    
    os.makedirs(settings.upload_dir, exist_ok=True)
    doc_id = str(uuid.uuid4())
    _, ext = os.path.splitext(file.filename)
    file_path = os.path.join(settings.upload_dir, f"{doc_id}{ext}")


    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    return doc_id, file_path