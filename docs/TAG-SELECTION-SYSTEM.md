# Tag Selection System Design

**Date:** 2025-10-05  
**Status:** Design Complete - Ready for Implementation  
**Phase:** 2 - Base AI Implementation

## Overview

The tag selection system provides users with an intuitive way to describe their current context (mood, environment, preferences) to receive AI-powered activity recommendations. The system uses grouped tags with smart contradiction prevention and flexible selection limits.

## Design Principles

1. **Grouped Organization** - Tags organized by category for easy discovery
2. **Exclusive Within Groups** - Can only select one tag per group (e.g., not both "sunny" and "rainy")
3. **Flexible Selection** - Minimum 3 tags, maximum 8 tags
4. **Contradiction Prevention** - Auto-disable conflicting tags
5. **User-Friendly** - Clear visual feedback and intuitive interaction

## Tag Groups

### 1. Mood Tags
```javascript
"mood": ["arty", "chill", "energetic", "creative", "relaxed", "social", "introverted"]
```
- **Purpose:** Capture user's emotional state and vibe
- **Selection:** Can select multiple mood tags
- **Examples:** "arty", "chill", "energetic"

### 2. Weather Tags
```javascript
"weather": ["sunny", "rainy", "cloudy", "snowy", "windy"]
```
- **Purpose:** Current weather conditions
- **Selection:** Exclusive (can only pick one)
- **Examples:** "sunny", "rainy", "cloudy"

### 3. Time Tags
```javascript
"time": ["morning", "afternoon", "evening", "night", "weekend", "weekday"]
```
- **Purpose:** Time of day and day type
- **Selection:** Exclusive (can only pick one)
- **Examples:** "morning", "evening", "weekend"

### 4. Location Tags
```javascript
"location": ["indoor", "outdoor", "home", "cafe", "park", "beach"]
```
- **Purpose:** Physical location and setting
- **Selection:** Exclusive (can only pick one)
- **Examples:** "indoor", "outdoor", "home"

### 5. Social Tags
```javascript
"social": ["alone", "with_friends", "with_family", "with_partner", "group_activity"]
```
- **Purpose:** Social context and company
- **Selection:** Exclusive (can only pick one)
- **Examples:** "alone", "with_friends", "with_family"

### 6. Energy Tags
```javascript
"energy": ["low_energy", "medium_energy", "high_energy"]
```
- **Purpose:** Energy level and activity intensity
- **Selection:** Exclusive (can only pick one)
- **Examples:** "low_energy", "high_energy"

### 7. Activity Type Tags
```javascript
"activity_type": ["physical", "mental", "artistic", "social", "learning", "entertainment"]
```
- **Purpose:** Type of activity preferred
- **Selection:** Exclusive (can only pick one)
- **Examples:** "physical", "artistic", "learning"

## Tag Contradictions

The system automatically prevents contradictory tag combinations:

```javascript
TAG_CONTRADICTIONS = {
    // Mood contradictions
    "quiet": ["loud", "energetic", "social"],
    "loud": ["quiet", "chill", "relaxed"],
    
    // Location contradictions
    "indoor": ["outdoor"],
    "outdoor": ["indoor"],
    
    // Social contradictions
    "alone": ["with_friends", "with_family", "with_partner", "group_activity"],
    "with_friends": ["alone"],
    "with_family": ["alone"],
    "with_partner": ["alone"],
    "group_activity": ["alone"],
    
    // Time contradictions
    "morning": ["evening", "night"],
    "evening": ["morning", "afternoon"],
    "night": ["morning", "afternoon"],
    
    // Weather contradictions
    "sunny": ["rainy", "cloudy", "snowy"],
    "rainy": ["sunny", "cloudy", "snowy"],
    "cloudy": ["sunny", "rainy", "snowy"],
    "snowy": ["sunny", "rainy", "cloudy"]
}
```

## Selection Rules

### Minimum Requirements
- **Minimum 3 tags** - Ensures meaningful context
- **No contradictions** - Cannot select conflicting tags
- **At least 2 different categories** - Prevents all tags from same group

### Maximum Limits
- **Maximum 8 tags** - Prevents overfitting and overwhelming context
- **One per group** - Within exclusive groups (weather, time, location, etc.)
- **Multiple mood tags allowed** - Mood is the only group allowing multiple selections

## User Interface Design

### Layout Structure
```
Tag Selector
├── Header: "Select your context (3-8 tags)"
├── Tag Groups (7 sections)
│   ├── Mood (multiple selection allowed)
│   ├── Weather (exclusive)
│   ├── Time (exclusive)
│   ├── Location (exclusive)
│   ├── Social (exclusive)
│   ├── Energy (exclusive)
│   └── Activity Type (exclusive)
└── Controls
    ├── Counter: "3/8"
    └── Submit Button: "Start Game"
```

### Visual States

#### Tag Button States
```css
/* Default state */
.tag-button {
    padding: 8px 16px;
    margin: 4px;
    border: 2px solid #ddd;
    border-radius: 20px;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
}

/* Selected state */
.tag-button.selected {
    background: #007bff;
    color: white;
    border-color: #007bff;
}

/* Disabled state */
.tag-button.disabled {
    background: #f8f9fa;
    color: #6c757d;
    border-color: #dee2e6;
    cursor: not-allowed;
    opacity: 0.5;
}

/* Hover state (only for enabled buttons) */
.tag-button:not(.disabled):hover {
    border-color: #007bff;
    background: #e3f2fd;
}
```

## JavaScript Implementation

### Core Tag Selector Class
```javascript
class TagSelector {
    constructor() {
        this.selectedTags = new Set();
        this.maxTags = 8;
        this.minTags = 3;
        this.tagGroups = {
            mood: ["arty", "chill", "energetic", "creative", "relaxed", "social", "introverted"],
            weather: ["sunny", "rainy", "cloudy", "snowy", "windy"],
            time: ["morning", "afternoon", "evening", "night", "weekend", "weekday"],
            location: ["indoor", "outdoor", "home", "cafe", "park", "beach"],
            social: ["alone", "with_friends", "with_family", "with_partner", "group_activity"],
            energy: ["low_energy", "medium_energy", "high_energy"],
            activity_type: ["physical", "mental", "artistic", "social", "learning", "entertainment"]
        };
        this.contradictions = {
            "quiet": ["loud", "energetic", "social"],
            "loud": ["quiet", "chill", "relaxed"],
            "indoor": ["outdoor"],
            "outdoor": ["indoor"],
            "alone": ["with_friends", "with_family", "with_partner", "group_activity"],
            "with_friends": ["alone"],
            "with_family": ["alone"],
            "with_partner": ["alone"],
            "group_activity": ["alone"],
            "morning": ["evening", "night"],
            "evening": ["morning", "afternoon"],
            "night": ["morning", "afternoon"],
            "sunny": ["rainy", "cloudy", "snowy"],
            "rainy": ["sunny", "cloudy", "snowy"],
            "cloudy": ["sunny", "rainy", "snowy"],
            "snowy": ["sunny", "rainy", "cloudy"]
        };
    }
    
    toggleTag(tag) {
        if (this.selectedTags.has(tag)) {
            // Unselect tag
            this.selectedTags.delete(tag);
        } else if (this.selectedTags.size < this.maxTags) {
            // Select tag (if under limit)
            this.selectedTags.add(tag);
        }
        
        this.updateUI();
    }
    
    isTagDisabled(tag) {
        // Check if tag is already selected
        if (this.selectedTags.has(tag)) return false;
        
        // Check if we're at max tags
        if (this.selectedTags.size >= this.maxTags) return true;
        
        // Check for contradictions with selected tags
        for (let selectedTag of this.selectedTags) {
            if (this.contradictions[selectedTag]?.includes(tag)) {
                return true;
            }
            if (this.contradictions[tag]?.includes(selectedTag)) {
                return true;
            }
        }
        
        return false;
    }
    
    updateUI() {
        // Update all tag buttons
        document.querySelectorAll('.tag-button').forEach(button => {
            const tag = button.dataset.tag;
            const isSelected = this.selectedTags.has(tag);
            const isDisabled = this.isTagDisabled(tag);
            
            button.classList.toggle('selected', isSelected);
            button.classList.toggle('disabled', isDisabled);
            button.disabled = isDisabled;
        });
        
        // Update submit button
        const submitButton = document.getElementById('submit-tags');
        submitButton.disabled = this.selectedTags.size < this.minTags;
        
        // Update counter
        document.getElementById('tag-counter').textContent = 
            `${this.selectedTags.size}/${this.maxTags}`;
    }
    
    getSelectedTags() {
        return Array.from(this.selectedTags);
    }
}
```

## Backend Validation

### Python Validation Function
```python
def validate_context_tags(tags):
    """Validate tag selection with contradictions and limits"""
    
    # Check minimum tags
    if len(tags) < 3:
        return False, "Please select at least 3 context tags"
    
    # Check maximum tags
    if len(tags) > 8:
        return False, "Please select no more than 8 context tags"
    
    # Check for contradictions
    contradictions = {
        "quiet": ["loud", "energetic", "social"],
        "loud": ["quiet", "chill", "relaxed"],
        "indoor": ["outdoor"],
        "outdoor": ["indoor"],
        "alone": ["with_friends", "with_family", "with_partner", "group_activity"],
        "with_friends": ["alone"],
        "with_family": ["alone"],
        "with_partner": ["alone"],
        "group_activity": ["alone"],
        "morning": ["evening", "night"],
        "evening": ["morning", "afternoon"],
        "night": ["morning", "afternoon"],
        "sunny": ["rainy", "cloudy", "snowy"],
        "rainy": ["sunny", "cloudy", "snowy"],
        "cloudy": ["sunny", "rainy", "snowy"],
        "snowy": ["sunny", "rainy", "cloudy"]
    }
    
    for tag in tags:
        if tag in contradictions:
            conflicting_tags = contradictions[tag]
            for conflicting_tag in conflicting_tags:
                if conflicting_tag in tags:
                    return False, f"'{tag}' and '{conflicting_tag}' cannot be selected together"
    
    return True, "Valid tag selection"
```

## User Experience Flow

1. **User sees grouped tags** - Easy to find what they want
2. **Clicks tags** - Only non-contradictory tags are enabled
3. **Visual feedback** - Selected tags highlighted, disabled tags grayed out
4. **Counter shows** - "3/8" tags selected
5. **Submit button** - Only enabled when 3+ tags selected
6. **At 8 tags** - All unselected tags become disabled
7. **Can unselect** - Click selected tag to remove it and enable others

## Example Valid Selections

### Minimal Context (3 tags)
```javascript
["arty", "indoor", "evening"]  // Mood + location + time
["chill", "outdoor", "sunny"]  // Mood + location + weather
["energetic", "morning", "alone"]  // Mood + time + social
```

### Rich Context (6-8 tags)
```javascript
["arty", "chill", "indoor", "evening", "alone", "low_energy", "artistic"]  // 7 tags
["energetic", "outdoor", "morning", "sunny", "with_friends", "high_energy", "physical"]  // 7 tags
```

### Invalid Selections
```javascript
["indoor", "outdoor"]  // ❌ Contradictory locations
["morning", "evening"]  // ❌ Contradictory times
["arty", "chill"]  // ❌ Too few tags (only 2)
["arty", "chill", "creative", "artistic", "relaxed", "mindful", "peaceful", "calm", "cozy"]  // ❌ Too many tags (9)
```

## Integration with AI System

### Context Vector Encoding
```python
def encode_context(tags):
    """Convert selected tags to 40-dimensional context vector"""
    context_vector = np.zeros(40)  # 40 total tags across all groups
    
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
        "physical": 32, "mental": 33, "artistic": 34, "social": 35, "learning": 36, "entertainment": 37
    }
    
    for tag in tags:
        if tag in tag_to_index:
            context_vector[tag_to_index[tag]] = 1.0
    
    return context_vector
```

## Next Steps

1. **Implement frontend tag selector** with JavaScript
2. **Create tag selection UI** with grouped layout
3. **Add contradiction prevention** logic
4. **Integrate with Base AI** recommendation system
5. **Test user experience** with various tag combinations

## Files to Create

- `frontend/js/tag-selector.js` - Tag selection logic
- `frontend/css/tag-selector.css` - Tag selection styles
- `frontend/html/tag-selector.html` - Tag selection markup
- `backend/utils/tag_validation.py` - Backend validation
- `backend/utils/context_encoding.py` - Context vector encoding

---

**Status:** Design Complete ✅  
**Ready for:** Frontend Implementation  
**Next Phase:** Base AI Integration
