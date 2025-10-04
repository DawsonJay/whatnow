# WhatNow Activity Schema

**Created**: 2025-10-04  
**Status**: Finalized for implementation

## Overview

This document defines the data structure for activities in the WhatNow recommendation system. The schema balances simplicity with flexibility, using core attributes for AI learning and flexible tags for extensibility.

## Database Schema (PostgreSQL)

```sql
CREATE TABLE activities (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Core attributes (1-10 scales)
    energy_physical FLOAT NOT NULL CHECK (energy_physical >= 0 AND energy_physical <= 10),
    energy_mental FLOAT NOT NULL CHECK (energy_mental >= 0 AND energy_mental <= 10),
    social_level FLOAT NOT NULL CHECK (social_level >= 0 AND social_level <= 10),
    
    -- Duration (minutes)
    duration_min INT NOT NULL CHECK (duration_min > 0),
    duration_max INT NOT NULL CHECK (duration_max >= duration_min),
    
    -- Location & Weather
    indoor BOOLEAN NOT NULL,
    outdoor BOOLEAN NOT NULL,  -- Some activities work for both
    weather_best JSONB DEFAULT '["sunny", "overcast"]'::jsonb,
    weather_avoid JSONB DEFAULT '[]'::jsonb,
    temperature_min FLOAT DEFAULT -10,  -- Celsius
    temperature_max FLOAT DEFAULT 40,
    
    -- Time preferences
    time_of_day JSONB DEFAULT '["morning", "afternoon", "evening", "night"]'::jsonb,
    
    -- Cost
    cost VARCHAR(20) CHECK (cost IN ('free', 'low', 'medium', 'high')),
    
    -- Category (main type)
    category VARCHAR(50) CHECK (category IN (
        'physical', 'creative', 'social', 'relaxing', 
        'productive', 'entertainment', 'learning', 'other'
    )),
    
    -- Flexible tags (this can grow infinitely)
    tags JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_activities_category ON activities(category);
CREATE INDEX idx_activities_tags ON activities USING GIN (tags);
CREATE INDEX idx_activities_energy ON activities(energy_physical, energy_mental);
```

## Field Definitions

### Core Attributes

**Energy Physical (0-10)**
- How physically demanding/tiring the activity is
- 0 = No physical effort (sleeping, meditation)
- 5 = Moderate effort (walking, casual cycling)
- 10 = Maximum effort (intense workout, rock climbing)

**Energy Mental (0-10)**
- How mentally demanding/draining the activity is
- 0 = No mental effort (napping, passive TV watching)
- 5 = Moderate focus (reading, cooking)
- 10 = High concentration (complex problem solving, learning new skill)

**Social Level (0-10)**
- How social the activity is
- 0 = Solo activity (reading alone, solo workout)
- 5 = Small group (coffee with 2-3 friends)
- 10 = Large group (party, team sports)

### Duration

**Duration Min/Max (minutes)**
- `duration_min`: Minimum time needed to do the activity
- `duration_max`: Maximum time the activity can reasonably extend to
- Example: Reading (min=15, max=240)
- Example: Movie (min=90, max=180)

### Location & Weather

**Indoor/Outdoor (boolean)**
- `indoor`: Can be done indoors
- `outdoor`: Can be done outdoors
- Both can be true (e.g., reading, meditation)
- Both can be false for online/virtual activities

**Weather Best (JSONB array)**
- Ideal weather conditions for this activity
- Values: `["sunny", "overcast", "partly_cloudy", "light_rain", "cloudy", "any"]`
- Example: Hiking = `["sunny", "overcast"]`
- Example: Reading = `["any"]`

**Weather Avoid (JSONB array)**
- Weather that prevents or ruins this activity
- Values: `["rain", "heavy_rain", "storm", "thunderstorm", "snow", "heavy_snow", "extreme_heat", "extreme_cold"]`
- Example: Hiking = `["rain", "storm", "snow"]`
- Example: Indoor yoga = `[]`

**Temperature Min/Max (Celsius)**
- Comfortable temperature range for this activity
- Example: Trail running (min=5, max=28)
- Example: Swimming outdoor (min=20, max=35)
- Example: Reading anywhere (min=10, max=35)

### Time Preferences

**Time of Day (JSONB array)**
- When this activity makes sense
- Values: `["morning", "afternoon", "evening", "night"]`
- Example: Gym workout = `["morning", "evening"]`
- Example: Reading = `["morning", "afternoon", "evening", "night"]`

### Cost

**Cost (enum)**
- Financial cost category
- Values: `"free"`, `"low"`, `"medium"`, `"high"`
- Example: Hiking = `"free"`
- Example: Coffee with friends = `"low"`
- Example: Rock climbing gym = `"medium"`
- Example: Spa day = `"high"`

### Category

**Category (enum)**
- Primary activity type for organization
- Values:
  - `physical`: Exercise, sports, active movement
  - `creative`: Arts, crafts, music, writing
  - `social`: Spending time with others
  - `relaxing`: Rest, calm activities
  - `productive`: Work, learning, organizing
  - `entertainment`: Movies, games, fun
  - `learning`: Education, skill development
  - `other`: Miscellaneous

### Tags (Flexible)

**Tags (JSONB array)**
- Free-form descriptors for additional categorization
- Can be added infinitely without schema changes
- Common tags:
  - **Activity type**: `outdoor`, `indoor`, `nature`, `urban`, `home`
  - **Intensity**: `intense`, `moderate`, `gentle`, `calm`
  - **Group size**: `solo`, `paired`, `small_group`, `large_group`
  - **Noise**: `quiet`, `loud`, `peaceful`
  - **Outcome**: `energizing`, `calming`, `fun`, `challenging`
  - **Skills**: `cardio`, `strength`, `flexibility`, `focus`, `creativity`
  - **Flexibility**: `flexible`, `structured`, `scheduled`

## Example Activities

### Trail Running
```json
{
    "name": "Trail Running",
    "description": "Run on nature trails",
    "energy_physical": 8.5,
    "energy_mental": 3.0,
    "social_level": 2.0,
    "duration_min": 30,
    "duration_max": 120,
    "indoor": false,
    "outdoor": true,
    "weather_best": ["sunny", "overcast"],
    "weather_avoid": ["rain", "storm", "snow"],
    "temperature_min": 5,
    "temperature_max": 28,
    "time_of_day": ["morning", "afternoon"],
    "cost": "free",
    "category": "physical",
    "tags": ["outdoor", "cardio", "nature", "solo"]
}
```

### Reading
```json
{
    "name": "Reading",
    "description": "Read a book or articles",
    "energy_physical": 1.0,
    "energy_mental": 5.0,
    "social_level": 0.0,
    "duration_min": 15,
    "duration_max": 240,
    "indoor": true,
    "outdoor": true,
    "weather_best": ["any"],
    "weather_avoid": [],
    "temperature_min": 10,
    "temperature_max": 35,
    "time_of_day": ["morning", "afternoon", "evening", "night"],
    "cost": "free",
    "category": "relaxing",
    "tags": ["quiet", "solo", "learning", "flexible"]
}
```

### Coffee with Friends
```json
{
    "name": "Coffee with Friends",
    "description": "Meet friends at a cafe",
    "energy_physical": 2.0,
    "energy_mental": 4.0,
    "social_level": 7.0,
    "duration_min": 45,
    "duration_max": 180,
    "indoor": true,
    "outdoor": true,
    "weather_best": ["any"],
    "weather_avoid": [],
    "temperature_min": 0,
    "temperature_max": 40,
    "time_of_day": ["morning", "afternoon", "evening"],
    "cost": "low",
    "category": "social",
    "tags": ["cafe", "conversation", "casual", "flexible"]
}
```

### Work on Personal Project
```json
{
    "name": "Work on Personal Project",
    "description": "Code, write, or work on a project",
    "energy_physical": 1.0,
    "energy_mental": 8.0,
    "social_level": 0.0,
    "duration_min": 30,
    "duration_max": 240,
    "indoor": true,
    "outdoor": false,
    "weather_best": ["any"],
    "weather_avoid": [],
    "temperature_min": 15,
    "temperature_max": 30,
    "time_of_day": ["morning", "afternoon", "evening", "night"],
    "cost": "free",
    "category": "productive",
    "tags": ["focus", "solo", "creative", "learning", "flexible"]
}
```

## Design Principles

### 1. Simplicity First
- Core attributes cover the essentials
- No over-engineering
- Easy to understand and populate

### 2. Flexibility Through Tags
- Tags can grow infinitely
- No schema changes needed for new descriptors
- AI can learn patterns in tags over time

### 3. AI-Ready
- All numeric fields (energy, social, duration) are on clear scales
- Easy to create feature vectors for contextual bandit
- Weather and time data structured for filtering

### 4. Human-Friendly
- Clear field names and values
- Intuitive scales (0-10)
- Easy to curate activity database

### 5. Future-Proof
- JSONB fields (weather_best, weather_avoid, time_of_day, tags) can expand
- Core attributes remain stable
- Can add new tags without breaking existing activities

## Validation Rules

```python
def validate_activity(activity):
    # Required fields
    assert activity.name, "Activity name required"
    assert 0 <= activity.energy_physical <= 10, "Physical energy must be 0-10"
    assert 0 <= activity.energy_mental <= 10, "Mental energy must be 0-10"
    assert 0 <= activity.social_level <= 10, "Social level must be 0-10"
    
    # Duration
    assert activity.duration_min > 0, "Duration must be positive"
    assert activity.duration_max >= activity.duration_min, "Max duration >= min duration"
    
    # Location
    assert activity.indoor or activity.outdoor, "Must be indoor, outdoor, or both"
    
    # Temperature
    assert activity.temperature_min < activity.temperature_max, "Invalid temperature range"
    
    # Cost
    assert activity.cost in ['free', 'low', 'medium', 'high'], "Invalid cost category"
    
    # Category
    valid_categories = ['physical', 'creative', 'social', 'relaxing', 
                       'productive', 'entertainment', 'learning', 'other']
    assert activity.category in valid_categories, "Invalid category"
```

## Initial Database Population

**Target**: 100-150 activities for MVP

**Categories to cover**:
- Physical Outdoor (20-25): Hiking, running, cycling, sports, etc.
- Physical Indoor (15-20): Gym, yoga, dance, martial arts, etc.
- Creative (15-20): Painting, writing, music, cooking, crafting, etc.
- Social (15-20): Coffee, dinner, games, events, etc.
- Relaxing (15-20): Reading, meditation, Netflix, bath, etc.
- Productive (15-20): Projects, learning, organizing, planning, etc.
- Entertainment (10-15): Movies, games, browsing, etc.

## Notes

- Weather values can be extended in the future (add "foggy", "windy", etc.)
- Time of day can be made more granular if needed (add "late_night", "dawn", etc.)
- Tags are the main expansion point - add new ones as patterns emerge
- Keep core attributes stable - these are what the AI learns from

---

**Status**: Ready for implementation  
**Next Steps**: Begin populating initial activity database

