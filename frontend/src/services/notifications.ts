import { api } from "./api";
import { NotificationResult, NotificationSettings } from "../types";

export async function getNotificationSettings(): Promise<NotificationSettings> {
  const response = await api.get<NotificationSettings>("/api/notifications/settings");
  return response.data;
}

export async function sendTestNotification(): Promise<NotificationResult> {
  const response = await api.post<NotificationResult>("/api/notifications/test");
  return response.data;
}

export async function sendHighPriorityNotifications(): Promise<NotificationResult> {
  const response = await api.post<NotificationResult>("/api/notifications/send-high-priority");
  return response.data;
}
