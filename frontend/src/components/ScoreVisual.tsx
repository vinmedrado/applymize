import { StrategyPriority } from "../types";

export function priorityTone(priority?: StrategyPriority | string) {
  if (priority === "HIGH_PRIORITY") return "border-emerald-200 bg-emerald-50 text-emerald-700";
  if (priority === "MEDIUM_PRIORITY") return "border-amber-200 bg-amber-50 text-amber-700";
  if (priority === "LOW_PRIORITY") return "border-red-200 bg-red-50 text-red-700";
  return "border-slate-200 bg-slate-100 text-slate-700";
}

export function priorityLabel(priority?: StrategyPriority | string) {
  if (priority === "HIGH_PRIORITY" || priority === "HIGH" || priority === "ALTA") return "Alta";
  if (priority === "MEDIUM_PRIORITY" || priority === "MEDIUM" || priority === "MEDIA" || priority === "MÉDIA") return "Média";
  if (priority === "LOW_PRIORITY" || priority === "LOW" || priority === "BAIXA") return "Baixa";
  return "Não informado";
}

export function StrategyBadge({ priority, score }: { priority?: StrategyPriority | string; score?: number }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${priorityTone(priority)}`}>
      {priorityLabel(priority)}
      {typeof score === "number" && <span>• {score}%</span>}
    </span>
  );
}

export function MatchProgress({ score, label = "Compatibilidade" }: { score?: number; label?: string }) {
  const value = Math.max(0, Math.min(100, Number(score || 0)));
  const bar = value >= 78 ? "bg-emerald-500" : value >= 58 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="min-w-28">
      <div className="mb-1 flex items-center justify-between text-[11px] font-semibold text-slate-600">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full rounded-full ${bar}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
