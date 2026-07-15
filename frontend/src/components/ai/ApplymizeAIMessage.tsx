import { User } from "lucide-react";
import { BrandLogo } from "../BrandLogo";

export type ApplymizeAIMessageRole = "user" | "assistant";

export type ApplymizeAIMessageData = {
  id: string;
  role: ApplymizeAIMessageRole;
  content: string;
  provider?: string;
  model?: string;
  fallbackUsed?: boolean;
};

export function ApplymizeAIMessage({ message }: { message: ApplymizeAIMessageData }) {
  const isAssistant = message.role === "assistant";

  return (
    <div className={`flex gap-3 ${isAssistant ? "justify-start" : "justify-end"}`}>
      {isAssistant && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-sm">
          <BrandLogo variant="mark" light className="h-5 w-5" />
        </div>
      )}

      <div className={`max-w-[82%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${isAssistant ? "border border-slate-200 bg-white text-slate-800" : "bg-slate-900 text-white"}`}>
        <div className="whitespace-pre-wrap">{message.content}</div>
        {isAssistant && message.provider && (
          <div className="mt-2 border-t border-slate-100 pt-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            {message.provider} · {message.model}
            {message.fallbackUsed ? " · fallback ativo" : ""}
          </div>
        )}
      </div>

      {!isAssistant && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-sm">
          <User size={16} />
        </div>
      )}
    </div>
  );
}
