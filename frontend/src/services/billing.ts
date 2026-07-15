import { api } from "./api";

export type Plan = {
  code: string;
  name: string;
  monthly_price: number | null;
  annual_price: number | null;
  description: string;
  features: string[];
};

export async function getPublicPlans(): Promise<{ plans: Plan[] }> {
  const { data } = await api.get("/api/public/billing/plans");
  return data;
}

export async function getBillingPlans(): Promise<{ plans: Plan[]; current_plan: string }> {
  const { data } = await api.get("/api/billing/plans");
  return data;
}

export async function getSubscription(): Promise<any> {
  const { data } = await api.get("/api/billing/subscription");
  return data;
}

export async function startCheckout(plan_code: string, billing_cycle = "monthly"): Promise<any> {
  const { data } = await api.post("/api/billing/checkout", { plan_code, billing_cycle });
  return data;
}
