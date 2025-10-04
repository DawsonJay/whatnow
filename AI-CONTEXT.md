# AI Context - WhatNow Project

## For New AI Assistants

When you first start working on this project, please follow these steps in order:

### 1. Read This Project's README
- **File**: `README.md` (in this directory)
- **Purpose**: Understand the WhatNow project overview, technical architecture, and goals
- **Key Points**: AI-powered activity recommendation system with two-layer learning, contextual bandits, 6-phase development plan

### 2. Read Technical Specification
- **File**: `SPECIFICATION.md` (in this directory)
- **Purpose**: Understand detailed technical implementation, database schema, AI architecture, and API design
- **Key Points**: Two-layer learning system (fast session + slow base), contextual bandits, FastAPI + PostgreSQL + React stack

### 3. Read and Apply Behaviors File
- **File**: `/home/james/Documents/portfolio-profile/behaviors.md`
- **Purpose**: Apply consistent behaviors and approaches throughout the session
- **Critical**: This file defines how to work with the portfolio-profile project system

### 4. Read Portfolio-Profile README
- **File**: `/home/james/Documents/portfolio-profile/README.md`
- **Purpose**: Understand the broader portfolio project context and structure
- **Key Points**: Canadian immigration goals, portfolio strategy, file organization

### 5. Read Chat Records for Context
- **Directory**: `/home/james/Documents/portfolio-profile/records/whatnow/`
- **Purpose**: Understand previous work, decisions made, and current project state
- **Files to read**: **Read the most recent 5-10 chat records** to get current project state
- **Note**: Always check for the most recent records first to understand current project state

### 6. Read Key Definitions (if needed)
- **Chat Context**: `/home/james/Documents/portfolio-profile/definitions/chat-context-definition.md`
- **Chat Records**: `/home/james/Documents/portfolio-profile/definitions/chat-record-definition.md`
- **Purpose**: Understand the capture system and documentation approach

## Project Status
- **Current Phase**: **Phase 1 Complete** - Backend API and Database Ready
- **Created**: 2025-10-04
- **Status**: ✅ Database populated, ✅ API deployed, ✅ 100% filtering system working
- **Next Phase**: Phase 2 - AI Implementation (Contextual Bandits)
- **Target Completion**: 6 weeks total development

## Key Behaviors to Remember
- Always use GMT/UTC timezone for timestamps (format: YYYY-MM-DD-HHMM)
- Discussion before coding - achieve full understanding before implementing
- Portfolio focus - consider what would be good for the portfolio
- Follow portfolio-profile project structure when creating files
- Ask about capture system after important moments
- Always include chat context when creating records
- **CRITICAL: NEVER commit or push to git without explicit user permission**

## WhatNow Project Overview
**WhatNow** is an AI-powered activity recommendation system that helps users decide what to do when they're feeling indecisive. It uses contextual bandits (reinforcement learning) with a unique two-layer learning system:

### Core Innovation
- **Fast within-session learning** (learning rate: 0.8) for immediate refinement
- **Slow cross-session learning** (learning rate: 0.02) for long-term preference building
- **Context-aware recommendations** based on mood, energy, social preference, time, and weather

### Technical Stack
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **Frontend**: React 18+ + TypeScript + Tailwind CSS
- **AI/ML**: Contextual bandits, reinforcement learning
- **Deployment**: Railway + Docker

### User Flow
1. Set context via sliders (mood, energy, social, time, weather)
2. Get 50 personalized activity suggestions
3. Pick top 3 favorites
4. Optionally regenerate for new suggestions influenced by picks
5. Accumulate favorites across rounds
6. Choose one final activity to do
7. AI learns from the session

## Portfolio Context
This project is part of a larger portfolio strategy for Canadian immigration (Express Entry by Jan 2026). The WhatNow project demonstrates:
- **AI/ML Skills**: Reinforcement learning, contextual bandits, two-layer learning architecture
- **Software Engineering**: Full-stack development, REST API design, database design
- **Problem-Solving**: Cold-start handling, exploration vs exploitation balance

## Current Development Plan
- **Phase 1**: ✅ Core Backend (Week 1-2) - FastAPI, database schema, comprehensive filtering
- **Phase 2**: AI Implementation (Week 2-3) - Two-layer learning system, contextual bandits
- **Phase 3**: Frontend (Week 3-4) - React UI with sliders and activity cards
- **Phase 4**: Integration & Testing (Week 4-5) - End-to-end testing
- **Phase 5**: Deployment (Week 5-6) - Railway deployment (already deployed!)
- **Phase 6**: Self-Training (Week 6+) - Real usage and AI training

## Phase 1 Achievements
- ✅ **Database Schema**: PostgreSQL with 72 production-ready activities
- ✅ **API Endpoints**: Full CRUD operations with comprehensive filtering
- ✅ **Filtering System**: 100% working - category, energy, duration, location, weather, time, tags, search
- ✅ **Railway Deployment**: Live API at https://whatnow-production.up.railway.app
- ✅ **Documentation**: Complete API filtering guide and technical specs

## Success Metrics
- AI learns preferences after 20-30 sessions
- Regeneration produces increasingly relevant suggestions
- One bad session doesn't break learned preferences
- Find desirable activity within 2-3 rounds
- Suggestions feel personalized after 20+ sessions

---
*This file was created on 2025-10-04-1620 and last updated on 2025-10-04-1620 to help new AI assistants quickly understand the WhatNow project context and get up to speed.*
