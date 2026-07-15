import { api } from "./api";
import { ApplicationQueueItem, QueueBuildResponse } from "../types";

export async function listApplicationQueue(): Promise<ApplicationQueueItem[]> {
  const response = await api.get<ApplicationQueueItem[]>("/api/application-agent/queue");
  return response.data;
}

export async function buildApplicationQueue(payload = {
  limit: 10,
  min_strategy_score: 58,
  generate_cv: true,
  generate_message: true
}): Promise<QueueBuildResponse> {
  const response = await api.post<QueueBuildResponse>("/api/application-agent/build-queue", payload);
  return response.data;
}

export async function approveQueueItem(queueId: number): Promise<ApplicationQueueItem> {
  const response = await api.post<ApplicationQueueItem>(`/api/application-agent/${queueId}/approve`);
  return response.data;
}

export async function skipQueueItem(queueId: number): Promise<ApplicationQueueItem> {
  const response = await api.post<ApplicationQueueItem>(`/api/application-agent/${queueId}/skip`);
  return response.data;
}

export async function markQueueItemApplied(queueId: number): Promise<ApplicationQueueItem> {
  const response = await api.post<ApplicationQueueItem>(`/api/application-agent/${queueId}/mark-applied`);
  return response.data;
}
