const sourceLabels: Record<string, string> = {
  gupy: "Gupy",
  vagas: "Vagas.com",
  remoteok: "RemoteOK",
  demo: "Demo",
  manual: "Manual"
};

export function JobSourceBadge({ source }: { source?: string }) {
  const normalized = (source || "manual").toLowerCase();
  const label = sourceLabels[normalized] || source || "Fonte não informada";
  return (
    <span className="inline-flex w-fit items-center rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-600">
      Fonte: {label}
    </span>
  );
}
