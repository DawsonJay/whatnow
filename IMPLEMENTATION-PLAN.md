# WhatNow Implementation Plan

## Project Pivot: From Manual Metadata to AI-Powered Recommendations

**Date:** 2025-10-05

**Status:** Planning Phase → Implementation Starting

---

## Executive Summary

**What Changed:**
- **Old Approach:** Manual metadata (physical/mental/social energy values, weather tags, cost, etc.)
- **New Approach:** AI learns everything from activity names/descriptions and user behavior
- **Why:** More scalable, easier to maintain, better user experience, stronger portfolio piece

**Key Innovation:**
- Two-tier AI: Base AI (slow, general) + Session AI (fast, personal)
- Semantic embeddings eliminate need for manual tagging
- Continuous learning from user comparisons

---

## Phase 1: Foundation - Embeddings

### Objectives
- Generate semantic embeddings for all activities
- Update database schema
- Verify embedding quality

### Tasks

#### 1.1 Install Dependencies
```bash
cd /home/james/Documents/whatnow
pip install sentence-transformers scikit-learn numpy
```

**Dependencies:**
- `sentence-transformers`: Generate embeddings
- `scikit-learn`: Base AI model (SGDClassifier)
- `numpy`: Vector operations

#### 1.2 Update Database Schema

**Migration SQL:**
```sql
-- Add embedding column to activities table
ALTER TABLE activities 
ADD COLUMN embedding TEXT;  -- Store as JSON string
```

#### 1.3 Create Embedding Generation Script

**File:** `scripts/generate_embeddings.py`

```python
from sentence_transformers import SentenceTransformer
import os
from database.connection import get_database_session
from database.models import Activity
import json

def generate_embeddings():
    # Load model
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Connect to database
    db = get_database_session()
    
    try:
        # Get all activities
        activities = db.query(Activity).all()
        print(f"Found {len(activities)} activities")
        
        # Generate embeddings
        for i, activity in enumerate(activities):
            # Combine name and description
            text = f"{activity.name}: {activity.description or ''}"
            
            # Generate embedding
            embedding = model.encode(text)
            
            # Store as JSON string
            activity.embedding = json.dumps(embedding.tolist())
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(activities)} activities")
        
        # Commit changes
        db.commit()
        print("✓ All embeddings generated and saved!")
        
        # Test similarity
        print("\nTesting similarity...")
        test_query = "creative indoor activity"
        query_embedding = model.encode(test_query)
        
        # Find similar activities (simple version)
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        embeddings_matrix = np.array([
            json.loads(a.embedding) for a in activities
        ])
        
        similarities = cosine_similarity([query_embedding], embeddings_matrix)[0]
        top_indices = np.argsort(similarities)[-5:][::-1]
        
        print(f"\nTop 5 matches for '{test_query}':")
        for idx in top_indices:
            print(f"  - {activities[idx].name} (similarity: {similarities[idx]:.3f})")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_embeddings()
```

**Run:**
```bash
python scripts/generate_embeddings.py
```

#### 1.4 Verification

**Create test script:** `scripts/test_embeddings.py`

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from database.connection import get_database_session
from database.models import Activity

def test_embeddings():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    db = get_database_session()
    
    activities = db.query(Activity).all()
    embeddings = np.array([json.loads(a.embedding) for a in activities])
    
    # Test queries
    test_cases = [
        "creative indoor rainy day",
        "outdoor adventure sunny",
        "relaxing evening activity",
        "energetic morning exercise"
    ]
    
    for query in test_cases:
        query_embedding = model.encode(query)
        similarities = cosine_similarity([query_embedding], embeddings)[0]
        top_idx = np.argmax(similarities)
        
        print(f"\nQuery: '{query}'")
        print(f"Top match: {activities[top_idx].name} ({similarities[top_idx]:.3f})")
    
    db.close()

if __name__ == "__main__":
    test_embeddings()
```

---

## Phase 2: Backend - Base AI

### Objectives
- Implement Base AI model with online learning
- Create new API endpoints
- Remove old metadata-based logic

### Tasks

#### 2.1 Create Base AI Module

**File:** `ai/base_model.py`

```python
from sklearn.linear_model import SGDClassifier
import numpy as np
import pickle
import os

class BaseAI:
    def __init__(self, model_path='ai/base_model.pkl'):
        self.model_path = model_path
        self.learning_rate = 0.01
        
        # Load existing model or create new
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            # Initialize SGD classifier for online learning
            self.model = SGDClassifier(
                loss='log_loss',
                learning_rate='constant',
                eta0=self.learning_rate,
                random_state=42
            )
            self.is_fitted = False
    
    def score(self, query_embedding, activity_embedding):
        """Score an activity for a given query"""
        if not hasattr(self, 'is_fitted') or not self.is_fitted:
            # Before training, just use cosine similarity
            return np.dot(query_embedding, activity_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(activity_embedding)
            )
        
        # After training, use model prediction
        feature_vector = self._create_feature_vector(query_embedding, activity_embedding)
        try:
            return self.model.predict_proba([feature_vector])[0][1]
        except:
            # Fallback to similarity
            return np.dot(query_embedding, activity_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(activity_embedding)
            )
    
    def train(self, query_embedding, chosen_embedding, rejected_embedding):
        """Update model from a comparison"""
        # Create training examples
        chosen_features = self._create_feature_vector(query_embedding, chosen_embedding)
        rejected_features = self._create_feature_vector(query_embedding, rejected_embedding)
        
        X = np.array([chosen_features, rejected_features])
        y = np.array([1, 0])  # 1 = chosen, 0 = rejected
        
        # Update model
        if not hasattr(self, 'is_fitted') or not self.is_fitted:
            self.model.fit(X, y)
            self.is_fitted = True
        else:
            self.model.partial_fit(X, y)
        
        # Save model periodically (every N updates)
        if not hasattr(self, 'update_count'):
            self.update_count = 0
        self.update_count += 1
        
        if self.update_count % 10 == 0:
            self.save()
    
    def _create_feature_vector(self, query_embedding, activity_embedding):
        """Create feature vector from query and activity embeddings"""
        # Combine embeddings in various ways
        similarity = np.dot(query_embedding, activity_embedding)
        element_wise_product = query_embedding * activity_embedding
        difference = query_embedding - activity_embedding
        
        # Concatenate features
        return np.concatenate([
            [similarity],
            element_wise_product,
            difference
        ])
    
    def save(self):
        """Save model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
    
    def load(self):
        """Load model from disk"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
                self.is_fitted = True

# Global instance
base_ai = BaseAI()
```

#### 2.2 Update API Endpoints

**File:** `main.py` - Replace old endpoints

```python
from fastapi import FastAPI, HTTPException
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from ai.base_model import base_ai
from database.connection import get_database_session
from database.models import Activity

app = FastAPI()

# Load embedding model (do this once at startup)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

@app.post("/game/start")
def start_game(request: dict):
    """
    Start a new game session
    Input: {"tags": ["arty", "chill", "indoor", "rainy"]}
    Output: List of top candidate activities
    """
    tags = request.get("tags", [])
    
    if not tags:
        raise HTTPException(status_code=400, detail="Tags required")
    
    db = get_database_session()
    
    try:
        # Generate query embedding from tags
        query_text = " ".join(tags)
        query_embedding = embedding_model.encode(query_text)
        
        # Get all activities
        activities = db.query(Activity).all()
        
        # Score each activity
        scored_activities = []
        for activity in activities:
            # Get activity embedding
            activity_embedding = np.array(json.loads(activity.embedding))
            
            # Calculate base similarity
            similarity = cosine_similarity([query_embedding], [activity_embedding])[0][0]
            
            # Add Base AI adjustment
            base_score = base_ai.score(query_embedding, activity_embedding)
            
            # Combined score
            final_score = 0.5 * similarity + 0.5 * base_score
            
            scored_activities.append({
                "id": activity.id,
                "name": activity.name,
                "description": activity.description,
                "embedding": activity_embedding.tolist(),
                "base_score": float(final_score)
            })
        
        # Return top 100 candidates
        scored_activities.sort(key=lambda x: x['base_score'], reverse=True)
        
        return {
            "candidates": scored_activities[:100],
            "total": len(activities)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/game/train")
def train(request: dict):
    """
    Train Base AI from a comparison
    Input: {
        "chosen_id": 1,
        "rejected_id": 5,
        "tags": ["arty", "chill", "indoor"]
    }
    """
    chosen_id = request.get("chosen_id")
    rejected_id = request.get("rejected_id")
    tags = request.get("tags", [])
    
    if not all([chosen_id, rejected_id, tags]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    db = get_database_session()
    
    try:
        # Get activities
        chosen = db.query(Activity).filter(Activity.id == chosen_id).first()
        rejected = db.query(Activity).filter(Activity.id == rejected_id).first()
        
        if not chosen or not rejected:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        # Generate query embedding
        query_text = " ".join(tags)
        query_embedding = embedding_model.encode(query_text)
        
        # Get activity embeddings
        chosen_embedding = np.array(json.loads(chosen.embedding))
        rejected_embedding = np.array(json.loads(rejected.embedding))
        
        # Train Base AI (slow learning rate)
        base_ai.train(query_embedding, chosen_embedding, rejected_embedding)
        
        return {"status": "ok", "message": "Base AI updated"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "healthy", "base_ai_trained": base_ai.is_fitted}
```

#### 2.3 Remove Old Endpoints

**Remove from `main.py`:**
- Old `/game/start` logic with manual filtering
- Old `/game/train` with energy value adjustments
- Old `/calibration/*` endpoints
- Old `/activities/{id}` PUT endpoint for updating energy values

#### 2.4 Test Backend

**Create test script:** `scripts/test_backend.py`

```python
import requests

API_URL = "http://localhost:8000"

def test_flow():
    # Test start game
    response = requests.post(f"{API_URL}/game/start", json={
        "tags": ["arty", "chill", "indoor", "rainy"]
    })
    
    print("Start game response:")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Candidates: {data['total']}")
    print(f"Top 3:")
    for i, activity in enumerate(data['candidates'][:3]):
        print(f"  {i+1}. {activity['name']} (score: {activity['base_score']:.3f})")
    
    # Test training
    chosen_id = data['candidates'][0]['id']
    rejected_id = data['candidates'][1]['id']
    
    response = requests.post(f"{API_URL}/game/train", json={
        "chosen_id": chosen_id,
        "rejected_id": rejected_id,
        "tags": ["arty", "chill", "indoor", "rainy"]
    })
    
    print(f"\nTrain response: {response.json()}")

if __name__ == "__main__":
    test_flow()
```

---

## Phase 3: Frontend - Session AI & New UI

### Objectives
- Replace energy sliders with tag selection
- Implement Session AI in JavaScript
- Update comparison game flow

### Tasks

#### 3.1 Design Tag Selection UI

**File:** `index.html` - Replace filters section

```html
<div class="filters-section">
    <h2>What's your vibe right now?</h2>
    
    <!-- Mood Tags -->
    <div class="tag-section">
        <label>🎨 Mood</label>
        <div class="tag-grid">
            <button class="tag-btn" data-tag="arty">Arty</button>
            <button class="tag-btn" data-tag="creative">Creative</button>
            <button class="tag-btn" data-tag="adventurous">Adventurous</button>
            <button class="tag-btn" data-tag="chill">Chill</button>
            <button class="tag-btn" data-tag="productive">Productive</button>
            <button class="tag-btn" data-tag="social">Social</button>
            <button class="tag-btn" data-tag="active">Active</button>
        </div>
    </div>
    
    <!-- Weather Tags -->
    <div class="tag-section">
        <label>🌤️ Weather</label>
        <div class="tag-grid">
            <button class="tag-btn" data-tag="sunny">☀️ Sunny</button>
            <button class="tag-btn" data-tag="rainy">🌧️ Rainy</button>
            <button class="tag-btn" data-tag="snowy">❄️ Snowy</button>
            <button class="tag-btn" data-tag="cloudy">☁️ Cloudy</button>
        </div>
    </div>
    
    <!-- Location Tags -->
    <div class="tag-section">
        <label>📍 Location</label>
        <div class="tag-grid">
            <button class="tag-btn" data-tag="indoor">🏠 Indoor</button>
            <button class="tag-btn" data-tag="outdoor">🌳 Outdoor</button>
            <button class="tag-btn" data-tag="home">🛋️ Home</button>
            <button class="tag-btn" data-tag="nature">🏞️ Nature</button>
        </div>
    </div>
    
    <!-- Time Tags -->
    <div class="tag-section">
        <label>🕐 Time</label>
        <div class="tag-grid">
            <button class="tag-btn" data-tag="morning">🌅 Morning</button>
            <button class="tag-btn" data-tag="afternoon">☀️ Afternoon</button>
            <button class="tag-btn" data-tag="evening">🌆 Evening</button>
            <button class="tag-btn" data-tag="night">🌙 Night</button>
        </div>
    </div>
    
    <!-- Energy Tags -->
    <div class="tag-section">
        <label>⚡ Energy</label>
        <div class="tag-grid">
            <button class="tag-btn" data-tag="energetic">⚡ Energetic</button>
            <button class="tag-btn" data-tag="tired">😴 Tired</button>
            <button class="tag-btn" data-tag="calm">🧘 Calm</button>
            <button class="tag-btn" data-tag="restless">🏃 Restless</button>
        </div>
    </div>
    
    <button class="start-btn" id="startBtn">Find Activities</button>
</div>

<style>
.tag-section {
    margin-bottom: 25px;
}

.tag-section label {
    display: block;
    font-weight: 600;
    margin-bottom: 10px;
    color: #333;
    font-size: 16px;
}

.tag-grid {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.tag-btn {
    padding: 10px 20px;
    border: 2px solid #e0e0e0;
    border-radius: 20px;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 14px;
    font-weight: 500;
}

.tag-btn:hover {
    border-color: #667eea;
    transform: translateY(-2px);
}

.tag-btn.selected {
    border-color: #667eea;
    background: #667eea;
    color: white;
}
</style>
```

#### 3.2 Implement Session AI

**File:** `index.html` - Add Session AI JavaScript

```javascript
class SessionAI {
    constructor() {
        // Track score adjustments for each activity
        this.boosts = {};
        this.learningRate = 0.3;
    }
    
    rank(candidates) {
        // Re-rank candidates using session preferences
        return candidates.map(activity => {
            const boost = this.boosts[activity.id] || 0;
            return {
                ...activity,
                session_score: activity.base_score + boost
            };
        }).sort((a, b) => b.session_score - a.session_score);
    }
    
    train(chosen, rejected, tags) {
        // Boost chosen activity
        if (!this.boosts[chosen.id]) this.boosts[chosen.id] = 0;
        this.boosts[chosen.id] += this.learningRate;
        
        // Penalize rejected activity
        if (!this.boosts[rejected.id]) this.boosts[rejected.id] = 0;
        this.boosts[rejected.id] -= this.learningRate;
        
        console.log(`Session AI updated: ${chosen.name} +${this.learningRate}, ${rejected.name} -${this.learningRate}`);
    }
    
    getStats() {
        const boosted = Object.values(this.boosts).filter(b => b > 0).length;
        const penalized = Object.values(this.boosts).filter(b => b < 0).length;
        return { boosted, penalized };
    }
}
```

#### 3.3 Update Game Flow

**File:** `index.html` - Update game logic

```javascript
const API_URL = 'https://whatnow-production.up.railway.app';

let candidates = [];
let sessionAI = null;
let selectedTags = new Set();
let comparisonCount = 0;
let currentChosen = null;

// Tag selection
document.querySelectorAll('.tag-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tag = btn.dataset.tag;
        
        if (selectedTags.has(tag)) {
            selectedTags.delete(tag);
            btn.classList.remove('selected');
        } else {
            selectedTags.add(tag);
            btn.classList.add('selected');
        }
        
        // Enable start button if tags selected
        document.getElementById('startBtn').disabled = selectedTags.size === 0;
    });
});

// Start game
document.getElementById('startBtn').addEventListener('click', async () => {
    if (selectedTags.size === 0) {
        alert('Please select at least one tag');
        return;
    }
    
    try {
        // Fetch candidates from backend
        const response = await fetch(`${API_URL}/game/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tags: Array.from(selectedTags)
            })
        });
        
        const data = await response.json();
        candidates = data.candidates;
        
        if (candidates.length < 2) {
            alert('Not enough activities found. Try different tags.');
            return;
        }
        
        // Initialize Session AI
        sessionAI = new SessionAI();
        
        // Reset state
        comparisonCount = 0;
        currentChosen = null;
        
        // Show game section
        document.querySelector('.filters-section').style.display = 'none';
        document.getElementById('gameSection').classList.add('active');
        
        // Display selected tags
        document.getElementById('selectedTags').textContent = 
            Array.from(selectedTags).join(', ');
        
        // Load first comparison
        loadNextComparison();
        
    } catch (error) {
        console.error('Error starting game:', error);
        alert('Failed to start game. Please try again.');
    }
});

function loadNextComparison() {
    // Re-rank candidates with Session AI
    candidates = sessionAI.rank(candidates);
    
    let activityA, activityB;
    
    if (currentChosen) {
        // King of the hill: keep chosen, get new challenger
        activityA = currentChosen;
        activityB = candidates.find(c => c.id !== activityA.id);
    } else {
        // Initial comparison
        activityA = candidates[0];
        activityB = candidates[1];
    }
    
    if (!activityB) {
        alert('No more activities to compare!');
        return;
    }
    
    // Display both activities
    displayActivity('activityA', activityA);
    displayActivity('activityB', activityB);
}

function displayActivity(cardId, activity) {
    const card = document.getElementById(cardId);
    card.querySelector('.activity-name').textContent = activity.name;
    card.querySelector('.activity-description').textContent = activity.description;
    card.querySelector('.activity-score').textContent = 
        `Score: ${activity.session_score.toFixed(3)}`;
}

async function handleChoice(chosenCard) {
    const chosen = chosenCard === 'activityA' ? 
        document.getElementById('activityA').activity :
        document.getElementById('activityB').activity;
    
    const rejected = chosenCard === 'activityA' ?
        document.getElementById('activityB').activity :
        document.getElementById('activityA').activity;
    
    // Update Session AI (fast learning)
    sessionAI.train(chosen, rejected, Array.from(selectedTags));
    
    // Send training data to backend (async, don't wait)
    fetch(`${API_URL}/game/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            chosen_id: chosen.id,
            rejected_id: rejected.id,
            tags: Array.from(selectedTags)
        })
    }).catch(err => console.error('Training error:', err));
    
    // Update state
    currentChosen = chosen;
    comparisonCount++;
    document.getElementById('comparisons').textContent = comparisonCount;
    
    // Load next comparison
    loadNextComparison();
}

// Attach to cards
document.getElementById('activityA').onclick = () => handleChoice('activityA');
document.getElementById('activityB').onclick = () => handleChoice('activityB');
```

---

## Phase 4: Integration & Testing

### Tasks

#### 4.1 End-to-End Testing

**Test Cases:**
1. Generate embeddings for all activities
2. Start backend server
3. Start frontend server
4. Select tags and start game
5. Make 10 comparisons
6. Verify Session AI learns preferences
7. Restart and verify Base AI improved

#### 4.2 Learning Rate Tuning

**Test different rates:**
- Base AI: Try 0.001, 0.01, 0.1
- Session AI: Try 0.1, 0.3, 0.5

**Metrics:**
- How quickly Session AI personalizes
- How stable Base AI remains
- Overall recommendation quality

#### 4.3 Performance Optimization

- Cache embedding model in memory
- Optimize database queries
- Minimize API round-trips
- Test with 1000+ activities

---

## Phase 5: Deployment & Polish

### Tasks

#### 5.1 Deploy Updates

```bash
# Commit changes
git add .
git commit -m "Implement AI-powered recommendation system"
git push

# Deploy to Railway (automatic)
```

#### 5.2 Documentation

- Update README with new system description
- Document tag system
- Add usage examples
- Create demo video/screenshots

#### 5.3 Future Enhancements

**Quick Wins:**
- Add more tag categories
- Improve tag UI
- Show recommendation explanations

**Longer Term:**
- Upgrade Session AI to TensorFlow.js
- Add user accounts
- Collaborative filtering
- Activity images

---

## Success Criteria

### Technical
- ✅ Embeddings generated for all activities
- ✅ Base AI learns from comparisons
- ✅ Session AI personalizes within 5-10 comparisons
- ✅ API response time < 500ms
- ✅ System scales to 1000+ activities

### User Experience
- ✅ Tag selection is intuitive
- ✅ Recommendations feel relevant
- ✅ Comparison game is engaging
- ✅ System improves over time (observable)

### Portfolio Value
- ✅ Demonstrates AI/ML understanding
- ✅ Shows engineering judgment
- ✅ Clean, maintainable code
- ✅ Well-documented system

---

## Timeline Estimate

**Phase 1 (Foundation):** 2-3 hours
- Set up dependencies
- Generate embeddings
- Verify quality

**Phase 2 (Backend):** 3-4 hours
- Implement Base AI
- Update API endpoints
- Test backend

**Phase 3 (Frontend):** 3-4 hours
- Build tag UI
- Implement Session AI
- Update game flow

**Phase 4 (Integration):** 2-3 hours
- End-to-end testing
- Tune parameters
- Fix bugs

**Phase 5 (Polish):** 2-3 hours
- Documentation
- Deployment
- Final testing

**Total:** 12-17 hours

---

## Next Steps

1. ✅ Create documentation (this file)
2. ⏭️ Create chat record
3. ⏭️ Begin Phase 1: Generate embeddings
4. ⏭️ Continue through phases sequentially

**Ready to start implementation!**