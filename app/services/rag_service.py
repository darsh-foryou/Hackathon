# app/services/rag_service.py

import os
import pandas as pd
import json
from PyPDF2 import PdfReader

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
