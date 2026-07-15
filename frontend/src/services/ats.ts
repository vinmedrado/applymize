import { api } from "./api";
import { AtsAnalysis } from "../types";

export async function analyzeMe(): Promise<AtsAnalysis> {
  const response = await api.get<AtsAnalysis>("/api/ats/analyze-me");
  return response.data;
}

export async function analyzeJob(jobId: number): Promise<AtsAnalysis> {
  const response = await api.get<AtsAnalysis>(`/api/ats/analyze-job/${jobId}`);
  return response.data;
}
