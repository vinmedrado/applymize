import { useEffect, useMemo, useState } from "react";
import { EmptyState } from "../components/EmptyState";
import { SkeletonCard } from "../components/Loading";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { listApplications, updateApplication } from "../services/applications";
import { listJobs } from "../services/jobs";
import { getFollowup } from "../services/advanced";
import { Application, ApplicationStatus, Job } from "../types";

const statuses: ApplicationStatus[] = ["saved", "applied", "interview", "rejected", "offer"];

const statusStyle: Record<string, string> = {
  saved: "bg-slate-100 text-slate-700",
  applied: "bg-blue-50 text-blue-700",
  interview: "bg-amber-50 text-amber-700",
  rejected: "bg-red-50 text-red-700",
  offer: "bg-emerald-50 text-emerald-700"
};

export function Applications() {
  const toast = useToast();
  const [applications, setApplications] = useState<Application[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [followups, setFollowups] = useState<Record<number, any>>({});

  async function load() {
    setLoading(true);
    try {
      const [appsData, jobsData] = await Promise.all([listApplications(), listJobs()]);
      setApplications(appsData);
      setJobs(jobsData.items);
    } catch (err) {
      toast.error("Erro ao carregar candidaturas", getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const jobsById = useMemo(() => Object.fromEntries(jobs.map((job) => [job.id, job])), [jobs]);

  async function generateFollowup(appId: number) {
    try {
      const data = await getFollowup(appId);
      setFollowups((prev) => ({ ...prev, [appId]: data }));
      toast.success("Follow-up gerado");
    } catch (err) {
      toast.error("Erro ao gerar follow-up", getApiError(err));
    }
  }

  async function changeStatus(appId: number, status: ApplicationStatus) {
    try {
      await updateApplication(appId, status);
      toast.success("Status atualizado", `Novo status: ${status}`);
      await load();
    } catch (err) {
      toast.error("Erro ao atualizar status", getApiError(err));
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Candidaturas</h1>
        <p className="mt-1 text-slate-500">Acompanhe status e próximos passos.</p>
      </div>

      {loading ? (
        <div className="grid gap-4">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <div className="grid gap-4">
          {applications.map((app) => {
            const job = jobsById[app.job_id];
            return (
              <article key={app.id} className="card p-5">
                <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-xl font-bold">{job?.title || `Job #${app.job_id}`}</h2>
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyle[app.status] || "bg-slate-100 text-slate-700"}`}>{app.status}</span>
                    </div>
                    <p className="mt-1 text-slate-500">{job?.company || "Empresa não carregada"}</p>
                    <p className="mt-3 text-sm text-slate-600">{app.notes || "Sem notas"}</p>
                    {app.next_action && <p className="mt-2 text-sm font-medium">Próxima ação: {app.next_action}</p>}
                  </div>

                  <div className="min-w-52">
                    <label className="text-sm font-medium">Status</label>
                    <select className="input mt-2" value={app.status} onChange={(e) => changeStatus(app.id, e.target.value as ApplicationStatus)}>
                      {statuses.map((status) => <option key={status} value={status}>{status}</option>)}
                    </select>
                    <button className="btn-secondary" onClick={() => generateFollowup(app.id)}>Gerar follow-up</button>
                  </div>
                  {followups[app.id] && <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm"><b>{followups[app.id].next_action}</b><p className="mt-2">{followups[app.id].message}</p></div>}
                </div>
              </article>
            );
          })}
          {applications.length === 0 && (
            <EmptyState title="Nenhuma candidatura" description="Crie candidaturas a partir da tela de vagas para acompanhar seu pipeline." />
          )}
        </div>
      )}
    </div>
  );
}
