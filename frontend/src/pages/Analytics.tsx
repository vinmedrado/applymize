import { useEffect, useState } from "react";
import { PageLoading } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { getAnalyticsOverview } from "../services/advanced";
import { AnalyticsOverview } from "../types";

function Metric({ label, value }: { label: string; value: string | number }) {
  return <div className="card p-5"><p className="text-sm text-slate-500">{label}</p><p className="mt-2 text-3xl font-bold">{value}</p></div>;
}

function BarList({ data, labelKey = "source" }: { data: Array<any>; labelKey?: string }) {
  const max = Math.max(...data.map((x) => x.count), 1);
  return (
    <div className="space-y-3">
      {data.map((x) => {
        const label = x[labelKey] || x.role || x.source || "Item";
        return (
          <div key={label}>
            <div className="mb-1 flex justify-between text-sm"><span>{label}</span><b>{x.count}</b></div>
            <div className="h-2 rounded-full bg-slate-100"><div className="h-2 rounded-full bg-blue-600" style={{ width: `${Math.max(8, (x.count / max) * 100)}%` }} /></div>
          </div>
        );
      })}
    </div>
  );
}

function Trend({ data }: { data: NonNullable<AnalyticsOverview["score_trend"]> }) {
  if (!data?.length) return <p className="text-sm text-slate-500">Ainda não há histórico suficiente.</p>;
  const width = 600;
  const height = 190;
  const points = data.map((x, i) => {
    const px = data.length === 1 ? width / 2 : (i / (data.length - 1)) * width;
    const py = height - (Math.min(Math.max(x.career_score, 0), 100) / 100) * height;
    return `${px},${py}`;
  }).join(" ");
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-48 w-full rounded-2xl bg-slate-50 p-3">
      <polyline points={points} fill="none" stroke="currentColor" strokeWidth="4" className="text-blue-600" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Analytics() {
  const toast = useToast();
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyticsOverview().then(setData).catch((err) => toast.error("Erro no analytics", getApiError(err))).finally(() => setLoading(false));
  }, []);

  if (loading || !data) return <PageLoading label="Carregando analytics..." />;

  return (
    <div className="space-y-6" data-tour="analytics-page">
      <section className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <p className="text-sm text-slate-500">Analytics pessoal</p>
        <h1 className="mt-2 text-3xl font-bold">Métricas da sua busca</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-500">Acompanhe evolução, decisões, qualidade das vagas e eficiência da sua estratégia.</p>
      </section>

      {data.warnings.map((w) => <div key={w} className="rounded-2xl bg-amber-50 p-4 text-sm text-amber-800">{w}</div>)}

      <div className="grid gap-4 md:grid-cols-4 xl:grid-cols-8">
        <Metric label="Vagas totais" value={data.jobs_total} />
        <Metric label="Vagas analisadas" value={data.jobs_analyzed} />
        <Metric label="Candidaturas" value={data.applications_total} />
        <Metric label="Taxa de resposta" value={`${data.response_rate}%`} />
        <Metric label="Match médio" value={`${data.average_match_score}%`} />
        <Metric label="Vagas fortes" value={data.high_match_jobs ?? 0} />
        <Metric label="Score carreira" value={`${data.career_score ?? 0}%`} />
        <Metric label="Eficiência" value={`${data.career_efficiency ?? 0}%`} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard title="Score evolutivo" subtitle="Histórico diário da sua busca"><Trend data={data.score_trend || []} /></SectionCard>
        <SectionCard title="Histórico de decisões" subtitle="Últimas ações relevantes">
          <div className="space-y-3">
            {(data.decision_history || []).slice(0, 8).map((item) => (
              <div key={item.id} className="rounded-2xl border border-slate-200 p-3">
                <div className="flex justify-between gap-3"><p className="font-semibold">{item.title}</p>{item.score > 0 && <b className="text-blue-700">{item.score}%</b>}</div>
                <p className="mt-1 text-xs uppercase tracking-wide text-slate-400">{item.type.replaceAll("_", " ")}</p>
                {item.detail && <p className="mt-2 line-clamp-2 text-sm text-slate-600">{item.detail}</p>}
              </div>
            ))}
            {!(data.decision_history || []).length && <p className="text-sm text-slate-500">Nenhuma decisão registrada ainda.</p>}
          </div>
        </SectionCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard title="Fontes mais usadas"><BarList data={data.top_sources} labelKey="source" /></SectionCard>
        <SectionCard title="Cargos mais frequentes"><BarList data={data.top_roles} labelKey="role" /></SectionCard>
      </div>
    </div>
  );
}
