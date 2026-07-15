import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { completeOnboarding, getOnboardingStatus } from "../services/onboarding";

const STORAGE_KEY = "applymize:onboarding-tour:v1";

type TourStep = {
  title: string;
  description: string;
  selector: string;
  route?: string;
};

const steps: TourStep[] = [
  { title: "Etapa 1 — Dashboard", description: "Veja um resumo das suas vagas, candidaturas, recomendações e alertas.", selector: "[data-tour='dashboard'], [data-tour='dashboard-page']", route: "/dashboard" },
  { title: "Etapa 2 — Meu Perfil", description: "Cadastre seus dados ou envie seu currículo. O sistema usa isso para calcular scores, CVs e recomendações.", selector: "[data-tour='profile'], [data-tour='profile-page']", route: "/profile" },
  { title: "Etapa 3 — Importar Vagas", description: "Busque vagas em fontes como Gupy, Vagas.com e RemoteOK.", selector: "[data-tour='jobs'], [data-tour='jobs-page']", route: "/jobs" },
  { title: "Etapa 4 — Analisador ATS", description: "Veja se seu currículo está forte para passar em triagens automáticas e humanas.", selector: "[data-tour='ats'], [data-tour='ats-page']", route: "/ats-analyzer" },
  { title: "Etapa 5 — Strategy Engine", description: "Descubra quais vagas valem mais a pena priorizar.", selector: "[data-tour='strategy'], [data-tour='dashboard-page']", route: "/dashboard" },
  { title: "Etapa 6 — Application Agent", description: "Organize candidaturas, gere CV, mensagem e acompanhe status.", selector: "[data-tour='application-agent'], [data-tour='application-agent-page']", route: "/application-agent" },
  { title: "Etapa 7 — Notificações", description: "Receba alertas de vagas prioritárias por Telegram ou WhatsApp.", selector: "[data-tour='notifications'], [data-tour='notifications-page']", route: "/notifications" },
  { title: "Etapa 8 — WhatsApp", description: "Conecte seu WhatsApp para receber alertas de vagas prioritárias.", selector: "[data-tour='whatsapp'], [data-tour='whatsapp-page']", route: "/whatsapp-pairing" },
  { title: "Etapa 9 — Analytics e Skill Gap", description: "Acompanhe evolução, lacunas de skills e oportunidades de melhoria.", selector: "[data-tour='analytics'], [data-tour='analytics-page'], [data-tour='skill-gap-page']", route: "/analytics" },
];

type Rect = { top: number; left: number; width: number; height: number };

function findTarget(selector: string): HTMLElement | null {
  try {
    return document.querySelector(selector) as HTMLElement | null;
  } catch {
    return null;
  }
}

function getViewportRect(selector: string): Rect | null {
  const element = findTarget(selector);
  if (!element) return null;
  const rect = element.getBoundingClientRect();
  if (rect.width <= 0 || rect.height <= 0) return null;
  return {
    top: Math.max(rect.top, 8),
    left: Math.max(rect.left, 8),
    width: Math.max(rect.width, 8),
    height: Math.max(rect.height, 8),
  };
}

function getTooltipStyle(rect: Rect | null): React.CSSProperties {
  const width = Math.min(430, window.innerWidth - 32);
  if (!rect) {
    return {
      position: "fixed",
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
      width,
      maxWidth: "calc(100vw - 32px)",
      zIndex: 10002,
    };
  }

  const margin = 16;
  const belowTop = rect.top + rect.height + margin;
  const aboveTop = rect.top - 260 - margin;
  const canPlaceBelow = belowTop + 260 < window.innerHeight;
  const canPlaceAbove = aboveTop > 16;

  let top = canPlaceBelow ? belowTop : canPlaceAbove ? aboveTop : Math.max(16, Math.min(rect.top + margin, window.innerHeight - 280));
  let left = Math.min(Math.max(rect.left, 16), window.innerWidth - width - 16);

  if (window.innerWidth < 720) {
    top = Math.min(Math.max(rect.top + rect.height + 12, 16), window.innerHeight - 300);
    left = 16;
  }

  return { position: "fixed", top, left, width, maxWidth: "calc(100vw - 32px)", zIndex: 10002 };
}

async function saveDone() {
  localStorage.setItem(STORAGE_KEY, "done");
  try {
    await completeOnboarding();
  } catch {
    // fallback localStorage
  }
}

export function OnboardingTour() {
  const navigate = useNavigate();
  const location = useLocation();
  const [running, setRunning] = useState(false);
  const [index, setIndex] = useState(0);
  const [targetRect, setTargetRect] = useState<Rect | null>(null);
  const [ready, setReady] = useState(false);
  const step = steps[index];

  const elementExists = useMemo(() => {
    if (!running || !step) return false;
    return Boolean(findTarget(step.selector));
  }, [running, step, location.pathname]);

  function startTour() {
    setReady(false);
    setIndex(0);
    setRunning(true);
  }

  function finish(save = true) {
    if (save) void saveDone();
    setRunning(false);
    setTargetRect(null);
    setReady(false);
  }

  function next() {
    if (index >= steps.length - 1) {
      finish(true);
      return;
    }
    setReady(false);
    setIndex((value) => value + 1);
  }

  function back() {
    setReady(false);
    setIndex((value) => Math.max(0, value - 1));
  }

  useEffect(() => {
    function handler() {
      setIndex(0);
      setRunning(true);
      setReady(false);
    }
    window.addEventListener("applymize:start-tour", handler);
    return () => window.removeEventListener("applymize:start-tour", handler);
  }, []);

  useEffect(() => {
    let active = true;
    async function loadStatus() {
      try {
        const status = await getOnboardingStatus();
        if (!active) return;
        if (status.completed) {
          localStorage.setItem(STORAGE_KEY, "done");
          return;
        }
        window.setTimeout(() => {
          if (active) startTour();
        }, 500);
      } catch {
        const seen = localStorage.getItem(STORAGE_KEY);
        if (!seen) {
          window.setTimeout(() => {
            if (active) startTour();
          }, 500);
        }
      }
    }
    void loadStatus();
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!running || !step?.route) return;
    if (location.pathname !== step.route) navigate(step.route);
  }, [running, index, step?.route, location.pathname]);

  useEffect(() => {
    if (!running || !step) return;
    let cancelled = false;

    function updateRect() {
      if (cancelled) return;
      setTargetRect(getViewportRect(step.selector));
      setReady(true);
    }

    const timer = window.setTimeout(() => {
      const target = findTarget(step.selector);
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "center", inline: "nearest" });
        window.setTimeout(updateRect, 420);
      } else {
        updateRect();
      }
    }, 160);

    window.addEventListener("resize", updateRect);
    window.addEventListener("scroll", updateRect, { passive: true });

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
      window.removeEventListener("resize", updateRect);
      window.removeEventListener("scroll", updateRect);
    };
  }, [running, index, location.pathname]);

  if (!running || !step) return null;

  return (
    <div className="fixed inset-0 z-[10000] pointer-events-none">
      <div className="fixed inset-0 bg-slate-950/50" />

      {ready && targetRect && (
        <div
          className="fixed rounded-3xl border-2 border-white bg-white/10 shadow-[0_0_0_9999px_rgba(15,23,42,0.48)] transition-all duration-200"
          style={{
            top: targetRect.top - 8,
            left: targetRect.left - 8,
            width: targetRect.width + 16,
            height: targetRect.height + 16,
            zIndex: 10001,
          }}
        />
      )}

      <div className="pointer-events-auto rounded-3xl bg-white p-5 shadow-2xl ring-1 ring-slate-200" style={getTooltipStyle(targetRect)}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Tutorial {index + 1}/{steps.length}</p>
            <h2 className="mt-1 text-xl font-extrabold text-slate-950">{step.title}</h2>
          </div>
          <button className="text-sm font-semibold text-slate-500 hover:text-slate-950" onClick={() => finish(true)}>Pular</button>
        </div>

        <p className="mt-3 text-sm leading-6 text-slate-600">{step.description}</p>

        {!elementExists && (
          <div className="mt-3 rounded-2xl bg-amber-50 p-3 text-sm text-amber-800">
            Esta área pode não estar visível agora. O tutorial continuará normalmente.
          </div>
        )}

        <div className="mt-5 flex flex-wrap items-center justify-between gap-2">
          <button className="btn-secondary" onClick={back} disabled={index === 0}>Voltar</button>
          <div className="flex gap-2">
            <button className="btn-secondary" onClick={() => finish(true)}>Pular</button>
            <button className="btn-primary" onClick={next}>{index >= steps.length - 1 ? "Finalizar" : "Próximo"}</button>
          </div>
        </div>
      </div>
    </div>
  );
}
