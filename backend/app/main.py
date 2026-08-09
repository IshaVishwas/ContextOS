from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.seed import seed_db
from app.api import conversations, messages, memories, chat, evaluation, auth
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run seeder on startup
    seed_db()
    yield

app = FastAPI(
    title="ContextOS API",
    description="AI infrastructure platform for contextual memory and operations.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [
    "http://localhost",
    "http://localhost:5173", # Vite default localhost
    "http://127.0.0.1",
    "http://127.0.0.1:5173", # Vite default 127.0.0.1
    FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to ContextOS API"}

# Add router inclusions here
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messages"])
app.include_router(memories.router, prefix="/api/v1/memories", tags=["Memories"])
app.include_router(chat.router, prefix="/api/v1/llm", tags=["LLM Chat"])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["evaluation"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
