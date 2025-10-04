"""
Pydantic schemas for WhatNow API
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ActivityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    energy_physical: float = Field(..., ge=0, le=10)
    energy_mental: float = Field(..., ge=0, le=10)
    social_level: float = Field(..., ge=0, le=10)
    duration_min: int = Field(..., gt=0)
    duration_max: int = Field(..., ge=0)
    indoor: bool
    outdoor: bool
    weather_best: List[str] = Field(default_factory=list)
    weather_avoid: List[str] = Field(default_factory=list)
    temperature_min: float = Field(default=-10)
    temperature_max: float = Field(default=40)
    time_of_day: List[str] = Field(default_factory=list)
    cost: Optional[str] = Field(None, regex="^(free|low|medium|high)$")
    category: Optional[str] = Field(None, regex="^(physical|creative|social|relaxing|productive|entertainment|learning|other)$")
    tags: List[str] = Field(default_factory=list)

class ActivityCreate(ActivityBase):
    pass

class ActivityResponse(ActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
