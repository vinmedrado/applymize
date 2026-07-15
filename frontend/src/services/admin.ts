import { api } from "./api";

export async function getAdminOverview(): Promise<any> {
  const { data } = await api.get("/api/admin/overview");
  return data;
}

export async function getRecruiterDashboard(): Promise<any> {
  const { data } = await api.get("/api/recruiter/dashboard");
  return data;
}
