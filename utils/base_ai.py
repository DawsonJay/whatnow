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
        self.context_dim = 43  # 43 context tags
        self.embedding_dim = 384  # 384-dimensional embeddings
    
    def get_recommendations(self, context_vector: np.ndarray, activities: List[Dict], top_k: int = 100) -> List[Dict]:
        """
        Get top activity recommendations based on context.
        
        Args:
            context_vector: 43-dimensional context vector
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
            context_vector: 43-dimensional context vector
            chosen_activity: The activity the user chose
            reward: Reward signal (1.0 for positive, 0.0 for negative)
        """
        try:
            # Validate context vector dimensions
            if len(context_vector) != 43:
                print(f"Error: Context vector has {len(context_vector)} dimensions, expected 43")
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
    
    def get_model_weights(self) -> Dict[str, Any]:
        """Get model weights for Session AI initialization."""
        if not self.is_fitted:
            return None
        
        return {
            "coef": self.model.coef_.tolist() if hasattr(self.model, 'coef_') else None,
            "intercept": self.model.intercept_.tolist() if hasattr(self.model, 'intercept_') else None,
            "classes": self.model.classes_.tolist() if hasattr(self.model, 'classes_') else None,
            "is_fitted": self.is_fitted
        }
    
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
    Convert context tags to 43-dimensional context vector.
    
    Args:
        context_tags: List of selected context tags
        
    Returns:
        43-dimensional numpy array
    """
    # Tag to index mapping (43 total tags)
    tag_to_index = {
        # Weather tags (0-4)
        "sunny": 0, "cloudy": 1, "raining": 2, "snowy": 3, "stormy": 4,
        
        # Time tags (5-8)
        "morning": 5, "afternoon": 6, "evening": 7, "night": 8,
        
        # Season tags (9-12)
        "spring": 9, "summer": 10, "autumn": 11, "winter": 12,
        
        # Intensity tags (13-17)
        "chill": 13, "tired": 14, "exciting": 15, "energetic": 16, "intense": 17,
        
        # Mood tags (18-39)
        "stressed": 18, "motivated": 19, "adventurous": 20, "nostalgic": 21, "romantic": 22,
        "playful": 23, "focused": 24, "distracted": 25, "inspired": 26, "friendly": 27,
        "shy": 28, "curious": 29, "analytical": 30, "emotional": 31, "burnt_out": 32,
        "artistic": 33, "practical": 34, "hungry": 35, "natural": 36, "urban": 37,
        "anxious": 38, "overwhelmed": 39, "upset": 40, "happy": 41, "festive": 42
    }
    
    # Initialize context vector (43 dimensions for all tags)
    context_vector = np.zeros(43)
    
    # Set selected tags to 1.0
    for tag in context_tags:
        if tag in tag_to_index:
            context_vector[tag_to_index[tag]] = 1.0
    
    return context_vector
