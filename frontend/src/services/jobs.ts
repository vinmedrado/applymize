import { api } from "./api";
import { Job, MatchScore, RankItem } from "../types";

export type JobsPage = {
  items: Job[];
  total: number;
  page: number;
  pageSize: number;
  hiddenIrrelevant: number;
};

export async function listJobs(q?: string, page = 1, pageSize = 50, includeIrrelevant = false): Promise<JobsPage> {
  const params: Record<string, string | number | boolean> = { page, page_size: pageSize, include_irrelevant: includeIrrelevant };
  if (q) params.q = q;
  const response = await api.get<{ items: Job[]; total: number; page: number; page_size: number; hidden_irrelevant: number }>("/api/jobs/paged", { params });
  return {
    items: response.data.items,
    total: response.data.total,
    page: response.data.page,
    pageSize: response.data.page_size,
    hiddenIrrelevant: response.data.hidden_irrelevant || 0,
  };
}

export async function getJob(jobId: number): Promise<Job> {
  const response = await api.get<Job>(`/api/jobs/${jobId}`);
  return response.data;
}

export async function createJob(payload: Partial<Job>): Promise<Job> {
  const response = await api.post<Job>("/api/jobs/", payload);
  return response.data;
}

export async function ingestJobs(
  provider = "remoteok",
  limit = 25,
  options: { term?: string; state?: string; city?: string; workplace_types?: string } = {}
): Promise<{ inserted: number; skipped: number; collected_by_provider: Record<string, number>; errors: Record<string, string>; jobs: Job[] }> {
  const response = await api.post("/api/jobs/ingest", null, { params: { provider, limit, ...options } });
  return response.data;
}

export async function listProviders(): Promise<Array<{ provider: string; enabled: boolean }>> {
  const response = await api.get("/api/providers");
  return response.data;
}

export async function providersHealth(): Promise<Array<{ provider: string; enabled: boolean; status: string; sample_count?: number; error?: string }>> {
  const response = await api.get("/api/providers/health");
  return response.data;
}

export async function scoreJob(jobId: number): Promise<MatchScore> {
  const response = await api.post<MatchScore>(`/api/matching/jobs/${jobId}`);
  return response.data;
}

export async function rankJobs(limit = 25): Promise<RankItem[]> {
  const response = await api.post<RankItem[]>("/api/matching/rank", null, { params: { limit } });
  return response.data;
}

export async function deleteJob(jobId: number): Promise<{ deleted: boolean }> {
  const response = await api.delete<{ deleted: boolean }>(`/api/jobs/${jobId}`);
  return response.data;
}
