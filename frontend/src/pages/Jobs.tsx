import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Search, Trash2 } from "lucide-react";
import { EmptyState } from "../components/EmptyState";
import { SkeletonCard, Spinner } from "../components/Loading";
import { useToast } from "../context/ToastContext";
import { useAuth } from "../context/AuthContext";
import { getApiError } from "../services/api";
import { createApplication } from "../services/applications";
import { deleteJob, ingestJobs, listJobs, listProviders, scoreJob } from "../services/jobs";
import { getStrategyRecommendations } from "../services/strategy";
import { JobSourceBadge } from "../components/JobSourceBadge";
import { MatchProgress, StrategyBadge } from "../components/ScoreVisual";
import { Job, MatchScore, StrategyRecommendation } from "../types";

function DescriptionPreview({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const shouldTrim = (text || "").length > 260;
  const visible = expanded || !shouldTrim ? text : `${text.slice(0, 260)}...`;
  return (
    <div>
      <p className="mt-3 text-sm leading-6 text-slate-700">{visible}</p>
      {shouldTrim && (
        <button className="mt-2 text-sm font-semibold text-slate-950 underline" onClick={() => setExpanded(!expanded)}>
          {expanded ? "Ver menos" : "Ver mais"}
        </button>
      )}
    </div>
  );
}

function pct(value?: number) {
  return `${Math.max(0, Math.min(100, Number(value || 0))).toFixed(1)}%`;
}

function AnalysisMetric({ label, value }: { label: string; value?: number }) {
  const normalized = Math.max(0, Math.min(100, Number(value || 0)));
  const tone = normalized >= 78 ? "bg-emerald-500" : normalized >= 58 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="analysis-metric">
      <div className="flex items-center justify-between gap-3 text-xs font-semibold text-slate-600">
        <span>{label}</span>
        <span className="font-bold text-slate-900">{pct(normalized)}</span>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full rounded-full ${tone}`} style={{ width: `${normalized}%` }} />
      </div>
    </div>
  );
}

function MatchAnalysisPanel({ score }: { score: MatchScore }) {
  const matched = score.matched_skills || [];
  const missing = score.missing_skills || [];
  return (
    <div className="analysis-panel">
      <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Análise de compatibilidade</p>
          <h3 className="text-base font-bold text-slate-950">Score geral: {pct(score.score)}</h3>
        </div>
        <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-slate-700 ring-1 ring-slate-200">
          Baseado no seu perfil e currículo
        </span>
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <AnalysisMetric label="Skills" value={score.skill_score} />
        <AnalysisMetric label="Senioridade" value={score.seniority_score} />
        <AnalysisMetric label="Palavras-chave" value={score.keyword_score} />
        <AnalysisMetric label="Score final" value={score.score} />
      </div>

      {(matched.length > 0 || missing.length > 0) && (
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <div className="rounded-xl bg-white p-3 ring-1 ring-slate-200">
            <p className="text-xs font-bold uppercase tracking-wide text-emerald-700">Pontos compatíveis</p>
            <p className="mt-1 text-sm text-slate-700">{matched.length ? matched.slice(0, 8).join(" · ") : "Nenhum ponto forte específico identificado."}</p>
          </div>
          <div className="rounded-xl bg-white p-3 ring-1 ring-slate-200">
            <p className="text-xs font-bold uppercase tracking-wide text-amber-700">Pontos de atenção</p>
            <p className="mt-1 text-sm text-slate-700">{missing.length ? missing.slice(0, 8).join(" · ") : "Nenhum gap relevante identificado."}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export function Jobs() {
  const toast = useToast();
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [scores, setScores] = useState<Record<number, MatchScore>>({});
  const [strategy, setStrategy] = useState<Record<number, StrategyRecommendation>>({});
  const [filters, setFilters] = useState({ q: "", company: "", location: "", remote: "all", priority: "all" });
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [provider, setProvider] = useState("all");
  const [providers, setProviders] = useState<Array<{ provider: string; enabled: boolean }>>([]);
  const [term, setTerm] = useState(user?.target_role || "");
  const [stateFilter, setStateFilter] = useState("");
  const [cityFilter, setCityFilter] = useState("");
  const [workplaceTypes, setWorkplaceTypes] = useState("remote,hybrid,on-site");
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});
  const [showOriginal, setShowOriginal] = useState<Record<number, boolean>>({});
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [totalJobs, setTotalJobs] = useState(0);
  const [hiddenIrrelevant, setHiddenIrrelevant] = useState(0);
  const [includeIrrelevant, setIncludeIrrelevant] = useState(false);

  async function load(pageToLoad = page) {
    setLoading(true);
    try {
      const data = await listJobs(filters.q || undefined, pageToLoad, pageSize, includeIrrelevant);
      setJobs(data.items);
      setTotalJobs(data.total);
      setHiddenIrrelevant(data.hiddenIrrelevant);
      const strategyData = await getStrategyRecommendations(Math.min(pageToLoad * pageSize, 100)).catch(() => []);
      setStrategy(Object.fromEntries(strategyData.map((item) => [item.job_id, item])));
    } catch (err) {
      toast.error("Erro ao carregar vagas", getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(1);
    listProviders().then(setProviders).catch((err) => toast.error("Erro ao carregar providers", getApiError(err)));
  }, []);

  useEffect(() => {
    if (!term && user?.target_role) setTerm(user.target_role);
  }, [term, user?.target_role]);

  useEffect(() => {
    if (!loading) load(1);
  }, [includeIrrelevant]);

  const totalPages = Math.max(1, Math.ceil(totalJobs / pageSize));

  async function goToPage(nextPage: number) {
    const safePage = Math.max(1, Math.min(totalPages, nextPage));
    setPage(safePage);
    await load(safePage);
  }

  const filtered = useMemo(() => {
    return jobs.filter((job) => {
      const byCompany = filters.company ? job.company.toLowerCase().includes(filters.company.toLowerCase()) : true;
      const byLocation = filters.location ? job.location.toLowerCase().includes(filters.location.toLowerCase()) : true;
      const byRemote = filters.remote === "all" ? true : String(job.remote) === filters.remote;
      const itemStrategy = strategy[job.id];
      const byPriority = filters.priority === "all" ? true : itemStrategy?.priority === filters.priority;
      return byCompany && byLocation && byRemote && byPriority;
    });
  }, [jobs, filters, strategy]);

  async function handleScore(jobId: number) {
    setActionLoading((prev) => ({ ...prev, [`score-${jobId}`]: true }));
    try {
      const score = await scoreJob(jobId);
      setScores((prev) => ({ ...prev, [jobId]: score }));
      toast.success("Análise concluída", `Match calculado: ${score.score}%`);
    } catch (err) {
      toast.error("Erro ao analisar vaga", getApiError(err));
    } finally {
      setActionLoading((prev) => ({ ...prev, [`score-${jobId}`]: false }));
    }
  }

  async function handleApply(jobId: number) {
    setActionLoading((prev) => ({ ...prev, [`apply-${jobId}`]: true }));
    try {
      await createApplication(jobId, "saved");
      toast.success("Adicionada à lista", "A vaga foi salva no seu acompanhamento.");
    } catch (err) {
      toast.error("Erro ao adicionar à lista", getApiError(err));
    } finally {
      setActionLoading((prev) => ({ ...prev, [`apply-${jobId}`]: false }));
    }
  }

  async function handleDelete(jobId: number) {
    const confirmed = window.confirm("Apagar esta vaga? Esta ação remove a vaga apenas deste tenant e não pode ser desfeita.");
    if (!confirmed) return;
    setActionLoading((prev) => ({ ...prev, [`delete-`]: true }));
    try {
      await deleteJob(jobId);
      setJobs((prev) => prev.filter((job) => job.id !== jobId));
      setScores((prev) => { const next = { ...prev }; delete next[jobId]; return next; });
      setStrategy((prev) => { const next = { ...prev }; delete next[jobId]; return next; });
      toast.success("Vaga apagada", "A lista foi atualizada.");
    } catch (err) {
      toast.error("Erro ao apagar vaga", getApiError(err));
    } finally {
      setActionLoading((prev) => ({ ...prev, [`delete-`]: false }));
    }
  }

  async function handleIngest() {
    setIngesting(true);
    try {
      const selectedProviders =
        provider === "all"
          ? providers.map((p) => p.provider)
          : [provider];

      let totalInserted = 0;
      let totalSkipped = 0;

      for (const p of selectedProviders) {
        const result = await ingestJobs(p, 300, {
          term,
          state: stateFilter,
          city: cityFilter,
          workplace_types: workplaceTypes,
        });

        totalInserted += result.inserted;
        totalSkipped += result.skipped;
      }

      toast.success(
        "Importação concluída",
        `${totalInserted} novas, ${totalSkipped} ignoradas.`
      );

      setPage(1);
      await load(1);
    } catch (err) {
      toast.error("Erro na importação", getApiError(err));
    } finally {
      setIngesting(false);
    }
  }

  return (
    <div className="page-shell" data-tour="jobs-page">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
        <div>
          <h1 className="page-title">Vagas</h1>
          <p className="page-subtitle">Importe, analise e organize oportunidades sem perder o controle.</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <select className="input min-w-44" value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="all">Todas as Plataformas</option>

            {providers.map((item) => {
              let label = item.provider;

              if (item.provider === "jobspy") {
                label = "Multiplataforma — Indeed e Google Jobs";
              }

              if (item.provider === "vagas") {
                label = "Vagas.com";
              }

              if (item.provider === "gupy") {
                label = "Gupy";
              }

              if (item.provider === "remoteok") {
                label = "RemoteOK";
              }

              if (item.provider === "linkedin") {
                label = "LinkedIn (Experimental)";
              }

              if (item.provider === "infojobs") {
                label = "InfoJobs";
              }

              return (
                <option key={item.provider} value={item.provider}>
                  {label}
                </option>
              );
            })}
          </select>
          <button className="btn-primary" onClick={handleIngest} disabled={ingesting}>
            {ingesting ? <Spinner label="Importando..." /> : "Importar vagas"}
          </button>
        </div>
      </div>

      <div className="soft-card grid gap-3 p-4 md:grid-cols-4">
        <div className="md:col-span-4"><p className="section-eyebrow">Filtros da busca</p></div>
        <input className="input" placeholder="Termo" value={term} onChange={(e) => setTerm(e.target.value)} />
        <input className="input" placeholder="Estado" value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} />
        <input className="input" placeholder="Cidade" value={cityFilter} onChange={(e) => setCityFilter(e.target.value)} />
        <input className="input" placeholder="remote,hybrid" value={workplaceTypes} onChange={(e) => setWorkplaceTypes(e.target.value)} />
      </div>

      <div className="soft-card grid gap-3 p-4 md:grid-cols-5">
        <div className="relative md:col-span-2">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input className="input pl-9" placeholder="Título ou texto" value={filters.q} onChange={(e) => { setPage(1); setFilters({ ...filters, q: e.target.value }); }} />
        </div>
        <input className="input" placeholder="Empresa" value={filters.company} onChange={(e) => setFilters({ ...filters, company: e.target.value })} />
        <input className="input" placeholder="Local" value={filters.location} onChange={(e) => setFilters({ ...filters, location: e.target.value })} />
        <select className="input" value={filters.priority} onChange={(e) => setFilters({ ...filters, priority: e.target.value })}>
          <option value="all">Todas prioridades</option>
          <option value="HIGH_PRIORITY">Alta prioridade</option>
          <option value="MEDIUM_PRIORITY">Média prioridade</option>
          <option value="LOW_PRIORITY">Baixa prioridade</option>
        </select>
        <label className="flex items-center gap-2 text-sm text-slate-600 md:col-span-5">
          <input
            type="checkbox"
            checked={includeIrrelevant}
            onChange={(event) => {
              setIncludeIrrelevant(event.target.checked);
              setPage(1);
            }}
          />
          Mostrar também vagas fora do cargo-alvo
          {!includeIrrelevant && hiddenIrrelevant > 0 && <span>({hiddenIrrelevant} ocultadas)</span>}
        </label>
        <button className="btn-secondary md:col-span-5" onClick={() => { setPage(1); load(1); }}>Atualizar lista</button>
      </div>

      {loading ? (
        <div className="grid gap-4"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>
      ) : (
        <div className="grid gap-4">
          {filtered.map((job) => {
            const score = scores[job.id];
            const strategyItem = strategy[job.id];
            return (
              <article key={job.id} className="job-card">
                <div className="job-card-layout">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-lg font-bold">{job.title}</h2>
                      {job.remote && <span className="badge">Remoto</span>}
                      {strategyItem && <StrategyBadge priority={strategyItem.priority} score={strategyItem.strategy_score} />}
                      {job.role_relevance_score != null && <span className="badge">Aderência {Math.round(job.role_relevance_score)}%</span>}
                    </div>
                    <div className="mt-2"><JobSourceBadge source={job.source} /></div>
                    <p className="mt-2 text-slate-500">{job.company} • {job.location || "Local não informado"}</p>
                    <div className="mt-4 flex flex-wrap gap-4">
                      {score && <MatchProgress score={score.score} />}
                      {strategyItem && <MatchProgress score={strategyItem.strategy_score} label="Prioridade" />}
                    </div>
                    {(job.title_original || job.description_original) && (
                      <button
                        className="mt-3 text-xs font-bold text-slate-500 underline"
                        onClick={() => setShowOriginal((prev) => ({ ...prev, [job.id]: !prev[job.id] }))}
                      >
                        {showOriginal[job.id] ? "Ver português" : "Ver original"}
                      </button>
                    )}
                    <DescriptionPreview text={showOriginal[job.id] ? (job.description_original || job.description) : job.description} />
                    {score && <MatchAnalysisPanel score={score} />}
                  </div>
                  <div className="action-rail">
                    {job.url ? (
                      <a
                        className="btn-primary justify-center text-xs"
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        title="Você será redirecionado para o site original"
                      >
                        🔗 Candidatar

                      </a>
                    ) : (
                      <button className="btn-primary justify-center opacity-50" disabled title="Link não disponível">Link não disponível</button>
                    )}
                    <button className="btn-secondary justify-center text-xs" onClick={() => handleApply(job.id)} disabled={actionLoading[`apply-${job.id}`]}>
                      {actionLoading[`apply-${job.id}`] ? <Spinner label="Adicionando..." /> : "Adicionar à lista"}
                    </button>
                    <Link className="btn-secondary justify-center text-xs" to={`/jobs/${job.id}`}>Detalhe</Link>
                    <button className="btn-secondary justify-center text-xs" onClick={() => handleScore(job.id)} disabled={actionLoading[`score-${job.id}`]}>
                      {actionLoading[`score-${job.id}`] ? <Spinner label="Analisando..." /> : "Analisar vaga"}
                    </button>
                    <button className="btn-secondary justify-center border-red-200 text-red-700 hover:bg-red-50" onClick={() => handleDelete(job.id)} disabled={actionLoading[`delete-${job.id}`]}>
                      {actionLoading[`delete-${job.id}`] ? <Spinner label="Apagando..." /> : <><Trash2 className="mr-2 h-4 w-4" /> Apagar vaga</>}
                    </button>
                  </div>
                </div>
              </article>
            );
          })}
          {filtered.length === 0 && <EmptyState title="Nenhuma vaga encontrada" description="Importe vagas ou ajuste os filtros." />}

          {totalJobs > pageSize && (
            <div className="pagination-bar">
              <span>
                Mostrando {jobs.length} de {totalJobs} vagas · Página {page} de {totalPages}
              </span>
              <div className="flex gap-2">
                <button className="btn-secondary" onClick={() => goToPage(page - 1)} disabled={page <= 1 || loading}>Anterior</button>
                <button className="btn-secondary" onClick={() => goToPage(page + 1)} disabled={page >= totalPages || loading}>Próxima</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
