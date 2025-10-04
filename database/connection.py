"""
Database connection utilities for WhatNow
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # For Railway deployment, provide a fallback or better error message
    print("WARNING: DATABASE_URL environment variable not found")
    print("This is expected during Railway deployment setup")
    # Use a dummy URL for now - Railway will provide the real one
    DATABASE_URL = "postgresql://dummy:dummy@localhost/dummy"

# Create SQLAlchemy engine with connection pooling and retry logic
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,     # Recycle connections every 5 minutes
    echo=False            # Set to True for debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
