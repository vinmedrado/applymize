import { api } from "./api";
import { StrategyRecommendation } from "../types";

export async function getStrategyRecommendations(limit = 25): Promise<StrategyRecommendation[]> {
  const response = await api.get<StrategyRecommendation[]>("/api/strategy/recommendations", {
    params: { limit }
  });
  return response.data;
}
