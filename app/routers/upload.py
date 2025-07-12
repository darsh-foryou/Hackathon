# app/routers/upload.py

from fastapi import APIRouter, UploadFile, File, Form
from app.models.upload import FileType
from app.services.rag_service import extract_text, create_vector_store
import shutil
import uuid

router = APIRouter()

@router.post("/upload_docs")
async def upload_document(file: UploadFile = File(...), file_type: FileType = Form(...)):
    try:
        file_id = str(uuid.uuid4())
        temp_path = f"temp_{file_id}_{file.filename}"
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = extract_text(temp_path, file_type.value)
        create_vector_store(text, index_name=file_id)
        return {"status": "success", "file_id": file_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}
