import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./tokenStorage";

export function hasPrivateBackendAccess(): boolean {
  const configured = String(import.meta.env.VITE_API_BASE_URL || "").trim();
  if (configured) return true;

  const hostname = window.location.hostname.toLowerCase();
  return (
    hostname === "localhost"
    || hostname === "127.0.0.1"
    || hostname === "::1"
    || hostname.endsWith(".local")
    || hostname.startsWith("10.")
    || hostname.startsWith("192.168.")
    || /^172\.(1[6-9]|2\d|3[01])\./.test(hostname)
  );
}

export function getApiBaseUrl(): string {
  const configured = String(import.meta.env.VITE_API_BASE_URL || "").trim();
  if (configured) return configured.replace(/\/$/, "");

  const protocol = window.location.protocol === "https:" ? "https:" : "http:";
  return `${protocol}//${window.location.hostname}:8001`;
}

const baseURL = getApiBaseUrl();

export const api = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json"
  }
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshing = false;
let queue: Array<(token: string | null) => void> = [];

function resolveQueue(token: string | null) {
  queue.forEach((callback) => callback(token));
  queue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    if (error.response?.status !== 401 || !original || original._retry || original.url?.includes("/api/auth/refresh")) {
      return Promise.reject(error);
    }

    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearTokens();
      if (!window.location.pathname.startsWith("/login")) window.location.assign("/login");
      return Promise.reject(error);
    }

    if (refreshing) {
      return new Promise((resolve, reject) => {
        queue.push((token) => {
          if (!token) {
            reject(error);
            return;
          }
          original.headers.Authorization = `Bearer ${token}`;
          resolve(api(original));
        });
      });
    }

    original._retry = true;
    refreshing = true;

    try {
      const response = await axios.post(`${baseURL}/api/auth/refresh`, {
        refresh_token: refreshToken
      });
      const accessToken = response.data.access_token;
      const nextRefreshToken = response.data.refresh_token;
      setTokens(accessToken, nextRefreshToken, Boolean(localStorage.getItem("applymize_refresh_token")));
      resolveQueue(accessToken);
      original.headers.Authorization = `Bearer ${accessToken}`;
      return api(original);
    } catch (refreshError) {
      resolveQueue(null);
      console.warn("Falha ao renovar token", refreshError);
      clearTokens();
      if (!window.location.pathname.startsWith("/login")) window.location.assign("/login");
      return Promise.reject(refreshError);
    } finally {
      refreshing = false;
    }
  }
);

export function getApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg || JSON.stringify(item)).join("\n");
    }
    if (typeof detail === "string") {
      return detail;
    }
    if (detail) {
      return JSON.stringify(detail);
    }
    if (error.code === "ECONNABORTED") {
      return "Tempo de resposta excedido. Verifique a API.";
    }
    return error.message;
  }
  return "Erro inesperado";
}
