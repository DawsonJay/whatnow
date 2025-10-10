# WhatNow - AI-Powered Activity Recommendations

A clean, modern web application that provides personalized activity recommendations using a two-layer AI learning system with semantic embeddings.

## Project Structure

```
whatnow-clean/
├── backend/          # FastAPI backend (deployed to Railway)
│   ├── main.py       # FastAPI application entry point
│   ├── requirements.txt
│   ├── railway.json  # Railway deployment config
│   ├── endpoints/    # API route handlers
│   ├── utils/        # Backend utilities (AI, database, embeddings)
│   ├── data/         # Activity data with embeddings
│   └── scripts/      # Utility scripts for data management
└── frontend/         # React frontend (Vite + TypeScript + Tailwind)
    ├── src/
    │   ├── pages/    # TagSelector, GamePage
    │   ├── components/ # Reusable UI components
    │   ├── hooks/    # Custom React hooks
    │   └── types.ts  # TypeScript type definitions
    └── package.json
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database (Railway hosted)
- **SQLAlchemy** - ORM
- **scikit-learn** - Machine learning (SGDClassifier)
- **sentence-transformers** - Semantic embeddings
- **Railway** - Cloud deployment platform

### Frontend
- **React** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool (fast, modern)
- **React Router** - Navigation and URL state management
- **Tailwind CSS** - Utility-first styling
- **Native Fetch API** - HTTP requests

## Features

### Tag-Based Selection System
- 5 tag groups: Weather, Time, Season, Intensity, Mood
- Minimum 3 tags, maximum 8 tags total
- Exclusive selection for most groups, multiple for Mood
- URL-based state management for bookmarkable recommendations

### Comparison Game Flow
- Side-by-side activity comparison
- Infinite game loop with pool management
- Real-time AI training after each choice
- Automatic fetching of more recommendations

### Two-Layer AI Learning
- **Base AI**: Slow, persistent learning (backend)
  - SGDClassifier with log loss
  - Trains on every user choice
  - Stored in PostgreSQL
- **Session AI**: Fast, temporary learning (frontend)
  - Initializes from Base AI weights
  - Learning rate: 0.3
  - Resets each session

## Development Setup

### Backend (Local)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

### Frontend (Local)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## Deployment

### Backend Deployment (Railway)
Backend is already deployed to Railway at:
`https://whatnow-production.up.railway.app`

To redeploy backend changes:
1. Commit changes to git
2. Push to Railway-connected repository
3. Railway auto-deploys on push

### Frontend Deployment (Future)
Frontend will be deployed as a static site to Railway or Vercel.

Build command: `npm run build`
Output directory: `dist/`

## API Endpoints

### `POST /activities/game/start`
Start a new game session with context tags.

**Request Body:**
```json
["sunny", "morning", "chill", "curious", "happy"]
```

**Response:**
```json
{
  "session_id": "uuid",
  "recommendations": [
    {"id": 1, "name": "Go for a morning walk"},
    {"id": 2, "name": "Read a book in the park"}
  ],
  "base_ai_weights": {
    "coefficients": [...],
    "intercept": [...],
    "classes": [...],
    "is_fitted": true
  }
}
```

### `POST /activities/game/train`
Train the Base AI with user's choice.

**Request Body:**
```json
{
  "session_id": "uuid",
  "chosen_activity_id": 1,
  "context_tags": ["sunny", "morning", "chill"]
}
```

## Data Management Scripts

### Generate Activity Embeddings
```bash
cd backend
python scripts/generate_activity_payload.py
```

Reads `data/activity_names.txt` and generates embeddings using sentence-transformers, saving to `data/activities_with_embeddings.json`.

### Upload Activities to Railway
```bash
cd backend
python scripts/upload_to_railway.py
```

Uploads activities from `data/activities_with_embeddings.json` to the Railway database.

## Portfolio Value

This project demonstrates:
- **Modern Full-Stack Development**: React + TypeScript + FastAPI
- **AI/ML Integration**: Semantic embeddings, contextual bandits, SGD classifier
- **Clean Architecture**: Separation of concerns, custom hooks, reusable components
- **Professional Deployment**: Railway cloud hosting, environment configuration
- **Best Practices**: TypeScript types, Tailwind utility classes, proper error handling
- **Problem-Solving**: Two-layer AI system, URL state management, infinite game loop

## Future Enhancements
- Enhanced Session AI with full weight updates
- Activity categories and filtering
- User accounts and preference persistence
- Social features (sharing recommendations)
- Mobile app version
- A/B testing for AI algorithms

## License
MIT License - See LICENSE file for details



