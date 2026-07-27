import { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Code2, Github, Play } from "lucide-react";
import { BrandLogo } from "./BrandLogo";

export function MarketingSection({
  children,
  className = "",
  id,
}: {
  children: ReactNode;
  className?: string;
  id?: string;
}) {
  return (
    <section
      id={id}
      className={`mx-auto w-full max-w-7xl px-4 py-16 sm:px-6 lg:px-8 ${className}`}
    >
      {children}
    </section>
  );
}

export function FeatureCard({ icon, title, description }: { icon: ReactNode; title: string; description: string }) {
  return (
    <article className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur transition hover:-translate-y-1 hover:shadow-xl">
      <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-700">{icon}</div>
      <h3 className="text-lg font-black text-slate-950">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
    </article>
  );
}

export function PublicShell({ children }: { children: ReactNode }) {
  return <div className="min-h-screen overflow-hidden bg-[#f7f9fc] text-slate-950">{children}</div>;
}

export function PublicHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/90 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/" aria-label="Ir para o início"><BrandLogo variant="sidebar" /></Link>
        <nav className="hidden items-center gap-5 text-sm font-semibold text-slate-600 md:flex" aria-label="Navegação pública">
          <Link to="/como-funciona" className="hover:text-slate-950">Por trás do projeto</Link>
          <Link to="/laboratorio-ats" className="hover:text-slate-950">Teste ATS</Link>
          <Link to="/linkedin-analyzer" className="hover:text-slate-950">LinkedIn</Link>
          <Link to="/demo" className="hover:text-slate-950">Demo interativa</Link>
        </nav>
        <div className="flex items-center gap-2">
          <a href="https://github.com/vinmedrado/applymize" target="_blank" rel="noreferrer" className="btn-secondary hidden sm:inline-flex">
            <Github className="mr-2 h-4 w-4" /> Código
          </a>
          <Link to="/demo" className="btn-primary"><Play className="mr-2 h-4 w-4" /> Explorar</Link>
        </div>
      </div>
    </header>
  );
}

export function PublicFooter() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-5 px-4 py-8 text-sm text-slate-500 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
        <BrandLogo variant="sidebar" />
        <p>Projeto autoral de Vinicius Medrado · portfólio full-stack e ferramenta pessoal.</p>
        <div className="flex flex-wrap gap-4 font-semibold text-slate-700">
          <Link to="/como-funciona" className="inline-flex items-center"><Code2 className="mr-1.5 h-4 w-4" /> Por trás</Link>
          <Link to="/laboratorio-ats">Teste ATS</Link>
          <Link to="/demo">Demo interativa</Link>
          <a href="https://github.com/vinmedrado/applymize" target="_blank" rel="noreferrer" className="inline-flex items-center"><Github className="mr-1.5 h-4 w-4" /> GitHub</a>
        </div>
      </div>
    </footer>
  );
}
