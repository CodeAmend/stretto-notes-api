# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, sessions, practice_items, journeys
from app.config import settings

app = FastAPI(
    title="StrettoNotes API",
    version="0.1.0",
    description="Voice-first practice journal for musicians"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(practice_items.router, prefix="/practice-items", tags=["Practice Items"])
app.include_router(journeys.router, prefix="/journeys", tags=["Journeys"])

@app.get("/")
async def root():
    return {
        "message": "StrettoNotes API",
        "version": "0.1.0",
        "docs": "/docs"
    }
