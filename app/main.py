# app/main.py
from fastapi import FastAPI
from app.routers import chat, upload


app = FastAPI(
    title="Multi-Agentic Conversational AI System",
    version="1.0.0"
)

app.include_router(chat.router)
app.include_router(upload.router)
