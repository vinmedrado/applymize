import { useEffect, useState } from "react";
import { Activity, BarChart3, Bot, Building2, ShieldCheck, Users } from "lucide-react";
import { getAdminOverview } from "../services/admin";
import { PremiumHero, PremiumMetric, PremiumPanel, PremiumTimeline, MiniFeature } from "../components/Premium";

export function AdminAnalytics() {
  const [data, setData] = useState<any>(null);
  useEffect(() => { getAdminOverview().then(setData).catch(() => setData(null)); }, []);
  const metrics = data?.metrics || {};
  const status = data?.application_status || {};
  const aiFeatures = data?.ai_features || {};
  const topStatus = Object.entries(status).slice(0, 5);
  const topAi = Object.entries(aiFeatures).slice(0, 5);

  return (
    <div className="space-y-6">
      <PremiumHero
        eyebrow="Admin OS"
        title="Centro executivo para acompanhar crescimento, uso de IA e saúde do tenant."
        description="Uma camada administrativa premium para operar o Applymize como SaaS real: usuários, vagas, candidaturas, consumo de IA e evolução comercial em uma visão única."
        icon={ShieldCheck}
      >
        <div className="grid min-w-[280px] gap-3 sm:grid-cols-2 lg:min-w-[420px]">
          <div className="rounded-3xl border border-white/15 bg-white/10 p-4 text-white backdrop-blur">
            <p className="text-xs font-black uppercase text-blue-100">Plano</p>
            <p className="mt-2 text-2xl font-black">{data?.tenant?.plan || "Pro"}</p>
          </div>
          <div className="rounded-3xl border border-white/15 bg-white/10 p-4 text-white backdrop-blur">
            <p className="text-xs font-black uppercase text-blue-100">Tenant</p>
            <p className="mt-2 truncate text-2xl font-black">{data?.tenant?.name || "Applymize"}</p>
          </div>
        </div>
      </PremiumHero>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <PremiumMetric label="Usuários" value={metrics.users || 0} helper="Contas ativas no tenant" trend="+ SaaS" />
        <PremiumMetric label="Vagas" value={metrics.jobs || 0} helper="Base indexada para matching" />
        <PremiumMetric label="Candidaturas" value={metrics.applications || 0} helper="Pipeline operacional" />
        <PremiumMetric label="Eventos IA" value={metrics.ai_events || 0} helper="Uso de copilotos e análises" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <PremiumPanel title="Status das candidaturas" subtitle="Distribuição resumida para entender gargalos do funil.">
          {topStatus.length ? (
            <div className="space-y-3">
              {topStatus.map(([key, value]) => (
                <div key={key} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm font-black capitalize text-slate-700">{key}</span>
                    <span className="text-lg font-black text-slate-950">{String(value)}</span>
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-white">
                    <div className="h-2 rounded-full bg-blue-600" style={{ width: `${Math.min(100, Number(value) * 12 || 8)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-3xl bg-slate-50 p-6 text-sm leading-6 text-slate-600">Ainda não há candidaturas suficientes para gerar distribuição. Conforme o sistema for usado, esta área vira um painel executivo real.</div>
          )}
        </PremiumPanel>

        <PremiumPanel title="Uso de IA por feature" subtitle="Controle de custo e valor percebido por módulo.">
          {topAi.length ? (
            <PremiumTimeline items={topAi.map(([key, value]) => ({ title: key, description: `${value} eventos registrados`, status: "IA" }))} />
          ) : (
            <div className="grid gap-3">
              <MiniFeature icon={Bot} title="Applymize IA" description="Histórico e respostas contextuais aparecerão aqui." />
              <MiniFeature icon={Activity} title="Fit Cultural" description="Eventos de treino comportamental alimentam a visão de uso." />
            </div>
          )}
        </PremiumPanel>
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <MiniFeature icon={Building2} title="Multiempresa" description="Estrutura preparada para separar tenants, roles e dados de cada cliente." />
        <MiniFeature icon={Users} title="Roles SaaS" description="Base para owner, recruiter, analyst e candidate dentro do mesmo ecossistema." />
        <MiniFeature icon={BarChart3} title="Analytics real" description="Métricas começam simples e evoluem para retenção, funil, uso e custo por IA." />
      </div>
    </div>
  );
}
