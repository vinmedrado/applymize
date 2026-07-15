import { api, getApiBaseUrl } from "./api";

export type DashboardSummary = {
  total_jobs: number;
  applications_total: number;
  active_applications: number;
  ranked_jobs: number;
  average_match_score: number;
  high_match_jobs: number;
  new_jobs_7d: number;
  response_rate: number;
  source_diversity: number;
  top_sources: Array<{ source: string; count: number }>;
  status_counts: Array<{ status: string; count: number }>;
  career_score?: number;
  score_buckets?: Array<{ label: string; count: number }>;
  score_trend?: Array<{ date: string; career_score: number; average_match_score: number; applications_total: number; high_match_jobs: number }>;
  decision_history?: Array<{ id: number; type: string; title: string; detail: string; score: number; job_id?: number | null; application_id?: number | null; created_at: string }>;
  latest_radar?: {
    provider: string;
    total_ingested: number;
    notified_count: number;
    created_at: string;
  } | null;
  realtime?: boolean;
  push_version?: number;
};

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await api.get<DashboardSummary>("/api/dashboard/summary");
  return response.data;
}

export function dashboardRealtimeUrl(): string {
  const baseURL = getApiBaseUrl();
  const wsBase = baseURL.replace(/^http/, "ws");
  return `${wsBase}/api/dashboard/realtime`;
}
