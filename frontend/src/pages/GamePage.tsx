import { useEffect, useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { GameStartResponse } from '../types';
import { API_ENDPOINTS, GAME_CONFIG } from '../config';
import { useGameState } from '../hooks/useGameState';
import ActivityCard from '../components/ActivityCard';
import LoadingSpinner from '../components/LoadingSpinner';

export default function GamePage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get context tags from URL (memoized to prevent infinite loops)
  const contextTags = useMemo(() => {
    const tags = searchParams.get('tags')?.split(',') || [];
    return tags.filter((tag) => tag && tag.trim() !== '');
  }, [searchParams]);

  const { currentLeft, currentRight, handleChoice, isLoadingMore, initializeGame } = useGameState();

  useEffect(() => {
    // Validate tags
    if (contextTags.length < GAME_CONFIG.minTags) {
      navigate('/', { replace: true });
      return;
    }

    initializeGameWithAPI();
  }, [contextTags, navigate]);

  const initializeGameWithAPI = async () => {
    try {
      setIsInitializing(true);
      setError(null);

      const response = await fetch(API_ENDPOINTS.gameStart, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(contextTags),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      const data: GameStartResponse = await response.json();

      if (!data.session_id || !data.recommendations || !Array.isArray(data.recommendations)) {
        throw new Error('Invalid response format from API');
      }

      initializeGame(data, contextTags);
    } catch (err) {
      console.error('Error initializing game:', err);
      setError(err instanceof Error ? err.message : 'Failed to start game');
    } finally {
      setIsInitializing(false);
    }
  };

  const handleBackToTags = () => {
    navigate('/', { replace: true });
  };

  if (isInitializing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 flex items-center justify-center">
        <LoadingSpinner message="Initializing game..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-2xl">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-700 mb-6">{error}</p>
          <button
            onClick={handleBackToTags}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            ← Back to Tags
          </button>
        </div>
      </div>
    );
  }

  if (!currentLeft || !currentRight) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 flex items-center justify-center">
        <LoadingSpinner message="Loading activities..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8 pt-4">
          <button
            onClick={handleBackToTags}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors backdrop-blur-sm"
          >
            ← Back to Tags
          </button>
          
          <div className="flex flex-wrap gap-2">
            {contextTags.map((tag) => (
              <span
                key={tag}
                className="px-3 py-1 bg-white/90 text-purple-700 rounded-full text-sm font-medium"
              >
                {tag.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>

        {/* Comparison Container */}
        <div className="grid md:grid-cols-2 gap-6 items-center">
          <ActivityCard activity={currentLeft} onChoose={() => handleChoice('left')} />

          <div className="hidden md:flex justify-center items-center">
            <div className="text-6xl font-bold text-white/30">VS</div>
          </div>
          <div className="md:hidden text-center">
            <div className="text-4xl font-bold text-white/30">VS</div>
          </div>

          <ActivityCard activity={currentRight} onChoose={() => handleChoice('right')} />
        </div>

        {/* Loading More Indicator */}
        {isLoadingMore && (
          <div className="mt-8 flex justify-center">
            <LoadingSpinner message="Loading more recommendations..." />
          </div>
        )}
      </div>
    </div>
  );
}



