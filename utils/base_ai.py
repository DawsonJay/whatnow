#!/usr/bin/env python3
"""
Base AI implementation for the WhatNow AI system.
Uses SGDClassifier for contextual bandits with slow learning.
"""

import json
import numpy as np
from sklearn.linear_model import SGDClassifier
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .database import AIModel

class BaseAI:
    """Base AI model using SGDClassifier for contextual bandits."""
    
    def __init__(self):
        self.model = SGDClassifier(
            learning_rate='adaptive',
            eta0=0.01,  # Slow learning rate for Base AI
            random_state=42,
            loss='log_loss'  # Logistic regression for binary classification
        )
        self.is_fitted = False
        self.context_dim = 40  # 40 context tags
        self.embedding_dim = 384  # 384-dimensional embeddings
    
    def get_recommendations(self, context_vector: np.ndarray, activities: List[Dict], top_k: int = 100) -> List[Dict]:
        """
        Get top activity recommendations based on context.
        
        Args:
            context_vector: 40-dimensional context vector
            activities: List of activity dictionaries with embeddings
            top_k: Number of top recommendations to return
            
        Returns:
            List of top activity recommendations
        """
        if len(activities) == 0:
            return []
        
        if not self.is_fitted:
            # Cold start: return random activities
            return np.random.choice(activities, size=min(top_k, len(activities)), replace=False).tolist()
        
        # Use the trained model to score activities
        scores = []
        for activity in activities:
            try:
                # Get the model's prediction for this context
                # The model learns which contexts lead to positive outcomes
                score = self.model.decision_function([context_vector])[0]
                scores.append(score)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip activities with invalid embeddings
                scores.append(0.0)
        
        # Get top-k activities by model score
        top_indices = np.argsort(scores)[-top_k:]
        return [activities[i] for i in top_indices]
    
    def train(self, context_vector: np.ndarray, chosen_activity: Dict, reward: float = 1.0):
        """
        Train the model with user feedback.
        
        Args:
            context_vector: 40-dimensional context vector
            chosen_activity: The activity the user chose
            reward: Reward signal (1.0 for positive, 0.0 for negative)
        """
        try:
            # Validate context vector dimensions
            if len(context_vector) != 40:
                print(f"Error: Context vector has {len(context_vector)} dimensions, expected 40")
                return False
            
            # For contextual bandits, we use the context vector as features
            # The model learns which contexts lead to positive outcomes
            
            # Train the model with context vector as features
            self.model.partial_fit([context_vector], [int(reward)], classes=[0, 1])
            self.is_fitted = True
            
            print(f"Model trained successfully with context: {context_vector[:5]}... (first 5 dims)")
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            print(f"Context vector shape: {context_vector.shape if hasattr(context_vector, 'shape') else 'No shape'}")
            print(f"Context vector type: {type(context_vector)}")
            return False
    
    def save_model(self, db: Session) -> bool:
        """Save the model weights to database."""
        try:
            if not self.is_fitted:
                return False
            
            # Get model weights
            weights_data = {
                "coef": self.model.coef_.tolist() if hasattr(self.model, 'coef_') else None,
                "intercept": self.model.intercept_.tolist() if hasattr(self.model, 'intercept_') else None,
                "classes": self.model.classes_.tolist() if hasattr(self.model, 'classes_') else None,
                "is_fitted": self.is_fitted
            }
            
            # Check if model exists in database
            ai_model = db.query(AIModel).first()
            
            if ai_model:
                # Update existing model
                ai_model.weights = json.dumps(weights_data)
            else:
                # Create new model
                ai_model = AIModel(weights=json.dumps(weights_data))
                db.add(ai_model)
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error saving model: {e}")
            db.rollback()
            return False
    
    def load_model(self, db: Session) -> bool:
        """Load the model weights from database."""
        try:
            ai_model = db.query(AIModel).first()
            
            if not ai_model:
                return False
            
            weights_data = json.loads(ai_model.weights)
            
            # Restore model state
            if weights_data.get("coef") is not None:
                self.model.coef_ = np.array(weights_data["coef"])
            if weights_data.get("intercept") is not None:
                self.model.intercept_ = np.array(weights_data["intercept"])
            if weights_data.get("classes") is not None:
                self.model.classes_ = np.array(weights_data["classes"])
            
            self.is_fitted = weights_data.get("is_fitted", False)
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

def encode_context(context_tags: List[str]) -> np.ndarray:
    """
    Convert context tags to 40-dimensional context vector.
    
    Args:
        context_tags: List of selected context tags
        
    Returns:
        40-dimensional numpy array
    """
    # Tag to index mapping (40 total tags)
    tag_to_index = {
        # Mood tags (0-6)
        "arty": 0, "chill": 1, "energetic": 2, "creative": 3, 
        "relaxed": 4, "social": 5, "introverted": 6,
        
        # Weather tags (7-11)
        "sunny": 7, "rainy": 8, "cloudy": 9, "snowy": 10, "windy": 11,
        
        # Time tags (12-17)
        "morning": 12, "afternoon": 13, "evening": 14, "night": 15,
        "weekend": 16, "weekday": 17,
        
        # Location tags (18-23)
        "indoor": 18, "outdoor": 19, "home": 20, "cafe": 21, "park": 22, "beach": 23,
        
        # Social tags (24-28)
        "alone": 24, "with_friends": 25, "with_family": 26, "with_partner": 27, "group_activity": 28,
        
        # Energy tags (29-31)
        "low_energy": 29, "medium_energy": 30, "high_energy": 31,
        
        # Activity type tags (32-37)
        "physical": 32, "mental": 33, "artistic": 34, "social": 35, "learning": 36, "entertainment": 37,
        
        # Additional tags (38-39)
        "productive": 38, "mindful": 39
    }
    
    # Initialize context vector
    context_vector = np.zeros(40)
    
    # Set selected tags to 1.0
    for tag in context_tags:
        if tag in tag_to_index:
            context_vector[tag_to_index[tag]] = 1.0
    
    return context_vector
