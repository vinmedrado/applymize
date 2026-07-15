import { api } from "./api";
import { AnalyticsOverview, RadarRun, SkillGapRoadmap } from "../types";

export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  const response = await api.get<AnalyticsOverview>("/api/analytics/overview");
  return response.data;
}

export async function getSkillGapRoadmap(): Promise<SkillGapRoadmap> {
  const response = await api.get<SkillGapRoadmap>("/api/skill-gap/roadmap");
  return response.data;
}

export async function runRadar(provider = "remoteok", limit = 25): Promise<RadarRun> {
  const response = await api.post<RadarRun>(`/api/radar/run?provider=${provider}&limit=${limit}`);
  return response.data;
}

export async function getRadarHistory(): Promise<RadarRun[]> {
  const response = await api.get<RadarRun[]>("/api/radar/history");
  return response.data;
}

export async function getFollowups(): Promise<any[]> {
  const response = await api.get<any[]>("/api/followups/");
  return response.data;
}

export async function getFollowup(applicationId: number): Promise<any> {
  const response = await api.get<any>(`/api/followups/${applicationId}`);
  return response.data;
}

export async function generateCoverLetter(jobId: number): Promise<any> {
  const response = await api.get<any>(`/api/cover-letter/jobs/${jobId}`);
  return response.data;
}
