import { ReactNode } from "react";

type Props = {
  title: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
};

export function SectionCard({ title, subtitle, children, action }: Props) {
  return (
    <section className="card overflow-hidden">
      <div className="flex flex-col justify-between gap-3 border-b border-slate-100 bg-white px-5 py-4 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-lg font-bold">{title}</h2>
          {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
        </div>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}
