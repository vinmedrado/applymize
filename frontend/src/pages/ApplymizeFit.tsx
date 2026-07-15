import { FormEvent, useMemo, useState } from "react";
import { ArrowRight, Brain, Building2, CheckCircle2, Clock3, MessageSquareText, RotateCcw, ShieldCheck, Sparkles, Target, UserRoundCheck, Wand2 } from "lucide-react";
import { getApiError } from "../services/api";
import { evaluateFitAnswer, FitEvaluation, FitQuestion, FitSession, startFitSession } from "../services/applymizeFit";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

const focusOptions = [
  "Fit cultural geral",
  "Gupy e testes comportamentais",
  "Entrevista com RH",
  "Comunicação e colaboração",
  "Autonomia e ownership",
  "Liderança e influência",
];

function ScoreRing({ score }: { score: number }) {
  const safe = Math.max(0, Math.min(100, score));
  return (
    <div className="relative flex h-28 w-28 items-center justify-center rounded-full bg-slate-100">
      <div
        className="absolute inset-0 rounded-full"
        style={{ background: `conic-gradient(#2563eb ${safe * 3.6}deg, #e2e8f0 0deg)` }}
      />
      <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-white shadow-inner">
        <span className="text-2xl font-black text-slate-950">{safe}</span>
      </div>
    </div>
  );
}

function EmptySession() {
  return (
    <div className="rounded-[2rem] border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-700">
        <Sparkles size={26} />
      </div>
      <h2 className="mt-4 text-2xl font-black text-slate-950">Treino ainda não iniciado</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-600">
        Informe a empresa, cargo e foco do treino. O Applymize Fit cria perguntas comportamentais personalizadas usando seu perfil profissional e avalia suas respostas como um recrutador.
      </p>
    </div>
  );
}

export function ApplymizeFit() {
  const { user } = useAuth();
  const toast = useToast();
  const [company, setCompany] = useState("Gupy / Empresa alvo");
  const [targetRole, setTargetRole] = useState(user?.target_role || "Analista de Dados e Automação");
  const [focus, setFocus] = useState("Gupy e testes comportamentais");
  const [session, setSession] = useState<FitSession | null>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [evaluations, setEvaluations] = useState<Record<string, FitEvaluation>>({});
  const [loadingStart, setLoadingStart] = useState(false);
  const [loadingEval, setLoadingEval] = useState(false);
  const [error, setError] = useState("");

  const activeQuestion: FitQuestion | null = session?.questions?.[activeIndex] ?? null;
  const currentEvaluation = activeQuestion ? evaluations[activeQuestion.id] : undefined;

  const averageScore = useMemo(() => {
    const values = Object.values(evaluations).map((item) => item.score);
    if (!values.length) return 0;
    return Math.round(values.reduce((acc, value) => acc + value, 0) / values.length);
  }, [evaluations]);

  async function start(event?: FormEvent) {
    event?.preventDefault();
    setError("");
    setLoadingStart(true);
    setEvaluations({});
    setActiveIndex(0);
    setAnswer("");
    try {
      const result = await startFitSession({ company, target_role: targetRole, focus });
      setSession(result);
      toast.success("Treino iniciado", "Perguntas personalizadas criadas pelo Applymize Fit.");
    } catch (err) {
      const message = getApiError(err);
      setError(message);
      toast.error("Erro ao iniciar treino", message);
    } finally {
      setLoadingStart(false);
    }
  }

  async function evaluate() {
    if (!activeQuestion) return;
    if (answer.trim().length < 5) {
      toast.error("Resposta muito curta", "Digite uma resposta antes de solicitar a avaliação.");
      return;
    }
    setError("");
    setLoadingEval(true);
    try {
      const result = await evaluateFitAnswer({ company, target_role: targetRole, focus, question: activeQuestion.question, answer });
      setEvaluations((prev) => ({ ...prev, [activeQuestion.id]: result }));
      toast.success("Resposta avaliada", `Score: ${result.score}/100`);
    } catch (err) {
      const message = getApiError(err);
      setError(message);
      toast.error("Erro ao avaliar resposta", message);
    } finally {
      setLoadingEval(false);
    }
  }

  function goNext() {
    if (!session) return;
    setActiveIndex((value) => Math.min(value + 1, session.questions.length - 1));
    setAnswer("");
  }

  function goBack() {
    setActiveIndex((value) => Math.max(value - 1, 0));
    setAnswer("");
  }

  return (
    <div className="space-y-6">
      <div className="overflow-hidden rounded-[2rem] border border-slate-200 bg-slate-950 shadow-2xl">
        <div className="relative grid gap-8 p-6 text-white md:p-8 lg:grid-cols-[1.05fr_0.95fr] lg:p-10">
          <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-blue-500/20 blur-3xl" />
          <div className="absolute -bottom-24 -left-20 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
          <div className="relative z-10">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-black uppercase tracking-wide text-blue-100">
              <UserRoundCheck size={14} /> Applymize Fit
            </div>
            <h1 className="mt-5 text-3xl font-black tracking-tight sm:text-4xl lg:text-5xl">Treine fit cultural, Gupy e entrevistas com IA contextual.</h1>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300 sm:text-base">
              O módulo cria perguntas de acordo com a empresa, cargo alvo e seu perfil profissional. Depois avalia suas respostas com leitura de RH, riscos, pontos fortes e uma versão melhorada para entrevista.
            </p>
            <div className="mt-6 grid gap-3 text-sm text-slate-200 sm:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4"><Brain className="mb-2 h-5 w-5 text-blue-200" /> Perguntas personalizadas</div>
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4"><ShieldCheck className="mb-2 h-5 w-5 text-emerald-200" /> Leitura de recrutador</div>
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4"><Target className="mb-2 h-5 w-5 text-cyan-200" /> Score comportamental</div>
            </div>
          </div>
          <form onSubmit={start} className="relative z-10 rounded-3xl border border-white/10 bg-white p-5 text-slate-950 shadow-2xl">
            <h2 className="text-xl font-black">Configurar treino</h2>
            <p className="mt-1 text-sm text-slate-500">Comece com uma empresa real ou processo seletivo que você quer simular.</p>
            <label className="mt-4 block text-sm font-bold">Empresa</label>
            <input className="input mt-2" value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Ex.: Itaú, Nubank, Gupy, Accenture" />
            <label className="mt-4 block text-sm font-bold">Cargo alvo</label>
            <input className="input mt-2" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} placeholder="Ex.: Analista de Dados Pleno" />
            <label className="mt-4 block text-sm font-bold">Foco do treino</label>
            <select className="input mt-2" value={focus} onChange={(e) => setFocus(e.target.value)}>
              {focusOptions.map((option) => <option key={option} value={option}>{option}</option>)}
            </select>
            {error && <div className="mt-4 rounded-2xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}
            <button className="btn-primary mt-5 w-full justify-center" disabled={loadingStart}>
              {loadingStart ? "Criando treino..." : session ? "Gerar novo treino" : "Iniciar treino"}
              {!loadingStart && <ArrowRight className="ml-2 h-4 w-4" />}
            </button>
          </form>
        </div>
      </div>

      {!session ? <EmptySession /> : (
        <div className="grid gap-6 xl:grid-cols-[320px_1fr]">
          <aside className="space-y-4">
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-black uppercase tracking-wide text-slate-400">Resumo do treino</p>
              <h2 className="mt-2 text-lg font-black text-slate-950">{session.company}</h2>
              <p className="mt-1 text-sm font-semibold text-slate-600">{session.target_role}</p>
              <p className="mt-3 text-sm leading-6 text-slate-600">{session.profile_summary}</p>
              <div className="mt-4 flex items-center gap-2 rounded-2xl bg-slate-50 p-3 text-xs font-semibold text-slate-500">
                <Clock3 size={14} /> {session.provider} · {session.model}{session.fallback_used ? " · fallback" : ""}
              </div>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-black uppercase tracking-wide text-slate-400">Progresso</p>
                  <h3 className="text-lg font-black text-slate-950">{Object.keys(evaluations).length}/{session.questions.length} avaliadas</h3>
                </div>
                <ScoreRing score={averageScore || 0} />
              </div>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-white p-3 shadow-sm">
              {session.questions.map((question, index) => (
                <button
                  key={question.id}
                  onClick={() => { setActiveIndex(index); setAnswer(""); }}
                  className={`mb-2 w-full rounded-2xl p-4 text-left transition ${index === activeIndex ? "bg-slate-950 text-white" : "bg-slate-50 text-slate-700 hover:bg-slate-100"}`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-black uppercase tracking-wide">Pergunta {index + 1}</span>
                    {evaluations[question.id] && <CheckCircle2 size={16} className="text-emerald-400" />}
                  </div>
                  <p className="mt-1 text-sm font-bold">{question.title}</p>
                  <p className={`mt-1 text-xs ${index === activeIndex ? "text-slate-300" : "text-slate-500"}`}>{question.dimension}</p>
                </button>
              ))}
            </div>
          </aside>

          <main className="space-y-6">
            {activeQuestion && (
              <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm md:p-8">
                <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div>
                    <p className="text-xs font-black uppercase tracking-wide text-blue-700">Pergunta {activeIndex + 1} · {activeQuestion.dimension}</p>
                    <h2 className="mt-2 text-2xl font-black text-slate-950">{activeQuestion.title}</h2>
                    <p className="mt-3 text-lg leading-8 text-slate-700">{activeQuestion.question}</p>
                  </div>
                  <div className="rounded-2xl bg-blue-50 p-4 text-sm text-blue-900 md:max-w-xs">
                    <strong>O que RH observa:</strong><br />{activeQuestion.what_recruiter_expects}
                  </div>
                </div>

                <label className="mt-6 block text-sm font-black text-slate-900">Sua resposta</label>
                <textarea
                  className="input mt-2 min-h-40"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Responda como se estivesse em uma etapa real da Gupy ou entrevista com RH. Tente usar contexto, ação e resultado."
                />
                <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex gap-2">
                    <button type="button" className="btn-secondary" onClick={goBack} disabled={activeIndex === 0}>Voltar</button>
                    <button type="button" className="btn-secondary" onClick={goNext} disabled={!session || activeIndex >= session.questions.length - 1}>Próxima</button>
                  </div>
                  <div className="flex gap-2">
                    <button type="button" className="btn-secondary" onClick={() => setAnswer("")}><RotateCcw className="mr-2 h-4 w-4" /> Limpar</button>
                    <button type="button" className="btn-primary" onClick={evaluate} disabled={loadingEval}>
                      {loadingEval ? "Avaliando..." : "Avaliar resposta"}
                      {!loadingEval && <Wand2 className="ml-2 h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {currentEvaluation ? (
              <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
                <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
                  <p className="text-xs font-black uppercase tracking-wide text-slate-400">Score da resposta</p>
                  <div className="mt-4 flex justify-center"><ScoreRing score={currentEvaluation.score} /></div>
                  <h3 className="mt-4 text-center text-2xl font-black text-slate-950">{currentEvaluation.level}</h3>
                  <p className="mt-3 text-center text-xs font-semibold text-slate-500">{currentEvaluation.provider} · {currentEvaluation.model}{currentEvaluation.fallback_used ? " · fallback" : ""}</p>
                </div>
                <div className="space-y-4 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="rounded-2xl bg-slate-50 p-4">
                    <p className="flex items-center gap-2 text-sm font-black text-slate-950"><MessageSquareText size={18} /> Leitura do recrutador</p>
                    <p className="mt-2 text-sm leading-6 text-slate-700">{currentEvaluation.recruiter_reading}</p>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl bg-emerald-50 p-4">
                      <p className="text-sm font-black text-emerald-900">Pontos fortes</p>
                      <ul className="mt-2 space-y-2 text-sm text-emerald-800">
                        {currentEvaluation.strengths.map((item) => <li key={item}>• {item}</li>)}
                      </ul>
                    </div>
                    <div className="rounded-2xl bg-amber-50 p-4">
                      <p className="text-sm font-black text-amber-900">Pontos de atenção</p>
                      <ul className="mt-2 space-y-2 text-sm text-amber-800">
                        {currentEvaluation.risks.map((item) => <li key={item}>• {item}</li>)}
                      </ul>
                    </div>
                  </div>
                  <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
                    <p className="text-sm font-black text-blue-950">Resposta melhorada para entrevista</p>
                    <p className="mt-2 whitespace-pre-line text-sm leading-7 text-blue-900">{currentEvaluation.improved_answer}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-950 p-4 text-white">
                    <p className="text-sm font-black">Próxima dica</p>
                    <p className="mt-2 text-sm leading-6 text-slate-200">{currentEvaluation.next_tip}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="rounded-[2rem] border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm">
                <Building2 className="mx-auto h-10 w-10 text-slate-400" />
                <h3 className="mt-3 text-xl font-black text-slate-950">Responda e peça avaliação</h3>
                <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-slate-600">O feedback aparece aqui com score, leitura de RH, riscos, pontos fortes e uma versão mais forte da resposta.</p>
              </div>
            )}
          </main>
        </div>
      )}
    </div>
  );
}
