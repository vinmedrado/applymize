import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Copy, ExternalLink } from "lucide-react";
import { PageLoading, Spinner } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { MarkdownBlock } from "../components/MarkdownBlock";
import { JobSourceBadge } from "../components/JobSourceBadge";
import { MatchProgress } from "../components/ScoreVisual";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { createApplication, generateCV, generateInterview } from "../services/applications";
import { generateCoverLetter } from "../services/advanced";
import { getJob, scoreJob } from "../services/jobs";
import { InterviewPrep, Job, MatchScore, Resume } from "../types";

function DescriptionPreview({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const shouldTrim = (text || "").length > 650;
  const visible = expanded || !shouldTrim ? text : `${text.slice(0, 650)}...`;
  return (
    <div>
      <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{visible}</p>
      {shouldTrim && (
        <button className="mt-3 text-sm font-semibold text-slate-950 underline" onClick={() => setExpanded(!expanded)}>
          {expanded ? "Ver menos" : "Ver mais"}
        </button>
      )}
    </div>
  );
}

function pct(value?: number) {
  return `${Math.max(0, Math.min(100, Number(value || 0))).toFixed(1)}%`;
}

function AnalysisMetric({ label, value }: { label: string; value?: number }) {
  const normalized = Math.max(0, Math.min(100, Number(value || 0)));
  const tone = normalized >= 78 ? "bg-emerald-500" : normalized >= 58 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="analysis-metric">
      <div className="flex items-center justify-between gap-3 text-xs font-semibold text-slate-600">
        <span>{label}</span>
        <span className="font-bold text-slate-900">{pct(normalized)}</span>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full rounded-full ${tone}`} style={{ width: `${normalized}%` }} />
      </div>
    </div>
  );
}

function MatchAnalysisPanel({ score }: { score: MatchScore }) {
  const matched = score.matched_skills || [];
  const missing = score.missing_skills || [];
  return (
    <div className="analysis-panel mt-0">
      <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Análise de compatibilidade</p>
          <h3 className="text-base font-bold text-slate-950">Score geral: {pct(score.score)}</h3>
        </div>
        <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-slate-700 ring-1 ring-slate-200">
          Baseado no seu perfil e currículo
        </span>
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <AnalysisMetric label="Skills" value={score.skill_score} />
        <AnalysisMetric label="Senioridade" value={score.seniority_score} />
        <AnalysisMetric label="Palavras-chave" value={score.keyword_score} />
        <AnalysisMetric label="Score final" value={score.score} />
      </div>

      {(matched.length > 0 || missing.length > 0) && (
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <div className="rounded-xl bg-white p-3 ring-1 ring-slate-200">
            <p className="text-xs font-bold uppercase tracking-wide text-emerald-700">Pontos compatíveis</p>
            <p className="mt-1 text-sm text-slate-700">{matched.length ? matched.slice(0, 10).join(" · ") : "Nenhum ponto forte específico identificado."}</p>
          </div>
          <div className="rounded-xl bg-white p-3 ring-1 ring-slate-200">
            <p className="text-xs font-bold uppercase tracking-wide text-amber-700">Pontos de atenção</p>
            <p className="mt-1 text-sm text-slate-700">{missing.length ? missing.slice(0, 10).join(" · ") : "Nenhum gap relevante identificado."}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export function JobDetail() {
  const toast = useToast();
  const { jobId } = useParams();
  const id = Number(jobId);
  const [job, setJob] = useState<Job | null>(null);
  const [score, setScore] = useState<MatchScore | null>(null);
  const [cv, setCv] = useState<Resume | null>(null);
  const [interview, setInterview] = useState<InterviewPrep | null>(null);
  const [cover, setCover] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [showTech, setShowTech] = useState(false);
  const [viewMode, setViewMode] = useState<"pt" | "original">("pt");

  useEffect(() => {
    getJob(id)
      .then(setJob)
      .catch((err) => toast.error("Erro ao carregar vaga", getApiError(err)))
      .finally(() => setLoading(false));
  }, [id]);

  async function runAction<T>(label: string, fn: () => Promise<T>, onSuccess: (value: T) => void, success: string) {
    setActionLoading(label);
    try {
      const value = await fn();
      onSuccess(value);
      toast.success(success);
    } catch (err) {
      toast.error("Erro na ação", getApiError(err));
    } finally {
      setActionLoading("");
    }
  }

  async function copyText(text: string, label: string) {
    await navigator.clipboard.writeText(text || "");
    toast.success(`${label} copiado`);
  }

  if (loading || !job) return <PageLoading label="Carregando vaga..." />;

  return (
    <div className="page-shell">
      <Link to="/jobs" className="inline-flex w-fit items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-slate-700 shadow-sm hover:bg-slate-50">
        <ArrowLeft className="h-4 w-4" /> Voltar para Vagas
      </Link>

      <section className="job-card">
        <div className="job-card-layout">
          <div className="min-w-0">
            <h1 className="text-2xl font-black tracking-tight">{viewMode === "original" ? (job.title_original || job.title) : job.title}</h1>
            <div className="mt-2"><JobSourceBadge source={job.source} /></div>
            <p className="mt-3 text-slate-500">{job.company} • {job.location || "Local não informado"}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="badge">{job.seniority}</span>
              <span className="badge">{job.employment_type}</span>
              {job.remote && <span className="badge">Remoto</span>}
            </div>
            <div className="mt-4 text-sm">
              <span className="font-semibold">Link da vaga: </span>
              {job.url ? (
                <a className="break-all text-slate-950 underline" href={job.url} target="_blank" rel="noreferrer">{job.url}</a>
              ) : (
                <span className="text-slate-500">Link não disponível</span>
              )}
            </div>
          </div>

          <div className="action-rail">
            {job.url ? (
              <a className="btn-primary justify-center" href={job.url} target="_blank" rel="noreferrer" title="Você será redirecionado para o site original">
                🔗 Candidatar
              </a>
            ) : (
              <button className="btn-primary justify-center opacity-50" disabled title="Link não disponível">Link não disponível</button>
            )}
            <button className="btn-secondary justify-center" disabled={!!actionLoading} onClick={() => runAction("apply", () => createApplication(id, "saved"), () => {}, "Vaga adicionada à lista")}>
              {actionLoading === "apply" ? <Spinner label="Adicionando..." /> : "Adicionar à lista"}
            </button>
            <button className="btn-secondary justify-center" disabled={!!actionLoading} onClick={() => runAction("score", () => scoreJob(id), setScore, "Análise concluída")}>
              {actionLoading === "score" ? <Spinner label="Analisando..." /> : "Analisar vaga"}
            </button>
            <button className="btn-secondary justify-center" disabled={!!actionLoading} onClick={() => runAction("cv", () => generateCV(id), setCv, "CV gerado")}>
              {actionLoading === "cv" ? <Spinner label="Gerando CV..." /> : "Gerar CV"}
            </button>
            <button className="btn-secondary justify-center" disabled={!!actionLoading} onClick={() => runAction("cover", () => generateCoverLetter(id), setCover, "Mensagem gerada")}>
              {actionLoading === "cover" ? <Spinner label="Gerando..." /> : "Gerar mensagem"}
            </button>
            <button className="btn-secondary justify-center" disabled={!!actionLoading} onClick={() => runAction("interview", () => generateInterview(id), setInterview, "Preparação gerada")}>
              {actionLoading === "interview" ? <Spinner label="Gerando..." /> : "Preparar entrevista"}
            </button>
          </div>
        </div>
      </section>

      {score && (
        <SectionCard title="Análise da vaga" subtitle="Resumo visual do matching">
          <MatchAnalysisPanel score={score} />
          <button className="mt-4 text-sm font-semibold underline" onClick={() => setShowTech(!showTech)}>Ver detalhes técnicos</button>
          {showTech && <pre className="mt-3 overflow-auto rounded-2xl bg-slate-50 p-4 text-xs text-slate-700 ring-1 ring-slate-200">{JSON.stringify(score, null, 2)}</pre>}
        </SectionCard>
      )}

      <SectionCard
        title="Descrição da vaga"
        action={
          <div className="inline-flex rounded-2xl bg-slate-100 p-1 text-sm font-semibold">
            <button className={`rounded-xl px-3 py-1 ${viewMode === "pt" ? "bg-white shadow-sm" : ""}`} onClick={() => setViewMode("pt")}>Português</button>
            <button className={`rounded-xl px-3 py-1 ${viewMode === "original" ? "bg-white shadow-sm" : ""}`} onClick={() => setViewMode("original")}>Original</button>
          </div>
        }
      >
        <DescriptionPreview text={viewMode === "original" ? (job.description_original || job.description) : job.description} />
        <h3 className="mt-6 font-semibold">Requisitos</h3>
        <DescriptionPreview text={job.requirements || "Não informado"} />
      </SectionCard>


      {cover && (
        <SectionCard title="Mensagens geradas" action={<button className="btn-secondary" onClick={() => copyText(cover.short_message, "Mensagem")}><Copy className="mr-2 h-4 w-4" /> Copiar curta</button>}>
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-2xl bg-slate-50 p-4"><b>Mensagem curta</b><p className="mt-2 text-sm">{cover.short_message}</p></div>
            <div className="rounded-2xl bg-slate-50 p-4"><b>LinkedIn</b><p className="mt-2 text-sm">{cover.linkedin_message}</p></div>
            <div className="rounded-2xl bg-slate-50 p-4 lg:col-span-2"><b>E-mail</b><pre className="mt-2 whitespace-pre-wrap text-sm">{cover.application_email}</pre></div>
          </div>
        </SectionCard>
      )}

      {cv && (
        <SectionCard title="CV ATS gerado" subtitle={`Versão ${cv.version}`} action={<button className="btn-secondary" onClick={() => copyText(cv.content_md, "CV")}><Copy className="mr-2 h-4 w-4" /> Copiar CV</button>}>
          <MarkdownBlock content={cv.content_md} />
        </SectionCard>
      )}

      {interview && (
        <SectionCard title="Preparação de entrevista" subtitle="Perguntas, gaps e plano de estudo" action={<button className="btn-secondary" onClick={() => copyText(interview.questions.join("\n"), "Perguntas")}><Copy className="mr-2 h-4 w-4" /> Copiar perguntas</button>}>
          <div className="rounded-2xl bg-slate-100 p-4 text-sm leading-6 text-slate-700">{interview.role_pitch}</div>
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <div><h3 className="font-semibold">Perguntas técnicas e comportamentais</h3><ul className="mt-3 space-y-2 text-sm text-slate-700">{interview.questions.map((q) => <li className="rounded-xl bg-white p-3 shadow-sm" key={q}>{q}</li>)}</ul></div>
            <div>
              <h3 className="font-semibold">Plano de estudo</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-700">{interview.study_plan.map((q) => <li className="rounded-xl bg-white p-3 shadow-sm" key={q}>{q}</li>)}</ul>
              <h3 className="mt-6 font-semibold">Gaps detectados</h3>
              <div className="mt-3 flex flex-wrap gap-2">{interview.weak_points.map((g) => <span className="badge" key={g}>{g}</span>)}</div>
            </div>
          </div>
        </SectionCard>
      )}
    </div>
  );
}
