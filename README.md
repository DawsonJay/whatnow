# WhatNow

**An AI-powered activity recommendation system that learns your preferences over time.**

## Overview

WhatNow helps you decide what to do when you're feeling indecisive. Set your current mood, energy level, social preference, available time, and weather conditions, and WhatNow suggests activities tailored to your preferences. The AI learns from your choices and gets better at predicting what you'll enjoy.

## Core Features

### 🎯 Smart Recommendations
- Input your current state using intuitive sliders (mood, energy, social, time)
- Get 50 personalized activity suggestions
- AI highlights top recommendations based on learned preferences

### 🔄 Iterative Refinement
- Pick your top 3 favorite activities from suggestions
- Regenerate for 50 new suggestions if needed
- Previous favorites accumulate across rounds
- Keep refining until you find the perfect activity

### 🧠 Two-Layer AI Learning System

**Within-Session Learning (Fast)**
- Temporary AI copy learns aggressively during your session (learning rate: 0.8)
- Each regeneration produces better suggestions based on your picks
- Helps you quickly zero in on what you want right now
- Resets after session ends

**Cross-Session Learning (Slow)**
- Persistent base AI learns gradually from all sessions (learning rate: 0.02)
- Builds long-term understanding of your preferences
- Robust to outliers - one bad session won't break it
- Gets smarter with every session

### 📊 Context-Aware Learning
- Learns different preferences for different contexts
- Understands "I like hiking when sunny and energetic, but Netflix when rainy and tired"
- Adapts to weather, time of day, season, and your current state

## How It Works

1. **Set Your Context**: Use sliders to indicate mood, social desire, energy, time available, and weather
2. **Get Suggestions**: AI generates 50 activity suggestions based on your context and learned preferences
3. **Pick Top 3**: Select your favorite activities from the suggestions
4. **Refine (Optional)**: Click regenerate for new suggestions influenced by your picks
5. **Repeat**: Keep refining until satisfied, accumulating favorites across rounds
6. **Choose & Do**: Pick one activity from your accumulated favorites to actually do
7. **AI Learns**: System learns from your choices to improve future suggestions

## Technology Stack

### Frontend
- **React** - UI framework
- **TypeScript** - type safety
- **Tailwind CSS** - styling
- **React DnD** (optional) - drag and drop interactions

### Backend
- **Python** - backend language
- **FastAPI** - REST API framework
- **PostgreSQL** - database for activities and user data
- **SQLAlchemy** - ORM

### AI/ML
- **Contextual Bandits** - recommendation algorithm
- **Reinforcement Learning** - continuous learning approach
- **Custom implementation** or **Vowpal Wabbit** - bandit library

### Deployment
- **Railway** - hosting platform
- **Docker** - containerization

## Project Status

**Status**: Planning Phase  
**Created**: 2025-10-04  
**Current Phase**: Specification and architecture design

## Development Roadmap

- [ ] Complete technical specification
- [ ] Design database schema
- [ ] Implement contextual bandit AI
- [ ] Build backend API
- [ ] Create frontend UI
- [ ] Implement two-layer learning system
- [ ] Add activity database with tagging system
- [ ] Deploy to Railway
- [ ] User testing and refinement

## Why WhatNow?

### Problem It Solves
- **Decision fatigue**: Too many choices, hard to decide
- **Mood mismatch**: Doing activities that don't fit your current state
- **Wasted time**: Scrolling through options without deciding

### Unique Value
- **Learns YOU**: Personalized to your specific preferences
- **Context-aware**: Adapts to your current mood and situation
- **Gets better**: Improves with every use
- **Fast refinement**: Quickly narrows down to what you want

## Portfolio Value

### AI/ML Skills Demonstrated
- Reinforcement learning (contextual bandits)
- Two-layer learning architecture
- Real-time model adaptation
- Long-term preference learning
- Context-aware recommendations

### Software Engineering Skills
- Full-stack web development
- REST API design
- Database design and optimization
- User experience design
- Deployment and hosting

### Problem-Solving
- Handles cold-start problem
- Robust to outlier sessions
- Balances exploration vs exploitation
- Adapts to changing user preferences

## License

TBD

## Contact

James - Portfolio Project

---

**WhatNow** - Because deciding what to do shouldn't be harder than actually doing it.

