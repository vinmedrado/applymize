import { useEffect, useMemo, useState } from "react";
import { ClipboardCheck, Search } from "lucide-react";

import { EmptyState } from "../components/EmptyState";
import { PageLoading, Spinner } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { analyzeJob, analyzeMe } from "../services/ats";
import { listJobs } from "../services/jobs";
import { AtsAnalysis, Job } from "../types";

function scoreTone(score: number) {
  if (score >= 85) return "bg-emerald-500";
  if (score >= 70) return "bg-lime-500";
  if (score >= 55) return "bg-amber-500";
  if (score >= 40) return "bg-orange-500";
  return "bg-red-500";
}

function gradeTone(grade: string) {
  if (grade === "A+" || grade === "A") return "bg-emerald-600 text-white";
  if (grade === "B") return "bg-lime-100 text-lime-800";
  if (grade === "C") return "bg-amber-100 text-amber-800";
  if (grade === "D") return "bg-orange-100 text-orange-800";
  return "bg-red-100 text-red-800";
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm font-semibold">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full rounded-full ${scoreTone(value)}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
    </div>
  );
}

function PriorityBadge({ priority }: { priority: string }) {
  const tone =
    priority === "alta"
      ? "bg-red-50 text-red-700 border-red-200"
      : priority === "média"
      ? "bg-amber-50 text-amber-700 border-amber-200"
      : "bg-slate-100 text-slate-700 border-slate-200";
  return <span className={`rounded-full border px-2.5 py-1 text-xs font-bold ${tone}`}>{priority}</span>;
}

export function AtsAnalyzer() {
  const toast = useToast();
  const [analysis, setAnalysis] = useState<AtsAnalysis | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    Promise.all([listJobs().catch(() => ({ items: [], total: 0, page: 1, pageSize: 50, hiddenIrrelevant: 0 })), analyzeMe().catch(() => null)])
      .then(([jobData, initialAnalysis]) => {
        setJobs(jobData.items);
        if (initialAnalysis) setAnalysis(initialAnalysis);
      })
      .finally(() => setInitialLoading(false));
  }, []);

  const selectedJob = useMemo(() => jobs.find((job) => String(job.id) === selectedJobId), [jobs, selectedJobId]);

  async function runAnalyzeMe() {
    setLoading(true);
    try {
      setAnalysis(await analyzeMe());
      toast.success("Análise concluída", "Seu currículo foi avaliado como ATS + RH.");
    } catch (err) {
      toast.error("Erro ao analisar currículo", getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  async function runAnalyzeJob() {
    if (!selectedJobId) {
      toast.info("Selecione uma vaga", "Escolha uma vaga para comparar com seu currículo.");
      return;
    }
    setLoading(true);
    try {
      setAnalysis(await analyzeJob(Number(selectedJobId)));
      toast.success("Análise contra vaga concluída", selectedJob?.title);
    } catch (err) {
      toast.error("Erro ao analisar contra vaga", getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  if (initialLoading) return <PageLoading label="Carregando ATS Analyzer..." />;

  return (
    <div className="space-y-6" data-tour="ats-page">
      <section className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <p className="text-sm text-slate-500">ATS/RH Analyzer</p>
        <h1 className="mt-2 text-3xl font-bold">Analisador ATS + Recrutador</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-500">
          Avalie estrutura, clareza, keywords, experiência, senioridade e chance de passar na triagem.
        </p>
      </section>

      <SectionCard title="Executar análise" subtitle="Analise seu currículo sozinho ou compare com uma vaga específica.">
        <div className="grid gap-3 lg:grid-cols-[1fr_auto_auto]">
          <select className="input" value={selectedJobId} onChange={(e) => setSelectedJobId(e.target.value)}>
            <option value="">Selecionar vaga para comparação</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>{job.title} — {job.company}</option>
            ))}
          </select>
          <button className="btn-secondary" onClick={runAnalyzeMe} disabled={loading}>
            {loading ? <Spinner label="Analisando..." /> : <><ClipboardCheck className="mr-2 h-4 w-4" /> Analisar meu currículo</>}
          </button>
          <button className="btn-primary" onClick={runAnalyzeJob} disabled={loading}>
            {loading ? <Spinner label="Comparando..." /> : <><Search className="mr-2 h-4 w-4" /> Analisar contra vaga</>}
          </button>
        </div>
      </SectionCard>

      {!analysis ? (
        <EmptyState title="Nenhuma análise ainda" description="Clique em Analisar meu currículo para começar." />
      ) : (
        <>
          <section className="grid gap-4 lg:grid-cols-[280px_1fr]">
            <div className="rounded-3xl bg-white p-6 text-center shadow-sm ring-1 ring-slate-200">
              <p className="text-sm font-semibold text-slate-500">Score geral</p>
              <p className="mt-3 text-6xl font-extrabold">{analysis.final_score}%</p>
              <span className={`mt-4 inline-flex rounded-full px-4 py-2 text-lg font-extrabold ${gradeTone(analysis.grade)}`}>
                {analysis.grade}
              </span>
              <p className="mt-4 text-sm leading-6 text-slate-600">{analysis.probability}</p>
            </div>

            <div className="card grid gap-4 p-6 md:grid-cols-2">
              <ScoreBar label="ATS Score" value={analysis.ats_score} />
              <ScoreBar label="RH Score" value={analysis.rh_score} />
              <ScoreBar label="Match Score" value={analysis.match_score} />
              <ScoreBar label="Keyword Score" value={analysis.keyword_score} />
              <ScoreBar label="Experience Score" value={analysis.experience_score} />
              <ScoreBar label="Clarity Score" value={analysis.clarity_score} />
              <ScoreBar label="Seniority Score" value={analysis.seniority_score} />
            </div>
          </section>

          {analysis.warnings.length > 0 && (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              <p className="font-bold">Avisos importantes</p>
              <ul className="mt-2 list-disc pl-5">
                {analysis.warnings.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
          )}

          <div className="grid gap-6 lg:grid-cols-2">
            <SectionCard title="Pontos fortes">
              <ul className="space-y-2 text-sm text-slate-700">
                {analysis.strengths.map((item) => <li className="rounded-xl bg-emerald-50 p-3 text-emerald-800" key={item}>{item}</li>)}
              </ul>
            </SectionCard>
            <SectionCard title="Pontos fracos">
              <ul className="space-y-2 text-sm text-slate-700">
                {analysis.weaknesses.map((item) => <li className="rounded-xl bg-red-50 p-3 text-red-800" key={item}>{item}</li>)}
              </ul>
            </SectionCard>
          </div>

          <SectionCard title="Palavras-chave faltantes" subtitle="Inclua naturalmente no currículo quando forem verdadeiras.">
            <div className="flex flex-wrap gap-2">
              {analysis.missing_keywords.length ? analysis.missing_keywords.map((item) => <span className="badge" key={item}>{item}</span>) : <p className="text-sm text-slate-500">Nenhuma keyword crítica faltante detectada.</p>}
            </div>
          </SectionCard>

          <SectionCard title="Ajustes recomendados">
            <div className="grid gap-3">
              {analysis.suggestions.map((item) => (
                <div key={`${item.priority}-${item.title}`} className="rounded-2xl border border-slate-200 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <PriorityBadge priority={item.priority} />
                    <h3 className="font-bold">{item.title}</h3>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
                </div>
              ))}
            </div>
          </SectionCard>
        </>
      )}
    </div>
  );
}
