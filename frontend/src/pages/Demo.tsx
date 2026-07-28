import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  BellRing,
  Bookmark,
  BookmarkCheck,
  Bot,
  BriefcaseBusiness,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleUserRound,
  ClipboardCheck,
  Clock3,
  Code2,
  FileSearch,
  Filter,
  Gauge,
  Github,
  LayoutDashboard,
  Linkedin,
  MapPin,
  MessageCircle,
  Play,
  Radar,
  RefreshCw,
  Search,
  Send,
  Settings2,
  ShieldCheck,
  Sparkles,
  Target,
  WandSparkles,
  Wifi,
} from "lucide-react";
import { BrandLogo } from "../components/BrandLogo";
import { PortfolioAIFloatingAssistant } from "../components/demo/PortfolioAIFloatingAssistant";
import { MatchProgress } from "../components/ScoreVisual";
import { useToast } from "../context/ToastContext";
import { analyzePublicResume, LocalAtsAnalysis } from "../services/publicAtsEngine";

type DemoView = "overview" | "jobs" | "applications" | "ats" | "profile" | "automation";

type DemoJob = {
  id: number;
  title: string;
  company: string;
  location: string;
  workplace: string;
  provider: string;
  score: number;
  relevance: number;
  skills: string[];
  summary: string;
  saved: boolean;
};

type DemoApplication = {
  id: number;
  jobId: number;
  title: string;
  company: string;
  status: "saved" | "applied" | "screening" | "interview" | "offer";
  updated: string;
};

const demoViews: Array<{
  id: DemoView;
  label: string;
  helper: string;
  icon: typeof LayoutDashboard;
}> = [
  { id: "overview", label: "Visão geral", helper: "Resumo do produto", icon: LayoutDashboard },
  { id: "jobs", label: "Vagas & match", helper: "Busca e priorização", icon: BriefcaseBusiness },
  { id: "applications", label: "Candidaturas", helper: "Pipeline pessoal", icon: ClipboardCheck },
  { id: "ats", label: "ATS real", helper: "Motor no navegador", icon: FileSearch },
  { id: "profile", label: "Perfil & LinkedIn", helper: "Posicionamento", icon: CircleUserRound },
  { id: "automation", label: "Automação", helper: "Providers e alertas", icon: Radar },
];

const initialJobs: DemoJob[] = [
  {
    id: 1,
    title: "Analista de Automação de Processos Pleno",
    company: "Nexa Operações",
    location: "São Paulo, SP",
    workplace: "Híbrido",
    provider: "Gupy",
    score: 94,
    relevance: 98,
    skills: ["Power Automate", "Python", "BPMN", "SQL"],
    summary: "Mapeamento e automação de processos, indicadores de eficiência e integrações entre sistemas.",
    saved: true,
  },
  {
    id: 2,
    title: "Business Process Automation Analyst",
    company: "Orbit Tech",
    location: "Remoto · Brasil",
    workplace: "Remoto",
    provider: "LinkedIn",
    score: 89,
    relevance: 93,
    skills: ["RPA", "APIs", "n8n", "Power BI"],
    summary: "Construção de fluxos automatizados e acompanhamento de métricas para áreas de negócio.",
    saved: false,
  },
  {
    id: 3,
    title: "Analista de Melhoria Contínua",
    company: "Vértice Serviços",
    location: "Santo André, SP",
    workplace: "Presencial",
    provider: "Vagas.com",
    score: 84,
    relevance: 88,
    skills: ["Lean", "BPMN", "Excel", "Power BI"],
    summary: "Redesenho de rotinas operacionais, redução de retrabalho e gestão de indicadores.",
    saved: false,
  },
];

const discoveredJob: DemoJob = {
  id: 4,
  title: "Analista de RPA e Integrações",
  company: "Aurora Digital",
  location: "Remoto · Brasil",
  workplace: "Remoto",
  provider: "InfoJobs",
  score: 87,
  relevance: 91,
  skills: ["RPA", "Python", "REST", "SQL"],
  summary: "Automação de rotinas e integração de dados com acompanhamento de SLA e qualidade.",
  saved: false,
};

const initialApplications: DemoApplication[] = [
  { id: 1, jobId: 1, title: initialJobs[0].title, company: initialJobs[0].company, status: "interview", updated: "Hoje, 09:42" },
  { id: 2, jobId: 2, title: initialJobs[1].title, company: initialJobs[1].company, status: "screening", updated: "Ontem, 17:10" },
  { id: 3, jobId: 3, title: initialJobs[2].title, company: initialJobs[2].company, status: "applied", updated: "25 jul, 14:30" },
];

const sampleResume = `VINICIUS EXEMPLO
vinicius@example.com | (11) 99999-9999
linkedin.com/in/vinicius-exemplo | github.com/vinicius-exemplo

RESUMO PROFISSIONAL
Analista de Automação de Processos com experiência em transformar rotinas manuais em fluxos digitais mensuráveis.

HABILIDADES E TECNOLOGIAS
Power Automate, Python, SQL, Excel, VBA, RPA, BPMN, Power BI, n8n, APIs REST e Git.

EXPERIÊNCIA PROFISSIONAL
Analista de Automação de Processos
- Automatizei 18 rotinas com Power Automate e Python, reduzindo 240 horas mensais de trabalho manual.
- Estruturei indicadores em Power BI e SQL para acompanhar SLA, erros e produtividade.
- Mapeei processos em BPMN e reduzi o retrabalho em 32%.

PROJETOS
- Pipeline de conciliação de dados com Python, SQL e alertas.
- Dashboard de eficiência operacional com Power BI e DAX.

FORMAÇÃO
Tecnologia em Análise e Desenvolvimento de Sistemas.

CERTIFICAÇÕES
Microsoft Power Platform Fundamentals e Lean Six Sigma Yellow Belt.`;

const sampleRole = "Analista de Automação de Processos Pleno";
const sampleJobDescription = "Power Automate, RPA, BPMN, Excel, APIs REST, SQL, Python, melhoria contínua, indicadores e documentação.";

const applicationStages: DemoApplication["status"][] = ["saved", "applied", "screening", "interview", "offer"];

const stageLabels: Record<DemoApplication["status"], string> = {
  saved: "Salva",
  applied: "Aplicada",
  screening: "Triagem",
  interview: "Entrevista",
  offer: "Oferta",
};

function DemoModeBadge({ compact = false }: { compact?: boolean }) {
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 font-black text-blue-800 ${compact ? "px-2.5 py-1 text-[11px]" : "px-3 py-1.5 text-xs"}`}>
      <Sparkles size={compact ? 13 : 15} />
      {compact ? (
        <>
          <span className="sm:hidden">Demo</span>
          <span className="hidden sm:inline">Modo demonstração</span>
        </>
      ) : "Modo demonstração"}
    </span>
  );
}

function StatCard({
  icon,
  label,
  value,
  helper,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  helper: string;
}) {
  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-black uppercase tracking-wide text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-black tracking-tight text-slate-950">{value}</p>
          <p className="mt-1 text-xs leading-5 text-slate-500">{helper}</p>
        </div>
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-blue-50 text-blue-700">{icon}</div>
      </div>
    </article>
  );
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  const tone = value >= 85 ? "bg-emerald-500" : value >= 70 ? "bg-blue-600" : "bg-amber-500";
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3 text-xs font-bold text-slate-600">
        <span>{label}</span>
        <span>{Math.round(value)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full ${tone}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
    </div>
  );
}

function OverviewPanel({
  jobs,
  applications,
  automationEnabled,
  onNavigate,
  onOpenAI,
}: {
  jobs: DemoJob[];
  applications: DemoApplication[];
  automationEnabled: boolean;
  onNavigate: (view: DemoView) => void;
  onOpenAI: () => void;
}) {
  const highMatches = jobs.filter((job) => job.score >= 85).length;
  return (
    <div className="space-y-5">
      <section className="relative overflow-hidden rounded-[2rem] bg-slate-950 p-6 text-white shadow-2xl lg:p-8">
        <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-blue-500/25 blur-3xl" />
        <div className="absolute -bottom-32 left-1/3 h-72 w-72 rounded-full bg-cyan-400/15 blur-3xl" />
        <div className="relative grid gap-7 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <p className="text-xs font-black uppercase tracking-[0.18em] text-blue-200">Career command center · dados ilustrativos</p>
            <h1 className="mt-3 max-w-3xl text-3xl font-black tracking-tight sm:text-4xl">Uma busca de emprego transformada em sistema.</h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
              Explore a jornada completa. As ações funcionam no navegador e mostram o comportamento do produto sem acessar contas, banco ou integrações pessoais.
            </p>
          </div>
          <div className="grid gap-2">
            <button type="button" onClick={onOpenAI} className="inline-flex items-center justify-center rounded-2xl bg-white px-5 py-3 text-sm font-black text-slate-950">
              Testar Applymize IA <Sparkles className="ml-2 h-4 w-4" />
            </button>
            <button type="button" onClick={() => onNavigate("jobs")} className="inline-flex items-center justify-center rounded-2xl border border-white/15 bg-white/5 px-5 py-3 text-sm font-black text-white">
              Explorar vagas <ArrowRight className="ml-2 h-4 w-4" />
            </button>
          </div>
        </div>
      </section>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={<Gauge size={21} />} label="ATS do perfil" value="89" helper="Motor determinístico e explicável" />
        <StatCard icon={<Target size={21} />} label="Vagas com alto fit" value={String(highMatches)} helper={`${jobs.length} oportunidades normalizadas`} />
        <StatCard icon={<ClipboardCheck size={21} />} label="Candidaturas" value={String(applications.length)} helper="Pipeline e próximos passos" />
        <StatCard icon={<BellRing size={21} />} label="Automação" value={automationEnabled ? "Ativa" : "Pausada"} helper="Alertas privados via WhatsApp" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-blue-700">Prioridades de hoje</p>
              <h2 className="mt-1 text-xl font-black">Próximas ações sugeridas</h2>
            </div>
            <Activity className="text-blue-700" />
          </div>
          <div className="mt-5 space-y-3">
            {[
              { title: "Preparar entrevista na Nexa Operações", helper: "Candidatura avançou para entrevista", view: "applications" as DemoView, tone: "bg-emerald-500" },
              { title: "Revisar 2 palavras-chave no currículo", helper: "BPMN e melhoria contínua aumentam a aderência", view: "ats" as DemoView, tone: "bg-blue-600" },
              { title: "Avaliar nova vaga remota", helper: "Match previsto acima de 85%", view: "jobs" as DemoView, tone: "bg-amber-500" },
            ].map((item) => (
              <button type="button" key={item.title} onClick={() => onNavigate(item.view)} className="flex w-full items-center gap-3 rounded-2xl border border-slate-100 bg-slate-50 p-4 text-left transition hover:border-blue-200 hover:bg-blue-50/50">
                <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${item.tone}`} />
                <span className="min-w-0 flex-1">
                  <span className="block font-bold text-slate-900">{item.title}</span>
                  <span className="mt-0.5 block text-xs text-slate-500">{item.helper}</span>
                </span>
                <ChevronRight className="h-4 w-4 shrink-0 text-slate-400" />
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-blue-700">Explicabilidade</p>
              <h2 className="mt-1 text-xl font-black">O que existe por trás</h2>
            </div>
            <Code2 className="text-blue-700" />
          </div>
          <div className="mt-5 space-y-3 text-sm">
            {["Ingestão multi-provider", "Deduplicação entre fontes", "Relevância por família profissional", "Elegibilidade e matching", "ATS/RH e automações"].map((item, index) => (
              <div key={item} className="flex items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-950 text-xs font-black text-white">{index + 1}</span>
                <span className="font-bold text-slate-700">{item}</span>
              </div>
            ))}
          </div>
          <Link to="/como-funciona" className="btn-primary mt-5 w-full justify-center">
            Abrir por trás do projeto <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </section>
      </div>
    </div>
  );
}

function JobsPanel({
  jobs,
  onSearch,
  onToggleSave,
  onApply,
}: {
  jobs: DemoJob[];
  onSearch: () => void;
  onToggleSave: (id: number) => void;
  onApply: (job: DemoJob) => void;
}) {
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const filtered = jobs.filter((job) => `${job.title} ${job.company} ${job.skills.join(" ")}`.toLowerCase().includes(query.toLowerCase()));
  const selected = jobs.find((job) => job.id === selectedId);

  return (
    <div className="space-y-5">
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-center">
          <div>
            <p className="text-xs font-black uppercase tracking-wide text-blue-700">Descoberta personalizada</p>
            <h1 className="mt-1 text-2xl font-black">Vagas relevantes para Automação de Processos</h1>
            <p className="mt-1 text-sm text-slate-500">Resultados demonstrativos ordenados por relevância, elegibilidade e aderência.</p>
          </div>
          <button type="button" onClick={onSearch} className="btn-primary px-4 py-3">
            <RefreshCw className="mr-2 h-4 w-4" /> Simular nova busca
          </button>
        </div>
        <div className="mt-5 grid gap-3 lg:grid-cols-[1fr_auto_auto]">
          <label className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input className="input pl-9" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar título, empresa ou skill" />
          </label>
          <button type="button" className="btn-secondary" onClick={() => setQuery("Power")}>
            <Filter className="mr-2 h-4 w-4" /> Filtrar Power Platform
          </button>
          <button type="button" className="btn-secondary" onClick={() => setQuery("")}>Limpar filtros</button>
        </div>
      </section>

      {selected && (
        <section className="rounded-3xl border border-blue-200 bg-blue-50/50 p-5 shadow-sm">
          <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="badge">Análise selecionada</span>
                <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-black text-emerald-800">{selected.relevance}% relevante</span>
              </div>
              <h2 className="mt-3 text-xl font-black">{selected.title}</h2>
              <p className="mt-1 text-sm font-semibold text-slate-600">{selected.company} · {selected.location}</p>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">{selected.summary}</p>
            </div>
            <div className="w-full rounded-2xl bg-white p-4 shadow-sm lg:w-64">
              <MatchProgress score={selected.score} label="Match calculado" />
              <button type="button" onClick={() => onApply(selected)} className="btn-primary mt-4 w-full justify-center">
                <Send className="mr-2 h-4 w-4" /> Candidatar na demo
              </button>
            </div>
          </div>
        </section>
      )}

      <div className="grid gap-4">
        {filtered.map((job) => (
          <article key={job.id} className="job-card p-5">
            <div className="grid gap-5 xl:grid-cols-[1fr_180px] xl:items-start">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2 text-xs font-bold text-slate-500">
                  <span className="rounded-full bg-slate-100 px-2.5 py-1">{job.provider}</span>
                  <span className="inline-flex items-center gap-1"><MapPin size={13} /> {job.location}</span>
                  <span>{job.workplace}</span>
                </div>
                <h2 className="mt-3 text-xl font-black tracking-tight text-slate-950">{job.title}</h2>
                <p className="mt-1 font-bold text-slate-600">{job.company}</p>
                <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-600">{job.summary}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {job.skills.map((skill) => <span key={skill} className="badge">{skill}</span>)}
                </div>
              </div>
              <div className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                <MatchProgress score={job.score} />
                <p className="mt-3 text-xs font-bold text-slate-500">Relevância do cargo: {job.relevance}%</p>
                <div className="mt-4 grid gap-2">
                  <button type="button" onClick={() => setSelectedId(job.id)} className="btn-primary w-full justify-center text-xs">
                    Ver análise
                  </button>
                  <button type="button" onClick={() => onToggleSave(job.id)} className="btn-secondary w-full justify-center text-xs">
                    {job.saved ? <BookmarkCheck className="mr-2 h-4 w-4" /> : <Bookmark className="mr-2 h-4 w-4" />}
                    {job.saved ? "Vaga salva" : "Salvar vaga"}
                  </button>
                </div>
              </div>
            </div>
          </article>
        ))}
        {!filtered.length && (
          <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center">
            <Search className="mx-auto h-8 w-8 text-slate-400" />
            <h2 className="mt-3 font-black">Nenhuma vaga neste filtro</h2>
            <p className="mt-1 text-sm text-slate-500">Limpe o termo para voltar aos resultados demonstrativos.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ApplicationsPanel({
  applications,
  onAdvance,
}: {
  applications: DemoApplication[];
  onAdvance: (id: number) => void;
}) {
  return (
    <div className="space-y-5">
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-xs font-black uppercase tracking-wide text-blue-700">Application tracker</p>
        <h1 className="mt-1 text-2xl font-black">Pipeline de candidaturas</h1>
        <p className="mt-1 text-sm text-slate-500">Use “Avançar etapa” para testar mudanças de estado durante esta visita.</p>
        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-5">
          {applicationStages.map((stage) => (
            <div key={stage} className="rounded-2xl border border-slate-100 bg-slate-50 p-3 text-center">
              <p className="text-xs font-black uppercase tracking-wide text-slate-500">{stageLabels[stage]}</p>
              <p className="mt-1 text-2xl font-black">{applications.filter((item) => item.status === stage).length}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        {applications.map((application) => {
          const atOffer = application.status === "offer";
          return (
            <article key={application.id} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <span className="badge">{stageLabels[application.status]}</span>
                  <h2 className="mt-3 text-lg font-black">{application.title}</h2>
                  <p className="mt-1 text-sm font-bold text-slate-500">{application.company}</p>
                </div>
                <ClipboardCheck className="shrink-0 text-blue-700" />
              </div>
              <div className="mt-5 flex items-center justify-between gap-3 rounded-2xl bg-slate-50 p-3 text-xs text-slate-500">
                <span className="inline-flex items-center gap-1.5"><Clock3 size={14} /> Atualizada {application.updated}</span>
                <span className="font-bold">ID demo #{application.id}</span>
              </div>
              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                <button type="button" onClick={() => onAdvance(application.id)} disabled={atOffer} className="btn-primary justify-center">
                  {atOffer ? <Check className="mr-2 h-4 w-4" /> : <ArrowRight className="mr-2 h-4 w-4" />}
                  {atOffer ? "Etapa final" : "Avançar etapa"}
                </button>
                <button type="button" className="btn-secondary justify-center" onClick={() => window.alert("Follow-up demonstrativo gerado: “Olá! Gostaria de reforçar meu interesse na oportunidade e saber sobre os próximos passos.”")}>
                  <WandSparkles className="mr-2 h-4 w-4" /> Gerar follow-up
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}

function AtsPanel() {
  const toast = useToast();
  const [resumeText, setResumeText] = useState(sampleResume);
  const [analysis, setAnalysis] = useState<LocalAtsAnalysis | null>(() => analyzePublicResume({
    resumeText: sampleResume,
    targetRole: sampleRole,
    jobDescription: sampleJobDescription,
  }));

  function analyze() {
    if (resumeText.trim().length < 120) {
      toast.error("Currículo muito curto", "Use o exemplo ou escreva pelo menos 120 caracteres.");
      return;
    }
    setAnalysis(analyzePublicResume({
      resumeText,
      targetRole: sampleRole,
      jobDescription: sampleJobDescription,
    }));
    toast.success("Análise executada no navegador", "Nenhum conteúdo foi enviado para um servidor.");
  }

  return (
    <div className="space-y-5">
      <section className="rounded-3xl border border-emerald-200 bg-emerald-50 p-5">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div>
            <p className="text-xs font-black uppercase tracking-wide text-emerald-800">Experimento funcional · não é mock</p>
            <h1 className="mt-1 text-2xl font-black text-slate-950">Motor ATS executado localmente</h1>
            <p className="mt-1 text-sm leading-6 text-emerald-900/75">Edite o currículo de exemplo e execute novamente. O mesmo motor público do laboratório calcula o resultado.</p>
          </div>
          <ShieldCheck className="h-10 w-10 shrink-0 text-emerald-700" />
        </div>
      </section>

      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <label className="text-sm font-black text-slate-800">Currículo de teste</label>
          <textarea className="input mt-2 min-h-[420px] resize-y font-mono text-xs leading-6" value={resumeText} onChange={(event) => setResumeText(event.target.value)} />
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            <button type="button" onClick={analyze} className="btn-primary justify-center py-3">
              <Play className="mr-2 h-4 w-4" /> Analisar agora
            </button>
            <button type="button" onClick={() => setResumeText(sampleResume)} className="btn-secondary justify-center">Restaurar exemplo</button>
          </div>
          <Link to="/laboratorio-ats" className="mt-4 inline-flex items-center text-sm font-black text-blue-700">
            Abrir laboratório com upload <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          {analysis ? (
            <>
              <div className="grid gap-5 sm:grid-cols-[160px_1fr] sm:items-center">
                <div className="rounded-[2rem] bg-slate-950 p-6 text-center text-white">
                  <p className="text-xs font-black uppercase tracking-wide text-blue-200">Score geral</p>
                  <p className="mt-2 text-6xl font-black">{Math.round(analysis.final_score)}</p>
                  <p className="mt-1 text-sm font-bold text-slate-300">Nota {analysis.grade}</p>
                </div>
                <div>
                  <h2 className="text-xl font-black">Leitura para a vaga de teste</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{analysis.probability}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {analysis.detected_skills.slice(0, 7).map((skill) => <span key={skill} className="badge">{skill}</span>)}
                  </div>
                </div>
              </div>
              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                <ScoreBar label="Estrutura ATS" value={analysis.ats_score} />
                <ScoreBar label="Leitura de RH" value={analysis.rh_score} />
                <ScoreBar label="Aderência à vaga" value={analysis.match_score} />
                <ScoreBar label="Palavras-chave" value={analysis.keyword_score} />
                <ScoreBar label="Experiência" value={analysis.experience_score} />
                <ScoreBar label="Clareza" value={analysis.clarity_score} />
              </div>
              <div className="mt-6 grid gap-4 lg:grid-cols-2">
                <article className="rounded-2xl border border-emerald-100 bg-emerald-50 p-4">
                  <h3 className="font-black text-emerald-900">Pontos fortes</h3>
                  <ul className="mt-3 space-y-2 text-sm leading-6 text-emerald-900/80">
                    {analysis.strengths.slice(0, 3).map((item) => <li key={item}>• {item}</li>)}
                  </ul>
                </article>
                <article className="rounded-2xl border border-amber-100 bg-amber-50 p-4">
                  <h3 className="font-black text-amber-900">Próximos ajustes</h3>
                  <ul className="mt-3 space-y-2 text-sm leading-6 text-amber-900/80">
                    {analysis.suggestions.slice(0, 3).map((item) => <li key={item.title}>• {item.title}</li>)}
                  </ul>
                </article>
              </div>
            </>
          ) : (
            <div className="flex min-h-[420px] flex-col items-center justify-center text-center">
              <FileSearch className="h-10 w-10 text-slate-400" />
              <h2 className="mt-3 font-black">Execute a análise</h2>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function ProfilePanel() {
  const toast = useToast();
  const [optimized, setOptimized] = useState(false);
  const [skillAdded, setSkillAdded] = useState(false);

  function optimize() {
    setOptimized(true);
    toast.success("Headline otimizada", "A demonstração aplicou uma sugestão sem chamar IA externa.");
  }

  return (
    <div className="space-y-5">
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-slate-950 text-white"><CircleUserRound size={30} /></div>
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-blue-700">Perfil demonstrativo</p>
              <h1 className="mt-1 text-2xl font-black">Vinicius Exemplo</h1>
              <p className="mt-1 text-sm font-bold text-slate-500">Dados & Automação · São Paulo</p>
            </div>
          </div>
          <div className="w-full max-w-sm">
            <div className="flex justify-between text-xs font-black text-slate-500"><span>Completude do perfil</span><span>92%</span></div>
            <div className="mt-2 h-2.5 overflow-hidden rounded-full bg-slate-100"><div className="h-full w-[92%] rounded-full bg-emerald-500" /></div>
          </div>
        </div>
      </section>

      <div className="grid gap-5 xl:grid-cols-[1fr_0.8fr]">
        <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-blue-700">LinkedIn Analyzer · demo</p>
              <h2 className="mt-1 text-xl font-black">Posicionamento profissional</h2>
            </div>
            <Linkedin className="text-blue-700" />
          </div>
          <div className="mt-5 rounded-2xl border border-slate-100 bg-slate-50 p-4">
            <p className="text-xs font-black uppercase tracking-wide text-slate-500">{optimized ? "Headline otimizada" : "Headline atual"}</p>
            <p className="mt-2 font-bold leading-6 text-slate-900">
              {optimized
                ? "Analista de Dados & Automação | SQL, Power BI, Python, ETL e eficiência operacional"
                : "Analista de Dados e Automação"}
            </p>
          </div>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <ScoreBar label="Clareza para recrutador" value={optimized ? 91 : 76} />
            <ScoreBar label="Palavras-chave ATS" value={optimized ? 94 : 81} />
            <ScoreBar label="Percepção de senioridade" value={84} />
            <ScoreBar label="Impacto de negócio" value={88} />
          </div>
          <button type="button" onClick={optimize} disabled={optimized} className="btn-primary mt-5">
            <WandSparkles className="mr-2 h-4 w-4" /> {optimized ? "Sugestão aplicada" : "Aplicar sugestão de headline"}
          </button>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-blue-700">Skill gap</p>
              <h2 className="mt-1 text-xl font-black">Competências priorizadas</h2>
            </div>
            <Target className="text-blue-700" />
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            {["Python", "SQL", "Power BI", "Power Automate", "BPMN", "APIs", "n8n"].map((skill) => <span key={skill} className="badge">{skill}</span>)}
            {skillAdded && <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-black text-emerald-800">Lean Six Sigma</span>}
          </div>
          <div className="mt-5 rounded-2xl border border-amber-100 bg-amber-50 p-4">
            <p className="text-xs font-black uppercase tracking-wide text-amber-800">Recomendação</p>
            <p className="mt-2 text-sm leading-6 text-amber-900/80">Adicionar melhoria contínua e Lean Six Sigma reforça a família profissional de processos.</p>
          </div>
          <button type="button" onClick={() => { setSkillAdded(true); toast.success("Skill adicionada na demo"); }} disabled={skillAdded} className="btn-secondary mt-5 w-full justify-center">
            <CheckCircle2 className="mr-2 h-4 w-4" /> {skillAdded ? "Skill adicionada" : "Adicionar skill sugerida"}
          </button>
        </section>
      </div>
    </div>
  );
}

function AutomationPanel({
  enabled,
  onToggle,
}: {
  enabled: boolean;
  onToggle: () => void;
}) {
  const toast = useToast();
  const [connected, setConnected] = useState(false);
  const [lastRun, setLastRun] = useState("Hoje, 09:00");

  function runNow() {
    setLastRun("Agora mesmo");
    toast.success("Execução demonstrativa concluída", "12 coletadas · 3 relevantes · 0 notificações duplicadas.");
  }

  return (
    <div className="space-y-5">
      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
          <div>
            <p className="text-xs font-black uppercase tracking-wide text-blue-700">Agendamento pessoal</p>
            <h1 className="mt-1 text-2xl font-black">Automação e alertas</h1>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">Esta tela simula controles reais. No ambiente privado, scheduler e Evolution API executam o fluxo.</p>
          </div>
          <button type="button" onClick={onToggle} className={`inline-flex items-center justify-center rounded-2xl px-5 py-3 text-sm font-black ${enabled ? "bg-emerald-600 text-white" : "bg-slate-200 text-slate-700"}`}>
            <Wifi className="mr-2 h-4 w-4" /> {enabled ? "Automação ativa" : "Automação pausada"}
          </button>
        </div>
      </section>

      <div className="grid gap-5 xl:grid-cols-[1.05fr_0.95fr]">
        <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-blue-700">Pipeline multi-provider</p>
              <h2 className="mt-1 text-xl font-black">Última execução: {lastRun}</h2>
            </div>
            <Settings2 className="text-blue-700" />
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {[
              { name: "Gupy", status: "Operacional", jobs: 4, tone: "text-emerald-700 bg-emerald-50" },
              { name: "LinkedIn", status: "Operacional", jobs: 5, tone: "text-emerald-700 bg-emerald-50" },
              { name: "Vagas.com", status: "Operacional", jobs: 3, tone: "text-emerald-700 bg-emerald-50" },
              { name: "JobSpy", status: "Cooldown 429", jobs: 0, tone: "text-amber-800 bg-amber-50" },
            ].map((provider) => (
              <article key={provider.name} className="rounded-2xl border border-slate-100 p-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="font-black">{provider.name}</span>
                  <span className={`rounded-full px-2.5 py-1 text-[11px] font-black ${provider.tone}`}>{provider.status}</span>
                </div>
                <p className="mt-3 text-sm text-slate-500">{provider.jobs} vagas coletadas na amostra</p>
              </article>
            ))}
          </div>
          <button type="button" onClick={runNow} disabled={!enabled} className="btn-primary mt-5 w-full justify-center py-3">
            <Play className="mr-2 h-4 w-4" /> Executar agora
          </button>
        </section>

        <section className="rounded-3xl bg-slate-950 p-5 text-white shadow-xl">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-blue-200">WhatsApp privado</p>
              <h2 className="mt-1 text-xl font-black">Prévia do alerta</h2>
            </div>
            <MessageCircle className="text-emerald-300" />
          </div>
          <div className="mt-5 rounded-3xl bg-[#e7f7e9] p-4 text-slate-900">
            <div className="rounded-2xl bg-white p-4 shadow-sm">
              <p className="text-xs font-black text-emerald-700">Applymize · nova oportunidade</p>
              <p className="mt-2 text-sm font-black">Analista de Automação de Processos Pleno</p>
              <p className="mt-1 text-xs text-slate-500">Nexa Operações · Híbrido · São Paulo</p>
              <p className="mt-3 text-sm"><strong>94% de match</strong> · Power Automate, Python, BPMN e SQL.</p>
            </div>
          </div>
          <button type="button" onClick={() => { setConnected(true); toast.info("Conexão simulada", "Nenhuma mensagem real foi enviada."); }} className="mt-5 inline-flex w-full items-center justify-center rounded-xl bg-white px-4 py-3 text-sm font-black text-slate-950">
            {connected ? <Check className="mr-2 h-4 w-4" /> : <MessageCircle className="mr-2 h-4 w-4" />}
            {connected ? "Canal demonstrativo conectado" : "Simular conexão"}
          </button>
        </section>
      </div>
    </div>
  );
}

export function Demo() {
  const toast = useToast();
  const requestedView = new URLSearchParams(window.location.search).get("view");
  const initialView = demoViews.some((view) => view.id === requestedView) ? requestedView as DemoView : "overview";
  const [activeView, setActiveView] = useState<DemoView>(initialView);
  const [aiOpen, setAiOpen] = useState(requestedView === "ai");
  const [jobs, setJobs] = useState(initialJobs);
  const [applications, setApplications] = useState(initialApplications);
  const [automationEnabled, setAutomationEnabled] = useState(true);

  const activeMeta = useMemo(() => demoViews.find((view) => view.id === activeView) || demoViews[0], [activeView]);

  function simulateSearch() {
    if (jobs.some((job) => job.id === discoveredJob.id)) {
      toast.info("Busca já executada", "A nova oportunidade continua no topo da lista demonstrativa.");
      return;
    }
    setJobs((current) => [discoveredJob, ...current]);
    toast.success("Busca demonstrativa concluída", "12 coletadas · 4 elegíveis · 1 nova oportunidade adicionada.");
  }

  function toggleSave(id: number) {
    setJobs((current) => current.map((job) => job.id === id ? { ...job, saved: !job.saved } : job));
    const job = jobs.find((item) => item.id === id);
    toast.success(job?.saved ? "Vaga removida dos salvos" : "Vaga salva", "O estado existe somente durante esta visita.");
  }

  function applyToJob(job: DemoJob) {
    if (applications.some((application) => application.jobId === job.id)) {
      toast.info("Candidatura já está no pipeline");
      setActiveView("applications");
      return;
    }
    const next: DemoApplication = {
      id: Math.max(...applications.map((item) => item.id), 0) + 1,
      jobId: job.id,
      title: job.title,
      company: job.company,
      status: "applied",
      updated: "Agora mesmo",
    };
    setApplications((current) => [next, ...current]);
    toast.success("Candidatura adicionada à demo", "Agora você pode avançar as etapas no pipeline.");
    setActiveView("applications");
  }

  function advanceApplication(id: number) {
    setApplications((current) => current.map((application) => {
      if (application.id !== id) return application;
      const index = applicationStages.indexOf(application.status);
      const status = applicationStages[Math.min(index + 1, applicationStages.length - 1)];
      return { ...application, status, updated: "Agora mesmo" };
    }));
    toast.success("Etapa atualizada", "O dashboard demonstrativo reage às suas ações.");
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#f5f8fc] text-slate-950">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-2 px-3 py-3 sm:gap-3 sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <Link to="/" className="shrink-0" aria-label="Voltar ao início"><BrandLogo variant="mark" /></Link>
            <div className="hidden min-w-0 sm:block">
              <p className="truncate text-sm font-black">Applymize · experiência guiada</p>
              <p className="truncate text-xs text-slate-500">Dados seguros e ilustrativos</p>
            </div>
          </div>
          <DemoModeBadge compact />
          <div className="flex items-center gap-2">
            <Link to="/como-funciona" className="btn-secondary hidden md:inline-flex"><Code2 className="mr-2 h-4 w-4" /> Por trás</Link>
            <a href="https://github.com/vinmedrado/applymize" target="_blank" rel="noreferrer" className="btn-primary px-3 sm:px-4" aria-label="Ver código no GitHub">
              <Github className="h-4 w-4 sm:mr-2" /> <span className="hidden sm:inline">Ver código</span>
            </a>
          </div>
        </div>
      </header>

      <div className="mx-auto grid w-full min-w-0 max-w-[1600px] grid-cols-[minmax(0,1fr)] lg:grid-cols-[250px_minmax(0,1fr)]">
        <aside className="min-w-0 border-b border-slate-200 bg-white p-3 lg:min-h-[calc(100vh-65px)] lg:border-b-0 lg:border-r lg:p-4">
          <div className="flex gap-2 overflow-x-auto pb-1 lg:block lg:space-y-2 lg:overflow-visible">
            {demoViews.map((view) => {
              const Icon = view.icon;
              const active = activeView === view.id;
              return (
                <button
                  type="button"
                  key={view.id}
                  onClick={() => setActiveView(view.id)}
                  className={`flex shrink-0 items-center gap-3 rounded-2xl px-3 py-2.5 text-left transition lg:w-full ${active ? "bg-slate-950 text-white shadow-lg" : "bg-slate-50 text-slate-600 hover:bg-blue-50 hover:text-blue-900"}`}
                >
                  <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${active ? "bg-white/10 text-blue-200" : "bg-white text-blue-700 shadow-sm"}`}><Icon size={18} /></span>
                  <span>
                    <span className="block whitespace-nowrap text-sm font-black">{view.label}</span>
                    <span className={`hidden text-[11px] lg:block ${active ? "text-slate-300" : "text-slate-400"}`}>{view.helper}</span>
                  </span>
                </button>
              );
            })}
          </div>
          <div className="mt-5 hidden rounded-3xl bg-blue-50 p-4 lg:block">
            <Bot className="text-blue-700" />
            <p className="mt-3 text-sm font-black text-blue-950">Explore sem receio</p>
            <p className="mt-1 text-xs leading-5 text-blue-900/65">Nada aqui altera dados reais. Recarregar a página restaura o exemplo.</p>
          </div>
          <Link to="/" className="mt-4 hidden items-center text-xs font-black text-slate-500 hover:text-slate-950 lg:inline-flex">
            <ArrowLeft className="mr-2 h-4 w-4" /> Voltar ao portfólio
          </Link>
        </aside>

        <main className="w-full min-w-0 max-w-full overflow-hidden p-4 sm:p-5 lg:p-6">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-slate-400">Módulo atual</p>
              <p className="mt-0.5 font-black">{activeMeta.label}</p>
            </div>
            <div className="hidden items-center gap-2 text-xs font-bold text-slate-500 sm:flex">
              <ShieldCheck className="h-4 w-4 text-emerald-600" /> Sem login · backend pessoal protegido · dados ilustrativos
            </div>
          </div>

          {activeView === "overview" && <OverviewPanel jobs={jobs} applications={applications} automationEnabled={automationEnabled} onNavigate={setActiveView} onOpenAI={() => setAiOpen(true)} />}
          {activeView === "jobs" && <JobsPanel jobs={jobs} onSearch={simulateSearch} onToggleSave={toggleSave} onApply={applyToJob} />}
          {activeView === "applications" && <ApplicationsPanel applications={applications} onAdvance={advanceApplication} />}
          {activeView === "ats" && <AtsPanel />}
          {activeView === "profile" && <ProfilePanel />}
          {activeView === "automation" && <AutomationPanel enabled={automationEnabled} onToggle={() => { setAutomationEnabled((current) => !current); toast.info(automationEnabled ? "Automação pausada na demo" : "Automação ativada na demo"); }} />}
        </main>
      </div>
      <PortfolioAIFloatingAssistant open={aiOpen} onOpenChange={setAiOpen} />
    </div>
  );
}
