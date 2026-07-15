import { useEffect, useState } from "react";
import { Bell, Send, MessageCircle } from "lucide-react";

import { PageLoading, Spinner } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { getNotificationSettings, sendHighPriorityNotifications, sendTestNotification } from "../services/notifications";
import { NotificationResult, NotificationSettings } from "../types";

function StatusBadge({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-bold ${ok ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>
      {label}: {ok ? "configurado" : "não configurado"}
    </span>
  );
}

export function Notifications() {
  const toast = useToast();
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [result, setResult] = useState<NotificationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState("");

  async function load() {
    setLoading(true);
    try {
      setSettings(await getNotificationSettings());
    } catch (err) {
      toast.error("Erro ao carregar notificações", getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function run(label: string, fn: () => Promise<NotificationResult>, success: string) {
    setAction(label);
    try {
      const response = await fn();
      setResult(response);
      toast.success(success, `${response.sent} envio(s), ${response.skipped || 0} ignorado(s).`);
      await load();
    } catch (err) {
      toast.error("Erro ao enviar notificação", getApiError(err));
    } finally {
      setAction("");
    }
  }

  if (loading || !settings) return <PageLoading label="Carregando notificações..." />;

  return (
    <div className="space-y-6" data-tour="notifications-page">
      <section className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <p className="text-sm text-slate-500">Notification Center</p>
        <h1 className="mt-2 text-3xl font-bold">Notificações controladas</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-500">Alertas opcionais de vagas de alta e média prioridade. Envio automático fica desativado por padrão.</p>
      </section>

      <SectionCard title="Status dos canais" subtitle={settings.responsible_use}>
        <div className="flex flex-wrap gap-2">
          <StatusBadge ok={settings.enabled} label="Notificações" />
          <StatusBadge ok={settings.telegram.configured} label="Telegram" />
          <StatusBadge ok={settings.whatsapp_evolution.configured} label="WhatsApp Evolution" />
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">Limite por execução: {settings.max_per_run}</span>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">Prioridade mínima: {settings.min_priority === "HIGH" ? "Alta" : settings.min_priority === "MEDIUM" ? "Média" : settings.min_priority === "LOW" ? "Baixa" : settings.min_priority}</span>
        </div>

        {!settings.enabled && (
          <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            Para enviar notificações, configure <b>NOTIFICATIONS_ENABLED=true</b> no .env e pelo menos um canal.
          </div>
        )}

        <div className="mt-4">
          <a className="btn-secondary" href="/whatsapp-pairing">
            <MessageCircle className="mr-2 h-4 w-4" /> Ir para pareamento WhatsApp
          </a>
        </div>
      </SectionCard>

      <SectionCard title="Ações manuais" subtitle="Nada é enviado sozinho. Você controla cada execução.">
        <div className="flex flex-wrap gap-3">
          <button className="btn-secondary" onClick={() => run("test", sendTestNotification, "Teste executado")} disabled={!!action}>
            {action === "test" ? <Spinner label="Enviando..." /> : <><Bell className="mr-2 h-4 w-4" /> Enviar teste</>}
          </button>
          <button className="btn-primary" onClick={() => run("priority", sendHighPriorityNotifications, "Envio de prioritárias executado")} disabled={!!action}>
            {action === "priority" ? <Spinner label="Enviando..." /> : <><Send className="mr-2 h-4 w-4" /> Enviar vagas prioritárias</>}
          </button>
        </div>
      </SectionCard>

      {result && (
        <SectionCard title="Resultado da última execução">
          <pre className="overflow-auto rounded-2xl bg-slate-50 p-4 text-sm text-slate-700 ring-1 ring-slate-200">{JSON.stringify(result, null, 2)}</pre>
        </SectionCard>
      )}
    </div>
  );
}
