import { ChangeEvent, FormEvent, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ClipboardCheck,
  Eraser,
  FileText,
  FlaskConical,
  Loader2,
  LockKeyhole,
  MessageCircle,
  SearchCheck,
  ShieldCheck,
  Upload,
} from "lucide-react";
import {
  MarketingSection,
  PublicFooter,
  PublicHeader,
  PublicShell,
} from "../components/marketing";
import { readDocumentFile } from "../services/browserDocument";
import { analyzePublicResume, LocalAtsAnalysis } from "../services/publicAtsEngine";

const SAMPLE_RESUME = `VINICIUS EXEMPLO
vinicius@example.com | (11) 99999-9999
linkedin.com/in/vinicius-exemplo | github.com/vinicius-exemplo

RESUMO PROFISSIONAL
Analista de Automação de Processos com experiência em transformar rotinas manuais em fluxos digitais mensuráveis.

HABILIDADES E TECNOLOGIAS
Power Automate, Python, SQL, Excel, VBA, RPA, BPMN, Power BI, n8n, APIs REST e Git.

EXPERIÊNCIA PROFISSIONAL
Analista de Automação de Processos
- Automatizei 18 rotinas operacionais com Power Automate e Python, reduzindo 240 horas mensais de trabalho manual.
- Estruturei indicadores em Power BI e SQL para acompanhar SLA, erros e produtividade.
- Mapeei processos em BPMN e implementei melhorias que reduziram o retrabalho em 32%.
- Integrei APIs REST entre sistemas internos e criei documentação para sustentação.

PROJETOS
- Pipeline de automação para conciliação de dados com Python, SQL e alertas.
- Dashboard de eficiência operacional com Power BI e DAX.

FORMAÇÃO
Tecnologia em Análise e Desenvolvimento de Sistemas.

CERTIFICAÇÕES
Microsoft Power Platform Fundamentals e Lean Six Sigma Yellow Belt.`;

const SAMPLE_JOB = `Analista de Automação de Processos Pleno
Buscamos profissional para mapear, redesenhar e automatizar processos.
Requisitos: Power Automate, RPA, BPMN, Excel, APIs REST e SQL.
Experiência com indicadores, melhoria contínua e documentação.
Diferenciais: Python, n8n, Lean Six Sigma e Power BI.`;

const scoreLabels: Array<[keyof LocalAtsAnalysis, string]> = [
  ["ats_score", "Estrutura ATS"],
  ["rh_score", "Leitura de RH"],
  ["match_score", "Aderência à vaga"],
  ["keyword_score", "Palavras-chave"],
  ["experience_score", "Experiência"],
  ["clarity_score", "Clareza"],
  ["seniority_score", "Senioridade"],
];

function scoreTone(score: number) {
  if (score >= 85) return "bg-emerald-500";
  if (score >= 70) return "bg-lime-500";
  if (score >= 55) return "bg-amber-500";
  if (score >= 40) return "bg-orange-500";
  return "bg-red-500";
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-sm font-bold text-slate-700">
        <span>{label}</span>
        <span>{Math.round(value)}%</span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full ${scoreTone(value)}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
    </div>
  );
}

function priorityTone(priority: string) {
  if (priority === "alta") return "border-red-200 bg-red-50 text-red-800";
  if (priority === "média") return "border-amber-200 bg-amber-50 text-amber-800";
  return "border-blue-200 bg-blue-50 text-blue-800";
}

export function PublicAtsLab() {
  const [resumeText, setResumeText] = useState("");
  const [targetRole, setTargetRole] = useState("Automação de Processos");
  const [jobDescription, setJobDescription] = useState("");
  const [fileName, setFileName] = useState("");
  const [fileLoading, setFileLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState<LocalAtsAnalysis | null>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  const whatsappMessage = useMemo(() => {
    if (!analysis) return "";
    const gaps = analysis.missing_keywords.slice(0, 5).join(", ") || "nenhuma palavra-chave crítica";
    return [
      "Resultado do Laboratório ATS Applymize",
      `Score geral: ${Math.round(analysis.final_score)}/100 (${analysis.grade})`,
      `Estrutura ATS: ${Math.round(analysis.ats_score)}%`,
      `Aderência: ${Math.round(analysis.match_score)}%`,
      `Principais pontos para revisar: ${gaps}.`,
      "Análise indicativa e transparente; não substitui a decisão de um recrutador.",
    ].join("\n");
  }, [analysis]);

  async function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setError("");
    setFileLoading(true);
    setAnalysis(null);
    try {
      const text = await readDocumentFile(file);
      setResumeText(text);
      setFileName(file.name);
    } catch (err) {
      setFileName("");
      setError(err instanceof Error ? err.message : "Não foi possível ler o arquivo.");
    } finally {
      setFileLoading(false);
      event.target.value = "";
    }
  }

  function handleAnalyze(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (resumeText.trim().length < 250) {
      setError("Insira pelo menos 250 caracteres do currículo para gerar uma análise útil.");
      return;
    }
    const result = analyzePublicResume({ resumeText, targetRole, jobDescription });
    setAnalysis(result);
    window.setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  }

  function loadSample() {
    setResumeText(SAMPLE_RESUME);
    setTargetRole("Automação de Processos");
    setJobDescription(SAMPLE_JOB);
    setFileName("exemplo-automacao.txt");
    setAnalysis(null);
    setError("");
  }

  function clearAll() {
    setResumeText("");
    setTargetRole("");
    setJobDescription("");
    setFileName("");
    setAnalysis(null);
    setError("");
  }

  return (
    <PublicShell>
      <PublicHeader />

      <section className="relative overflow-hidden bg-slate-950 text-white">
        <div className="absolute left-1/3 top-0 h-96 w-96 rounded-full bg-blue-500/20 blur-3xl" />
        <MarketingSection className="relative py-16 sm:py-20">
          <div className="grid items-center gap-10 lg:grid-cols-[1fr_0.8fr]">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-bold text-blue-100">
                <FlaskConical size={17} /> Experimento público real
              </div>
              <h1 className="mt-6 text-4xl font-black tracking-tight sm:text-5xl">
                Teste seu currículo como um ATS e um recrutador fariam.
              </h1>
              <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-300">
                Carregue PDF, DOCX ou TXT, compare com uma vaga e entenda cada dimensão do score. Sem login, sem IA e sem enviar seu currículo.
              </p>
            </div>
            <div className="rounded-[2rem] border border-white/10 bg-white/10 p-6 backdrop-blur">
              <div className="flex items-start gap-3">
                <LockKeyhole className="mt-1 shrink-0 text-emerald-300" />
                <div>
                  <h2 className="font-black">Processamento local</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    O conteúdo fica na memória desta página. Ao fechar ou atualizar, os dados desaparecem.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </MarketingSection>
      </section>

      <MarketingSection className="py-10">
        <form onSubmit={handleAnalyze} className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm lg:p-7">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs font-black uppercase tracking-wide text-blue-700">1. Currículo</p>
                <h2 className="mt-1 text-xl font-black">Carregue ou cole o conteúdo</h2>
              </div>
              <button type="button" onClick={loadSample} className="btn-secondary">Usar exemplo</button>
            </div>

            <label className="mt-5 flex cursor-pointer items-center justify-center rounded-2xl border-2 border-dashed border-blue-200 bg-blue-50/60 p-5 text-center transition hover:border-blue-400">
              <input type="file" accept=".pdf,.docx,.txt,application/pdf,text/plain" className="sr-only" onChange={handleFile} disabled={fileLoading} />
              <span>
                {fileLoading ? <Loader2 className="mx-auto h-7 w-7 animate-spin text-blue-700" /> : <Upload className="mx-auto h-7 w-7 text-blue-700" />}
                <span className="mt-2 block font-black text-slate-900">{fileLoading ? "Lendo arquivo..." : "Selecionar PDF, DOCX ou TXT"}</span>
                <span className="mt-1 block text-xs text-slate-500">Até 8 MB · leitura feita no navegador</span>
              </span>
            </label>

            {fileName && (
              <div className="mt-3 flex items-center gap-2 rounded-xl bg-emerald-50 px-3 py-2 text-sm font-bold text-emerald-800">
                <FileText size={16} /> {fileName}
              </div>
            )}

            <label className="mt-5 block text-sm font-bold text-slate-700" htmlFor="resume-text">Texto do currículo</label>
            <textarea
              id="resume-text"
              className="input mt-2 min-h-[330px] resize-y"
              placeholder="Cole aqui o texto do currículo..."
              value={resumeText}
              onChange={(event) => {
                setResumeText(event.target.value);
                setAnalysis(null);
              }}
            />
            <p className="mt-2 text-right text-xs text-slate-400">{resumeText.length.toLocaleString("pt-BR")} caracteres</p>
          </section>

          <section className="space-y-6">
            <div className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm lg:p-7">
              <p className="text-xs font-black uppercase tracking-wide text-blue-700">2. Contexto desejado</p>
              <h2 className="mt-1 text-xl font-black">Compare com um cargo ou vaga</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">A descrição é opcional, mas deixa a leitura de palavras-chave mais específica.</p>

              <label className="mt-5 block text-sm font-bold text-slate-700" htmlFor="target-role">Cargo alvo</label>
              <input
                id="target-role"
                className="input mt-2"
                placeholder="Ex.: Automação de Processos"
                value={targetRole}
                onChange={(event) => setTargetRole(event.target.value)}
              />

              <label className="mt-5 block text-sm font-bold text-slate-700" htmlFor="job-description">Descrição da vaga</label>
              <textarea
                id="job-description"
                className="input mt-2 min-h-[210px] resize-y"
                placeholder="Cole responsabilidades e requisitos da vaga..."
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
              />
            </div>

            {error && (
              <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-800">
                <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" /> {error}
              </div>
            )}

            <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
              <button type="submit" className="btn-primary justify-center px-6 py-3 text-base" disabled={fileLoading}>
                <SearchCheck className="mr-2 h-5 w-5" /> Analisar agora
              </button>
              <button type="button" onClick={clearAll} className="btn-secondary px-5 py-3" aria-label="Limpar dados">
                <Eraser className="mr-2 h-4 w-4" /> Limpar
              </button>
            </div>
          </section>
        </form>
      </MarketingSection>

      {analysis && (
        <div ref={resultRef}>
          <MarketingSection className="scroll-mt-24 py-8">
            <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
              <div>
                <p className="text-sm font-black uppercase tracking-wide text-blue-700">Resultado local</p>
                <h2 className="mt-2 text-3xl font-black">Leitura ATS + RH</h2>
              </div>
              <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-bold text-emerald-800">
                <ShieldCheck size={17} /> Nenhum dado enviado
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
              <aside className="rounded-[2rem] bg-slate-950 p-7 text-center text-white shadow-xl">
                <p className="text-sm font-bold text-slate-300">Score geral</p>
                <p className="mt-3 text-7xl font-black">{Math.round(analysis.final_score)}</p>
                <span className="mt-4 inline-flex rounded-full bg-white/10 px-5 py-2 text-xl font-black">Nota {analysis.grade}</span>
                <p className="mt-5 text-sm leading-6 text-slate-300">{analysis.probability}</p>
              </aside>

              <section className="grid gap-x-8 gap-y-5 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2">
                {scoreLabels.map(([key, label]) => (
                  <ScoreBar key={String(key)} label={label} value={analysis[key] as number} />
                ))}
              </section>
            </div>

            {analysis.warnings.length > 0 && (
              <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-900">
                <h3 className="flex items-center gap-2 font-black"><AlertTriangle size={18} /> Avisos da leitura</h3>
                <ul className="mt-3 list-disc space-y-1 pl-5">
                  {analysis.warnings.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </div>
            )}

            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              <article className="rounded-3xl border border-emerald-200 bg-emerald-50 p-6">
                <h3 className="flex items-center gap-2 font-black text-emerald-900"><CheckCircle2 size={20} /> Pontos fortes</h3>
                <ul className="mt-4 space-y-3 text-sm leading-6 text-emerald-900">
                  {analysis.strengths.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </article>
              <article className="rounded-3xl border border-red-200 bg-red-50 p-6">
                <h3 className="flex items-center gap-2 font-black text-red-900"><AlertTriangle size={20} /> Pontos de atenção</h3>
                <ul className="mt-4 space-y-3 text-sm leading-6 text-red-900">
                  {analysis.weaknesses.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </article>
            </div>

            <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
              <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="text-xl font-black">Ajustes recomendados</h3>
                <div className="mt-5 space-y-3">
                  {analysis.suggestions.map((item) => (
                    <article key={`${item.priority}-${item.title}`} className={`rounded-2xl border p-4 ${priorityTone(item.priority)}`}>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="rounded-full bg-white/70 px-2.5 py-1 text-xs font-black uppercase">{item.priority}</span>
                        <h4 className="font-black">{item.title}</h4>
                      </div>
                      <p className="mt-2 text-sm leading-6 opacity-90">{item.description}</p>
                    </article>
                  ))}
                </div>
              </section>

              <section className="space-y-6">
                <article className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
                  <h3 className="font-black">Palavras-chave faltantes</h3>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {analysis.missing_keywords.length
                      ? analysis.missing_keywords.map((keyword) => <span key={keyword} className="badge">{keyword}</span>)
                      : <p className="text-sm text-slate-500">Nenhuma lacuna crítica detectada.</p>}
                  </div>
                </article>

                <article className="rounded-[2rem] bg-[#0b7a3e] p-6 text-white shadow-xl">
                  <div className="flex items-center gap-2">
                    <MessageCircle size={22} />
                    <h3 className="font-black">Prévia para WhatsApp</h3>
                  </div>
                  <pre className="mt-4 whitespace-pre-wrap rounded-2xl bg-black/15 p-4 font-sans text-sm leading-6 text-emerald-50">{whatsappMessage}</pre>
                  <a
                    href={`https://wa.me/?text=${encodeURIComponent(whatsappMessage)}`}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-4 inline-flex w-full items-center justify-center rounded-xl bg-white px-5 py-3 text-sm font-black text-emerald-900"
                  >
                    Abrir no WhatsApp <ArrowRight className="ml-2 h-4 w-4" />
                  </a>
                  <p className="mt-3 text-xs leading-5 text-emerald-100">O botão apenas abre a mensagem. Nada é enviado automaticamente.</p>
                </article>
              </section>
            </div>
          </MarketingSection>
        </div>
      )}

      <MarketingSection className="py-10">
        <div className="grid gap-6 rounded-[2rem] border border-slate-200 bg-white p-6 lg:grid-cols-[0.8fr_1.2fr] lg:p-8">
          <div>
            <ClipboardCheck className="text-blue-700" size={28} />
            <h2 className="mt-4 text-2xl font-black">O que este score significa?</h2>
            <p className="mt-3 text-sm leading-7 text-slate-600">
              É uma avaliação determinística e explicável da estrutura, contatos, skills, evidências, senioridade e aderência ao texto da vaga.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {[
              "Não representa todos os ATS do mercado.",
              "Não inventa experiência nem recomenda palavras falsas.",
              "Não usa IA generativa nesta página.",
              "A decisão final continua sendo humana.",
            ].map((item) => (
              <div key={item} className="flex items-start gap-2 rounded-2xl bg-slate-50 p-4 text-sm font-semibold text-slate-700">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-blue-700" /> {item}
              </div>
            ))}
          </div>
        </div>
        <div className="mt-6 text-center">
          <Link to="/como-funciona" className="inline-flex items-center font-black text-blue-700">
            Entenda todo o sistema por trás <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </div>
      </MarketingSection>

      <PublicFooter />
    </PublicShell>
  );
}
