# app/models/upload.py
from pydantic import BaseModel
from enum import Enum

class FileType(str, Enum):
    pdf = "pdf"
    txt = "txt"
    csv = "csv"
    json = "json"
