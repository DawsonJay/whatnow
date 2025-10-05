# WhatNow AI

**An AI-powered activity recommendation system with semantic embeddings and two-layer learning.**

## Overview

WhatNow uses AI to help you discover activities that match your current mood and context. The system learns your preferences through a two-layer AI architecture and provides personalized recommendations using semantic embeddings.

## Core Features

### 🧠 Two-Layer AI Learning System

**Base AI (Backend) - Slow Learning**
- Learns general patterns across all users (learning rate: 0.01)
- Uses SGDClassifier for online learning
- Stores model weights in database for persistence
- Gets smarter with every user interaction

**Session AI (Frontend) - Fast Learning**
- Learns individual user preferences quickly (learning rate: 0.3)
- JavaScript-based SGDClassifier
- Resets each session, starts as clone of Base AI
- Adapts to user's current session preferences

### 🎯 Semantic Activity Matching
- Uses sentence embeddings (all-MiniLM-L6-v2) for activity understanding
- Activities matched by semantic similarity, not manual metadata
- Context tags (mood, energy, weather) combined with embeddings
- AI learns which activities users prefer in different contexts

### 📊 Context-Aware Recommendations
- Users select mood/context tags instead of sliders
- AI finds semantically similar activities
- Learns user preferences for different tag combinations
- Adapts to weather, time, energy, and social context

## How It Works

1. **Select Context Tags**: Choose mood tags (chill, energetic, focused) and context (indoor, outdoor, rainy, etc.)
2. **Backend Ranking**: Base AI uses embeddings to find similar activities, returns top 100 candidates
3. **Frontend Re-ranking**: Session AI re-ranks based on your individual preferences
4. **Compare Activities**: System shows 2 activities for you to choose between
5. **AI Learning**: Both AIs learn from your choice and get better at recommendations
6. **Repeat**: Continue comparing until you find the perfect activity

## Technology Stack

### Backend
- **Python** - backend language
- **FastAPI** - REST API framework
- **PostgreSQL** - database for activities and embeddings
- **SQLAlchemy** - ORM
- **sentence-transformers** - embedding generation (local only)

### AI/ML
- **Sentence Embeddings** - semantic activity understanding
- **SGDClassifier** - online learning for both AIs
- **Two-layer architecture** - Base AI (persistent) + Session AI (temporary)

### Frontend (Planned)
- **JavaScript** - Session AI implementation
- **Modern UI** - tag-based interface instead of sliders
- **Real-time learning** - AI updates after each comparison

### Deployment
- **Railway** - hosting platform
- **Fast deployments** - no heavy AI dependencies in production

## Project Status

**Status**: Phase 1 Complete - AI Infrastructure Ready  
**Created**: 2025-10-04  
**Current Phase**: Backend API deployed with AI-ready infrastructure

## Development Roadmap

- [x] Complete technical specification
- [x] Design AI-focused database schema
- [x] Build FastAPI backend with organized structure
- [x] Deploy to Railway with fast deployments
- [x] Create local embedding generation system
- [ ] Implement Base AI with online learning
- [ ] Create Session AI in JavaScript frontend
- [ ] Build tag-based UI interface
- [ ] End-to-end testing and optimization

## Phase 1 Achievements

### ✅ **AI Infrastructure**
- **Simplified database schema** (id, name, embedding) for AI system
- **FastAPI backend** with organized endpoint structure
- **Railway deployment** at https://whatnow-production.up.railway.app
- **Fast deployments** (2-3 minutes) without heavy AI dependencies

### ✅ **API Endpoints**
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `DELETE /activities/clear` - Clear all activities
- `POST /activities/bulk-upload` - Upload activities with pre-computed embeddings
- `GET /activities/` - List activities with pagination

### ✅ **Local Development Tools**
- **Embedding generation script** for all 1250 activities
- **Upload script** for Railway database population
- **Organized code structure** with endpoints/ and utils/ directories

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

