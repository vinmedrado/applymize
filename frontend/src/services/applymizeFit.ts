import { api } from "./api";

export type FitQuestion = {
  id: string;
  title: string;
  question: string;
  dimension: string;
  what_recruiter_expects: string;
};

export type FitSession = {
  session_id: string;
  company: string;
  target_role: string;
  focus: string;
  profile_summary: string;
  questions: FitQuestion[];
  provider: string;
  model: string;
  fallback_used: boolean;
};

export type FitEvaluation = {
  score: number;
  level: string;
  recruiter_reading: string;
  strengths: string[];
  risks: string[];
  improved_answer: string;
  next_tip: string;
  provider: string;
  model: string;
  fallback_used: boolean;
};

export async function startFitSession(payload: { company: string; target_role: string; focus: string }): Promise<FitSession> {
  const response = await api.post<FitSession>("/api/applymize-fit/start", payload);
  return response.data;
}

export async function evaluateFitAnswer(payload: {
  company: string;
  target_role: string;
  focus: string;
  question: string;
  answer: string;
}): Promise<FitEvaluation> {
  const response = await api.post<FitEvaluation>("/api/applymize-fit/evaluate", payload);
  return response.data;
}
