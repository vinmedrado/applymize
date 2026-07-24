import { Link } from "react-router-dom";
import { ArrowLeft, Bot, ClipboardCheck, Linkedin, MessageCircle, Radar, Sparkles, Users, BarChart3, ShieldCheck } from "lucide-react";
import { MarketingSection, PublicShell } from "../components/marketing";
import { BrandLogo } from "../components/BrandLogo";

const demoItems = [
  { icon: <Bot />, title: "Applymize IA", value: "Contextual", desc: "Mockup de conversa com histórico, recomendações e linguagem para entrevistas." },
  { icon: <ClipboardCheck />, title: "ATS Score", value: "88/100", desc: "Leitura visual de aderência, gaps e palavras-chave do currículo." },
  { icon: <Linkedin />, title: "LinkedIn Score", value: "86/100", desc: "Preview de headline, recruiter insights e visibilidade profissional." },
  { icon: <Users />, title: "Applymize Fit", value: "88%", desc: "Preparação mockada para testes Gupy, entrevistas e fit cultural." },
  { icon: <Radar />, title: "Smart Matching", value: "12 vagas", desc: "Oportunidades simuladas por aderência, localização e senioridade." },
  { icon: <MessageCircle />, title: "WhatsApp", value: "Ativo", desc: "Alertas automáticos demonstrativos sem chamar providers reais." }
];

function DemoMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-black uppercase tracking-wide text-blue-700">{label}</p>
      <h3 className="mt-2 text-3xl font-black text-slate-950">{value}</h3>
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
      <div className="h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-gradient-to-r from-blue-700 to-cyan-500" style={{ width: `${value}%` }} /></div>
    </div>
  );
}

export function Demo() {
  return (
    <PublicShell>
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <BrandLogo />
          <Link to="/" className="btn-secondary"><ArrowLeft className="mr-2 h-4 w-4" /> Voltar</Link>
        </div>
      </header>

      <section className="relative overflow-hidden bg-slate-950 text-white">
        <div className="absolute left-1/2 top-0 h-96 w-96 -translate-x-1/2 rounded-full bg-blue-500/20 blur-3xl" />
        <MarketingSection className="relative py-20">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-sm font-black uppercase tracking-wide text-blue-200">Demonstração pública · 100% mockada</p>
            <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">Uma experiência visual do ecossistema Applymize.</h1>
            <p className="mt-5 text-lg leading-8 text-slate-300">
              Esta demo parece produto funcionando, mas usa somente dados visuais e estáticos. Nenhum endpoint de IA, Groq, Ollama, análise real ou provider é chamado.
            </p>
            <div className="mt-8 flex justify-center gap-3">
              <Link to="/register" className="rounded-2xl bg-white px-6 py-3 text-sm font-black text-slate-950">Criar conta</Link>
              <Link to="/laboratorio-ats" className="rounded-2xl border border-white/15 bg-white/10 px-6 py-3 text-sm font-black text-white">Testar ATS real</Link>
            </div>
          </div>
        </MarketingSection>
      </section>

      <MarketingSection>
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {demoItems.map((item) => (
            <article key={item.title} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-700">{item.icon}</div>
              <p className="text-sm font-bold text-slate-500">{item.title}</p>
              <h2 className="mt-2 text-3xl font-black text-slate-950">{item.value}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600">{item.desc}</p>
            </article>
          ))}
        </div>

        <div className="mt-10 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-xl shadow-slate-200/60">
            <div className="mb-6 flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-black uppercase tracking-wide text-blue-700">Dashboard Preview</p>
                <h2 className="mt-2 text-2xl font-black text-slate-950">Central de evolução profissional</h2>
              </div>
              <ShieldCheck className="h-10 w-10 text-emerald-600" />
            </div>
            <div className="grid gap-4 sm:grid-cols-4">
              <DemoMetric label="ATS" value="88" />
              <DemoMetric label="LinkedIn" value="86" />
              <DemoMetric label="Fit" value="88%" />
              <DemoMetric label="Vagas" value="12" />
            </div>
            <div className="mt-6 rounded-3xl bg-slate-50 p-5">
              <div className="mb-4 flex items-center gap-2 text-sm font-black text-slate-700"><BarChart3 size={18} /> Analytics simulados</div>
              <div className="space-y-4">
                <VisualBar label="Clareza profissional" value={89} />
                <VisualBar label="Palavras-chave aderentes" value={91} />
                <VisualBar label="Perfil para recrutador" value={84} />
                <VisualBar label="Prontidão para entrevista" value={88} />
              </div>
            </div>
          </section>

          <aside className="rounded-[2rem] bg-slate-950 p-6 text-white shadow-2xl">
            <p className="text-xs font-black uppercase tracking-wide text-blue-200">Applymize Fit · mockup</p>
            <h2 className="mt-2 text-2xl font-black">Prepare-se para Gupy e entrevistas.</h2>
            <div className="mt-6 space-y-3">
              {["Conte sobre um desafio que resolveu com dados.", "Como você lida com prioridades conflitantes?", "Explique um projeto técnico para uma pessoa de negócio."].map((question) => (
                <div key={question} className="rounded-2xl border border-white/10 bg-white/10 p-4 text-sm leading-6 text-slate-100">{question}</div>
              ))}
            </div>
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl bg-white/10 p-4"><p className="text-xs text-slate-300">Comunicação</p><p className="mt-1 text-2xl font-black">92%</p></div>
              <div className="rounded-2xl bg-white/10 p-4"><p className="text-xs text-slate-300">Autonomia</p><p className="mt-1 text-2xl font-black">87%</p></div>
            </div>
          </aside>
        </div>
      </MarketingSection>
    </PublicShell>
  );
}
