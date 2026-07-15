import { api } from "./api";
import { WhatsAppSessionStatus } from "../types";

export async function getWhatsAppSession(): Promise<WhatsAppSessionStatus> {
  const response = await api.get<WhatsAppSessionStatus>("/api/whatsapp/session");
  return response.data;
}

export async function createWhatsAppSession(phone_number?: string): Promise<WhatsAppSessionStatus> {
  const response = await api.post<WhatsAppSessionStatus>("/api/whatsapp/session", { phone_number });
  return response.data;
}

export async function getWhatsAppStatus(): Promise<WhatsAppSessionStatus> {
  const response = await api.get<WhatsAppSessionStatus>("/api/whatsapp/session/status");
  return response.data;
}

export async function saveWhatsAppPhone(phone_number: string): Promise<WhatsAppSessionStatus> {
  const response = await api.post<WhatsAppSessionStatus>("/api/whatsapp/session", { phone_number });
  return response.data;
}

export async function createWhatsAppInstance(): Promise<WhatsAppSessionStatus> {
  const response = await api.post<WhatsAppSessionStatus>("/api/whatsapp/session/connect");
  return response.data;
}

export async function checkWhatsAppConnection(): Promise<WhatsAppSessionStatus> {
  const response = await api.get<WhatsAppSessionStatus>("/api/whatsapp/session/status");
  return response.data;
}

export async function getWhatsAppQrCode(): Promise<WhatsAppSessionStatus> {
  const response = await api.get<WhatsAppSessionStatus>("/api/whatsapp/session/qrcode");
  return response.data;
}

export async function sendWhatsAppTest(target_number = ""): Promise<WhatsAppSessionStatus> {
  const response = await api.post<WhatsAppSessionStatus>("/api/whatsapp/session/test", { target_number: target_number || undefined });
  return response.data;
}

export async function disconnectWhatsApp(): Promise<WhatsAppSessionStatus> {
  const response = await api.post<WhatsAppSessionStatus>("/api/whatsapp/session/disconnect");
  return response.data;
}

export async function deleteWhatsAppSession(): Promise<{ deleted: boolean; message: string }> {
  const response = await api.delete("/api/whatsapp/session");
  return response.data;
}
