import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { CheckCircle2, Loader2, Send, ShieldCheck, X } from "lucide-react";
import { ApplymizeAIMessage } from "../ai/ApplymizeAIMessage";
import { BrandLogo } from "../BrandLogo";
import {
  askPublicCareerAI,
  loadPublicCareerAIResult,
  PublicCareerAIError,
  PublicCareerAIResult,
} from "../../services/publicCareerAi";

const QUICK_SUGGESTIONS = [
  "O que este projeto demonstra sobre a capacidade técnica de Vinicius?",
  "Quais decisões de arquitetura mais se destacam no Applymize?",
  "Como o Applymize transforma um problema real em produto?",
];

export function PortfolioAIFloatingAssistant({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [storedResult] = useState(loadPublicCareerAIResult);
  const [input, setInput] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState(storedResult?.question || "");
  const [result, setResult] = useState<PublicCareerAIResult | null>(storedResult);
  const [loading, setLoading] = useState(false);
  const [blocked, setBlocked] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const used = Boolean(result);
  const canSend = useMemo(
    () => input.trim().length > 0 && input.trim().length <= 500 && !loading && !used && !blocked,
    [blocked, input, loading, used],
  );

  useEffect(() => {
    if (!open) return;
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }, [loading, open, result, submittedQuestion]);

  async function submitMessage(text?: string) {
    const question = (text ?? input).trim();
    if (!question || question.length > 500 || loading || used || blocked) return;

    setInput("");
    setSubmittedQuestion(question);
    setLoading(true);
    setError("");
    try {
      setResult(await askPublicCareerAI(question));
    } catch (requestError) {
      if (requestError instanceof PublicCareerAIError) {
        setError(requestError.message);
        setBlocked(requestError.status === 429);
      } else {
        setError("Não foi possível acessar a IA agora.");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    submitMessage();
  }

  return (
    <>
      <button
        type="button"
        className="fixed bottom-5 right-5 z-50 flex items-center gap-2 rounded-full bg-slate-950 px-5 py-4 text-sm font-bold text-white shadow-2xl transition hover:-translate-y-0.5 hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-200 sm:right-6"
        onClick={() => onOpenChange(!open)}
        aria-label={open ? "Fechar Applymize IA" : "Abrir Applymize IA"}
        aria-expanded={open}
        aria-controls="portfolio-ai-chat"
      >
        <span className="relative flex h-5 w-5 items-center justify-center">
          <BrandLogo variant="mark" light className="h-5 w-5" />
          {!open && !used && <span className="absolute -right-1 -top-1 h-2.5 w-2.5 rounded-full bg-emerald-400 ring-2 ring-slate-950" />}
          {!open && used && <CheckCircle2 className="absolute -right-2 -top-2 h-3.5 w-3.5 rounded-full bg-slate-950 text-emerald-400" />}
        </span>
        <span className="hidden sm:inline">Applymize IA</span>
      </button>

      {open && (
        <section
          id="portfolio-ai-chat"
          role="dialog"
          aria-modal="true"
          aria-label="Applymize IA para recrutadores"
          className="fixed inset-0 z-50 flex w-screen min-w-0 max-w-full flex-col overflow-hidden border border-slate-200 bg-slate-50 shadow-2xl md:bottom-24 md:left-auto md:right-6 md:top-auto md:h-[min(700px,calc(100vh-7rem))] md:w-[min(560px,calc(100vw-2rem))] md:rounded-3xl"
        >
          <header className="bg-slate-950 px-4 py-3 text-white md:px-5 md:py-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex min-w-0 items-center gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-white/10">
                  <BrandLogo variant="mark" light className="h-7 w-7" />
                </div>
                <div className="min-w-0">
                  <h2 className="text-base font-bold">Applymize IA</h2>
                  <p className="truncate text-xs text-slate-300">Demonstração pública · 1 consulta real</p>
                </div>
              </div>
              <button
                type="button"
                className="rounded-2xl p-2 text-slate-300 transition hover:bg-white/10 hover:text-white"
                onClick={() => onOpenChange(false)}
                aria-label="Fechar Applymize IA"
              >
                <X size={18} />
              </button>
            </div>
          </header>

          <div className="border-b border-slate-200 bg-white px-4 py-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="inline-flex items-center gap-2 text-xs font-bold text-emerald-700">
                <ShieldCheck size={15} /> Contexto público · chave protegida
              </span>
              <span className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-black ${used ? "bg-emerald-50 text-emerald-700" : "bg-indigo-50 text-indigo-700"}`}>
                {used ? "Crédito utilizado" : "1 crédito disponível"}
              </span>
            </div>
            {!used && (
              <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
                {QUICK_SUGGESTIONS.map((suggestion) => (
                  <button
                    type="button"
                    key={suggestion}
                    className="shrink-0 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700 disabled:opacity-50"
                    onClick={() => submitMessage(suggestion)}
                    disabled={loading || blocked}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto px-3 py-4 md:px-4">
            <ApplymizeAIMessage
              message={{
                id: "welcome",
                role: "assistant",
                content: used
                  ? "Olá! Esta é a consulta de IA pública do Applymize. Sua resposta ficou preservada neste navegador."
                  : "Olá! Eu sou o Applymize IA. Nesta demonstração, você pode fazer uma pergunta sobre a arquitetura, o produto ou as decisões técnicas do projeto.",
              }}
            />

            {submittedQuestion && (
              <ApplymizeAIMessage message={{ id: "question", role: "user", content: submittedQuestion }} />
            )}

            {loading && (
              <div className="flex items-center gap-3 text-sm font-medium text-slate-500">
                <div className="flex h-8 w-8 items-center justify-center rounded-2xl bg-indigo-600 text-white">
                  <BrandLogo variant="mark" light className="h-5 w-5" />
                </div>
                <Loader2 className="h-4 w-4 animate-spin" />
                Montando resposta com o contexto público...
              </div>
            )}

            {result && (
              <ApplymizeAIMessage
                message={{
                  id: "answer",
                  role: "assistant",
                  content: result.answer,
                  provider: result.provider,
                  model: result.model,
                }}
              />
            )}

            {error && (
              <div role="alert" className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900">
                {error}
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="border-t border-slate-200 bg-white p-3 pb-[calc(0.75rem+env(safe-area-inset-bottom))] md:p-4">
            {!used && !blocked ? (
              <form onSubmit={handleSubmit}>
                <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2 focus-within:border-indigo-300 focus-within:bg-white">
                  <textarea
                    className="max-h-28 min-h-[44px] flex-1 resize-none bg-transparent px-2 py-2 text-sm outline-none placeholder:text-slate-400"
                    placeholder="Pergunte sobre o projeto..."
                    value={input}
                    maxLength={500}
                    disabled={loading}
                    onChange={(event) => setInput(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" && !event.shiftKey) {
                        event.preventDefault();
                        submitMessage();
                      }
                    }}
                  />
                  <button
                    className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={!canSend}
                    type="submit"
                    aria-label="Enviar pergunta"
                  >
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send size={17} />}
                  </button>
                </div>
                <p className="mt-2 text-center text-[11px] leading-4 text-slate-400">
                  A pergunta é enviada à Groq. Não informe dados pessoais.
                </p>
              </form>
            ) : (
              <p className="text-center text-xs font-semibold leading-5 text-slate-500">
                {used ? "Crédito utilizado. A resposta permanece disponível neste navegador." : "O crédito deste acesso não está disponível agora."}
              </p>
            )}
          </div>
        </section>
      )}
    </>
  );
}
