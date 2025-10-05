"""
Pydantic schemas for WhatNow AI API
"""

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class ActivityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    embedding: str = Field(..., description="JSON string of embedding vector")

class ActivityResponse(BaseModel):
    id: int
    name: str
    embedding: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
