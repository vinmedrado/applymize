import { useEffect, useState } from "react";
import { Radar as RadarIcon, RefreshCcw } from "lucide-react";
import { PageLoading, Spinner } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { getRadarHistory, runRadar } from "../services/advanced";
import { RadarRun } from "../types";

export function Radar() {
  const toast = useToast();
  const [history, setHistory] = useState<RadarRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [provider, setProvider] = useState("remoteok");

  async function load() {
    setLoading(true);
    try { setHistory(await getRadarHistory()); } catch (err) { toast.error("Erro no Radar", getApiError(err)); } finally { setLoading(false); }
  }
  useEffect(() => { load(); }, []);

  async function execute() {
    setRunning(true);
    try {
      const result = await runRadar(provider, 25);
      toast.success("Radar executado", result.message);
      await load();
    } catch (err) { toast.error("Erro ao rodar Radar", getApiError(err)); } finally { setRunning(false); }
  }

  if (loading) return <PageLoading label="Carregando Radar..." />;

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <p className="text-sm text-slate-500">Daily Job Radar</p>
        <h1 className="mt-2 text-3xl font-bold">Radar diário de vagas</h1>
        <p className="mt-2 text-sm text-slate-500">Execução manual e segura. Integra com notificações quando configuradas.</p>
      </section>
      <SectionCard title="Executar radar">
        <div className="flex flex-wrap gap-3">
          <select className="input max-w-xs" value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="remoteok">RemoteOK</option><option value="gupy">Gupy</option><option value="vagas">Vagas.com</option><option value="all">All</option>
          </select>
          <button className="btn-primary" onClick={execute} disabled={running}>{running ? <Spinner label="Rodando..." /> : <><RadarIcon className="mr-2 h-4 w-4" /> Rodar Radar</>}</button>
        </div>
      </SectionCard>
      <SectionCard title="Histórico">
        <div className="grid gap-3">{history.map((run) => (
          <div className="rounded-2xl bg-slate-50 p-4" key={run.id}>
            <div className="flex flex-wrap justify-between gap-2"><b>{run.provider}</b><span>{run.status}</span></div>
            <p className="mt-2 text-sm text-slate-600">Ingeridas: {run.total_ingested} • High Priority: {run.high_priority_count} • Notificadas: {run.notified_count}</p>
            <p className="mt-1 text-sm text-slate-500">{run.message}</p>
          </div>
        ))}{history.length === 0 && <p className="text-sm text-slate-500">Sem execuções ainda.</p>}</div>
      </SectionCard>
    </div>
  );
}
