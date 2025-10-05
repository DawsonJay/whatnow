"""
SQLAlchemy models for WhatNow
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy import JSON
from sqlalchemy.sql import func
from database.connection import Base

class Activity(Base):
    __tablename__ = "activities"
    
    # Core fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Energy attributes (0-10 scale)
    energy_physical = Column(Float, nullable=False)
    energy_mental = Column(Float, nullable=False)
    social_level = Column(Float, nullable=False)
    
    # Duration (minutes)
    duration_min = Column(Integer, nullable=False)
    duration_max = Column(Integer, nullable=False)
    
    # Location & Weather
    indoor = Column(Boolean, nullable=False)
    outdoor = Column(Boolean, nullable=False)
    weather_best = Column(JSON, default=list)
    weather_avoid = Column(JSON, default=list)
    temperature_min = Column(Float, default=-10)
    temperature_max = Column(Float, default=40)
    
    # Time preferences
    time_of_day = Column(JSON, default=list)
    
    # Cost and category
    cost = Column(String(20))
    category = Column(String(50), index=True)
    
    # Flexible tags
    tags = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
