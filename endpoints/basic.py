#!/usr/bin/env python3
"""
Basic endpoints for the WhatNow AI system.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "WhatNow AI API",
        "version": "2.0.0",
        "description": "AI-powered activity recommendation system",
        "endpoints": {
            "health": "/health",
            "activities": "/activities/*"
        }
    }

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "WhatNow AI API"}
