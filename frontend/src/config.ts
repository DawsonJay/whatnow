// Application configuration

export const API_BASE_URL = 'https://whatnow-production.up.railway.app';

export const API_ENDPOINTS = {
  gameStart: `${API_BASE_URL}/activities/game/start`,
  gameTrain: `${API_BASE_URL}/activities/game/train`,
} as const;

export const GAME_CONFIG = {
  minTags: 3,
  maxTags: 8,
  sessionAILearningRate: 0.3,
  contextDim: 43,
  embeddingDim: 384,
} as const;



