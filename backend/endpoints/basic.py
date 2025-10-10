#!/usr/bin/env python3
"""
Basic endpoints for the WhatNow AI system.
"""

from fastapi import APIRouter

router = APIRouter()

# Root endpoint moved to main.py to serve frontend

@router.get("/health")
def health_check():
    """Health check endpoint."""
    print("Health check endpoint called")  # Debug logging
    return {"status": "healthy", "service": "WhatNow AI API"}
