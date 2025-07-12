# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, upload, crm

app = FastAPI(
    title="Multi-Agentic Conversational AI System",
    description="A comprehensive AI system with RAG, CRM integration, and conversational capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(crm.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Multi-Agentic Conversational AI System",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/v1/chat",
            "upload": "/api/v1/upload_docs",
            "crm": "/api/v1/crm"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Multi-Agentic AI System"}
