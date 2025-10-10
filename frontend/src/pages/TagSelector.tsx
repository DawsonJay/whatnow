import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SelectedTags, TagGroups } from '../types';
import { GAME_CONFIG } from '../config';
import TagGroup from '../components/TagGroup';

const TAG_GROUPS: TagGroups = {
  weather: {
    title: 'Weather',
    tags: ['sunny', 'cloudy', 'raining', 'snowy', 'stormy'],
    exclusive: true,
  },
  time: {
    title: 'Time',
    tags: ['morning', 'afternoon', 'evening', 'night'],
    exclusive: true,
  },
  season: {
    title: 'Season',
    tags: ['spring', 'summer', 'autumn', 'winter'],
    exclusive: true,
  },
  intensity: {
    title: 'Intensity',
    tags: ['chill', 'tired', 'exciting', 'energetic', 'intense'],
    exclusive: true,
  },
  mood: {
    title: 'Mood (Select Multiple)',
    tags: [
      'stressed', 'motivated', 'adventurous', 'nostalgic', 'romantic',
      'playful', 'focused', 'distracted', 'inspired', 'friendly',
      'shy', 'curious', 'analytical', 'emotional', 'burnt_out',
      'artistic', 'practical', 'hungry', 'natural', 'urban',
      'anxious', 'overwhelmed', 'upset', 'happy', 'festive',
    ],
    exclusive: false,
  },
};

export default function TagSelector() {
  const navigate = useNavigate();
  const [selectedTags, setSelectedTags] = useState<SelectedTags>({
    weather: null,
    time: null,
    season: null,
    intensity: null,
    mood: [],
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleTagSelect = (group: keyof SelectedTags, tag: string) => {
    setSelectedTags((prev) => {
      if (group === 'mood') {
        const isSelected = prev.mood.includes(tag);
        return {
          ...prev,
          mood: isSelected ? prev.mood.filter((t) => t !== tag) : [...prev.mood, tag],
        };
      } else {
        return {
          ...prev,
          [group]: prev[group] === tag ? null : tag,
        };
      }
    });
  };

  const getTotalTags = () => {
    return (
      (selectedTags.weather ? 1 : 0) +
      (selectedTags.time ? 1 : 0) +
      (selectedTags.season ? 1 : 0) +
      (selectedTags.intensity ? 1 : 0) +
      selectedTags.mood.length
    );
  };

  const canStartGame = () => {
    const totalTags = getTotalTags();
    return totalTags >= GAME_CONFIG.minTags && totalTags <= GAME_CONFIG.maxTags;
  };

  const handleStartGame = () => {
    if (!canStartGame()) return;

    setIsLoading(true);

    // Build context tags array
    const contextTags = [
      selectedTags.weather,
      selectedTags.time,
      selectedTags.season,
      selectedTags.intensity,
      ...selectedTags.mood,
    ].filter((tag): tag is string => tag !== null && tag !== undefined);

    // Navigate to game page with tags in URL
    const tagsParam = contextTags.join(',');
    navigate(`/game?tags=${encodeURIComponent(tagsParam)}`);
  };

  const totalTags = getTotalTags();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-700 text-white p-8 text-center">
          <h1 className="text-5xl font-light mb-2">WhatNow</h1>
          <p className="text-lg opacity-90">AI-powered activity recommendations</p>
        </div>

        {/* Content */}
        <div className="p-8 space-y-6">
          {/* Tag Groups */}
          {(Object.keys(TAG_GROUPS) as Array<keyof SelectedTags>).map((groupKey) => (
            <TagGroup
              key={groupKey}
              title={TAG_GROUPS[groupKey].title}
              tags={TAG_GROUPS[groupKey].tags}
              selected={selectedTags[groupKey]}
              onTagSelect={(tag) => handleTagSelect(groupKey, tag)}
              exclusive={TAG_GROUPS[groupKey].exclusive}
            />
          ))}

          {/* Selection Info */}
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <h4 className="font-semibold text-gray-700 mb-2">Selection Rules</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Select any combination of tags (minimum {GAME_CONFIG.minTags}, maximum {GAME_CONFIG.maxTags} total)</li>
              <li>• You can select from any group: Weather, Time, Season, Intensity, or Mood</li>
              <li>• Mix and match however you want!</li>
            </ul>
            <div className="mt-2 text-sm font-medium text-gray-700">
              Selected: {totalTags} / {GAME_CONFIG.maxTags} tags
            </div>
          </div>

          {/* Start Button */}
          <button
            onClick={handleStartGame}
            disabled={!canStartGame() || isLoading}
            className={`w-full py-4 px-6 rounded-lg text-lg font-medium transition-all duration-200 ${
              canStartGame() && !isLoading
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isLoading ? 'Starting Game...' : 'Get AI Recommendations'}
          </button>
        </div>
      </div>
    </div>
  );
}

