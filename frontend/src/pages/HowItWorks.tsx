import { Link } from "react-router-dom";
import {
  ArrowRight,
  BellRing,
  Bot,
  BriefcaseBusiness,
  CheckCircle2,
  Database,
  FileSearch,
  Filter,
  GitMerge,
  LockKeyhole,
  MessageCircle,
  Radar,
  SearchCheck,
  ShieldCheck,
  Sparkles,
  UserRoundSearch,
} from "lucide-react";
import {
  MarketingSection,
  PublicFooter,
  PublicHeader,
  PublicShell,
} from "../components/marketing";

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

const truthTable = [
  {
    status: "Funcional",
    tone: "border-emerald-200 bg-emerald-50 text-emerald-900",
    title: "Plataforma autenticada",
    description: "Perfil, descoberta de vagas, matching, ATS, candidaturas, automações e alertas conectados ao backend.",
  },
  {
    status: "Real e local",
    tone: "border-blue-200 bg-blue-50 text-blue-900",
    title: "Laboratório ATS público",
    description: "O arquivo é lido e pontuado no navegador. Não chama IA, não exige login e não envia o currículo.",
  },
  {
    status: "Demonstração",
    tone: "border-amber-200 bg-amber-50 text-amber-900",
    title: "Showcases públicos",
    description: "Dashboard e alguns resultados visuais usam dados ilustrativos e são identificados como demonstração.",
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
              <Sparkles size={16} /> Por trás do produto
            </div>
            <h1 className="mt-6 text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
              Da intenção profissional até a oportunidade certa.
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
              O Applymize não é apenas uma interface. Existe um pipeline que transforma perfil, currículo e preferências em buscas personalizadas, filtros explicáveis, análises e alertas.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link to="/laboratorio-ats" className="inline-flex items-center justify-center rounded-2xl bg-white px-6 py-3 font-black text-slate-950">
                Experimentar o ATS <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
              <Link to="/demo" className="inline-flex items-center justify-center rounded-2xl border border-white/15 bg-white/10 px-6 py-3 font-black text-white">
                Ver interface demonstrativa
              </Link>
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
