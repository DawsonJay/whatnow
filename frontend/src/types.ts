// Type definitions for WhatNow application

export interface Activity {
  id: number;
  name: string;
}

export interface GameStartResponse {
  session_id: string;
  recommendations: Activity[];
  base_ai_weights: BaseAIWeights | null;
}

export interface BaseAIWeights {
  coefficients: number[][] | null;
  intercept: number[] | null;
  classes: number[] | null;
  is_fitted: boolean;
}

export interface TrainRequest {
  session_id: string;
  chosen_activity_id: number;
  context_tags: string[];
}

export interface SelectedTags {
  weather: string | null;
  time: string | null;
  season: string | null;
  intensity: string | null;
  mood: string[];
}

export interface TagGroup {
  title: string;
  tags: string[];
  exclusive: boolean;
}

export type TagGroups = {
  weather: TagGroup;
  time: TagGroup;
  season: TagGroup;
  intensity: TagGroup;
  mood: TagGroup;
};



