#!/usr/bin/env python3
"""
WhatNow FastAPI Application - Minimal Version for Railway
"""

from fastapi import FastAPI

# Create FastAPI app
app = FastAPI(
    title="WhatNow API",
    description="AI-powered activity recommendation system",
    version="1.0.0"
)

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "WhatNow API", "status": "running"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "whatnow"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)