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

# Create FastAPI application
app = FastAPI(
    title="WhatNow AI API",
    description="AI-powered activity recommendation system with semantic embeddings",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    init_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)