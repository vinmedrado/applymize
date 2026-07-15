import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { BarChart3, Bell, HelpCircle, Bot, Briefcase, ClipboardCheck, Home, Linkedin, LogOut, Menu, MessageCircle, Radar, Timer, TrendingUp, User, UserRoundCheck, X, CreditCard, ShieldCheck, Building2, FileText } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { OnboardingTour } from "./OnboardingTour";
import { ApplymizeAIButton } from "./ai/ApplymizeAIButton";
import { BrandLogo } from "./BrandLogo";

const navGroups = [
  {
    title: "Visão geral",
    items: [
      { to: "/dashboard", label: "Dashboard", icon: Home },
      { to: "/analytics", label: "Analytics", icon: BarChart3 },
      { to: "/skill-gap", label: "Evolução", icon: TrendingUp }
    ]
  },
  {
    title: "Operação de vagas",
    items: [
      { to: "/jobs", label: "Vagas", icon: Briefcase },
      { to: "/applications", label: "Candidaturas", icon: UserRoundCheck },
      { to: "/application-agent", label: "Candidaturas inteligentes", icon: Bot },
      { to: "/radar", label: "Radar de vagas", icon: Radar }
    ]
  },
  {
    title: "Inteligência",
    items: [
      { to: "/ats-analyzer", label: "Analisador ATS", icon: ClipboardCheck },
      { to: "/app/linkedin-analyzer", label: "LinkedIn Analyzer", icon: Linkedin },
      { to: "/applymize-fit", label: "Applymize Fit", icon: UserRoundCheck },
      { to: "/cv-pro", label: "CV Pro", icon: FileText },
      { to: "/profile", label: "Meu Perfil", icon: User }
    ]
  },
  {
    title: "SaaS & Comercial",
    items: [
      { to: "/billing", label: "Planos & Billing", icon: CreditCard },
      { to: "/admin", label: "Admin Analytics", icon: ShieldCheck },
      { to: "/recruiter", label: "Recruiter Panel", icon: Building2 }
    ]
  },
  {
    title: "Automação e canais",
    items: [
      { to: "/automation", label: "Automação", icon: Timer },
      { to: "/notifications", label: "Notificações", icon: Bell },
      { to: "/whatsapp-pairing", label: "WhatsApp", icon: MessageCircle }
    ]
  }
];

function getTourKey(path: string) {
  const map: Record<string, string> = {
    "/dashboard": "dashboard",
    "/profile": "profile",
    "/jobs": "jobs",
    "/ats-analyzer": "ats",
    "/app/linkedin-analyzer": "linkedin-analyzer",
    "/application-agent": "application-agent",
    "/notifications": "notifications",
    "/automation": "automation",
    "/whatsapp-pairing": "whatsapp",
    "/analytics": "analytics",
    "/skill-gap": "skill-gap",
    "/applymize-fit": "applymize-fit",
    "/billing": "billing",
    "/admin": "admin",
    "/recruiter": "recruiter",
    "/cv-pro": "cv-pro"
  };
  return map[path];
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <>
      <div className="mb-5">
        <BrandLogo />
      </div>

      <nav className="space-y-5 pb-5">
        {navGroups.map((group) => (
          <section key={group.title}>
            <p className="mb-2 px-2 text-[11px] font-black uppercase tracking-wide text-slate-400">{group.title}</p>
            <div className="space-y-1.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    data-tour={getTourKey(item.to)}
                    onClick={onNavigate}
                    className={({ isActive }) => `nav-item ${isActive ? "nav-item-active" : "nav-item-idle"}`}
                  >
                    <Icon size={18} />
                    <span className="min-w-0 truncate">{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          </section>
        ))}
      </nav>
      <div className="mt-auto rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-50 to-white p-4 text-xs text-slate-600">
        <p className="font-black text-slate-950">Applymize OS</p>
        <p className="mt-1 leading-5">IA, ATS, Fit, LinkedIn e automação em um workspace SaaS.</p>
      </div>
    </>
  );
}

export function Layout() {
  const { user, logout } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  function startTutorial() {
    window.dispatchEvent(new Event("applymize:start-tour"));
  }

  async function handleLogout() {
    await logout();
    toast.success("Sessão encerrada", "Logout realizado com sucesso.");
    navigate("/login");
  }

  return (
    <div className="app-shell">
      <aside className="app-sidebar overflow-y-auto">
        <SidebarContent />
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-slate-950/40 lg:hidden">
          <aside className="flex h-full w-80 max-w-[86vw] flex-col overflow-y-auto bg-white p-5 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-xs font-black uppercase tracking-wide text-slate-400">Menu</p>
              <button className="rounded-xl p-2 hover:bg-slate-100" onClick={() => setMobileOpen(false)} aria-label="Fechar menu">
                <X size={20} />
              </button>
            </div>
            <SidebarContent onNavigate={() => setMobileOpen(false)} />
          </aside>
        </div>
      )}

      <div className="app-main">
        <header className="app-header">
          <div className="flex items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <button className="rounded-xl border border-slate-200 p-2 lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Abrir menu">
                <Menu size={20} />
              </button>
              <div className="min-w-0">
                <p className="truncate text-xs text-slate-500 sm:text-sm">Tenant: {user?.tenant_name}</p>
                <h2 className="truncate text-base font-black sm:text-xl">Olá, {user?.full_name}</h2>
              </div>
            </div>

            <div className="flex shrink-0 items-center gap-2">
              <div className="hidden rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-black text-blue-800 md:block">
                {user?.target_role || user?.role}
              </div>
              <div className="hidden rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1.5 text-xs font-black text-emerald-700 xl:block">
                SaaS Ready
              </div>
              <button className="btn-secondary hidden sm:inline-flex" onClick={startTutorial}>
                <HelpCircle className="mr-2 h-4 w-4" /> Tutorial
              </button>
              <button className="btn-secondary" onClick={handleLogout}>
                <LogOut className="mr-0 h-4 w-4 sm:mr-2" />
                <span className="hidden sm:inline">Sair</span>
              </button>
            </div>
          </div>
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
      <OnboardingTour />
      <ApplymizeAIButton />
    </div>
  );
}
