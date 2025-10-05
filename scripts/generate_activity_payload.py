#!/usr/bin/env python3
"""
Generate activity payload with embeddings for Railway backend
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os

def generate_activity_payload():
    """Generate JSON payload with activities and embeddings"""
    
    # Load the sentence transformer model
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Read activity names from file
    print("Reading activity names...")
    with open('data/activity_names.txt', 'r') as f:
        activity_names = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(activity_names)} activities")
    
    # Generate embeddings and create payload
    activities = []
    
    for i, name in enumerate(activity_names):
        print(f"Processing {i+1}/{len(activity_names)}: {name}")
        
        # Generate embedding for the activity name
        embedding = model.encode(name)
        
        # Create activity object
        activity = {
            "name": name,
            "embedding": json.dumps(embedding.tolist())  # Convert to JSON string
        }
        
        activities.append(activity)
    
    # Create the payload
    payload = {
        "activities": activities,
        "count": len(activities),
        "model": "all-MiniLM-L6-v2",
        "embedding_dimension": len(embedding)
    }
    
    # Save to JSON file
    output_file = "data/activities_with_embeddings.json"
    with open(output_file, 'w') as f:
        json.dump(payload, f, indent=2)
    
    print(f"\n✓ Generated payload with {len(activities)} activities")
    print(f"✓ Saved to {output_file}")
    print(f"✓ Embedding dimension: {len(embedding)}")
    
    # Test a few embeddings
    print("\nTesting embeddings...")
    test_queries = [
        "creative indoor activity",
        "outdoor adventure",
        "relaxing evening",
        "energetic morning exercise"
    ]
    
    for query in test_queries:
        query_embedding = model.encode(query)
        
        # Find most similar activity
        similarities = []
        for activity in activities[:10]:  # Test with first 10 activities
            activity_embedding = np.array(json.loads(activity['embedding']))
            similarity = np.dot(query_embedding, activity_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(activity_embedding)
            )
            similarities.append((activity['name'], similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nQuery: '{query}'")
        print(f"Top match: {similarities[0][0]} (similarity: {similarities[0][1]:.3f})")
    
    return output_file

if __name__ == "__main__":
    generate_activity_payload()
