import { api } from "./api";
import { UserProfile } from "../types";

export async function getProfile(): Promise<UserProfile> {
  const response = await api.get<UserProfile>("/api/profile/me");
  return response.data;
}

export async function updateProfile(payload: Partial<UserProfile>): Promise<UserProfile> {
  const response = await api.put<UserProfile>("/api/profile/me", payload);
  return response.data;
}

export async function addSkill(name: string): Promise<UserProfile> {
  const response = await api.post<UserProfile>("/api/profile/skills", { name, level: "intermediate", category: "technical" });
  return response.data;
}

export async function uploadResume(file: File): Promise<{ extracted_text: string; parsed_data: Record<string, unknown> }> {
  const data = new FormData();
  data.append("file", file);
  const response = await api.post("/api/profile/upload-resume", data, { headers: { "Content-Type": "multipart/form-data" } });
  return response.data;
}

export async function parseResume(): Promise<{ extracted_text: string; parsed_data: Record<string, unknown>; profile: UserProfile }> {
  const response = await api.post("/api/profile/parse-resume");
  return response.data;
}


export async function getModernResumeHtml(): Promise<string> {
  const response = await api.get<string>("/api/profile/resume-modern", { responseType: "text" });
  return response.data;
}
