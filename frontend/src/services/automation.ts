import { api } from "./api";
import { AutomationSettingsPayload, AutomationStatus } from "../types";

export async function getAutomationStatus(): Promise<AutomationStatus> {
  const response = await api.get<AutomationStatus>("/api/automation/status");
  return response.data;
}

export async function updateAutomationSettings(payload: AutomationSettingsPayload): Promise<AutomationStatus> {
  const response = await api.put<AutomationStatus>("/api/automation/settings", payload);
  return response.data;
}
