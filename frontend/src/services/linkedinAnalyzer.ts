import { api } from "./api";
export type LinkedInAnalysis = { score: number; categories: Record<string, number>; strengths: string[]; weaknesses: string[]; ats_keywords: string[]; suggested_headline: string; suggested_about: string; recruiter_feedback: string; ats_feedback: string; improvement_actions: string[]; };
export type LinkedInAnalyzePayload = { linkedin_url?: string; profile_text: string; target_role?: string; };
export async function analyzeLinkedInProfile(payload: LinkedInAnalyzePayload): Promise<LinkedInAnalysis> { const response = await api.post<LinkedInAnalysis>("/api/linkedin-analyzer/analyze", payload); return response.data; }
export async function analyzeLinkedInDemo(payload: LinkedInAnalyzePayload): Promise<LinkedInAnalysis> { const response = await api.post<LinkedInAnalysis>("/api/public/linkedin-analyzer/demo", payload); return response.data; }
