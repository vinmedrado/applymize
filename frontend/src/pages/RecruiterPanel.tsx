import { useEffect, useState } from "react";
import { Briefcase, Building2, Kanban, ShieldCheck, Sparkles, Users } from "lucide-react";
import { getRecruiterDashboard } from "../services/admin";
import { PremiumHero, PremiumMetric, PremiumPanel, MiniFeature } from "../components/Premium";

const stages = ["saved", "applied", "screening", "interview", "technical", "offer", "hired", "rejected"];
const labels: Record<string, string> = {
  saved: "Salvos",
  applied: "Aplicados",
  screening: "Triagem",
  interview: "Entrevista",
  technical: "Técnico",
  offer: "Oferta",
  hired: "Contratado",
  rejected: "Reprovado"
};

export function RecruiterPanel() {
  const [data, setData] = useState<any>(null);
  useEffect(() => { getRecruiterDashboard().then(setData).catch(() => setData(null)); }, []);
  const summary = data?.summary || {};

  return (
    <div className="space-y-6">
      <PremiumHero
        eyebrow="Recruiter Workspace"
        title="Pipeline inteligente para vender o Applymize como HRTech B2B."
        description="Uma visão premium para recrutadores acompanharem candidatos, ranking IA, etapas de seleção e qualidade do funil em uma experiência única."
        icon={Building2}
      >
        <div className="rounded-3xl border border-white/15 bg-white/10 p-4 text-white backdrop-blur lg:min-w-[360px]">
          <p className="text-xs font-black uppercase tracking-wide text-blue-100">Recruiter Intelligence</p>
          <div className="mt-4 grid grid-cols-3 gap-3">
            <div><p className="text-2xl font-black">{summary.active_jobs || 0}</p><p className="text-xs text-blue-100">vagas</p></div>
            <div><p className="text-2xl font-black">{summary.candidates || 0}</p><p className="text-xs text-blue-100">candidatos</p></div>
            <div><p className="text-2xl font-black">{summary.avg_score || 0}%</p><p className="text-xs text-blue-100">score</p></div>
          </div>
        </div>
      </PremiumHero>

      <div className="grid gap-4 md:grid-cols-3">
        <PremiumMetric label="Vagas ativas" value={summary.active_jobs || 0} helper="Posições em acompanhamento" />
        <PremiumMetric label="Candidatos" value={summary.candidates || 0} helper="Pessoas no pipeline" />
        <PremiumMetric label="Score médio" value={`${summary.avg_score || 0}%`} helper="Aderência média calculada" trend="IA" />
      </div>

      <PremiumPanel title="Kanban de recrutamento" subtitle="Pipeline visual para operação B2B e triagem inteligente." action={<span className="badge">Mock + dados reais</span>}>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8">
          {stages.map((stage, index) => (
            <div key={stage} className="rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-4 shadow-sm">
              <div className="flex items-center justify-between gap-2">
                <p className="text-[11px] font-black uppercase tracking-wide text-slate-500">{labels[stage]}</p>
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-50 text-xs font-black text-blue-700">{index + 1}</span>
              </div>
              <p className="mt-4 text-3xl font-black text-slate-950">{data?.pipeline?.[stage] || 0}</p>
            </div>
          ))}
        </div>
      </PremiumPanel>

      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <PremiumPanel title="Ranking IA de candidatos" subtitle="Quando houver candidaturas, o painel prioriza quem tem maior aderência.">
          <div className="space-y-3">
            {(data?.candidates || []).map((item: any) => (
              <div key={item.application_id} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-black text-slate-950">{item.candidate}</p>
                    <p className="text-sm text-slate-500">{item.job} • {item.company}</p>
                  </div>
                  <span className="w-fit rounded-full bg-blue-50 px-3 py-1 text-sm font-black text-blue-700">{item.score}% match</span>
                </div>
              </div>
            ))}
            {!(data?.candidates || []).length && (
              <div className="rounded-3xl bg-slate-50 p-6 text-sm leading-6 text-slate-600">
                Sem candidatos ainda. Conforme candidaturas entrarem, o ranking aparecerá aqui com score, justificativa e etapa recomendada.
              </div>
            )}
          </div>
        </PremiumPanel>

        <div className="grid gap-4">
          <MiniFeature icon={Sparkles} title="Ranking explicável" description="Cada candidato pode receber score com justificativa para recrutadores." />
          <MiniFeature icon={ShieldCheck} title="Governança" description="Estrutura preparada para roles, auditoria e separação por tenant." />
          <MiniFeature icon={Users} title="Experiência B2B" description="O Applymize deixa de ser apenas candidato e vira plataforma de seleção." />
        </div>
      </div>
    </div>
  );
}
