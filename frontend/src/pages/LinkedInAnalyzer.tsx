import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Eye,
  Gauge,
  LayoutDashboard,
  Linkedin,
  Loader2,
  Lock,
  SearchCheck,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  UserRoundCheck,
  Wand2,
  AlertTriangle,
} from "lucide-react";
import { BrandLogo } from "../components/BrandLogo";
import { MarketingSection, PublicShell } from "../components/marketing";
import { analyzeLinkedInProfile, LinkedInAnalysis } from "../services/linkedinAnalyzer";
import { useAuth } from "../context/AuthContext";
import { getApiError } from "../services/api";

function PremiumBadge({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-black text-white shadow-sm backdrop-blur">
      {children}
    </span>
  );
}

function MockMetric({ label, value, helper }: { label: string; value: string; helper: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-4 shadow-sm backdrop-blur">
      <p className="text-xs font-bold uppercase tracking-wide text-slate-300">{label}</p>
      <p className="mt-2 text-3xl font-black text-white">{value}</p>
      <p className="mt-1 text-xs leading-5 text-slate-400">{helper}</p>
    </div>
  );
}

function ScoreRing({ value, label }: { value: number; label: string }) {
  const radius = 52;
  const stroke = 10;
  const normalized = radius - stroke / 2;
  const circumference = normalized * 2 * Math.PI;
  const offset = circumference - (value / 100) * circumference;
  return (
    <div className="flex flex-col items-center justify-center rounded-[2rem] border border-slate-200 bg-white p-6 shadow-xl shadow-slate-200/70">
      <div className="relative h-32 w-32">
        <svg className="h-32 w-32 -rotate-90" viewBox="0 0 104 104">
          <circle cx="52" cy="52" r={normalized} stroke="#e2e8f0" strokeWidth={stroke} fill="transparent" />
          <circle
            cx="52"
            cy="52"
            r={normalized}
            stroke="#2563eb"
            strokeWidth={stroke}
            fill="transparent"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-4xl font-black text-slate-950">{value}</span>
        </div>
      </div>
      <p className="mt-3 text-sm font-black uppercase tracking-wide text-slate-500">{label}</p>
    </div>
  );
}

function InsightCard({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) {
  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
      <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-50 text-blue-700">{icon}</div>
      <h3 className="font-black text-slate-950">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{text}</p>
    </article>
  );
}

function VisualBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-xs font-black uppercase tracking-wide text-slate-500">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-gradient-to-r from-blue-700 to-cyan-500" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function PublicLinkedInShowcase() {
  const { isAuthenticated } = useAuth();
  const ctaTo = isAuthenticated ? "/app/linkedin-analyzer" : "/register";
  const ctaLabel = isAuthenticated ? "Analisar meu perfil real" : "Crie sua conta para analisar seu perfil real com IA";

  return (
    <PublicShell>
      <header className="border-b border-white/10 bg-slate-950/95 text-white backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <BrandLogo />
          <div className="flex items-center gap-2">
            <Link to="/" className="rounded-xl border border-white/15 bg-white/10 px-4 py-2 text-sm font-bold text-white hover:bg-white/15">
              <ArrowLeft className="mr-2 inline h-4 w-4" /> Voltar
            </Link>
            <Link to={ctaTo} className="hidden rounded-xl bg-white px-4 py-2 text-sm font-black text-slate-950 sm:inline-flex">
              {isAuthenticated ? "Análise real" : "Criar conta"}
            </Link>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden bg-slate-950 text-white">
        <div className="absolute left-1/2 top-0 h-96 w-96 -translate-x-1/2 rounded-full bg-blue-500/20 blur-3xl" />
        <div className="absolute right-[-10%] top-40 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl" />
        <MarketingSection className="relative py-20 sm:py-24">
          <div className="grid items-center gap-10 lg:grid-cols-[0.9fr_1.1fr]">
            <div>
              <div className="mb-5 flex flex-wrap gap-2">
                <PremiumBadge><Linkedin size={14} /> Showcase público</PremiumBadge>
                <PremiumBadge><Lock size={14} /> Sem Groq/Ollama</PremiumBadge>
              </div>
              <h1 className="max-w-4xl text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
                Veja como seu LinkedIn pode ser analisado por uma plataforma inteligente de carreira.
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
                Esta página é uma demonstração visual premium. Nenhum dado é solicitado, nenhuma IA real é chamada e nenhum token é consumido no ambiente público.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link to={ctaTo} className="inline-flex items-center justify-center rounded-2xl bg-white px-6 py-3 text-sm font-black text-slate-950 shadow-xl shadow-blue-950/20 transition hover:-translate-y-0.5">
                  {ctaLabel} <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
                <Link to="/demo" className="inline-flex items-center justify-center rounded-2xl border border-white/15 bg-white/10 px-6 py-3 text-sm font-black text-white backdrop-blur transition hover:bg-white/15">
                  Ver demo do ecossistema
                </Link>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -inset-6 rounded-[2.5rem] bg-gradient-to-br from-blue-500/25 to-cyan-400/10 blur-2xl" />
              <div className="relative rounded-[2rem] border border-white/10 bg-white/[0.06] p-4 shadow-2xl backdrop-blur-xl">
                <div className="rounded-[1.5rem] border border-white/10 bg-slate-900/90 p-5">
                  <div className="mb-5 flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-black uppercase tracking-wide text-blue-200">LinkedIn Analyzer</p>
                      <h2 className="text-xl font-black">Profile Intelligence Preview</h2>
                    </div>
                    <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-xs font-black text-emerald-200">Mock demo</span>
                  </div>
                  <div className="grid gap-4 sm:grid-cols-3">
                    <MockMetric label="LinkedIn Score" value="86" helper="Visibilidade forte" />
                    <MockMetric label="ATS readiness" value="91%" helper="Keywords bem posicionadas" />
                    <MockMetric label="Recruiter fit" value="Alto" helper="Narrativa clara" />
                  </div>
                  <div className="mt-5 rounded-3xl bg-white p-5 text-slate-950">
                    <div className="grid gap-5 lg:grid-cols-[180px_1fr]">
                      <ScoreRing value={86} label="LinkedIn Score" />
                      <div className="space-y-4">
                        <VisualBar label="Headline otimizada" value={88} />
                        <VisualBar label="Palavras-chave ATS" value={91} />
                        <VisualBar label="Clareza para recrutador" value={84} />
                        <VisualBar label="Percepção de senioridade" value={79} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </MarketingSection>
      </section>

      <MarketingSection className="py-16">
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <aside className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-black uppercase tracking-wide text-blue-700">Perfil analisado · Mockup</p>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-slate-950">Analista de Dados & Automação</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Preview visual de como o Applymize transforma um perfil técnico em narrativa clara para recrutadores, ATS e entrevistas.
            </p>
            <div className="mt-6 space-y-4">
              <VisualBar label="Recruiter visibility" value={87} />
              <VisualBar label="Seniority perception" value={81} />
              <VisualBar label="Business impact" value={84} />
              <VisualBar label="Technical clarity" value={89} />
            </div>
          </aside>

          <section className="grid gap-5 md:grid-cols-2">
            <InsightCard icon={<Wand2 size={20} />} title="Headline otimizada" text="Analista de Dados & Automação | SQL, Power BI, Python, ETL e eficiência operacional." />
            <InsightCard icon={<SearchCheck size={20} />} title="Keywords detectadas" text="SQL, Power BI, Python, ETL, automação, dashboards, análise de dados e indicadores." />
            <InsightCard icon={<UserRoundCheck size={20} />} title="Recruiter insights" text="Perfil comunica boa ponte entre tecnologia, operação e impacto para áreas de negócio." />
            <InsightCard icon={<ShieldCheck size={20} />} title="ATS readiness" text="Sugestão visual de melhorias para deixar palavras-chave e resultados mais escaneáveis." />
          </section>
        </div>
      </MarketingSection>

      <MarketingSection className="py-10">
        <div className="rounded-[2.25rem] border border-slate-200 bg-white p-6 shadow-xl shadow-slate-200/70 lg:p-8">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-[1.75rem] border border-red-100 bg-red-50 p-6">
              <p className="text-xs font-black uppercase tracking-wide text-red-700">Antes</p>
              <h3 className="mt-3 text-xl font-black text-slate-950">Resumo técnico pouco posicionado</h3>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                “Trabalho com Excel, SQL, Power BI e automações. Tenho experiência com relatórios, processos e análises.”
              </p>
            </div>
            <div className="rounded-[1.75rem] border border-emerald-100 bg-emerald-50 p-6">
              <p className="text-xs font-black uppercase tracking-wide text-emerald-700">Depois</p>
              <h3 className="mt-3 text-xl font-black text-slate-950">Narrativa orientada a valor</h3>
              <p className="mt-3 text-sm leading-7 text-slate-700">
                “Atuo com dados e automação para transformar processos manuais em análises confiáveis, usando SQL, Power BI, Python e ETL para reduzir retrabalho e apoiar decisões.”
              </p>
            </div>
          </div>
        </div>
      </MarketingSection>

      <MarketingSection className="py-16">
        <div className="rounded-[2.5rem] bg-slate-950 p-8 text-white shadow-2xl lg:p-12">
          <div className="grid items-center gap-8 lg:grid-cols-[1fr_auto]">
            <div>
              <p className="text-sm font-black uppercase tracking-wide text-blue-200">Análise real protegida</p>
              <h2 className="mt-3 text-3xl font-black tracking-tight">Crie sua conta para analisar seu perfil real com IA.</h2>
              <p className="mt-3 max-w-2xl text-slate-300">
                O consumo real de IA só acontece dentro da área autenticada, respeitando usuário, tenant, limites diários e proteção de custos.
              </p>
            </div>
            <Link to={ctaTo} className="inline-flex items-center justify-center rounded-2xl bg-white px-6 py-3 text-sm font-black text-slate-950">
              {ctaLabel} <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        </div>
      </MarketingSection>
    </PublicShell>
  );
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-1.5 flex justify-between text-sm font-semibold text-slate-700">
        <span>{label}</span>
        <span>{value}/100</span>
      </div>
      <div className="h-2 rounded-full bg-slate-100">
        <div className="h-2 rounded-full bg-blue-700" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
    </div>
  );
}

export function PrivateLinkedInAnalyzer() {
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [targetRole, setTargetRole] = useState("Analista de Dados");
  const [profileText, setProfileText] = useState("");
  const [analysis, setAnalysis] = useState<LinkedInAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze(event?: FormEvent) {
    event?.preventDefault();
    setError("");
    setAnalysis(null);
    if (profileText.trim().length < 80) {
      setError("Cole pelo menos um trecho do seu perfil para a análise ficar útil.");
      return;
    }
    setLoading(true);
    try {
      const payload = { linkedin_url: linkedinUrl || undefined, profile_text: profileText, target_role: targetRole || undefined };
      const result = await analyzeLinkedInProfile(payload);
      setAnalysis(result);
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-shell">
      <div className="flex flex-col justify-between gap-4 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm lg:flex-row lg:items-center">
        <div>
          <p className="text-xs font-black uppercase tracking-wide text-blue-700">Análise real · área privada</p>
          <h1 className="mt-2 text-2xl font-black tracking-tight text-slate-950">LinkedIn Analyzer</h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-600">
            Aqui a análise real está liberada para usuário autenticado. O consumo de IA respeita limite diário, tenant e usuário logado.
          </p>
        </div>
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-bold text-emerald-900">
          <Lock className="mr-2 inline h-4 w-4" /> IA real protegida
        </div>
      </div>

      <form onSubmit={handleAnalyze} className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm lg:p-6">
          <label className="text-sm font-bold text-slate-700">URL do LinkedIn opcional</label>
          <input className="input mt-2" placeholder="https://www.linkedin.com/in/seu-perfil" value={linkedinUrl} onChange={(e) => setLinkedinUrl(e.target.value)} />

          <label className="mt-4 block text-sm font-bold text-slate-700">Cargo alvo</label>
          <input className="input mt-2" placeholder="Analista de Dados" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} />

          <label className="mt-4 block text-sm font-bold text-slate-700">Cole aqui o texto do seu perfil</label>
          <textarea
            className="input mt-2 min-h-[260px] resize-y"
            placeholder="Cole headline, Sobre, experiências, skills e principais informações do LinkedIn..."
            value={profileText}
            onChange={(e) => setProfileText(e.target.value)}
          />
          {error && <p className="mt-3 rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}
          <button className="btn-primary mt-5 w-full justify-center py-3" disabled={loading}>
            {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <Sparkles className="mr-2 h-5 w-5" />} Analisar LinkedIn real
          </button>
        </section>

        <section className="rounded-[2rem] border border-slate-200 bg-slate-950 p-5 text-white shadow-xl lg:p-6">
          <p className="text-xs font-black uppercase tracking-wide text-blue-200">Como usar</p>
          <h2 className="mt-2 text-2xl font-black">Cole seu conteúdo real para receber uma leitura estratégica.</h2>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            A URL é opcional. A análise usa o conteúdo fornecido para avaliar headline, Sobre, experiências, palavras-chave, clareza para recrutador e aderência ATS.
          </p>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {[
              { icon: <Gauge size={18} />, label: "Score visual" },
              { icon: <Target size={18} />, label: "Keywords ATS" },
              { icon: <Eye size={18} />, label: "Visão recrutador" },
              { icon: <TrendingUp size={18} />, label: "Melhorias práticas" },
            ].map((item) => (
              <div key={item.label} className="rounded-2xl border border-white/10 bg-white/10 p-4 text-sm font-bold">
                <span className="mr-2 inline-flex text-blue-200">{item.icon}</span>{item.label}
              </div>
            ))}
          </div>
        </section>
      </form>

      {analysis && (
        <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
          <aside className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-black uppercase tracking-wide text-blue-700">LinkedIn Score · Análise real</p>
            <div className="mt-4 flex items-end gap-2">
              <span className="text-6xl font-black text-slate-950">{analysis.score}</span>
              <span className="mb-2 text-xl font-bold text-slate-400">/100</span>
            </div>
            <div className="mt-6 space-y-4">
              {Object.entries(analysis.categories).map(([key, value]) => (
                <ScoreBar key={key} label={key.replaceAll("_", " ")} value={value} />
              ))}
            </div>
          </aside>

          <section className="space-y-5">
            <div className="grid gap-5 md:grid-cols-2">
              <article className="rounded-3xl border border-emerald-200 bg-emerald-50 p-5">
                <h2 className="mb-3 flex items-center gap-2 font-black text-emerald-900"><CheckCircle2 size={20} /> Pontos fortes</h2>
                <ul className="space-y-2 text-sm leading-6 text-emerald-900">
                  {analysis.strengths.map((item) => <li key={item}>• {item}</li>)}
                </ul>
              </article>
              <article className="rounded-3xl border border-amber-200 bg-amber-50 p-5">
                <h2 className="mb-3 flex items-center gap-2 font-black text-amber-900"><AlertTriangle size={20} /> Melhorias</h2>
                <ul className="space-y-2 text-sm leading-6 text-amber-900">
                  {analysis.weaknesses.map((item) => <li key={item}>• {item}</li>)}
                </ul>
              </article>
            </div>

            <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-black">Headline sugerida</h2>
              <p className="mt-3 rounded-2xl bg-slate-50 p-4 text-sm font-semibold text-slate-800">{analysis.suggested_headline}</p>
            </article>

            <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-black">Sobre sugerido</h2>
              <p className="mt-3 whitespace-pre-line rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">{analysis.suggested_about}</p>
            </article>

            <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-black">Palavras-chave ATS/LinkedIn</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {analysis.ats_keywords.map((keyword) => <span key={keyword} className="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-800">{keyword}</span>)}
              </div>
            </article>

            <div className="grid gap-5 md:grid-cols-2">
              <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="text-lg font-black">Feedback recrutador</h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">{analysis.recruiter_feedback}</p>
              </article>
              <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="text-lg font-black">Feedback ATS</h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">{analysis.ats_feedback}</p>
              </article>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

export function LinkedInAnalyzer() {
  return <PublicLinkedInShowcase />;
}
