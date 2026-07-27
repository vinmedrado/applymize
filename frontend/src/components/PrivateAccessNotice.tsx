import { Code2, LockKeyhole, Play } from "lucide-react";
import { Link } from "react-router-dom";
import { BrandLogo } from "./BrandLogo";

export function PrivateAccessNotice() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_#dbeafe,_#f8fafc_48%)] p-4">
      <section className="w-full max-w-2xl rounded-[2rem] border border-slate-200 bg-white p-7 shadow-2xl shadow-slate-200/70 sm:p-10">
        <BrandLogo variant="auth" />
        <div className="mt-8 inline-flex items-center gap-2 rounded-full bg-amber-50 px-3 py-1.5 text-xs font-black uppercase tracking-wide text-amber-800">
          <LockKeyhole size={15} /> Ambiente privado
        </div>
        <h1 className="mt-4 text-3xl font-black tracking-tight text-slate-950 sm:text-4xl">
          O login real não fica exposto no portfólio.
        </h1>
        <p className="mt-4 max-w-xl leading-7 text-slate-600">
          A plataforma autenticada usa serviços e dados pessoais em um ambiente local. Para avaliar a experiência completa com segurança, use a demo interativa: ela reproduz os principais fluxos com dados ilustrativos e sem cadastro.
        </p>
        <div className="mt-7 flex flex-col gap-3 sm:flex-row">
          <Link to="/demo" className="btn-primary justify-center px-6 py-3">
            <Play className="mr-2 h-4 w-4" /> Abrir demo interativa
          </Link>
          <Link to="/como-funciona" className="inline-flex items-center justify-center rounded-xl border border-slate-200 px-6 py-3 font-black text-slate-800 transition hover:bg-slate-50">
            <Code2 className="mr-2 h-4 w-4" /> Ver por trás do projeto
          </Link>
        </div>
        <Link to="/" className="mt-6 inline-block text-sm font-bold text-slate-500 underline">
          Voltar ao início
        </Link>
      </section>
    </main>
  );
}
