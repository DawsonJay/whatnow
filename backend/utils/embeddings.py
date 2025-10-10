#!/usr/bin/env python3
"""
Embedding generation utilities for the WhatNow AI system.
"""

import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(titles: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of activity titles.
    
    Args:
        titles: List of activity title strings
        
    Returns:
        List of embedding vectors (each as a list of floats)
    """
    if not titles:
        return []
    
    # Generate embeddings for all titles at once
    embeddings = model.encode(titles, convert_to_tensor=False)
    
    # Convert numpy arrays to lists for JSON serialization
    return [embedding.tolist() for embedding in embeddings]

def create_activity_payload(titles: List[str]) -> List[Dict[str, Any]]:
    """
    Create a payload for bulk activity creation with embeddings.
    
    Args:
        titles: List of activity title strings
        
    Returns:
        List of dictionaries with 'name' and 'embedding' fields
    """
    if not titles:
        return []
    
    embeddings = generate_embeddings(titles)
    
    payload = []
    for title, embedding in zip(titles, embeddings):
        payload.append({
            "name": title,
            "embedding": embedding
        })
    
    return payload
