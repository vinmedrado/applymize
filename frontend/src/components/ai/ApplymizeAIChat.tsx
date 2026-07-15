import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Bot, History, Loader2, MoreVertical, Plus, Send, Trash2, X } from "lucide-react";
import { getApiError } from "../../services/api";
import {
  CareerAIConversation,
  deleteCareerAIConversation,
  listCareerAIConversations,
  listCareerAIMessages,
  renameCareerAIConversation,
  sendCareerAIMessage
} from "../../services/careerAi";
import { ApplymizeAIMessage, ApplymizeAIMessageData } from "./ApplymizeAIMessage";
import { BrandLogo } from "../BrandLogo";

const QUICK_SUGGESTIONS = [
  "Explique minha experiência",
  "Analise meu currículo",
  "Como melhorar meu ATS?",
  "Estou apto para essa vaga?",
  "Me ajude em entrevistas"
];

const WELCOME_MESSAGE: ApplymizeAIMessageData = {
  id: "welcome",
  role: "assistant",
  content: "Olá! Eu sou o Applymize IA. Posso te ajudar a explicar sua experiência, melhorar ATS, preparar respostas de entrevista e analisar aderência com base no seu perfil real."
};

function newId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function ApplymizeAIChat({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [providerLabel, setProviderLabel] = useState("contextual");
  const [conversations, setConversations] = useState<CareerAIConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [conversationMenuId, setConversationMenuId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ApplymizeAIMessageData[]>([WELCOME_MESSAGE]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading]);
  const activeConversation = conversations.find((item) => item.id === activeConversationId) || null;

  async function refreshConversations(nextActiveId?: number | null) {
    const items = await listCareerAIConversations();
    setConversations(items);
    if (typeof nextActiveId !== "undefined") {
      setActiveConversationId(nextActiveId);
    }
  }

  useEffect(() => {
    if (!open) return;
    refreshConversations().catch(() => undefined);
  }, [open]);

  async function loadConversation(conversationId: number) {
    setHistoryLoading(true);
    setActiveConversationId(conversationId);
    setConversationMenuId(null);
    setMobileHistoryOpen(false);
    try {
      const remoteMessages = await listCareerAIMessages(conversationId);
      const mapped: ApplymizeAIMessageData[] = remoteMessages
        .filter((message) => message.role === "user" || message.role === "assistant")
        .map((message) => ({
          id: String(message.id),
          role: message.role as "user" | "assistant",
          content: message.content,
          provider: message.provider || undefined,
          model: message.model || undefined
        }));
      setMessages(mapped.length ? mapped : [WELCOME_MESSAGE]);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    } catch (error) {
      setMessages([{ ...WELCOME_MESSAGE, content: getApiError(error) || "Não consegui carregar essa conversa." }]);
    } finally {
      setHistoryLoading(false);
    }
  }

  async function startNewConversation() {
    setActiveConversationId(null);
    setMessages([WELCOME_MESSAGE]);
    setInput("");
    setConversationMenuId(null);
    setMobileHistoryOpen(false);
  }

  async function renameConversation(conversation: CareerAIConversation) {
    const nextTitle = window.prompt("Novo nome da conversa", conversation.title);
    if (!nextTitle?.trim()) return;
    try {
      await renameCareerAIConversation(conversation.id, nextTitle.trim());
      await refreshConversations(activeConversationId);
    } catch (error) {
      setMessages((current) => [...current, { id: newId(), role: "assistant", content: getApiError(error) || "Não consegui renomear essa conversa." }]);
    } finally {
      setConversationMenuId(null);
    }
  }

  async function removeConversation(conversation: CareerAIConversation) {
    if (!window.confirm(`Excluir a conversa "${conversation.title}"?`)) return;
    try {
      await deleteCareerAIConversation(conversation.id);
      const nextActive = activeConversationId === conversation.id ? null : activeConversationId;
      await refreshConversations(nextActive);
      if (activeConversationId === conversation.id) {
        setMessages([WELCOME_MESSAGE]);
      }
    } catch (error) {
      setMessages((current) => [...current, { id: newId(), role: "assistant", content: getApiError(error) || "Não consegui excluir essa conversa." }]);
    } finally {
      setConversationMenuId(null);
    }
  }

  async function submitMessage(text?: string) {
    const message = (text ?? input).trim();
    if (!message || loading) return;

    setInput("");
    setLoading(true);
    setMessages((current) => [...current.filter((item) => item.id !== "welcome"), { id: newId(), role: "user", content: message }]);

    try {
      const response = await sendCareerAIMessage(message, activeConversationId);
      setActiveConversationId(response.conversation_id);
      setProviderLabel(response.fallback_used ? `${response.provider} fallback` : response.provider);
      setMessages((current) => [
        ...current,
        {
          id: newId(),
          role: "assistant",
          content: response.answer,
          provider: response.provider,
          model: response.model,
          fallbackUsed: response.fallback_used
        }
      ]);
      await refreshConversations(response.conversation_id);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: newId(),
          role: "assistant",
          content: getApiError(error) || "Não consegui responder agora. Verifique a configuração da IA e tente novamente."
        }
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    submitMessage();
  }

  function renderConversationList(mode: "desktop" | "mobile") {
    return (
      <>
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Histórico</p>
            <h4 className="text-sm font-bold text-slate-900">Conversas</h4>
          </div>
          <button className="rounded-xl bg-slate-950 p-2 text-white transition hover:bg-indigo-700" onClick={startNewConversation} title="Nova conversa">
            <Plus size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-3">
          {conversations.length === 0 && <p className="px-2 py-6 text-sm text-slate-500">Nenhuma conversa salva ainda.</p>}
          <div className="space-y-2">
            {conversations.map((conversation) => (
              <div key={conversation.id} className={`group relative rounded-2xl border px-3 py-2 transition ${activeConversationId === conversation.id ? "border-indigo-200 bg-indigo-50" : "border-slate-100 bg-white hover:border-slate-200 hover:bg-slate-50"}`}>
                <button className="block w-full pr-8 text-left" onClick={() => loadConversation(conversation.id)}>
                  <span className="block truncate text-sm font-semibold text-slate-800">{conversation.title}</span>
                  <span className="block truncate text-[11px] text-slate-400">{new Date(conversation.updated_at).toLocaleDateString("pt-BR")}</span>
                </button>
                <button className="absolute right-2 top-2 rounded-lg p-1 text-slate-400 hover:bg-white hover:text-slate-700" onClick={() => setConversationMenuId(conversationMenuId === conversation.id ? null : conversation.id)} aria-label="Opções da conversa">
                  <MoreVertical size={15} />
                </button>
                {conversationMenuId === conversation.id && (
                  <div className="absolute right-2 top-9 z-10 w-36 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-lg">
                    <button className="block w-full px-3 py-2 text-left text-xs font-semibold text-slate-700 hover:bg-slate-50" onClick={() => renameConversation(conversation)}>Renomear</button>
                    <button className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs font-semibold text-red-600 hover:bg-red-50" onClick={() => removeConversation(conversation)}><Trash2 size={13} /> Excluir</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
        {mode === "mobile" && (
          <div className="border-t border-slate-200 p-3">
            <button className="btn-secondary w-full" onClick={() => setMobileHistoryOpen(false)}>Voltar para o chat</button>
          </div>
        )}
      </>
    );
  }

  if (!open) return null;

  return (
    <section className="fixed inset-0 z-50 flex overflow-hidden border border-slate-200 bg-slate-50 shadow-2xl md:bottom-24 md:right-6 md:top-auto md:h-[min(760px,calc(100vh-7rem))] md:w-[min(920px,calc(100vw-2rem))] md:rounded-3xl">
      <aside className="hidden w-72 shrink-0 border-r border-slate-200 bg-white md:flex md:flex-col">
        {renderConversationList("desktop")}
      </aside>

      {mobileHistoryOpen && (
        <div className="absolute inset-0 z-20 flex bg-white md:hidden">
          <aside className="flex h-full w-full flex-col bg-white">
            {renderConversationList("mobile")}
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="bg-slate-950 px-4 py-3 text-white md:px-5 md:py-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10">
                <BrandLogo variant="mark" light className="h-7 w-7" />
              </div>
              <div>
                <h3 className="text-base font-bold">Applymize IA</h3>
                <p className="line-clamp-1 text-xs text-slate-300">{activeConversation?.title || "Nova conversa"} · {providerLabel}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button className="rounded-2xl p-2 text-slate-300 transition hover:bg-white/10 hover:text-white md:hidden" onClick={() => setMobileHistoryOpen(true)} aria-label="Abrir histórico">
                <History size={18} />
              </button>
              <button className="rounded-2xl p-2 text-slate-300 transition hover:bg-white/10 hover:text-white" onClick={startNewConversation} aria-label="Nova conversa">
                <Plus size={18} />
              </button>
              <button className="rounded-2xl p-2 text-slate-300 transition hover:bg-white/10 hover:text-white" onClick={onClose} aria-label="Fechar Applymize IA">
                <X size={18} />
              </button>
            </div>
          </div>
        </header>

        <div className="border-b border-slate-200 bg-white px-4 py-3">
          <div className="flex gap-2 overflow-x-auto pb-1">
            {QUICK_SUGGESTIONS.map((suggestion) => (
              <button
                key={suggestion}
                className="shrink-0 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700"
                onClick={() => submitMessage(suggestion)}
                disabled={loading}
              >
                {suggestion}
              </button>
            ))}
          </div>
          <div className="mt-3 flex items-center gap-2 overflow-x-auto md:hidden">
            <button className="shrink-0 rounded-full border border-slate-200 bg-slate-950 px-3 py-1.5 text-xs font-semibold text-white" onClick={() => setMobileHistoryOpen(true)}>Ver histórico</button>
            {conversations.slice(0, 6).map((conversation) => (
              <button
                key={conversation.id}
                className={`shrink-0 rounded-full border px-3 py-1.5 text-xs font-semibold transition ${activeConversationId === conversation.id ? "border-indigo-200 bg-indigo-50 text-indigo-700" : "border-slate-200 bg-white text-slate-600"}`}
                onClick={() => loadConversation(conversation.id)}
                disabled={historyLoading}
              >
                {conversation.title}
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto px-3 py-3 md:px-4 md:py-4">
          {historyLoading && <div className="text-sm font-medium text-slate-500">Carregando conversa...</div>}
          {messages.map((message) => (
            <ApplymizeAIMessage key={message.id} message={message} />
          ))}
          {loading && (
            <div className="flex items-center gap-3 text-sm font-medium text-slate-500">
              <div className="flex h-8 w-8 items-center justify-center rounded-2xl bg-indigo-600 text-white">
                <Bot size={16} />
              </div>
              <Loader2 className="h-4 w-4 animate-spin" />
              Montando resposta com seu contexto...
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <form className="border-t border-slate-200 bg-white p-3 pb-[calc(0.75rem+env(safe-area-inset-bottom))] md:p-4" onSubmit={handleSubmit}>
          <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2 focus-within:border-indigo-300 focus-within:bg-white">
            <textarea
              className="max-h-28 min-h-[44px] flex-1 resize-none bg-transparent px-2 py-2 text-sm outline-none placeholder:text-slate-400"
              placeholder="Pergunte sobre currículo, ATS, entrevista ou vaga..."
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  submitMessage();
                }
              }}
            />
            <button className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50" disabled={!canSend} type="submit" aria-label="Enviar mensagem">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send size={17} />}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
