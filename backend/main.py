#!/usr/bin/env python3
"""
WhatNow AI API - Main application file.

A clean, organized FastAPI application for AI-powered activity recommendations.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints.basic import router as basic_router
from endpoints.activities import router as activities_router
from utils.database import init_database
from contextlib import asynccontextmanager

# Initialize database on startup using lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on application startup."""
    try:
        init_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Don't fail the startup if database is not available
        pass
    yield
    # Cleanup code here if needed

# Create FastAPI application
app = FastAPI(
    title="WhatNow AI API",
    description="AI-powered activity recommendation system with semantic embeddings",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(basic_router)
app.include_router(activities_router)

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)