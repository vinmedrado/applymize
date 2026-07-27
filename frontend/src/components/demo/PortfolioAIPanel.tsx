import { FormEvent, useState } from "react";
import { Bot, CheckCircle2, Cpu, Database, Send, ShieldCheck, Sparkles } from "lucide-react";
import {
  askPublicCareerAI,
  loadPublicCareerAIResult,
  PublicCareerAIError,
  PublicCareerAIResult,
} from "../../services/publicCareerAi";

const suggestions = [
  "O que este projeto demonstra sobre a capacidade técnica de Vinicius?",
  "Quais decisões de arquitetura mais se destacam no Applymize?",
  "Como o Applymize transforma um problema real em produto?",
];

export function PortfolioAIPanel() {
  const [storedResult] = useState(loadPublicCareerAIResult);
  const [question, setQuestion] = useState(storedResult?.question || suggestions[0]);
  const [result, setResult] = useState<PublicCareerAIResult | null>(storedResult);
  const [loading, setLoading] = useState(false);
  const [blocked, setBlocked] = useState(false);
  const [error, setError] = useState("");
  const used = Boolean(result);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (used || blocked || loading) return;
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

  return (
    <div className="space-y-5">
      <section className="relative overflow-hidden rounded-[2rem] bg-slate-950 p-6 text-white shadow-2xl lg:p-8">
        <div className="absolute -right-16 -top-20 h-64 w-64 rounded-full bg-violet-500/25 blur-3xl" />
        <div className="absolute -bottom-28 left-1/3 h-64 w-64 rounded-full bg-blue-500/20 blur-3xl" />
        <div className="relative grid gap-7 xl:grid-cols-[0.85fr_1.15fr] xl:items-start">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full border border-violet-300/25 bg-violet-300/10 px-3 py-1.5 text-xs font-black text-violet-100">
              <Sparkles size={14} /> Applymize IA
            </span>
            <h1 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">Faça uma pergunta sobre o projeto.</h1>
            <p className="mt-3 max-w-xl text-sm leading-7 text-slate-300">
              Uma consulta real para o recrutador avaliar a experiência de IA contextual. A resposta usa somente fatos públicos do Applymize.
            </p>
            <div className="mt-5 inline-flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
              {used ? <CheckCircle2 className="text-emerald-300" /> : <span className="text-2xl font-black text-violet-200">1</span>}
              <span>
                <span className="block text-sm font-black">{used ? "Crédito utilizado" : "1 crédito de demonstração"}</span>
                <span className="block text-xs text-slate-400">Uma resposta por visitante</span>
              </span>
            </div>
          </div>

          <form onSubmit={submit} className="rounded-3xl border border-white/10 bg-white/[0.07] p-4 backdrop-blur sm:p-5">
            {!used && (
              <>
                <p className="text-xs font-black uppercase tracking-wide text-violet-200">Perguntas sugeridas</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {suggestions.map((suggestion) => (
                    <button
                      type="button"
                      key={suggestion}
                      onClick={() => setQuestion(suggestion)}
                      disabled={loading || blocked}
                      className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-left text-xs font-bold leading-5 text-slate-200 transition hover:border-violet-300/40 hover:bg-violet-300/10 disabled:opacity-50"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
                <label className="mt-4 block">
                  <span className="text-xs font-black uppercase tracking-wide text-slate-300">Sua pergunta</span>
                  <textarea
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    maxLength={500}
                    rows={4}
                    disabled={loading || blocked}
                    className="mt-2 w-full resize-none rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm leading-6 text-white outline-none transition placeholder:text-slate-500 focus:border-violet-300/60 disabled:opacity-60"
                    placeholder="Pergunte sobre arquitetura, produto ou decisões técnicas..."
                  />
                  <span className="mt-1 block text-right text-[11px] font-bold text-slate-500">{question.length}/500</span>
                </label>
                <button
                  type="submit"
                  disabled={loading || blocked || !question.trim()}
                  className="mt-3 inline-flex w-full items-center justify-center rounded-2xl bg-white px-5 py-3 text-sm font-black text-slate-950 transition hover:bg-violet-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? <><Cpu className="mr-2 h-4 w-4 animate-pulse" /> Gerando resposta...</> : <><Send className="mr-2 h-4 w-4" /> Usar meu crédito</>}
                </button>
              </>
            )}

            {used && result && (
              <div aria-live="polite">
                <div className="flex items-center gap-2 text-xs font-black uppercase tracking-wide text-emerald-200">
                  <Bot size={16} /> Resposta da Applymize IA
                </div>
                <p className="mt-3 text-xs font-bold leading-5 text-slate-400">Pergunta: {storedResult?.question || question}</p>
                <div className="mt-4 whitespace-pre-wrap rounded-2xl bg-white p-4 text-sm leading-7 text-slate-800 shadow-xl">
                  {result.answer}
                </div>
                <p className="mt-3 text-[11px] font-bold text-slate-500">Processado por {result.provider} · {result.model}</p>
              </div>
            )}

            {error && (
              <div role="alert" className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-4 text-sm leading-6 text-amber-100">
                {error}
              </div>
            )}
          </form>
        </div>
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs font-black uppercase tracking-wide text-blue-700">Como funciona por trás</p>
            <h2 className="mt-1 text-xl font-black">IA real, superfície pública mínima</h2>
          </div>
          <span className="inline-flex items-center gap-2 text-xs font-black text-emerald-700"><ShieldCheck size={16} /> Chave fora do navegador</span>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          {[
            { icon: Bot, title: "1. Contexto controlado", detail: "A pergunta recebe somente fatos públicos do projeto; dados pessoais e backend privado ficam fora." },
            { icon: ShieldCheck, title: "2. Função Netlify", detail: "Validação de origem, tamanho e limite por IP/domínio protegem a consulta e o orçamento." },
            { icon: Database, title: "3. Groq", detail: "A função chama o modelo no servidor e devolve apenas a resposta final, sem expor o segredo." },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.title} className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                <Icon className="text-blue-700" size={20} />
                <h3 className="mt-3 font-black">{item.title}</h3>
                <p className="mt-1 text-xs leading-5 text-slate-500">{item.detail}</p>
              </article>
            );
          })}
        </div>
        <p className="mt-4 text-xs leading-5 text-slate-500">
          Transparência: a pergunta é enviada à Groq para processamento. Não informe dados pessoais. O resultado fica salvo somente neste navegador para preservar o único crédito.
        </p>
      </section>
    </div>
  );
}
