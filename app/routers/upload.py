# app/routers/upload.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.upload import FileType
from app.services.rag_service import extract_text, create_vector_store
from app.services.crm_service import crm_service
import shutil
import uuid
import os

router = APIRouter()

@router.post("/upload_docs")
async def upload_document(
    file: UploadFile = File(...), 
    file_type: FileType = Form(...),
    user_id: str = Form(...)
):
    """
    Upload a document for a specific user and process it for RAG
    """
    try:
        # Validate user exists
        user = crm_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create temporary file path
        temp_path = f"temp_{file_id}_{file.filename}"
        
        # Save uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(temp_path)
        
        # Extract text from file
        text = extract_text(temp_path, file_type.value)
        
        # Create vector store with user-specific naming
        vector_store_name = f"{user_id}_{file_id}"
        create_vector_store(text, vector_store_name)
        
        # Save file metadata to MongoDB
        vector_store_path = f"app/vector_store/{vector_store_name}"
        success = crm_service.save_file_metadata(
            file_id=file_id,
            user_id=user_id,
            filename=file.filename,
            file_type=file_type.value,
            file_size=file_size,
            vector_store_path=vector_store_path
        )
        
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save file metadata")
        
        return {
            "status": "success", 
            "file_id": file_id,
            "filename": file.filename,
            "file_type": file_type.value,
            "file_size": file_size,
            "message": f"File '{file.filename}' uploaded and processed successfully for user {user_id}"
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{user_id}")
async def get_user_files(user_id: str):
    """
    Get all files uploaded by a specific user
    """
    try:
        # Validate user exists
        user = crm_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        files = crm_service.get_user_files(user_id)
        return {
            "user_id": user_id,
            "files": files,
            "total_files": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{file_id}")
async def delete_user_file(file_id: str, user_id: str):
    """
    Delete a file for a specific user
    """
    try:
        # Get file metadata
        file_info = crm_service.get_file_by_id(file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if user owns the file
        if file_info["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Soft delete from MongoDB
        success = crm_service.delete_file(file_id, user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete file")
        
        # Optionally delete vector store files (you might want to keep them for backup)
        # vector_store_path = file_info["vector_store_path"]
        # if os.path.exists(vector_store_path):
        #     shutil.rmtree(vector_store_path)
        
        return {
            "status": "success",
            "message": f"File '{file_info['filename']}' deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
