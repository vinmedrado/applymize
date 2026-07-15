import { StrategyPriority } from "../types";
import { priorityLabel, priorityTone } from "./ScoreVisual";

export function PriorityBadge({ priority }: { priority: StrategyPriority }) {
  return (
    <span className={`rounded-full border px-3 py-1 text-xs font-extrabold tracking-wide ${priorityTone(priority)}`}>
      {priorityLabel(priority)}
    </span>
  );
}
