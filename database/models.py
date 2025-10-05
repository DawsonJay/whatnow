"""
SQLAlchemy models for WhatNow AI System
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database.connection import Base

class Activity(Base):
    __tablename__ = "activities"
    
    # Core fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    embedding = Column(Text, nullable=False)  # JSON string of embedding vector
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
