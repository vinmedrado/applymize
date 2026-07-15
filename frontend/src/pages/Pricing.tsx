import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, CheckCircle2, Shield, Sparkles, Bot, Building2, CreditCard } from "lucide-react";
import { BrandLogo } from "../components/BrandLogo";
import { getPublicPlans, Plan } from "../services/billing";
import { MiniFeature, PremiumCTA } from "../components/Premium";

export function Pricing() {
  const [plans, setPlans] = useState<Plan[]>([]);
  useEffect(() => { getPublicPlans().then((data) => setPlans(data.plans)).catch(() => setPlans([])); }, []);
  const fallback = [
    { code: "free", name: "Free", monthly_price: 0, annual_price: 0, description: "Validação inicial.", features: ["ATS básico", "Demo IA"] },
    { code: "pro", name: "Pro", monthly_price: 49, annual_price: 490, description: "Copiloto de carreira completo.", features: ["IA contextual", "LinkedIn Analyzer", "Fit Cultural"] },
    { code: "recruiter", name: "Recruiter", monthly_price: 149, annual_price: 1490, description: "Inteligência para recrutadores.", features: ["Pipeline", "Ranking IA", "Analytics RH"] },
  ] as Plan[];
  const list = plans.length ? plans : fallback;

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_#dbeafe,_transparent_34rem),linear-gradient(180deg,#f8fafc,#eef5fb)]">
      <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/80 px-5 py-4 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <BrandLogo />
          <div className="flex items-center gap-2">
            <Link to="/" className="btn-secondary hidden sm:inline-flex">Início</Link>
            <Link to="/login" className="btn-primary">Entrar</Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-14">
        <section className="relative overflow-hidden rounded-[2rem] border border-blue-100 bg-slate-950 p-8 text-white shadow-2xl shadow-slate-300/40 sm:p-10 lg:p-14">
          <div className="absolute -right-20 -top-20 h-80 w-80 rounded-full bg-blue-500/30 blur-3xl" />
          <div className="absolute -bottom-24 left-1/4 h-80 w-80 rounded-full bg-cyan-400/20 blur-3xl" />
          <div className="relative mx-auto max-w-4xl text-center">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-black text-blue-100"><Sparkles size={16} /> SaaS monetizável</div>
            <h1 className="text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">Planos para carreira, IA e recrutamento inteligente.</h1>
            <p className="mt-5 text-lg leading-8 text-blue-50/85">Estrutura preparada para Stripe, limites por plano, venda B2C e expansão B2B com painel recruiter.</p>
          </div>
        </section>

        <div className="mt-12 grid gap-5 lg:grid-cols-4">
          {list.map((plan) => (
            <section key={plan.code} className={`relative rounded-[1.75rem] border bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl ${plan.code === "pro" ? "border-blue-500 ring-4 ring-blue-100" : "border-slate-200"}`}>
              {plan.code === "pro" && <span className="absolute -top-3 left-6 rounded-full bg-blue-700 px-3 py-1 text-xs font-black text-white">Mais vendido</span>}
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-700"><CreditCard /></div>
              <h2 className="mt-5 text-2xl font-black text-slate-950">{plan.name}</h2>
              <p className="mt-3 min-h-12 text-sm leading-6 text-slate-600">{plan.description}</p>
              <p className="mt-6 text-4xl font-black text-slate-950">{plan.monthly_price === null ? "Sob consulta" : `R$${plan.monthly_price}`}</p>
              {plan.monthly_price !== null && <p className="text-sm text-slate-500">/mês</p>}
              <div className="mt-6 space-y-3">{plan.features.map((feature) => <p key={feature} className="flex gap-2 text-sm text-slate-700"><CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" /> {feature}</p>)}</div>
              <Link to="/register" className="btn-primary mt-7 w-full justify-center">Começar <ArrowRight className="ml-2 h-4 w-4" /></Link>
            </section>
          ))}
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          <MiniFeature icon={Bot} title="IA com limite por plano" description="Applymize IA, LinkedIn Analyzer e Fit podem respeitar cotas comerciais." />
          <MiniFeature icon={Building2} title="Recruiter B2B" description="Plano dedicado para empresas com pipeline e ranking IA de candidatos." />
          <MiniFeature icon={Shield} title="Checkout seguro" description="Sem chaves reais, o sistema simula checkout para demo; com Stripe, usa Price IDs e webhooks." />
        </div>

        <div className="mt-10">
          <PremiumCTA>
            <div className="grid gap-5 lg:grid-cols-[1fr_auto] lg:items-center">
              <div>
                <h2 className="text-2xl font-black">Pronto para demonstrar como produto comercial.</h2>
                <p className="mt-2 text-sm leading-6 text-blue-100">A página mostra valor antes do login e conecta com o ecossistema interno: IA, ATS, Fit, LinkedIn e Recruiter.</p>
              </div>
              <Link to="/demo" className="rounded-xl bg-white px-5 py-3 text-center font-black text-slate-950">Ver demonstração</Link>
            </div>
          </PremiumCTA>
        </div>
      </main>
    </div>
  );
}
