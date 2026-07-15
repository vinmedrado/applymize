export function Spinner({ label = "Carregando..." }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-slate-500">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-950" />
      <span>{label}</span>
    </div>
  );
}

export function PageLoading({ label = "Carregando..." }: { label?: string }) {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <Spinner label={label} />
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="card animate-pulse p-5">
      <div className="h-5 w-1/3 rounded bg-slate-200" />
      <div className="mt-4 h-4 w-2/3 rounded bg-slate-200" />
      <div className="mt-3 h-4 w-full rounded bg-slate-200" />
      <div className="mt-3 h-4 w-5/6 rounded bg-slate-200" />
    </div>
  );
}
