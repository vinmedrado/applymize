import { useState } from "react";
import { MessageCircle } from "lucide-react";
import { ApplymizeAIChat } from "./ApplymizeAIChat";
import { BrandLogo } from "../BrandLogo";

export function ApplymizeAIButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        className="fixed bottom-5 right-5 z-50 flex items-center gap-2 rounded-full bg-slate-950 px-5 py-4 text-sm font-bold text-white shadow-2xl transition hover:-translate-y-0.5 hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-200 sm:right-6"
        onClick={() => setOpen((current) => !current)}
        aria-label="Abrir Applymize IA"
      >
        <span className="relative flex h-5 w-5 items-center justify-center">
          {open ? <MessageCircle size={19} /> : <BrandLogo variant="mark" light className="h-5 w-5" />}
          {!open && <span className="absolute -right-1 -top-1 h-2.5 w-2.5 rounded-full bg-emerald-400 ring-2 ring-slate-950" />}
        </span>
        <span className="hidden sm:inline">Applymize IA</span>
      </button>
      <ApplymizeAIChat open={open} onClose={() => setOpen(false)} />
    </>
  );
}
