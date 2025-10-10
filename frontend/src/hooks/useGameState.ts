import { useState, useCallback } from 'react';
import { Activity, GameStartResponse } from '../types';
import { API_ENDPOINTS } from '../config';
import { useSessionAI } from './useSessionAI';

interface GameState {
  pool: Activity[];
  currentLeft: Activity | null;
  currentRight: Activity | null;
  sessionId: string | null;
  contextTags: string[];
}

export function useGameState() {
  const [gameState, setGameState] = useState<GameState>({
    pool: [],
    currentLeft: null,
    currentRight: null,
    sessionId: null,
    contextTags: [],
  });

  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const { initializeSessionAI, trainSessionAI } = useSessionAI();

  const initializeGame = useCallback(
    (data: GameStartResponse, contextTags: string[]) => {
      const pool = [...data.recommendations];
      
      // Pick first two random activities
      const leftIndex = Math.floor(Math.random() * pool.length);
      const leftActivity = pool[leftIndex];
      
      let rightIndex;
      do {
        rightIndex = Math.floor(Math.random() * pool.length);
      } while (rightIndex === leftIndex && pool.length > 1);
      const rightActivity = pool[rightIndex];

      setGameState({
        pool,
        currentLeft: leftActivity,
        currentRight: rightActivity,
        sessionId: data.session_id,
        contextTags,
      });

      // Initialize Session AI with Base AI weights
      initializeSessionAI(data.base_ai_weights);
    },
    [initializeSessionAI]
  );

  const displayNextPair = useCallback((updatedPool: Activity[]) => {
    if (updatedPool.length < 2) {
      // Not enough activities to display a pair
      return { left: null, right: null };
    }

    const leftIndex = Math.floor(Math.random() * updatedPool.length);
    const leftActivity = updatedPool[leftIndex];

    let rightIndex;
    do {
      rightIndex = Math.floor(Math.random() * updatedPool.length);
    } while (rightIndex === leftIndex);
    const rightActivity = updatedPool[rightIndex];

    return { left: leftActivity, right: rightActivity };
  }, []);

  const fetchMoreRecommendations = useCallback(async () => {
    if (!gameState.contextTags.length) return;

    setIsLoadingMore(true);

    try {
      const response = await fetch(API_ENDPOINTS.gameStart, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(gameState.contextTags),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: GameStartResponse = await response.json();

      // Add new recommendations to pool
      setGameState((prev) => {
        const newPool = [...prev.pool, ...data.recommendations];
        const nextPair = displayNextPair(newPool);
        
        return {
          ...prev,
          pool: newPool,
          currentLeft: nextPair.left,
          currentRight: nextPair.right,
        };
      });
    } catch (error) {
      console.error('Error fetching more recommendations:', error);
    } finally {
      setIsLoadingMore(false);
    }
  }, [gameState.contextTags, displayNextPair]);

  const trainBaseAI = useCallback(
    async (activityId: number) => {
      if (!gameState.sessionId) return;

      try {
        await fetch(API_ENDPOINTS.gameTrain, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: gameState.sessionId,
            chosen_activity_id: activityId,
            context_tags: gameState.contextTags,
          }),
        });
      } catch (error) {
        console.error('Error training Base AI:', error);
      }
    },
    [gameState.sessionId, gameState.contextTags]
  );

  const handleChoice = useCallback(
    async (winnerPosition: 'left' | 'right') => {
      const winner = winnerPosition === 'left' ? gameState.currentLeft : gameState.currentRight;
      const loser = winnerPosition === 'left' ? gameState.currentRight : gameState.currentLeft;

      if (!winner || !loser) return;

      // Remove loser from pool
      const updatedPool = gameState.pool.filter((activity) => activity.id !== loser.id);

      // Train Session AI
      trainSessionAI(gameState.contextTags, winner.id, 1.0);

      // Train Base AI via API
      await trainBaseAI(winner.id);

      // Check if we need more recommendations
      if (updatedPool.length <= 1) {
        await fetchMoreRecommendations();
      } else {
        // Display next pair
        const nextPair = displayNextPair(updatedPool);
        setGameState((prev) => ({
          ...prev,
          pool: updatedPool,
          currentLeft: nextPair.left,
          currentRight: nextPair.right,
        }));
      }
    },
    [gameState, trainSessionAI, trainBaseAI, fetchMoreRecommendations, displayNextPair]
  );

  return {
    pool: gameState.pool,
    currentLeft: gameState.currentLeft,
    currentRight: gameState.currentRight,
    handleChoice,
    isLoadingMore,
    initializeGame,
  };
}



