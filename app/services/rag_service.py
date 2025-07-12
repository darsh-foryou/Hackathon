# app/services/rag_service.py

import os
import pandas as pd
import json
from PyPDF2 import PdfReader
from typing import List, Optional
import shutil

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
VECTOR_DIR = "app/vector_store"

def extract_text(file_path: str, file_type: str) -> str:
    if file_type == "pdf":
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file_type == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_type == "csv":
        df = pd.read_csv(file_path)
        return df.to_string()
    elif file_type == "json":
        with open(file_path, "r", encoding="utf-8") as f:
            return json.dumps(json.load(f), indent=2)
    else:
        raise ValueError("Unsupported file type")

def create_vector_store(text: str, index_name: str):
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([text])
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs, embeddings)
    
    os.makedirs(VECTOR_DIR, exist_ok=True)
    db.save_local(f"{VECTOR_DIR}/{index_name}")
    return True

def search_vector_store(query: str, user_id: str = None, top_k: int = 3) -> str:
    """
    Search the vector store for relevant documents
    If user_id is provided, search only user's documents
    """
    try:
        embeddings = OpenAIEmbeddings()
        
        if user_id:
            # Search user-specific documents
            from app.services.crm_service import crm_service
            user_files = crm_service.get_user_files(user_id)
            
            if not user_files:
                return "No documents found for this user."
            
            # Search across all user's documents
            all_relevant_content = []
            for file_info in user_files:
                vector_store_path = file_info["vector_store_path"]
                if os.path.exists(vector_store_path):
                    try:
                        db = FAISS.load_local(vector_store_path, embeddings)
                        docs = db.similarity_search(query, k=2)  # Get top 2 from each file
                        for doc in docs:
                            all_relevant_content.append(f"From {file_info['filename']}:\n{doc.page_content}")
                    except Exception as e:
                        print(f"Error searching file {file_info['filename']}: {e}")
                        continue
            
            if all_relevant_content:
                return "\n\n".join(all_relevant_content[:top_k * 2])  # Limit total results
            else:
                return "No relevant documents found in your uploaded files."
        else:
            # Search all available indices (legacy behavior)
            available_indices = []
            for item in os.listdir(VECTOR_DIR):
                if os.path.isdir(os.path.join(VECTOR_DIR, item)):
                    available_indices.append(item)
            
            if not available_indices:
                return "No documents have been uploaded yet."
            
            # Use the first available index
            index_path = f"{VECTOR_DIR}/{available_indices[0]}"
            db = FAISS.load_local(index_path, embeddings)
            
            # Search for relevant documents
            docs = db.similarity_search(query, k=top_k)
            
            # Combine relevant content
            relevant_content = []
            for i, doc in enumerate(docs, 1):
                relevant_content.append(f"Document {i}:\n{doc.page_content}\n")
            
            return "\n".join(relevant_content) if relevant_content else "No relevant documents found."
        
    except Exception as e:
        return f"Error searching vector store: {str(e)}"

def get_available_indices() -> List[str]:
    """
    Get list of available vector store indices
    """
    try:
        if not os.path.exists(VECTOR_DIR):
            return []
        
        indices = []
        for item in os.listdir(VECTOR_DIR):
            if os.path.isdir(os.path.join(VECTOR_DIR, item)):
                indices.append(item)
        
        return indices
    except Exception:
        return []

def delete_vector_store(index_name: str) -> bool:
    """
    Delete a vector store index
    """
    try:
        index_path = f"{VECTOR_DIR}/{index_name}"
        if os.path.exists(index_path):
            shutil.rmtree(index_path)
            return True
        return False
    except Exception:
        return False

def get_user_document_summary(user_id: str) -> dict:
    """
    Get a summary of user's uploaded documents
    """
    try:
        from app.services.crm_service import crm_service
        user_files = crm_service.get_user_files(user_id)
        
        summary = {
            "total_files": len(user_files),
            "file_types": {},
            "total_size": 0,
            "files": []
        }
        
        for file_info in user_files:
            file_type = file_info["file_type"]
            file_size = file_info["file_size"]
            
            summary["file_types"][file_type] = summary["file_types"].get(file_type, 0) + 1
            summary["total_size"] += file_size
            summary["files"].append({
                "filename": file_info["filename"],
                "file_type": file_type,
                "file_size": file_size,
                "uploaded_at": file_info["uploaded_at"].isoformat()
            })
        
        return summary
    except Exception as e:
        return {"error": str(e)}
