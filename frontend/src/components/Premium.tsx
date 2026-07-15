import { ReactNode } from "react";
import { ArrowUpRight, LucideIcon } from "lucide-react";

type PremiumHeroProps = {
  eyebrow: string;
  title: string;
  description: string;
  icon?: LucideIcon;
  children?: ReactNode;
};

export function PremiumHero({ eyebrow, title, description, icon: Icon, children }: PremiumHeroProps) {
  return (
    <section className="premium-hero overflow-hidden p-6 sm:p-8">
      <div className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-blue-400/20 blur-3xl" />
      <div className="absolute -bottom-20 left-1/3 h-60 w-60 rounded-full bg-cyan-300/20 blur-3xl" />
      <div className="relative grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
        <div>
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs font-black uppercase tracking-wide text-blue-100 backdrop-blur">
            {Icon && <Icon className="h-4 w-4" />}
            {eyebrow}
          </div>
          <h1 className="max-w-4xl text-3xl font-black tracking-tight text-white sm:text-4xl lg:text-5xl">{title}</h1>
          <p className="mt-4 max-w-3xl text-sm leading-7 text-blue-50/90 sm:text-base">{description}</p>
        </div>
        {children && <div className="relative z-10">{children}</div>}
      </div>
    </section>
  );
}

type PremiumMetricProps = {
  label: string;
  value: string | number;
  helper?: string;
  trend?: string;
};

export function PremiumMetric({ label, value, helper, trend }: PremiumMetricProps) {
  return (
    <div className="premium-card p-5">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-black uppercase tracking-wide text-slate-500">{label}</p>
        {trend && <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-black text-emerald-700">{trend}</span>}
      </div>
      <p className="mt-3 text-3xl font-black tracking-tight text-slate-950">{value}</p>
      {helper && <p className="mt-2 text-sm leading-6 text-slate-500">{helper}</p>}
    </div>
  );
}

type PremiumPanelProps = {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
};

export function PremiumPanel({ title, subtitle, action, children }: PremiumPanelProps) {
  return (
    <section className="premium-card p-5 sm:p-6">
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-xl font-black tracking-tight text-slate-950">{title}</h2>
          {subtitle && <p className="mt-1 text-sm leading-6 text-slate-500">{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

type TimelineItem = {
  title: string;
  description: string;
  status?: string;
};

export function PremiumTimeline({ items }: { items: TimelineItem[] }) {
  return (
    <div className="space-y-3">
      {items.map((item, index) => (
        <div key={item.title} className="flex gap-3 rounded-2xl border border-slate-200 bg-white p-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-blue-50 text-sm font-black text-blue-700">{index + 1}</div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <p className="font-black text-slate-950">{item.title}</p>
              {item.status && <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-bold text-slate-600">{item.status}</span>}
            </div>
            <p className="mt-1 text-sm leading-6 text-slate-500">{item.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

type MiniFeatureProps = {
  icon: LucideIcon;
  title: string;
  description: string;
};

export function MiniFeature({ icon: Icon, title, description }: MiniFeatureProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white/80 p-4 shadow-sm">
      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-50 text-blue-700"><Icon className="h-5 w-5" /></div>
      <h3 className="mt-4 font-black text-slate-950">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
    </div>
  );
}

export function PremiumCTA({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-950 to-blue-950 p-6 text-white shadow-2xl shadow-slate-300/30">
      {children}
    </div>
  );
}

export function ExternalBadge({ label }: { label: string }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-black text-blue-800">
      {label} <ArrowUpRight className="h-3 w-3" />
    </span>
  );
}
