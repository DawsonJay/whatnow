import { useState, useCallback } from 'react';
import { BaseAIWeights } from '../types';
import { GAME_CONFIG } from '../config';

interface SessionAI {
  weights: BaseAIWeights | null;
  learningRate: number;
}

export function useSessionAI() {
  const [sessionAI, setSessionAI] = useState<SessionAI>({
    weights: null,
    learningRate: GAME_CONFIG.sessionAILearningRate,
  });

  const initializeSessionAI = useCallback((baseAIWeights: BaseAIWeights | null) => {
    setSessionAI((prev) => ({
      ...prev,
      weights: baseAIWeights,
    }));
  }, []);

  const trainSessionAI = useCallback(
    (contextTags: string[], activityId: number, reward: number) => {
      // Simplified Session AI training
      // In a full implementation, this would update model weights using gradient descent
      // For now, we just log the training event
      if (sessionAI.weights) {
        console.log('Session AI training:', {
          contextTags,
          activityId,
          reward,
          learningRate: sessionAI.learningRate,
        });
      }
    },
    [sessionAI]
  );

  return {
    sessionAI,
    initializeSessionAI,
    trainSessionAI,
  };
}



