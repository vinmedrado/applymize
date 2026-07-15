import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight, FileCheck2, History, Radio, Sparkles, TrendingUp } from "lucide-react";
import { StatCard } from "../components/StatCard";
import { SectionCard } from "../components/SectionCard";
import { SkeletonCard } from "../components/Loading";
import { EmptyState } from "../components/EmptyState";
import { useToast } from "../context/ToastContext";
import { listApplications } from "../services/applications";
import { rankJobs } from "../services/jobs";
import { getStrategyRecommendations } from "../services/strategy";
import { getDashboardSummary, dashboardRealtimeUrl, DashboardSummary } from "../services/dashboard";
import { getAccessToken } from "../services/tokenStorage";
import { PriorityBadge } from "../components/PriorityBadge";
import { Application, RankItem, StrategyRecommendation } from "../types";

function MiniMetric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-950">{value}</p>
    </div>
  );
}

function BarList({ data }: { data: Array<{ label?: string; source?: string; count: number }> }) {
  const max = Math.max(...data.map((x) => x.count), 1);
  return (
    <div className="space-y-3">
      {data.map((item) => {
        const label = item.label || item.source || "Item";
        return (
          <div key={label}>
            <div className="mb-1 flex justify-between text-sm">
              <span className="font-medium text-slate-700">{label}</span>
              <span className="text-slate-500">{item.count}</span>
            </div>
            <div className="h-2 rounded-full bg-slate-100">
              <div className="h-2 rounded-full bg-blue-600" style={{ width: `${Math.max(8, (item.count / max) * 100)}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function TrendChart({ data }: { data: NonNullable<DashboardSummary["score_trend"]> }) {
  if (!data.length) {
    return <p className="text-sm text-slate-500">Sem histórico suficiente ainda. O sistema começa a gravar a evolução a partir de agora.</p>;
  }
  const width = 560;
  const height = 180;
  const points = data.map((item, index) => {
    const x = data.length === 1 ? width / 2 : (index / (data.length - 1)) * width;
    const y = height - (Math.min(Math.max(item.career_score, 0), 100) / 100) * height;
    return `${x},${y}`;
  }).join(" ");
  const latest = data[data.length - 1];
  return (
    <div>
      <svg viewBox={`0 0 ${width} ${height}`} className="h-44 w-full overflow-visible rounded-2xl bg-slate-50 p-3">
        <polyline points={points} fill="none" stroke="currentColor" strokeWidth="4" className="text-blue-600" strokeLinecap="round" strokeLinejoin="round" />
        {data.map((item, index) => {
          const x = data.length === 1 ? width / 2 : (index / (data.length - 1)) * width;
          const y = height - (Math.min(Math.max(item.career_score, 0), 100) / 100) * height;
          return <circle key={`${item.date}-${index}`} cx={x} cy={y} r="5" className="fill-white stroke-blue-600" strokeWidth="3" />;
        })}
      </svg>
      <p className="mt-3 text-sm text-slate-600">
        Score evolutivo atual: <strong>{latest.career_score}%</strong> · Match médio: <strong>{latest.average_match_score}%</strong>
      </p>
    </div>
  );
}

function DecisionHistoryList({ items }: { items: NonNullable<DashboardSummary["decision_history"]> }) {
  if (!items.length) {
    return <p className="text-sm text-slate-500">Nenhuma decisão registrada ainda. Ao analisar vagas e atualizar candidaturas, o histórico aparece aqui.</p>;
  }
  return (
    <div className="space-y-3">
      {items.slice(0, 6).map((item) => (
        <div key={item.id} className="rounded-2xl border border-slate-200 bg-white p-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="font-semibold text-slate-900">{item.title}</p>
            {item.score > 0 && <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">{item.score}%</span>}
          </div>
          <p className="mt-1 text-xs uppercase tracking-wide text-slate-400">{item.type.replaceAll("_", " ")}</p>
          {item.detail && <p className="mt-2 line-clamp-2 text-sm text-slate-600">{item.detail}</p>}
        </div>
      ))}
    </div>
  );
}

export function Dashboard() {
  const toast = useToast();
  const [stats, setStats] = useState<DashboardSummary | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [ranked, setRanked] = useState<RankItem[]>([]);
  const [strategy, setStrategy] = useState<StrategyRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [realtime, setRealtime] = useState(false);

  useEffect(() => {
    Promise.all([
      getDashboardSummary(),
      listApplications(),
      rankJobs(10).catch(() => []),
      getStrategyRecommendations(10).catch(() => []),
    ])
      .then(([statsData, appsData, rankData, strategyData]) => {
        setStats(statsData);
        setApplications(appsData);
        setRanked(rankData);
        setStrategy(strategyData);
      })
      .catch((err) => toast.error("Erro ao carregar dashboard", String(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;

    let socket: WebSocket | null = null;
    try {
      socket = new WebSocket(dashboardRealtimeUrl());
      socket.onopen = () => {
        socket?.send(JSON.stringify({ token }));
        setRealtime(true);
      };
      socket.onmessage = (event) => {
        try {
          setStats(JSON.parse(event.data));
        } catch {
          // ignora payload inválido sem quebrar o dashboard
        }
      };
      socket.onclose = () => setRealtime(false);
      socket.onerror = () => setRealtime(false);
    } catch {
      setRealtime(false);
    }

    return () => socket?.close();
  }, []);

  const latestApplications = useMemo(() => applications.slice(0, 5), [applications]);

  if (loading || !stats) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid gap-4 md:grid-cols-3"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-sm text-slate-500">Applymize Intelligence</p>
              <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${realtime ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200" : "bg-slate-100 text-slate-500"}`}>
                <Radio className="mr-1 h-3 w-3" /> {realtime ? "Tempo real ativo" : "Tempo real em espera"}
              </span>
            </div>
            <h1 className="mt-2 text-3xl font-bold">Seu painel de oportunidades</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-500">Dashboard com push realtime, gráficos, score evolutivo e histórico das decisões principais.</p>
          </div>
          <Link className="btn bg-white text-slate-950 hover:bg-slate-100" to="/jobs">Ver vagas <ArrowUpRight className="ml-2 h-4 w-4" /></Link>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Total de vagas" value={stats.total_jobs} helper="Vagas cadastradas no tenant" />
        <StatCard label="Candidaturas ativas" value={stats.active_applications} helper="Aplicadas, triagem, entrevista ou teste" />
        <StatCard label="Score de carreira" value={`${stats.career_score ?? 0}%`} helper="Evolução combinando match, atividade e resposta" />
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <MiniMetric label="Match médio" value={`${stats.average_match_score}%`} />
        <MiniMetric label="Vagas fortes" value={stats.high_match_jobs} />
        <MiniMetric label="Novas em 7 dias" value={stats.new_jobs_7d} />
        <MiniMetric label="Taxa de resposta" value={`${stats.response_rate}%`} />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <SectionCard title="Score evolutivo" subtitle="Tracking diário da sua busca" action={<TrendingUp className="h-5 w-5 text-slate-500" />}>
          <TrendChart data={stats.score_trend || []} />
        </SectionCard>
        <SectionCard title="Distribuição de score" subtitle="Qualidade das vagas analisadas">
          <BarList data={stats.score_buckets || []} />
        </SectionCard>
        <SectionCard title="Fontes principais" subtitle="Origem das vagas no banco">
          <BarList data={stats.top_sources || []} />
        </SectionCard>
      </div>

      <div data-tour="strategy">
        <SectionCard title="Recomendações" subtitle="TOP vagas priorizadas pelo Strategy Engine">
          <div className="grid gap-3">
            {strategy.slice(0, 5).map((item) => (
              <Link key={item.job_id} to={`/jobs/${item.job_id}`} className="rounded-2xl border border-slate-200 p-4 transition hover:border-slate-400 hover:shadow-sm">
                <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
                  <div>
                    <p className="font-semibold">{item.title}</p>
                    <p className="text-sm text-slate-500">{item.company} • {item.location || "Local não informado"}</p>
                    <p className="mt-2 text-sm text-slate-600">{item.explanation}</p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <PriorityBadge priority={item.priority} />
                    <span className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">{item.strategy_score}%</span>
                  </div>
                </div>
              </Link>
            ))}
            {strategy.length === 0 && <EmptyState title="Sem recomendações" description="Cadastre ou importe vagas para o Strategy Engine priorizar oportunidades." action={<Link className="btn-primary" to="/jobs">Ir para vagas</Link>} />}
          </div>
        </SectionCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <SectionCard title="Vagas recomendadas" subtitle="Amostra rápida do matching engine" action={<Sparkles className="h-5 w-5 text-slate-500" />}>
          <div className="space-y-3">
            {ranked.slice(0, 5).map((item, index) => (
              <Link key={item.job_id} to={`/jobs/${item.job_id}`} className="block rounded-2xl border border-slate-200 p-4 transition hover:border-slate-400 hover:shadow-sm">
                <div className="flex items-start justify-between gap-3">
                  <div><p className="text-xs font-semibold text-slate-400">#{index + 1}</p><p className="font-semibold">{item.title}</p><p className="text-sm text-slate-500">{item.company}</p></div>
                  <span className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">{item.score}%</span>
                </div>
                <p className="mt-2 line-clamp-2 text-sm text-slate-600">{item.explanation}</p>
              </Link>
            ))}
            {ranked.length === 0 && <EmptyState title="Nenhum ranking ainda" description="Cadastre ou importe vagas e gere o ranking para visualizar recomendações." action={<Link className="btn-primary" to="/jobs">Ir para vagas</Link>} />}
          </div>
        </SectionCard>

        <SectionCard title="Histórico de decisões" subtitle="Ações importantes registradas" action={<History className="h-5 w-5 text-slate-500" />}>
          <DecisionHistoryList items={stats.decision_history || []} />
        </SectionCard>

        <SectionCard title="Últimas candidaturas" subtitle="Status recentes do seu pipeline" action={<FileCheck2 className="h-5 w-5 text-slate-500" />}>
          <div className="space-y-3">
            {latestApplications.map((app) => (
              <div key={app.id} className="rounded-2xl border border-slate-200 p-4">
                <div className="flex items-center justify-between"><p className="font-semibold">Candidatura #{app.id}</p><span className="badge">{app.status}</span></div>
                <p className="mt-2 text-sm text-slate-500">Job ID: {app.job_id}</p>
              </div>
            ))}
            {latestApplications.length === 0 && <EmptyState title="Nenhuma candidatura" description="Crie uma candidatura a partir da tela de vagas para começar seu acompanhamento." action={<Link className="btn-primary" to="/jobs">Buscar vagas</Link>} />}
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
