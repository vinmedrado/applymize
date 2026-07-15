import { api } from "./api";

export type OnboardingStatus = {
  completed: boolean;
};

export async function getOnboardingStatus(): Promise<OnboardingStatus> {
  const response = await api.get<OnboardingStatus>("/api/user/onboarding-status");
  return response.data;
}

export async function completeOnboarding(): Promise<OnboardingStatus> {
  const response = await api.post<OnboardingStatus>("/api/user/onboarding-complete");
  return response.data;
}
