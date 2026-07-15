import { api } from "./api";
import { Application, ApplicationStatus, Resume, InterviewPrep } from "../types";

export async function listApplications(): Promise<Application[]> {
  const response = await api.get<Application[]>("/api/applications/");
  return response.data;
}

export async function createApplication(jobId: number, status: ApplicationStatus = "saved"): Promise<Application> {
  const response = await api.post<Application>("/api/applications/", {
    job_id: jobId,
    status,
    notes: "",
    next_action: ""
  });
  return response.data;
}

export async function updateApplication(applicationId: number, status: ApplicationStatus): Promise<Application> {
  const response = await api.patch<Application>(`/api/applications/${applicationId}`, {
    status
  });
  return response.data;
}

export async function generateCV(jobId: number): Promise<Resume> {
  const response = await api.post<Resume>(`/api/cv/jobs/${jobId}`);
  return response.data;
}

export async function generateInterview(jobId: number): Promise<InterviewPrep> {
  const response = await api.get<InterviewPrep>(`/api/interview/jobs/${jobId}`);
  return response.data;
}
