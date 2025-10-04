# WhatNow API - Comprehensive Filtering Guide

## 🎯 **Enhanced Activities Endpoint**

The `/activities` endpoint now supports comprehensive filtering across all activity attributes.

## 📋 **Available Filters**

### **Basic Filters**
- `category` - Filter by activity category
- `cost` - Filter by cost level (free, low, medium, high)

### **Energy Filters** (0-10 scale)
- `energy_physical_min` - Minimum physical energy required
- `energy_physical_max` - Maximum physical energy required
- `energy_mental_min` - Minimum mental energy required
- `energy_mental_max` - Maximum mental energy required
- `social_level_min` - Minimum social interaction level
- `social_level_max` - Maximum social interaction level

### **Duration Filters** (minutes)
- `duration_min` - Minimum activity duration
- `duration_max` - Maximum activity duration

### **Location Filters**
- `indoor` - Activities that can be done indoors (true/false)
- `outdoor` - Activities that can be done outdoors (true/false)

### **Weather Filters**
- `weather` - Filter by weather condition (sunny, rainy, overcast, etc.)
- `temperature_min` - Minimum temperature (°C)
- `temperature_max` - Maximum temperature (°C)

### **Time Filters**
- `time_of_day` - Filter by time preference (morning, afternoon, evening, night)

### **Tag Filters**
- `tag` - Filter by specific activity tags

### **Search**
- `search` - Text search in activity names and descriptions

## 🔍 **Filter Examples**

### **Basic Category Filtering**
```
GET /activities?category=physical
GET /activities?category=creative
GET /activities?category=social
```

### **Energy Level Filtering**
```
GET /activities?energy_physical_min=5&energy_physical_max=8
GET /activities?social_level_max=3
GET /activities?energy_mental_min=6
```

### **Duration Filtering**
```
GET /activities?duration_max=60
GET /activities?duration_min=30&duration_max=120
```

### **Location Filtering**
```
GET /activities?indoor=true
GET /activities?outdoor=true
GET /activities?indoor=true&outdoor=false
```

### **Weather Filtering**
```
GET /activities?weather=sunny
GET /activities?weather=rainy
GET /activities?temperature_min=20&temperature_max=30
```

### **Time of Day Filtering**
```
GET /activities?time_of_day=morning
GET /activities?time_of_day=evening
```

### **Tag Filtering**
```
GET /activities?tag=cardio
GET /activities?tag=social
GET /activities?tag=creative
```

### **Search Filtering**
```
GET /activities?search=yoga
GET /activities?search=music
GET /activities?search=outdoor
```

### **Complex Combinations**
```
GET /activities?category=physical&energy_physical_min=5&indoor=true&duration_max=60
GET /activities?social_level_min=5&weather=sunny&time_of_day=afternoon
GET /activities?cost=free&tag=exercise&search=cardio
```

## 🎯 **Use Cases for AI Contextual Filtering**

### **User Context Examples**

**"I'm tired and want something relaxing indoors"**
```
GET /activities?energy_physical_max=3&indoor=true&category=relaxing
```

**"I want to be social but not too energetic"**
```
GET /activities?social_level_min=5&energy_physical_max=5&category=social
```

**"It's raining and I have 30 minutes"**
```
GET /activities?weather=rainy&duration_max=30&indoor=true
```

**"I want something creative in the evening"**
```
GET /activities?category=creative&time_of_day=evening&indoor=true
```

**"I want free outdoor activities for sunny weather"**
```
GET /activities?cost=free&outdoor=true&weather=sunny
```

## 🚀 **Perfect for AI Integration**

This comprehensive filtering system provides the foundation for:

1. **Contextual Bandit AI** - Filter activities based on user context
2. **Smart Recommendations** - Combine multiple filters for personalized results
3. **Weather Integration** - Filter by current weather conditions
4. **Time-based Suggestions** - Filter by time of day and available time
5. **Energy Matching** - Match activities to user's current energy level
6. **Social Preferences** - Filter by desired social interaction level

## 📊 **Current Database Status**

- **72 Activities** across 7 categories
- **All filter attributes** populated with realistic values
- **JSON fields** for flexible weather, time, and tag filtering
- **Ready for AI integration** with comprehensive contextual data

The enhanced filtering system provides everything needed for the AI-powered recommendation engine!
