import { api } from "./api";
import { TokenPair, UserMe } from "../types";

export type RegisterPayload = {
  tenant_name: string;
  full_name: string;
  email: string;
  password: string;
  skills: string;
  seniority: string;
  target_role: string;
  job_country?: string;
  job_state?: string;
  job_state_code?: string;
  job_cities?: string[];
  job_all_cities?: boolean;
  job_remote_preference?: string;
  job_city_code?: string;
};

export async function register(payload: RegisterPayload): Promise<TokenPair> {
  const response = await api.post<TokenPair>("/api/auth/register", payload);
  return response.data;
}

export async function login(email: string, password: string): Promise<TokenPair> {
  const response = await api.post<TokenPair>("/api/auth/login", { email, password });
  return response.data;
}

export async function logout(refreshToken: string): Promise<void> {
  await api.post("/api/auth/logout", { refresh_token: refreshToken });
}

export async function me(): Promise<UserMe> {
  const response = await api.get<UserMe>("/api/auth/me");
  return response.data;
}


export async function forgotPassword(email: string): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>("/api/auth/forgot-password", { email });
  return response.data;
}

export async function resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>("/api/auth/reset-password", { token, new_password: newPassword });
  return response.data;
}
