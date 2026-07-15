import { useEffect, useState } from "react";
import { CheckCircle2, PlugZap, QrCode, RefreshCcw, Save, Send, Smartphone, Unplug } from "lucide-react";
import { QRCodeSVG } from "qrcode.react";

import { PageLoading, Spinner } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import {
  checkWhatsAppConnection,
  createWhatsAppInstance,
  deleteWhatsAppSession,
  disconnectWhatsApp,
  getWhatsAppQrCode,
  getWhatsAppStatus,
  saveWhatsAppPhone,
  sendWhatsAppTest,
} from "../services/whatsapp";
import { WhatsAppSessionStatus } from "../types";

function statusTone(status?: string) {
  if (status === "connected") return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (status === "waiting_qrcode" || status === "waiting_qr") return "bg-amber-50 text-amber-700 border-amber-200";
  if (status === "phone_missing" || status === "not_configured") return "bg-orange-50 text-orange-700 border-orange-200";
  if (status === "disconnected") return "bg-slate-100 text-slate-700 border-slate-200";
  if (status === "error") return "bg-red-50 text-red-700 border-red-200";
  return "bg-slate-100 text-slate-700 border-slate-200";
}

function friendlyStatus(status?: string) {
  const labels: Record<string, string> = {
    connected: "Conectado",
    waiting_qr: "Aguardando QR Code",
    waiting_qrcode: "Aguardando QR Code",
    disconnected: "Desconectado",
    phone_missing: "Telefone não salvo",
    not_configured: "Não configurado",
    error: "Erro",
    phone_saved: "Telefone salvo",
  };
  return labels[status || ""] || status || "Não configurado";
}

export function WhatsAppPairing() {
  const toast = useToast();
  const [status, setStatus] = useState<WhatsAppSessionStatus | null>(null);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState("");

  async function load() {
    setLoading(true);
    try {
      const response = await getWhatsAppStatus();
      setStatus(response);
      setPhoneNumber(response.phone_number || "");
    } catch (err) {
      toast.error("Erro ao consultar WhatsApp", getApiError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function run(label: string, fn: () => Promise<WhatsAppSessionStatus>, success: string) {
    setAction(label);
    try {
      const response = await fn();
      setStatus(response);
      if (response.phone_number !== undefined) setPhoneNumber(response.phone_number || "");
      if (["error", "not_configured", "phone_missing", "number_missing"].includes(response.status)) {
        toast.error("Ação não concluída", response.message);
      } else {
        toast.success(success, response.message);
      }
    } catch (err) {
      toast.error("Erro na ação WhatsApp", getApiError(err));
    } finally {
      setAction("");
    }
  }

  if (loading || !status) return <PageLoading label="Carregando pareamento WhatsApp..." />;

  const qr = status.qrcode || status.qr_code || "";
  const isBase64Image = status.qrcode_type === "base64" || status.qr_type === "base64" || status.qrcode_type === "base64_image" || status.qr_type === "base64_image" || qr.startsWith("data:image");

  return (
    <div className="space-y-6" data-tour="whatsapp-page">
      <section className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <p className="text-sm text-slate-500">WhatsApp / Pareamento</p>
        <h1 className="mt-2 text-3xl font-bold">Conecte seu WhatsApp dentro do Applymize</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-500">
          Salve seu telefone, crie a conexão, escaneie o QR Code e envie um teste sem abrir a Evolution API manualmente.
        </p>
      </section>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="card p-5">
          <p className="text-sm text-slate-500">Configuração</p>
          <div className={`mt-3 inline-flex rounded-full border px-3 py-1 text-sm font-bold ${status.configured ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-red-200 bg-red-50 text-red-700"}`}>
            {status.configured ? "Backend configurado" : "Backend não configurado"}
          </div>
          <p className="mt-3 text-sm text-slate-600">A API key fica protegida no backend.</p>
        </div>
        <div className="card p-5">
          <p className="text-sm text-slate-500">Instância</p>
          <p className="mt-2 break-all font-bold">{status.instance_name || status.instance_id || "Gerada por usuário/tenant"}</p>
          <div className={`mt-3 inline-flex rounded-full border px-3 py-1 text-sm font-bold ${statusTone(status.status)}`}>
            {friendlyStatus(status.status)}
          </div>
        </div>
        <div className="card p-5">
          <p className="text-sm text-slate-500">Conexão</p>
          <div className="mt-3 flex items-center gap-2">
            <CheckCircle2 className={status.connected ? "text-emerald-600" : "text-slate-400"} />
            <span className="font-semibold">{status.connected ? "Conectado" : "Não conectado"}</span>
          </div>
          <p className="mt-3 text-sm text-slate-600">{status.message}</p>
          {status.connected && (
            <p className="mt-2 text-xs text-emerald-700">
              Sessão estabilizada{status.cached ? " · status em cache" : ""}.
            </p>
          )}
        </div>
      </div>

      {!status.configured && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          Configure EVOLUTION_API_URL e EVOLUTION_API_KEY no .env. O frontend continua acessando apenas o backend do Applymize.
        </div>
      )}

      <SectionCard title="1 — Configuração" subtitle="Use DDI + DDD + número. Ex: 5511999999999. Não precisa WhatsApp Business.">
        <div className="grid gap-3 lg:grid-cols-[1fr_auto]">
          <div className="relative">
            <Smartphone className="pointer-events-none absolute left-3 top-3 h-5 w-5 text-slate-400" />
            <input
              className="input pl-10"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="5511999999999"
            />
          </div>
          <button className="btn-primary" onClick={() => run("phone", () => saveWhatsAppPhone(phoneNumber), "Telefone salvo")} disabled={!!action}>
            {action === "phone" ? <Spinner label="Salvando..." /> : <><Save className="mr-2 h-4 w-4" /> Salvar telefone</>}
          </button>
        </div>
      </SectionCard>

      <SectionCard title="2 — Conexão" subtitle="Crie a conexão e verifique o status sem mexer na Evolution API.">
        <div className="flex flex-wrap gap-3">
          <button className="btn-primary" onClick={() => run("connect", createWhatsAppInstance, "Conexão preparada")} disabled={!!action}>
            {action === "connect" ? <Spinner label="Criando..." /> : <><PlugZap className="mr-2 h-4 w-4" /> Criar conexão</>}
          </button>
          <button className="btn-secondary" onClick={() => run("qrcode", getWhatsAppQrCode, "QR Code atualizado")} disabled={!!action}>
            {action === "qrcode" ? <Spinner label="Atualizando..." /> : <><QrCode className="mr-2 h-4 w-4" /> Atualizar QR Code</>}
          </button>
          <button className="btn-secondary" onClick={() => run("check", checkWhatsAppConnection, "Status atualizado")} disabled={!!action}>
            {action === "check" ? <Spinner label="Verificando..." /> : <><RefreshCcw className="mr-2 h-4 w-4" /> Verificar conexão</>}
          </button>
          <button className="btn-secondary" onClick={() => run("disconnect", disconnectWhatsApp, "Instância desconectada")} disabled={!!action}>
            {action === "disconnect" ? <Spinner label="Desconectando..." /> : <><Unplug className="mr-2 h-4 w-4" /> Desconectar</>}
          </button>
          <button className="btn-secondary border-red-200 text-red-700 hover:bg-red-50" onClick={async () => {
            if (!window.confirm("Apagar a sessão WhatsApp deste usuário?")) return;
            setAction("delete");
            try {
              const response = await deleteWhatsAppSession();
              toast.success("Sessão removida", response.message);
              await load();
            } catch (err) {
              toast.error("Erro ao apagar sessão", getApiError(err));
            } finally {
              setAction("");
            }
          }} disabled={!!action}>
            {action === "delete" ? <Spinner label="Apagando..." /> : "Apagar sessão"}
          </button>
        </div>
      </SectionCard>

      <SectionCard title="3 — QR Code" subtitle="Abra o WhatsApp > Dispositivos conectados > Conectar dispositivo.">
        <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
          {qr ? (
            <div className="flex flex-col items-center gap-4">
              {isBase64Image ? (
                <img src={qr} alt="QR Code WhatsApp" className="h-72 w-72 rounded-2xl bg-white object-contain p-3 shadow-sm" />
              ) : (
                <div className="rounded-2xl bg-white p-4 shadow-sm">
                  <QRCodeSVG value={qr} size={256} />
                </div>
              )}
              <p className="text-sm text-slate-600">Depois de escanear, clique em “Verificar conexão”.</p>
            </div>
          ) : (
            <div>
              <QrCode className="mx-auto h-16 w-16 text-slate-500" />
              <p className="mt-3 font-semibold text-slate-700">QR Code ainda não disponível</p>
              <p className="mt-1 text-sm text-slate-500">Clique em “Atualizar QR Code”.</p>
            </div>
          )}
        </div>
      </SectionCard>

      <SectionCard title="4 — Teste" subtitle="Envia uma mensagem controlada para o telefone salvo.">
        <button className="btn-primary" onClick={() => run("test", () => sendWhatsAppTest(""), "Mensagem teste enviada")} disabled={!!action || !status.target_number_configured}>
          {action === "test" ? <Spinner label="Enviando..." /> : <><Send className="mr-2 h-4 w-4" /> Enviar mensagem teste</>}
        </button>
        {!status.target_number_configured && (
          <p className="mt-3 text-sm text-amber-700">Salve seu telefone antes de enviar a mensagem teste.</p>
        )}
      </SectionCard>
    </div>
  );
}
