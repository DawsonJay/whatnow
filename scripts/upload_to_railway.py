#!/usr/bin/env python3
"""
Upload activity payload to Railway backend
"""

import json
import requests
import sys

def upload_to_railway():
    """Upload activities with embeddings to Railway backend"""
    
    # Load the payload
    print("Loading activity payload...")
    with open('data/activities_with_embeddings.json', 'r') as f:
        payload = json.load(f)
    
    print(f"Loaded {payload['count']} activities")
    
    # Railway API URL
    api_url = "https://whatnow-production.up.railway.app"
    
    # Clear existing activities first
    print("\nClearing existing activities...")
    try:
        response = requests.delete(f"{api_url}/activities/clear")
        if response.status_code == 200:
            print("✓ Database cleared")
        else:
            print(f"Warning: Clear failed with status {response.status_code}")
    except Exception as e:
        print(f"Warning: Could not clear database: {e}")
    
    # Upload new activities
    print(f"\nUploading {len(payload['activities'])} activities...")
    try:
        response = requests.post(
            f"{api_url}/activities/bulk-upload",
            json={"activities": payload['activities']},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Successfully uploaded {result['imported']} activities")
            print(f"✓ Message: {result['message']}")
        else:
            print(f"✗ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = upload_to_railway()
    if success:
        print("\n🎉 Upload completed successfully!")
    else:
        print("\n❌ Upload failed!")
        sys.exit(1)
