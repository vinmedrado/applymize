import { Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  Bot,
  Brain,
  Briefcase,
  CheckCircle2,
  ClipboardCheck,
  History,
  Linkedin,
  MessageCircle,
  Radar,
  ShieldCheck,
  Sparkles,
  Target,
  Users,
  Wand2,
} from "lucide-react";
import { BrandLogo } from "../components/BrandLogo";
import { FeatureCard, MarketingSection, PublicShell } from "../components/marketing";

const features = [
  { icon: <Bot size={22} />, title: "Applymize IA", description: "Assistente contextual baseado no currículo, perfil, histórico e objetivos profissionais." },
  { icon: <ClipboardCheck size={22} />, title: "ATS Analyzer", description: "Score, gaps, palavras-chave e leitura otimizada para sistemas e recrutadores." },
  { icon: <Linkedin size={22} />, title: "LinkedIn Analyzer", description: "Showcase público premium e análise real protegida apenas na área autenticada." },
  { icon: <Users size={22} />, title: "Applymize Fit", description: "Preparação visual para testes Gupy, entrevistas, cultura, comunicação e liderança." },
  { icon: <Target size={22} />, title: "Smart Matching", description: "Priorização de vagas por aderência, localização, senioridade e requisitos reais." },
  { icon: <MessageCircle size={22} />, title: "WhatsApp Alerts", description: "Alertas automáticos de oportunidades relevantes no canal mais prático para o usuário." },
  { icon: <Radar size={22} />, title: "Multi-provider Jobs", description: "Centralização de oportunidades de diferentes fontes sem busca manual repetitiva." },
  { icon: <History size={22} />, title: "Histórico IA", description: "Conversas persistentes para entrevistas, currículo, LinkedIn e posicionamento." },
];

function MetricPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
      <p className="text-xs font-black uppercase tracking-wide text-blue-100">{label}</p>
      <p className="mt-2 text-2xl font-black text-white">{value}</p>
    </div>
  );
}

function DashboardPreview() {
  return (
    <div className="relative z-10 rounded-[2rem] border border-slate-200 bg-white p-4 shadow-2xl shadow-slate-300/40">
      <div className="rounded-[1.5rem] bg-slate-950 p-5 text-white">
        <div className="mb-5 flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-black uppercase tracking-wide text-blue-200">Dashboard mockup</p>
            <h2 className="text-xl font-black">Career Command Center</h2>
          </div>
          <span className="rounded-full bg-emerald-400/20 px-3 py-1 text-xs font-bold text-emerald-200">visual demo</span>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <MetricPill label="ATS Score" value="88" />
          <MetricPill label="LinkedIn" value="86" />
          <MetricPill label="Vagas fit" value="12" />
        </div>
        <div className="mt-5 grid gap-4 lg:grid-cols-[0.85fr_1.15fr]">
          <div className="rounded-3xl border border-white/10 bg-white/10 p-4">
            <p className="text-xs font-black uppercase tracking-wide text-slate-300">Applymize IA</p>
            <div className="mt-4 space-y-3 text-sm">
              <div className="ml-auto max-w-[88%] rounded-2xl bg-blue-600 p-3">Como explico minha experiência com SQL?</div>
              <div className="max-w-[95%] rounded-2xl bg-white/10 p-3 leading-6 text-slate-100">
                Mostre que você usa SQL para transformar dados em decisões, criando consultas, bases e indicadores para reduzir retrabalho.
              </div>
            </div>
          </div>
          <div className="rounded-3xl bg-white p-4 text-slate-950">
            <p className="text-xs font-black uppercase tracking-wide text-slate-500">Matching pipeline</p>
            <div className="mt-4 space-y-3">
              {["Analista de Dados · 94%", "BI Analyst · 89%", "Automation Analyst · 87%"].map((item, index) => (
                <div key={item} className="flex items-center justify-between rounded-2xl bg-slate-50 p-3 text-sm font-bold">
                  <span>{item}</span>
                  <span className="rounded-full bg-blue-50 px-2 py-1 text-xs text-blue-800">#{index + 1}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function VisualBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-xs font-black uppercase tracking-wide text-slate-500">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-gradient-to-r from-blue-700 to-cyan-500" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function FitCard({ title, value, description }: { title: string; value: string; description: string }) {
  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-black uppercase tracking-wide text-blue-700">{title}</p>
      <h3 className="mt-2 text-3xl font-black text-slate-950">{value}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
    </article>
  );
}

export function Landing() {
  return (
    <PublicShell>
      <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <BrandLogo variant="sidebar" />
          <nav className="hidden items-center gap-6 text-sm font-semibold text-slate-600 md:flex">
            <a href="#recursos">Recursos</a>
            <a href="#linkedin">LinkedIn</a>
            <a href="#fit">Applymize Fit</a>
            <Link to="/demo" className="hover:text-slate-950">Demo</Link>
            <Link to="/pricing" className="hover:text-slate-950">Planos</Link>
          </nav>
          <div className="flex items-center gap-2">
            <Link to="/login" className="btn-secondary">Entrar</Link>
            <Link to="/pricing" className="btn-primary hidden sm:inline-flex">Ver planos</Link>
          </div>
        </div>
      </header>

      <MarketingSection className="relative pb-12 pt-14 lg:pb-20 lg:pt-20">
        <div className="absolute -right-24 top-16 h-72 w-72 rounded-full bg-blue-200/30 blur-3xl" />
        <div className="absolute -left-24 top-48 h-72 w-72 rounded-full bg-cyan-200/30 blur-3xl" />
        <div className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="relative z-10">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-bold text-blue-800">
              <Sparkles size={16} /> Career AI + ATS + automação
            </div>
            <h1 className="max-w-4xl text-4xl font-black tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
              Carreira, ATS e IA trabalhando juntos para acelerar sua evolução profissional.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              O Applymize combina currículo, LinkedIn, vagas, entrevistas, automações e IA contextual em uma experiência SaaS moderna, visual e profissional.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link to="/register" className="btn-primary justify-center px-6 py-3 text-base">
                Criar conta <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link to="/demo" className="btn-secondary justify-center px-6 py-3 text-base">Ver demonstração</Link>
            </div>
            <div className="mt-8 grid gap-3 text-sm text-slate-600 sm:grid-cols-3">
              {["IA protegida por login", "Landing 100% mockada", "ATS + LinkedIn + Fit"].map((item) => (
                <div key={item} className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-600" /> {item}</div>
              ))}
            </div>
          </div>
          <DashboardPreview />
        </div>
      </MarketingSection>

      <MarketingSection id="recursos" className="pt-8">
        <div className="mx-auto mb-10 max-w-3xl text-center">
          <p className="text-sm font-black uppercase tracking-wide text-blue-700">Ecossistema premium</p>
          <h2 className="mt-3 text-3xl font-black tracking-tight sm:text-4xl">Tudo que transforma busca de emprego em estratégia.</h2>
          <p className="mt-4 text-slate-600">IA, ATS, LinkedIn, matching, automação, WhatsApp e preparação para entrevistas em uma experiência visual de produto real.</p>
        </div>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => <FeatureCard key={feature.title} {...feature} />)}
        </div>
      </MarketingSection>

      <MarketingSection id="linkedin" className="pt-8">
        <div className="grid items-center gap-8 rounded-[2.25rem] border border-slate-200 bg-white p-6 shadow-xl shadow-slate-200/60 lg:grid-cols-[0.9fr_1.1fr] lg:p-10">
          <div>
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-700"><Linkedin size={24} /></div>
            <h2 className="text-3xl font-black">LinkedIn Analyzer como showcase, não formulário público.</h2>
            <p className="mt-4 leading-7 text-slate-600">
              A página pública mostra uma análise premium já concluída, com scores, insights, before/after e CTA. A análise real fica somente na área privada para proteger tokens e experiência.
            </p>
            <Link to="/linkedin-analyzer" className="btn-primary mt-6 inline-flex">Ver LinkedIn showcase</Link>
          </div>
          <div className="rounded-[2rem] bg-slate-50 p-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl bg-white p-5 shadow-sm"><p className="text-xs font-black text-blue-700">LinkedIn Score</p><h3 className="mt-2 text-4xl font-black">86</h3></div>
              <div className="rounded-3xl bg-white p-5 shadow-sm"><p className="text-xs font-black text-blue-700">ATS readiness</p><h3 className="mt-2 text-4xl font-black">91%</h3></div>
            </div>
            <div className="mt-5 space-y-4 rounded-3xl bg-white p-5 shadow-sm">
              <VisualBar label="Recruiter visibility" value={87} />
              <VisualBar label="Seniority perception" value={81} />
              <VisualBar label="Keywords detected" value={91} />
            </div>
          </div>
        </div>
      </MarketingSection>

      <MarketingSection id="fit" className="pt-8">
        <div className="rounded-[2.25rem] bg-slate-950 p-6 text-white shadow-2xl lg:p-10">
          <div className="grid gap-8 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
            <div>
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 text-blue-200"><Users size={24} /></div>
              <h2 className="text-3xl font-black">Applymize Fit: prepare-se para testes Gupy e entrevistas.</h2>
              <p className="mt-4 leading-7 text-slate-300">
                Showcase visual para perguntas comportamentais, score cultural, colaboração, liderança, comunicação e autonomia. Público é mockado; IA real só na área autenticada.
              </p>
              <Link to="/demo" className="mt-6 inline-flex rounded-xl bg-white px-5 py-3 text-sm font-black text-slate-950">Ver mockup completo</Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <FitCard title="Score cultural" value="88" description="Aderência simulada a colaboração, autonomia e comunicação." />
              <FitCard title="Feedback RH" value="Forte" description="Resposta clara, objetiva e orientada por exemplos profissionais." />
              <FitCard title="Comunicação" value="92%" description="Clareza, confiança e estrutura para entrevistas." />
              <FitCard title="Liderança" value="81%" description="Sinais de ownership, melhoria contínua e visão de negócio." />
            </div>
          </div>
        </div>
      </MarketingSection>

      <MarketingSection className="pt-8">
        <div className="rounded-[2rem] bg-slate-950 p-8 text-white shadow-2xl lg:p-12">
          <div className="grid items-center gap-8 lg:grid-cols-[1fr_auto]">
            <div>
              <h2 className="text-3xl font-black">Uma primeira impressão de produto premium, com backend real por trás.</h2>
              <p className="mt-3 max-w-2xl text-slate-300">Landing, demo e LinkedIn público são showcases mockados. Recursos com IA real ficam protegidos no dashboard autenticado.</p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
              <Link to="/register" className="rounded-xl bg-white px-5 py-3 text-center font-bold text-slate-950">Criar conta</Link>
              <Link to="/linkedin-analyzer" className="rounded-xl border border-white/20 px-5 py-3 text-center font-bold text-white">Ver LinkedIn showcase</Link>
            </div>
          </div>
        </div>
      </MarketingSection>
    </PublicShell>
  );
}
