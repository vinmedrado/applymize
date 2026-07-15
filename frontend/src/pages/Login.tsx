import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { getApiError } from "../services/api";
import { forgotPassword } from "../services/auth";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { BrandLogo } from "../components/BrandLogo";

export function Login() {
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("Demo123!");
  const [remember, setRemember] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password, remember);
      toast.success("Login realizado", "Bem-vindo ao Applymize.");
      const rawFrom = (location.state as { from?: string } | null)?.from;
      const publicRoutes = ["/", "/login", "/register", "/demo", "/linkedin-analyzer"];
      const from = rawFrom && !publicRoutes.includes(rawFrom) ? rawFrom : "/dashboard";
      window.location.href = "/dashboard";
    } catch (err) {
      const message = getApiError(err);
      setError(message);
      toast.error("Falha no login", message);
    } finally {
      setLoading(false);
    }
  }

  async function requestReset() {
    if (!email) {
      toast.error("Informe seu e-mail", "Digite o e-mail cadastrado para receber o link.");
      return;
    }
    setResetLoading(true);
    try {
      const result = await forgotPassword(email);
      toast.success("Verifique seu e-mail", result.message);
    } catch (err) {
      const message = getApiError(err);
      toast.error("Erro ao recuperar senha", message);
    } finally {
      setResetLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_#e2e8f0,_#f8fafc_45%)] p-4">
      <form onSubmit={submit} className="card w-full max-w-md p-8">
        <div className="mb-8">
          <BrandLogo variant="auth" />
          <h2 className="mt-8 text-2xl font-bold">Entrar no Applymize</h2>
          <p className="mt-2 text-sm text-slate-500">Acesse sua central de inteligência de carreira.</p>
        </div>

        {error && <div className="mb-5 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        <label className="block text-sm font-medium">E-mail</label>
        <input className="input mt-2" value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />

        <div className="mt-4 flex items-center justify-between gap-3">
          <label className="block text-sm font-medium">Senha</label>
          <button type="button" className="text-xs font-semibold text-slate-700 underline disabled:opacity-50" onClick={requestReset} disabled={resetLoading}>
            {resetLoading ? "Enviando..." : "Esqueceu a senha?"}
          </button>
        </div>
        <div className="relative mt-2">
          <input className="input pr-12" value={password} onChange={(e) => setPassword(e.target.value)} type={showPassword ? "text" : "password"} required />
          <button
            type="button"
            className="absolute inset-y-0 right-3 my-auto text-sm font-semibold text-slate-600"
            onClick={() => setShowPassword((value) => !value)}
            aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
          >
            {showPassword ? "🙈" : "👁️"}
          </button>
        </div>

        <label className="mt-4 flex items-center gap-2 text-sm text-slate-600">
          <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
          Manter sessão neste navegador
        </label>

        <button className="btn-primary mt-6 w-full" disabled={loading}>
          {loading ? "Entrando..." : "Entrar"}
        </button>

        <p className="mt-5 text-center text-sm text-slate-600">
          Não tem conta? <Link className="font-semibold text-slate-950 underline" to="/register">Criar conta</Link>
        </p>
      </form>
    </div>
  );
}
