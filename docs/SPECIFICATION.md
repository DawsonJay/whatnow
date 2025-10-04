# WhatNow - Technical Specification

**Created**: 2025-10-04-1620 UTC  
**Status**: Draft v1.0

## 1. Project Overview

### 1.1 Purpose
WhatNow is an AI-powered activity recommendation system that helps users decide what to do based on their current mood, energy, social preferences, time availability, and weather conditions. The system uses contextual bandits (reinforcement learning) to learn user preferences over time.

### 1.2 Core Innovation
Two-layer learning system:
- **Fast within-session learning** for immediate refinement
- **Slow cross-session learning** for long-term preference building
- Robust to outlier sessions while remaining responsive to current mood

### 1.3 Target Users
- People experiencing decision fatigue
- Users wanting personalized activity suggestions
- Anyone looking to optimize their leisure time
- Initial user: Developer (self-training)

---

## 2. User Experience Flow

### 2.1 Session Flow

```
1. User opens app
   ↓
2. Set context via sliders:
   - Mood (1-10)
   - Social (solo → group)
   - Energy (low → high)
   - Time available (15min → 4+ hours)
   - Weather (current conditions)
   ↓
3. Click "Generate Suggestions"
   ↓
4. AI generates 50 activity suggestions
   - Displayed in scrollable list
   - Each shows: name, duration, energy, social level, tags
   ↓
5. User selects top 3 favorites (checkboxes)
   ↓
6. User can either:
   a) Click "Regenerate" → get 50 NEW suggestions (influenced by picks)
      - Top 3 move to "Favorites Pool"
      - Return to step 5 with new suggestions
   b) Click "Done Picking" → move to final selection
   ↓
7. View accumulated favorites (3-15+ activities)
   ↓
8. Pick ONE activity to actually do
   ↓
9. Session ends, AI learns
```

### 2.2 Regeneration Behavior

**Round 1**: Initial suggestions based on context + base AI preferences
**Round 2+**: New suggestions influenced by previous picks within session
- Session AI learns quickly (learning rate = 0.8)
- Suggestions become more similar to what user picked
- Still includes some exploration/variety

### 2.3 Learning After Session

**Session AI** (temporary):
- Learned quickly during session
- Used for within-session refinement
- **Discarded** at session end

**Base AI** (persistent):
- Learns slowly from all picks (learning rate = 0.02)
- Learns more from final choice (learning rate = 0.05)
- Saved to database for next session

---

## 3. Data Architecture

### 3.1 Activity Schema

```python
Activity:
  id: UUID
  name: string (required)
  description: string (optional)
  
  # Core attributes (1-10 scale)
  energy_level: float (1-10)
  social_level: float (1-10, 1=solo, 10=large group)
  
  # Time
  duration_min: int (minutes)
  duration_max: int (minutes)
  
  # Weather
  indoor: boolean
  weather_good: list[string] (e.g., ["sunny", "overcast"])
  weather_avoid: list[string] (e.g., ["raining", "windy"])
  
  # Time of day
  time_of_day: list[string] (e.g., ["morning", "afternoon", "evening", "night"])
  
  # Additional attributes
  cost: enum["free", "low", "medium", "high"]
  equipment_needed: list[string]
  location_type: enum["home", "local", "travel"]
  
  # Tags for categorization
  tags: list[string] (e.g., ["outdoor", "creative", "physical", "social"])
  
  # Metadata
  created_at: timestamp
  updated_at: timestamp
```

### 3.2 User Context Schema

```python
Context:
  # User input (sliders)
  mood: float (1-10)
  social: float (1-10)
  energy: float (1-10)
  time_available: int (minutes)
  
  # Environmental (auto-detected or manual)
  weather: string (e.g., "sunny", "rainy")
  temperature: float (celsius)
  time_of_day: string (e.g., "morning", "afternoon")
  day_of_week: string
  season: string
  
  # Timestamp
  timestamp: datetime
```

### 3.3 Session Schema

```python
Session:
  id: UUID
  user_id: UUID (for future multi-user support)
  context: Context (embedded document)
  
  # Rounds of refinement
  rounds: list[Round]
  
  # Final selection
  accumulated_favorites: list[Activity.id]
  final_choice: Activity.id
  
  # Metadata
  started_at: timestamp
  ended_at: timestamp
  total_rounds: int

Round:
  round_number: int
  suggestions: list[Activity.id] (50 activities)
  user_picks: list[Activity.id] (3 activities)
  timestamp: timestamp
```

### 3.4 AI Model State Schema

```python
BanditModel:
  id: UUID
  user_id: UUID
  
  # Model parameters (specific to bandit implementation)
  activity_scores: dict[Activity.id -> float]
  context_weights: dict[string -> float]
  feature_weights: dict[string -> float]
  
  # Learning metadata
  total_sessions: int
  total_interactions: int
  last_updated: timestamp
  
  # Serialized model (for complex implementations)
  model_state: blob (pickled model)
```

---

## 4. AI Architecture

### 4.1 Contextual Bandit Approach

**Algorithm**: Multi-armed contextual bandit with linear reward model

**Context Vector** (features):
```python
context_vector = [
  mood,           # 1-10
  social,         # 1-10
  energy,         # 1-10
  time_available, # minutes (normalized)
  is_sunny,       # 0/1
  is_rainy,       # 0/1
  is_morning,     # 0/1
  is_afternoon,   # 0/1
  is_evening,     # 0/1
  is_weekend,     # 0/1
  temperature,    # celsius (normalized)
  # ... additional features
]
```

**Activity Vector** (features):
```python
activity_vector = [
  energy_level,   # 1-10
  social_level,   # 1-10
  duration,       # minutes (normalized)
  indoor,         # 0/1
  is_physical,    # 0/1 (from tags)
  is_creative,    # 0/1 (from tags)
  is_productive,  # 0/1 (from tags)
  is_relaxing,    # 0/1 (from tags)
  # ... additional features
]
```

**Combined Feature Vector**:
```python
features = concatenate([context_vector, activity_vector, 
                        context ⊗ activity])  # Include interactions
```

**Reward Model**:
```python
score(activity, context) = w^T * features + exploration_bonus
```

### 4.2 Two-Layer Learning

**Base Model (Persistent)**:
```python
class BaseModel:
  learning_rate = 0.02  # Slow learning
  
  def update(self, context, activity, reward):
    # Update weights using gradient descent
    gradient = (reward - predicted_reward) * features
    self.weights += self.learning_rate * gradient
  
  def save_to_database(self):
    # Serialize and store in PostgreSQL
```

**Session Model (Temporary)**:
```python
class SessionModel:
  learning_rate = 0.8  # Fast learning
  
  def __init__(self, base_model):
    # Deep copy base model
    self.weights = copy(base_model.weights)
  
  def update(self, context, activity, reward):
    # Update weights using gradient descent (fast)
    gradient = (reward - predicted_reward) * features
    self.weights += self.learning_rate * gradient
  
  # Not saved to database - discarded after session
```

### 4.3 Recommendation Generation

**Filtering**:
```python
def filter_activities(all_activities, context):
  filtered = []
  for activity in all_activities:
    # Hard constraints
    if activity.duration_min > context.time_available:
      continue
    if context.weather in activity.weather_avoid:
      continue
    if activity.indoor == False and context.weather == "raining":
      continue
    
    filtered.append(activity)
  return filtered
```

**Scoring & Selection**:
```python
def recommend(context, model, count=50):
  # Filter by hard constraints
  candidates = filter_activities(all_activities, context)
  
  # Score each candidate
  scores = []
  for activity in candidates:
    features = extract_features(context, activity)
    score = model.predict(features)
    
    # Add exploration bonus (epsilon-greedy or UCB)
    exploration = calculate_exploration_bonus(activity, model)
    final_score = score + exploration
    
    scores.append((activity, final_score))
  
  # Sort by score and return top N
  scores.sort(key=lambda x: x[1], reverse=True)
  return [activity for activity, score in scores[:count]]
```

### 4.4 Learning Process

**Within Session**:
```python
# Round 1
session_model = copy(base_model)
suggestions = recommend(context, session_model, count=50)
user_picks = [activity1, activity2, activity3]

# Update session model (fast learning)
for activity in user_picks:
  session_model.update(context, activity, reward=+1)

for activity in not_picked:
  session_model.update(context, activity, reward=0)

# Round 2 (if user regenerates)
suggestions = recommend(context, session_model, count=50)
# Suggestions now influenced by Round 1 picks
```

**Cross Session**:
```python
# After session ends
all_picks = [round1_picks + round2_picks + ...]

# Update base model (slow learning)
for activity in all_picks:
  base_model.update(context, activity, reward=+1, lr=0.02)

# Extra weight for final choice
base_model.update(context, final_choice, reward=+1, lr=0.05)

# Save to database
base_model.save_to_database()

# Discard session model
del session_model
```

---

## 5. Technical Stack

### 5.1 Backend

**Framework**: FastAPI (Python 3.11+)
- Fast, modern Python web framework
- Automatic OpenAPI documentation
- Type hints and validation (Pydantic)
- Async support for scalability

**Database**: PostgreSQL 15+
- JSONB support for flexible schemas
- Good performance for complex queries
- Railway-compatible

**ORM**: SQLAlchemy 2.0
- Type-safe queries
- Migration support (Alembic)
- Connection pooling

**AI/ML Libraries**:
- NumPy - numerical computations
- scikit-learn - feature engineering, normalization
- Vowpal Wabbit (optional) - production bandit implementation
- Custom implementation - for learning purposes

### 5.2 Frontend

**Framework**: React 18+ with TypeScript
- Component-based architecture
- Type safety
- Modern hooks-based approach

**Styling**: Tailwind CSS
- Utility-first CSS
- Responsive design
- Fast development

**State Management**: React Context + hooks
- Simple state management
- No need for Redux initially

**UI Components**:
- Slider inputs (mood, energy, social, time)
- Activity cards with checkboxes
- Favorites pool display
- Responsive layout

### 5.3 Deployment

**Platform**: Railway
- Easy deployment
- PostgreSQL hosting
- Environment variable management
- Automatic HTTPS

**Containerization**: Docker
- Reproducible builds
- Easy local development
- Railway-compatible

---

## 6. API Design

### 6.1 Endpoints

**GET /api/activities**
- Returns all activities (for admin/debugging)
- Optional filters: tags, energy_level, social_level

**POST /api/session/start**
```json
Request:
{
  "context": {
    "mood": 7,
    "social": 5,
    "energy": 8,
    "time_available": 120,
    "weather": "sunny",
    "temperature": 18
  }
}

Response:
{
  "session_id": "uuid",
  "suggestions": [
    {
      "id": "uuid",
      "name": "Trail running",
      "energy_level": 8,
      "social_level": 2,
      "duration_min": 30,
      "duration_max": 120,
      "tags": ["outdoor", "physical", "nature"]
    },
    // ... 49 more
  ]
}
```

**POST /api/session/{session_id}/pick**
```json
Request:
{
  "picks": ["activity_id1", "activity_id2", "activity_id3"]
}

Response:
{
  "status": "picks_recorded",
  "accumulated_favorites": ["activity_id1", "activity_id2", "activity_id3"]
}
```

**POST /api/session/{session_id}/regenerate**
```json
Request:
{
  "picks": ["activity_id1", "activity_id2", "activity_id3"]
}

Response:
{
  "suggestions": [
    // ... 50 new suggestions influenced by picks
  ],
  "accumulated_favorites": ["activity_id1", ..., "activity_id6"]
}
```

**POST /api/session/{session_id}/complete**
```json
Request:
{
  "final_choice": "activity_id"
}

Response:
{
  "status": "session_complete",
  "learning_applied": true
}
```

### 6.2 Error Handling

- 400 Bad Request - Invalid input data
- 404 Not Found - Session/activity not found
- 500 Internal Server Error - Server error

---

## 7. Initial Activity Database

### 7.1 Activity Categories

**Physical Outdoor**:
- Hiking, Trail running, Cycling, Rock climbing, Kayaking, Swimming, 
  Beach volleyball, Soccer, Tennis, Frisbee, etc.

**Physical Indoor**:
- Gym workout, Yoga, Rock climbing (gym), Swimming (pool), 
  Dance class, Martial arts, etc.

**Creative**:
- Painting, Drawing, Writing, Photography, Music practice, 
  Crafting, Cooking, Baking, etc.

**Social**:
- Coffee with friends, Dinner party, Board games, Movie night, 
  Pub quiz, etc.

**Relaxing**:
- Reading, Meditation, Napping, Podcast listening, Netflix, 
  Bath, Massage, etc.

**Productive**:
- Work on project, Learn new skill, Organize space, Meal prep, 
  Finance planning, etc.

**Adventurous**:
- Try new restaurant, Explore new neighborhood, Day trip, 
  New hobby, etc.

### 7.2 Initial Dataset Size

Target: **100-200 activities** for MVP
- Provides enough variety
- Covers major activity types
- Allows for meaningful learning

---

## 8. Development Phases

### Phase 1: Core Backend (Week 1-2)
- [ ] Set up FastAPI project structure
- [ ] Design and implement database schema
- [ ] Create Activity model and CRUD operations
- [ ] Implement contextual bandit (simple version)
- [ ] Create API endpoints
- [ ] Populate initial activity database

### Phase 2: AI Implementation (Week 2-3)
- [ ] Implement base model (persistent learning)
- [ ] Implement session model (temporary learning)
- [ ] Feature extraction and normalization
- [ ] Recommendation algorithm with filtering
- [ ] Learning rate implementation (0.02 vs 0.8)
- [ ] Model persistence to database

### Phase 3: Frontend (Week 3-4)
- [ ] Set up React + TypeScript project
- [ ] Create slider components
- [ ] Activity card components
- [ ] Session flow implementation
- [ ] Favorites pool display
- [ ] API integration

### Phase 4: Integration & Testing (Week 4-5)
- [ ] Connect frontend to backend
- [ ] End-to-end testing
- [ ] Fix bugs and refine UX
- [ ] Add loading states and error handling
- [ ] Responsive design testing

### Phase 5: Deployment (Week 5-6)
- [ ] Docker containerization
- [ ] Railway deployment setup
- [ ] PostgreSQL setup on Railway
- [ ] Environment configuration
- [ ] Production testing

### Phase 6: Self-Training & Refinement (Week 6+)
- [ ] Use app daily for 2-4 weeks
- [ ] Train AI with real usage data
- [ ] Monitor learning progress
- [ ] Refine activity database
- [ ] Adjust learning rates if needed

---

## 9. Success Metrics

### 9.1 Technical Success
- [ ] AI learns preferences after 20-30 sessions
- [ ] Regeneration produces increasingly relevant suggestions
- [ ] One bad session doesn't break learned preferences
- [ ] System handles 100+ activities efficiently

### 9.2 User Experience Success
- [ ] Find desirable activity within 2-3 rounds
- [ ] Suggestions feel personalized after 20+ sessions
- [ ] Context changes (weather, mood) produce appropriate suggestions
- [ ] System is fast and responsive

### 9.3 Portfolio Value
- [ ] Demonstrates reinforcement learning skills
- [ ] Shows full-stack development capability
- [ ] Exhibits system design thinking
- [ ] Provides real-world problem-solving example

---

## 10. Future Enhancements

### 10.1 Feature Ideas
- Multi-user support (each user has their own AI)
- Social features (share activities with friends)
- Activity completion tracking and history
- Seasonal activity suggestions
- Location-based filtering
- Weather API integration
- Calendar integration
- Mobile app (React Native)
- Activity photos and ratings
- User-generated activities

### 10.2 AI Improvements
- Deep learning models (neural networks)
- More sophisticated exploration strategies
- Collaborative filtering (learn from similar users)
- Time-series patterns (weekly/seasonal preferences)
- Confidence scores for recommendations
- Explanation of why activities were suggested

---

## 11. Open Questions

### 11.1 To Decide During Development
- Exact learning rate values (0.02 and 0.8 are starting points)
- Number of suggestions per round (50 or different?)
- Exploration strategy (epsilon-greedy, UCB, Thompson sampling?)
- Feature engineering details (which activity/context interactions matter?)
- Database indexing strategy for performance
- Caching strategy for recommendations

### 11.2 To Test Through Usage
- How many sessions needed for good personalization? (estimate: 20-50)
- Does regeneration actually improve suggestions noticeably?
- Are 50 suggestions too many or too few?
- Should there be a "surprise me" mode with high exploration?

---

## 12. Notes

### 12.1 Design Decisions

**Why two-layer learning?**
- Fast session learning provides immediate value (good UX)
- Slow base learning provides robustness (good AI design)
- Separates "what I want today" from "what I generally like"

**Why contextual bandits over deep learning?**
- Works well with limited data (cold start)
- Interpretable (can understand why suggestions were made)
- Fast training and inference
- Demonstrates RL knowledge for portfolio

**Why regeneration over single round?**
- Allows exploration when nothing appeals
- Provides more training data for AI
- Better UX (user feels in control)
- Showcases iterative refinement

### 12.2 Potential Challenges

**Cold start**: Initial suggestions will be random
- Solution: Populate with reasonable defaults based on context
- User needs to train system through 20-50 sessions

**Activity database quality**: Tagging must be accurate
- Solution: Careful manual curation initially
- Future: Allow user feedback on activity attributes

**Learning rate tuning**: May need adjustment based on real usage
- Solution: Start with 0.02 and 0.8, monitor and adjust
- Could make configurable for experimentation

**Deployment costs**: Railway costs if traffic grows
- Solution: Optimize database queries, implement caching
- Consider moving to cheaper hosting if needed

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-04-1620 UTC  
**Next Review**: After Phase 1 completion

