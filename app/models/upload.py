# app/models/upload.py
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

class FileType(str, Enum):
    pdf = "pdf"
    txt = "txt"
    csv = "csv"
    json = "json"

class FileUploadRequest(BaseModel):
    user_id: str
    file_type: FileType

class FileMetadata(BaseModel):
    file_id: str
    user_id: str
    filename: str
    file_type: FileType
    file_size: int
    vector_store_path: str
    uploaded_at: datetime
    is_active: bool = True
