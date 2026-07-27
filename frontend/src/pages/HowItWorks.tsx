import { Link } from "react-router-dom";
import {
  ArrowRight,
  BellRing,
  Bot,
  Boxes,
  BriefcaseBusiness,
  CheckCircle2,
  Code2,
  Database,
  FileSearch,
  Filter,
  Github,
  GitMerge,
  LockKeyhole,
  Radar,
  SearchCheck,
  Server,
  ShieldCheck,
  Sparkles,
  TestTube2,
  UserRoundSearch,
  Workflow,
} from "lucide-react";
import {
  MarketingSection,
  PublicFooter,
  PublicHeader,
  PublicShell,
} from "../components/marketing";

const repositoryUrl = "https://github.com/vinmedrado/applymize";

const pipeline = [
  {
    icon: <FileSearch size={22} />,
    step: "01",
    title: "Currículo e objetivo",
    description: "O perfil reúne currículo, cargo alvo, senioridade, skills, localização e preferências reais.",
  },
  {
    icon: <Radar size={22} />,
    step: "02",
    title: "Descoberta de vagas",
    description: "Buscas independentes consultam múltiplas fontes com termos derivados do objetivo de cada usuário.",
  },
  {
    icon: <GitMerge size={22} />,
    step: "03",
    title: "Normalização",
    description: "Vagas são padronizadas, deduplicadas e guardam a origem e o termo que levou à descoberta.",
  },
  {
    icon: <Filter size={22} />,
    step: "04",
    title: "Elegibilidade",
    description: "Cargo, família profissional, senioridade, modalidade e localização removem resultados incompatíveis.",
  },
  {
    icon: <SearchCheck size={22} />,
    step: "05",
    title: "ATS e aderência",
    description: "Estrutura, palavras-chave, experiência e contexto da vaga compõem scores explicáveis.",
  },
  {
    icon: <BellRing size={22} />,
    step: "06",
    title: "Automação",
    description: "O agendador atualiza oportunidades e prepara alertas somente quando há vagas realmente relevantes.",
  },
];

const layers = [
  {
    icon: <Database size={22} />,
    title: "Dados isolados",
    description: "Perfis, vagas, candidaturas e análises respeitam usuário e tenant.",
  },
  {
    icon: <BriefcaseBusiness size={22} />,
    title: "Operação rastreável",
    description: "Cada execução registra provedor, termo pesquisado, quantidade recebida e decisões de filtro.",
  },
  {
    icon: <Bot size={22} />,
    title: "IA com contexto",
    description: "Recursos autenticados podem usar o histórico e o perfil profissional sem expor chaves no navegador.",
  },
  {
    icon: <ShieldCheck size={22} />,
    title: "Regras antes da IA",
    description: "Filtros determinísticos protegem relevância, custos e consistência antes de qualquer camada generativa.",
  },
];

const stack = [
  {
    icon: <Code2 size={22} />,
    title: "React + TypeScript",
    detail: "Interface responsiva em Vite, com rotas públicas, área autenticada e demo isolada.",
    path: "frontend/src",
  },
  {
    icon: <Server size={22} />,
    title: "FastAPI",
    detail: "API modular com autenticação, serviços de vagas, ATS, candidaturas e automações.",
    path: "backend",
  },
  {
    icon: <Boxes size={22} />,
    title: "PostgreSQL + Redis",
    detail: "Persistência relacional, migrações Alembic, filas e execução assíncrona.",
    path: "alembic",
  },
  {
    icon: <Workflow size={22} />,
    title: "Workers + integrações",
    detail: "Pipeline de ingestão, agendador e notificações desacoplados da experiência web.",
    path: "backend/services",
  },
];

const evidence = [
  {
    label: "ATS público no navegador",
    path: "frontend/src/services/publicAtsEngine.ts",
    description: "Motor determinístico que analisa texto localmente e explica o score.",
  },
  {
    label: "Ingestão de vagas",
    path: "backend/services/job_ingestion.py",
    description: "Orquestra descoberta, normalização, deduplicação e persistência.",
  },
  {
    label: "Relevância profissional",
    path: "backend/services/job_role_relevance.py",
    description: "Evita que termos parecidos desviem a busca para famílias de cargo incorretas.",
  },
  {
    label: "Agendador de automações",
    path: "backend/services/automation_scheduler.py",
    description: "Coordena buscas recorrentes e a entrega de resultados relevantes.",
  },
];

const truthTable = [
  {
    status: "Funcional no ambiente privado",
    tone: "border-emerald-200 bg-emerald-50 text-emerald-900",
    title: "Plataforma autenticada",
    description: "Perfil, descoberta de vagas, matching, ATS, candidaturas, automações e alertas conectados ao backend local.",
  },
  {
    status: "Real e local",
    tone: "border-blue-200 bg-blue-50 text-blue-900",
    title: "Laboratório ATS público",
    description: "O arquivo é lido e pontuado no navegador. Não chama IA, não exige login e não envia o currículo.",
  },
  {
    status: "Demonstração interativa",
    tone: "border-amber-200 bg-amber-50 text-amber-900",
    title: "Experiência para avaliação",
    description: "Busca, matching, pipeline, perfil e automações usam dados ilustrativos e estado temporário no navegador.",
  },
  {
    status: "Integração futura",
    tone: "border-slate-200 bg-slate-50 text-slate-800",
    title: "Importação oficial do LinkedIn",
    description: "Não fazemos scraping de URL. A evolução prevista é OAuth aprovado; hoje usamos PDF ou texto fornecido.",
  },
];

export function HowItWorks() {
  return (
    <PublicShell>
      <PublicHeader />

      <section className="relative overflow-hidden bg-slate-950 text-white">
        <div className="absolute -left-20 top-10 h-80 w-80 rounded-full bg-blue-500/20 blur-3xl" />
        <div className="absolute right-0 top-40 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
        <MarketingSection className="relative py-20 sm:py-24">
          <div className="max-w-4xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-bold text-blue-100">
              <Sparkles size={16} /> Por trás do projeto
            </div>
            <h1 className="mt-6 text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
              Arquitetura, decisões e limites visíveis.
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
              O Applymize é um portfólio full-stack e uma ferramenta de uso pessoal. Esta página abre a caixa-preta: mostra como perfil, vagas e preferências atravessam o sistema e separa, com clareza, produto real de demonstração pública.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link to="/demo" className="inline-flex items-center justify-center rounded-2xl bg-white px-6 py-3 font-black text-slate-950">
                Explorar a demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
              <a
                href={repositoryUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center justify-center rounded-2xl border border-white/15 bg-white/10 px-6 py-3 font-black text-white"
              >
                <Github className="mr-2 h-4 w-4" /> Ver código no GitHub
              </a>
            </div>
          </div>
        </MarketingSection>
      </section>

      <MarketingSection>
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-black uppercase tracking-wide text-blue-700">Pipeline principal</p>
          <h2 className="mt-3 text-3xl font-black tracking-tight sm:text-4xl">Como os dados atravessam o sistema</h2>
          <p className="mt-4 leading-7 text-slate-600">
            Cada etapa reduz ruído antes que a vaga chegue ao dashboard ou ao WhatsApp.
          </p>
        </div>
        <div className="relative mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {pipeline.map((item) => (
            <article key={item.step} className="relative rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-700">{item.icon}</div>
                <span className="text-3xl font-black text-slate-200">{item.step}</span>
              </div>
              <h3 className="mt-5 text-xl font-black">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
            </article>
          ))}
        </div>
      </MarketingSection>

      <MarketingSection className="pt-4">
        <div className="grid gap-8 rounded-[2.25rem] bg-slate-950 p-6 text-white lg:grid-cols-[0.85fr_1.15fr] lg:p-10">
          <div>
            <p className="text-sm font-black uppercase tracking-wide text-blue-200">Arquitetura aplicada</p>
            <h2 className="mt-3 text-3xl font-black">Automação de Processos não deveria virar Analista de Dados por acidente.</h2>
            <p className="mt-4 leading-7 text-slate-300">
              O cargo alvo gera termos de busca próprios. Depois, a família profissional e os sinais presentes no título e na descrição validam a vaga. Senioridade e localização entram como filtros separados.
            </p>
            <div className="mt-6 rounded-3xl border border-white/10 bg-white/10 p-5">
              <p className="text-xs font-black uppercase tracking-wide text-blue-200">Exemplo de fluxo</p>
              <p className="mt-3 font-bold">Automação de Processos → RPA / BPM / Power Automate → validação do título → elegibilidade → ranking</p>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {layers.map((item) => (
              <article key={item.title} className="rounded-3xl border border-white/10 bg-white/10 p-5">
                <div className="text-blue-200">{item.icon}</div>
                <h3 className="mt-4 font-black">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-300">{item.description}</p>
              </article>
            ))}
          </div>
        </div>
      </MarketingSection>

      <MarketingSection className="pt-4">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-black uppercase tracking-wide text-blue-700">Implementação</p>
          <h2 className="mt-3 text-3xl font-black">A stack e as evidências estão abertas</h2>
          <p className="mt-4 leading-7 text-slate-600">
            Os cartões abaixo levam diretamente aos pontos do repositório que materializam cada decisão.
          </p>
        </div>
        <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {stack.map((item) => (
            <a
              key={item.title}
              href={`${repositoryUrl}/tree/main/${item.path}`}
              target="_blank"
              rel="noreferrer"
              className="group rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-blue-300 hover:shadow-lg"
            >
              <div className="text-blue-700">{item.icon}</div>
              <h3 className="mt-4 font-black">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.detail}</p>
              <span className="mt-4 inline-flex items-center text-xs font-black text-blue-700">
                {item.path} <ArrowRight className="ml-1 h-3.5 w-3.5 transition group-hover:translate-x-1" />
              </span>
            </a>
          ))}
        </div>
        <div className="mt-6 grid gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-5 md:grid-cols-2">
          {evidence.map((item) => (
            <a
              key={item.path}
              href={`${repositoryUrl}/blob/main/${item.path}`}
              target="_blank"
              rel="noreferrer"
              className="rounded-2xl bg-white p-5 shadow-sm transition hover:ring-2 hover:ring-blue-200"
            >
              <div className="flex items-center gap-2 text-blue-700">
                <TestTube2 size={18} />
                <span className="font-black">{item.label}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
              <code className="mt-3 block overflow-hidden text-ellipsis text-xs text-slate-500">{item.path}</code>
            </a>
          ))}
        </div>
      </MarketingSection>

      <MarketingSection className="pt-4">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-black uppercase tracking-wide text-blue-700">Transparência</p>
          <h2 className="mt-3 text-3xl font-black">O que é real e o que é demonstração</h2>
        </div>
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          {truthTable.map((item) => (
            <article key={item.title} className={`rounded-3xl border p-6 ${item.tone}`}>
              <div className="flex items-center gap-2 text-xs font-black uppercase tracking-wide">
                <CheckCircle2 size={16} /> {item.status}
              </div>
              <h3 className="mt-3 text-xl font-black">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 opacity-80">{item.description}</p>
            </article>
          ))}
        </div>
      </MarketingSection>

      <MarketingSection className="pt-4">
        <div className="grid items-center gap-8 rounded-[2.25rem] border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-8 shadow-xl shadow-slate-200/50 lg:grid-cols-[1fr_auto]">
          <div>
            <div className="flex items-center gap-2 text-blue-700"><LockKeyhole size={20} /><span className="text-sm font-black uppercase tracking-wide">Teste sem cadastro</span></div>
            <h2 className="mt-3 text-3xl font-black">Quer validar o raciocínio do ATS?</h2>
            <p className="mt-3 max-w-2xl leading-7 text-slate-600">
              Carregue um currículo e, se quiser, uma vaga. A análise acontece localmente e mostra cada dimensão do score.
            </p>
          </div>
          <Link to="/laboratorio-ats" className="btn-primary px-6 py-3 text-base">
            Abrir laboratório <UserRoundSearch className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </MarketingSection>

      <PublicFooter />
    </PublicShell>
  );
}
