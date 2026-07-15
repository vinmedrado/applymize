import { useEffect, useState } from "react";
import { PageLoading } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { getSkillGapRoadmap } from "../services/advanced";
import { SkillGapRoadmap } from "../types";

function priorityClass(priority: string) {
  if (priority === "alta") return "bg-red-50 text-red-700";
  if (priority === "média") return "bg-amber-50 text-amber-700";
  return "bg-slate-100 text-slate-700";
}

export function SkillGap() {
  const toast = useToast();
  const [data, setData] = useState<SkillGapRoadmap | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSkillGapRoadmap().then(setData).catch((err) => toast.error("Erro no roadmap", getApiError(err))).finally(() => setLoading(false));
  }, []);

  if (loading || !data) return <PageLoading label="Carregando evolução..." />;

  return (
    <div className="space-y-6" data-tour="skill-gap-page">
      <section className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <p className="text-sm text-slate-500">Skill Gap Roadmap</p>
        <h1 className="mt-2 text-3xl font-bold">Evolução profissional</h1>
        <p className="mt-2 text-sm text-slate-500">{data.jobs_analyzed} vagas analisadas.</p>
      </section>
      {data.warnings.map((w) => <div key={w} className="rounded-2xl bg-amber-50 p-4 text-sm text-amber-800">{w}</div>)}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard title="Skills fortes">
          <div className="flex flex-wrap gap-2">{data.strong_skills.map((x) => <span className="badge" key={x.skill}>{x.skill} • {x.count}</span>)}</div>
        </SectionCard>
        <SectionCard title="Skills faltantes">
          <div className="flex flex-wrap gap-2">{data.missing_skills.map((x) => <span className="badge" key={x.skill}>{x.skill} • {x.count}</span>)}</div>
        </SectionCard>
      </div>
      <SectionCard title="Roadmap priorizado">
        <div className="grid gap-3">{data.roadmap.map((item) => (
          <div key={item.skill} className="rounded-2xl border border-slate-200 p-4">
            <div className="flex flex-wrap items-center gap-2"><span className={`rounded-full px-3 py-1 text-xs font-bold ${priorityClass(item.priority)}`}>{item.priority}</span><b>{item.skill}</b><span className="text-sm text-slate-500">aparece em {item.count} vagas</span></div>
            <p className="mt-2 text-sm text-slate-600">{item.action}</p>
          </div>
        ))}</div>
      </SectionCard>
    </div>
  );
}
