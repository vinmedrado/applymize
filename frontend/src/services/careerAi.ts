import { api } from "./api";

export type CareerAIResponse = {
  conversation_id: number;
  answer: string;
  provider: string;
  model: string;
  fallback_used: boolean;
};

export type CareerAIConversation = {
  id: number;
  title: string;
  summary: string;
  pinned: boolean;
  archived: boolean;
  created_at: string;
  updated_at: string;
};

export type CareerAIMessage = {
  id: number;
  conversation_id: number;
  role: "user" | "assistant" | "system";
  content: string;
  provider: string;
  model: string;
  tokens_estimated?: number | null;
  created_at: string;
};

export async function sendCareerAIMessage(message: string, conversationId?: number | null): Promise<CareerAIResponse> {
  const response = await api.post<CareerAIResponse>("/api/career-ai/chat", {
    message,
    conversation_id: conversationId ?? null
  });
  return response.data;
}

export async function listCareerAIConversations(): Promise<CareerAIConversation[]> {
  const response = await api.get<CareerAIConversation[]>("/api/career-ai/conversations");
  return response.data;
}

export async function createCareerAIConversation(title?: string): Promise<CareerAIConversation> {
  const response = await api.post<CareerAIConversation>("/api/career-ai/conversations", { title: title || undefined });
  return response.data;
}

export async function renameCareerAIConversation(conversationId: number, title: string): Promise<CareerAIConversation> {
  const response = await api.patch<CareerAIConversation>(`/api/career-ai/conversations/${conversationId}`, { title });
  return response.data;
}

export async function deleteCareerAIConversation(conversationId: number): Promise<{ ok: boolean }> {
  const response = await api.delete<{ ok: boolean }>(`/api/career-ai/conversations/${conversationId}`);
  return response.data;
}

export async function listCareerAIMessages(conversationId: number): Promise<CareerAIMessage[]> {
  const response = await api.get<CareerAIMessage[]>(`/api/career-ai/conversations/${conversationId}/messages`);
  return response.data;
}
