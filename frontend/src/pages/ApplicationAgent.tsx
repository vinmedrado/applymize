import { useEffect, useMemo, useState } from "react";
import { Copy, ExternalLink, RefreshCcw } from "lucide-react";
import { EmptyState } from "../components/EmptyState";
import { PageLoading } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { MarkdownBlock } from "../components/MarkdownBlock";
import { StrategyBadge } from "../components/ScoreVisual";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { approveQueueItem, buildApplicationQueue, listApplicationQueue, markQueueItemApplied, skipQueueItem } from "../services/applicationAgent";
import { ApplicationQueueItem } from "../types";

const statusClass: Record<string, string> = {
  queued: "bg-slate-100 text-slate-700",
  approved: "bg-blue-50 text-blue-700",
  skipped: "bg-amber-50 text-amber-700",
  applied: "bg-emerald-50 text-emerald-700",
  failed: "bg-red-50 text-red-700"
};

function gradeClass(grade: string) {
  if (grade === "A") return "bg-emerald-600 text-white";
  if (grade === "B") return "bg-emerald-100 text-emerald-800";
  if (grade === "C") return "bg-amber-100 text-amber-800";
  if (grade === "D") return "bg-orange-100 text-orange-800";
  return "bg-red-100 text-red-800";
}

function priorityFromScore(score: number) {
  if (score >= 78) return "HIGH_PRIORITY";
  if (score >= 58) return "MEDIUM_PRIORITY";
  return "LOW_PRIORITY";
}

export function ApplicationAgent() {
  const toast = useToast();
  const [items, setItems] = useState<ApplicationQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [building, setBuilding] = useState(false);
  const [statusFilter, setStatusFilter] = useState("all");

  const visibleItems = useMemo(() => {
    return items
      .filter((item) => statusFilter === "all" || item.status === statusFilter)
      .sort((a, b) => b.strategy_score - a.strategy_score);
  }, [items, statusFilter]);

  async function load() {
    setLoading(true);
    try {
      setItems(await listApplicationQueue());
    } catch (err) {
      toast.error("Erro ao carregar fila", getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function buildQueue() {
    setBuilding(true);
    try {
      const result = await buildApplicationQueue({ limit: 10, min_strategy_score: 58, generate_cv: true, generate_message: true });
      toast.success("Fila criada", `${result.created} criadas, ${result.skipped} ignoradas, ${result.blocked_low_priority} bloqueadas.`);
      await load();
    } catch (err) {
      toast.error("Erro ao criar fila", getApiError(err));
    } finally {
      setBuilding(false);
    }
  }

  async function runAction(action: () => Promise<ApplicationQueueItem>, success: string) {
    try {
      await action();
      toast.success(success);
      await load();
    } catch (err) {
      toast.error("Erro na ação", getApiError(err));
    }
  }

  async function copy(text: string, label: string) {
    await navigator.clipboard.writeText(text || "");
    toast.success(`${label} copiado`);
  }

  if (loading) return <PageLoading label="Carregando candidaturas inteligentes..." />;

  return (
    <div className="space-y-6" data-tour="application-agent-page">
      <section className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div>
            <p className="text-sm text-slate-500">Minhas candidaturas inteligentes</p>
            <h1 className="mt-2 text-3xl font-bold">Fila assistida e segura</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-500">Gere CV e mensagem, aprove manualmente e aplique no site original. Nada é enviado sozinho.</p>
          </div>
          <button className="btn bg-white text-slate-950 hover:bg-slate-100" onClick={buildQueue} disabled={building}>
            <RefreshCcw className="mr-2 h-4 w-4" /> {building ? "Gerando..." : "Criar fila recomendada"}
          </button>
        </div>
      </section>

      <div className="card p-4">
        <label className="text-sm font-medium">Filtro de status</label>
        <select className="input mt-2 max-w-xs" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">Todos</option><option value="queued">queued</option><option value="approved">approved</option><option value="skipped">skipped</option><option value="applied">applied</option><option value="failed">failed</option>
        </select>
      </div>

      {items.length === 0 ? (
        <EmptyState title="Fila vazia" description="Importe/cadastre vagas, gere recomendações e crie uma fila segura." action={<button className="btn-primary" onClick={buildQueue}>Criar fila</button>} />
      ) : (
        <div className="grid gap-5">
          {visibleItems.map((item) => (
            <SectionCard
              key={item.id}
              title={item.job_title || `Vaga #${item.job_id}`}
              subtitle={`${item.company || "Empresa"} • ${item.location || "Local não informado"}`}
              action={
                <div className="flex flex-wrap items-center gap-2">
                  <StrategyBadge priority={priorityFromScore(item.strategy_score)} score={item.strategy_score} />
                  <span className={`rounded-full px-3 py-1 text-xs font-bold ${gradeClass(item.evaluation_grade)}`}>Grade {item.evaluation_grade}</span>
                  <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusClass[item.status] || "bg-slate-100 text-slate-700"}`}>{item.status}</span>
                </div>
              }
            >
              <div className="grid gap-5 xl:grid-cols-2">
                <div>
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <h3 className="font-semibold">Mensagem sugerida</h3>
                    <button className="btn-secondary" onClick={() => copy(item.cover_message, "Mensagem")}><Copy className="mr-2 h-4 w-4" /> Copiar</button>
                  </div>
                  <div className="min-h-32 rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-700">{item.cover_message || "Mensagem ainda não gerada."}</div>
                </div>
                <div>
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <h3 className="font-semibold">CV gerado</h3>
                    <button className="btn-secondary" onClick={() => copy(item.generated_cv, "CV")}><Copy className="mr-2 h-4 w-4" /> Copiar</button>
                  </div>
                  <div className="max-h-96 overflow-auto rounded-2xl bg-slate-50 p-3">
                    {item.generated_cv ? <MarkdownBlock content={item.generated_cv} /> : <p className="text-sm text-slate-500">CV ainda não gerado.</p>}
                  </div>
                </div>
              </div>

              {item.failure_reason && <div className="mt-4 rounded-2xl bg-red-50 p-3 text-sm text-red-700">{item.failure_reason}</div>}

              <div className="mt-5 flex flex-wrap gap-2">
                {item.job_url ? (
                  <a className="btn-primary" href={item.job_url} target="_blank" rel="noreferrer" title="Você será redirecionado para o site original">
                    🔗 Candidatar na vaga <span className="ml-1 text-xs opacity-80">(abre em nova aba)</span>
                  </a>
                ) : (
                  <button className="btn-primary opacity-50" disabled title="Link não disponível">Link não disponível</button>
                )}
                <button className="btn-secondary" onClick={() => runAction(() => approveQueueItem(item.id), "Candidatura aprovada")}>Aprovar</button>
                <button className="btn-secondary" onClick={() => runAction(() => skipQueueItem(item.id), "Candidatura pulada")}>Pular</button>
                <button className="btn-secondary" onClick={() => runAction(() => markQueueItemApplied(item.id), "Marcada como aplicada")}>Marcar como aplicada</button>
              </div>
            </SectionCard>
          ))}
        </div>
      )}
    </div>
  );
}
