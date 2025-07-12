# app/services/rag_service.py

import os
import pandas as pd
import json
from PyPDF2 import PdfReader
from typing import List, Optional

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

def search_vector_store(query: str, index_name: Optional[str] = None, top_k: int = 3) -> str:
    """
    Search the vector store for relevant documents
    """
    try:
        embeddings = OpenAIEmbeddings()
        
        if index_name:
            # Search specific index
            index_path = f"{VECTOR_DIR}/{index_name}"
            if os.path.exists(index_path):
                db = FAISS.load_local(index_path, embeddings)
            else:
                return "No documents found for the specified index."
        else:
            # Search all available indices
            available_indices = []
            for item in os.listdir(VECTOR_DIR):
                if os.path.isdir(os.path.join(VECTOR_DIR, item)):
                    available_indices.append(item)
            
            if not available_indices:
                return "No documents have been uploaded yet."
            
            # Use the first available index (you could implement more sophisticated selection)
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
            import shutil
            shutil.rmtree(index_path)
            return True
        return False
    except Exception:
        return False
