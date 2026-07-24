import { useEffect, useMemo, useState } from "react";
import { CalendarClock, Clock3, Power, RefreshCcw, Save, Send, ShieldCheck } from "lucide-react";

import { PageLoading, Spinner } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { getAutomationStatus, updateAutomationSettings } from "../services/automation";
import { AutomationMode, AutomationSettingsPayload, AutomationStatus } from "../types";

type FormState = {
  enabled: boolean;
  mode: AutomationMode;
  interval_minutes: string;
  times: string;
  window_start: string;
  window_end: string;
  search_terms: string;
  min_role_relevance: string;
};

function formatDateTime(value?: string | null) {
  if (!value) return "Nunca executado";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

function statusLabel(enabled: boolean) {
  return enabled ? "Ativa" : "Inativa";
}

function modeLabel(mode: AutomationMode) {
  const labels: Record<AutomationMode, string> = {
    interval: "A cada X minutos",
    fixed: "Horários fixos",
    window: "Janela de horário",
  };
  return labels[mode];
}

function toForm(status: AutomationStatus): FormState {
  return {
    enabled: Boolean(status.enabled),
    mode: status.mode || "interval",
    interval_minutes: status.interval_minutes ? String(status.interval_minutes) : "60",
    times: (status.times && status.times.length ? status.times : ["08:00", "12:00", "18:00"]).join(", "),
    window_start: status.window_start || "08:00",
    window_end: status.window_end || "18:00",
    search_terms: (status.search_terms || []).join("\n"),
    min_role_relevance: String(status.min_role_relevance || 55),
  };
}

function splitTimes(value: string) {
  return value
    .split(/[;,\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function validateTime(value: string) {
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(value);
}

export function Automation() {
  const toast = useToast();
  const [status, setStatus] = useState<AutomationStatus | null>(null);
  const [form, setForm] = useState<FormState>({
    enabled: false,
    mode: "interval",
    interval_minutes: "60",
    times: "08:00, 12:00, 18:00",
    window_start: "08:00",
    window_end: "18:00",
    search_terms: "",
    min_role_relevance: "55",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setApiError(null);
    try {
      const response = await getAutomationStatus();
      setStatus(response);
      setForm(toForm(response));
    } catch (err) {
      const message = getApiError(err);
      setApiError(message);
      toast.error("Erro ao carregar automação", message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const validationError = useMemo(() => {
    if (form.mode === "interval") {
      const minutes = Number(form.interval_minutes);
      if (!Number.isFinite(minutes) || minutes < 15) return "Intervalo deve ser maior ou igual a 15 minutos.";
    }

    if (form.mode === "fixed") {
      const times = splitTimes(form.times);
      if (!times.length) return "Informe pelo menos um horário fixo.";
      if (times.some((item) => !validateTime(item))) return "Horários fixos devem estar no formato HH:MM.";
    }

    if (form.mode === "window") {
      if (!form.window_start || !form.window_end) return "Informe início e fim da janela.";
      if (!validateTime(form.window_start) || !validateTime(form.window_end)) return "Janela deve usar o formato HH:MM.";
    }

    const relevance = Number(form.min_role_relevance);
    if (!Number.isFinite(relevance) || relevance < 40 || relevance > 95) {
      return "A aderência mínima deve ficar entre 40% e 95%.";
    }
    if (!splitTimes(form.search_terms).length) return "Informe pelo menos um termo de busca.";

    return null;
  }, [form]);

  async function handleSave() {
    if (validationError) {
      toast.error("Corrija a configuração", validationError);
      return;
    }

    const payload: AutomationSettingsPayload = {
      enabled: form.enabled,
      mode: form.mode,
      interval_minutes: form.mode === "interval" ? Number(form.interval_minutes) : null,
      times: form.mode === "fixed" ? splitTimes(form.times) : null,
      window_start: form.mode === "window" ? form.window_start : null,
      window_end: form.mode === "window" ? form.window_end : null,
      search_terms: splitTimes(form.search_terms),
      min_role_relevance: Number(form.min_role_relevance),
    };

    setSaving(true);
    try {
      await updateAutomationSettings(payload);
      toast.success("Automação salva", "Configurações atualizadas com sucesso.");
      await load();
    } catch (err) {
      toast.error("Erro ao salvar automação", getApiError(err));
    } finally {
      setSaving(false);
    }
  }

  if (loading && !status && !apiError) return <PageLoading label="Carregando automação..." />;

  return (
    <div className="space-y-6" data-tour="automation-page">
      <section className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <p className="text-sm text-slate-500">Automação</p>
        <h1 className="mt-2 text-3xl font-bold">Scheduler de vagas no WhatsApp</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-500">
          Controle quando o Applymize busca vagas, calcula prioridade e envia alertas pelo WhatsApp. A automação continua desligada até você ativar.
        </p>
      </section>

      {apiError && !status && (
        <SectionCard title="Não foi possível carregar o status" subtitle="A tela continua disponível para nova tentativa sem ficar em branco.">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{apiError}</div>
          <button className="btn-secondary mt-4" onClick={load} disabled={loading}>
            {loading ? <Spinner label="Tentando..." /> : <><RefreshCcw className="mr-2 h-4 w-4" /> Tentar novamente</>}
          </button>
        </SectionCard>
      )}

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="card p-5">
          <p className="text-sm text-slate-500">Scheduler</p>
          <div className={`mt-3 inline-flex rounded-full border px-3 py-1 text-sm font-bold ${status?.scheduler_enabled ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-amber-200 bg-amber-50 text-amber-700"}`}>
            {status?.scheduler_enabled ? "Ligado no backend" : "Desligado no backend"}
          </div>
        </div>
        <div className="card p-5">
          <p className="text-sm text-slate-500">Automação</p>
          <div className={`mt-3 inline-flex rounded-full border px-3 py-1 text-sm font-bold ${form.enabled ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-slate-200 bg-slate-100 text-slate-700"}`}>
            {statusLabel(form.enabled)}
          </div>
        </div>
        <div className="card p-5">
          <p className="text-sm text-slate-500">Última execução</p>
          <p className="mt-2 font-bold text-slate-900">{formatDateTime(status?.last_run)}</p>
        </div>
        <div className="card p-5">
          <p className="text-sm text-slate-500">Próxima estimada</p>
          <p className="mt-2 font-bold text-slate-900">{formatDateTime(status?.next_run_estimate)}</p>
        </div>
        <div className="card p-5">
          <p className="text-sm text-slate-500">Notificações enviadas</p>
          <p className="mt-2 text-2xl font-black text-slate-900">{status?.total_notifications_sent ?? 0}</p>
        </div>
      </div>

      <SectionCard title="Configurações da automação" subtitle="Essas opções valem apenas para o usuário/tenant logado.">
        <div className="space-y-5">
          <label className="flex cursor-pointer items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-white p-3 text-slate-700 shadow-sm"><Power className="h-5 w-5" /></div>
              <div>
                <p className="font-bold text-slate-900">Ativar automação</p>
                <p className="text-sm text-slate-500">Quando ativo, o backend poderá enviar vagas elegíveis automaticamente.</p>
              </div>
            </div>
            <input
              type="checkbox"
              className="h-6 w-6 accent-blue-700"
              checked={form.enabled}
              onChange={(e) => setForm((prev) => ({ ...prev, enabled: e.target.checked }))}
            />
          </label>

          <div className="grid gap-4 lg:grid-cols-3">
            <label className="block lg:col-span-2">
              <span className="mb-1 block text-sm font-bold text-slate-700">Cargos e termos buscados</span>
              <textarea
                className="input min-h-36"
                value={form.search_terms}
                onChange={(e) => setForm((prev) => ({ ...prev, search_terms: e.target.value }))}
                placeholder={"Automação de Processos\nAnalista de Processos\nRPA\nPower Automate"}
              />
              <p className="mt-1 text-xs text-slate-500">Use uma linha ou vírgula por termo. O primeiro deve representar seu cargo-alvo principal.</p>
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-bold text-slate-700">Aderência mínima (%)</span>
              <input
                className="input"
                type="number"
                min={40}
                max={95}
                value={form.min_role_relevance}
                onChange={(e) => setForm((prev) => ({ ...prev, min_role_relevance: e.target.value }))}
              />
              <p className="mt-1 text-xs text-slate-500">Vagas abaixo desse valor não entram nem são enviadas.</p>
            </label>
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <label className="block">
              <span className="mb-1 block text-sm font-bold text-slate-700">Modo</span>
              <select className="input" value={form.mode} onChange={(e) => setForm((prev) => ({ ...prev, mode: e.target.value as AutomationMode }))}>
                <option value="interval">A cada X minutos</option>
                <option value="fixed">Horários fixos</option>
                <option value="window">Janela de horário</option>
              </select>
            </label>

            <div className="rounded-2xl border border-slate-200 bg-white p-4 lg:col-span-2">
              <div className="flex items-start gap-3">
                <Clock3 className="mt-0.5 h-5 w-5 text-slate-500" />
                <div>
                  <p className="font-bold text-slate-900">{modeLabel(form.mode)}</p>
                  <p className="mt-1 text-sm text-slate-500">
                    {form.mode === "interval" && "Executa novamente quando o intervalo mínimo desde a última execução for atingido."}
                    {form.mode === "fixed" && "Executa em horários específicos configurados pelo usuário."}
                    {form.mode === "window" && "Executa somente dentro da janela de horário configurada."}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {form.mode === "interval" && (
            <label className="block max-w-md">
              <span className="mb-1 block text-sm font-bold text-slate-700">Intervalo em minutos</span>
              <input
                className="input"
                type="number"
                min={15}
                step={1}
                value={form.interval_minutes}
                onChange={(e) => setForm((prev) => ({ ...prev, interval_minutes: e.target.value }))}
              />
              <p className="mt-1 text-xs text-slate-500">Mínimo permitido: 15 minutos.</p>
            </label>
          )}

          {form.mode === "fixed" && (
            <label className="block">
              <span className="mb-1 block text-sm font-bold text-slate-700">Horários fixos</span>
              <input
                className="input"
                value={form.times}
                onChange={(e) => setForm((prev) => ({ ...prev, times: e.target.value }))}
                placeholder="08:00, 12:00, 18:00"
              />
              <p className="mt-1 text-xs text-slate-500">Separe por vírgula, ponto e vírgula ou quebra de linha. Exemplo: 08:00, 12:00, 18:00.</p>
            </label>
          )}

          {form.mode === "window" && (
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-1 block text-sm font-bold text-slate-700">Início da janela</span>
                <input
                  className="input"
                  type="time"
                  value={form.window_start}
                  onChange={(e) => setForm((prev) => ({ ...prev, window_start: e.target.value }))}
                />
              </label>
              <label className="block">
                <span className="mb-1 block text-sm font-bold text-slate-700">Fim da janela</span>
                <input
                  className="input"
                  type="time"
                  value={form.window_end}
                  onChange={(e) => setForm((prev) => ({ ...prev, window_end: e.target.value }))}
                />
              </label>
            </div>
          )}

          {validationError && (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{validationError}</div>
          )}

          <div className="flex flex-wrap items-center gap-3">
            <button className="btn-primary" onClick={handleSave} disabled={saving || Boolean(validationError)}>
              {saving ? <Spinner label="Salvando..." /> : <><Save className="mr-2 h-4 w-4" /> Salvar automação</>}
            </button>
            <button className="btn-secondary" onClick={load} disabled={loading || saving}>
              {loading ? <Spinner label="Atualizando..." /> : <><RefreshCcw className="mr-2 h-4 w-4" /> Recarregar status</>}
            </button>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Segurança operacional" subtitle="Resumo dos controles usados pelo scheduler.">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <ShieldCheck className="h-5 w-5 text-slate-600" />
            <p className="mt-2 font-bold">Opt-in por usuário</p>
            <p className="mt-1 text-sm text-slate-500">A automação só envia quando você ativa nesta tela.</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <Send className="h-5 w-5 text-slate-600" />
            <p className="mt-2 font-bold">Sem duplicidade</p>
            <p className="mt-1 text-sm text-slate-500">Vagas já notificadas para o usuário são ignoradas.</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <CalendarClock className="h-5 w-5 text-slate-600" />
            <p className="mt-2 font-bold">Controle de execução</p>
            <p className="mt-1 text-sm text-slate-500">O backend respeita modo, horários e janela configurados.</p>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
