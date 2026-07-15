import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { getApiError } from "../services/api";
import { resetPassword } from "../services/auth";
import { useToast } from "../context/ToastContext";
import { BrandLogo } from "../components/BrandLogo";

export function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const toast = useToast();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (!token) {
      setError("Token de recuperação ausente.");
      return;
    }
    if (password !== confirmPassword) {
      setError("As senhas não conferem.");
      return;
    }
    setLoading(true);
    try {
      const result = await resetPassword(token, password);
      toast.success("Senha redefinida", result.message);
      navigate("/login");
    } catch (err) {
      const message = getApiError(err);
      setError(message);
      toast.error("Erro ao redefinir senha", message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_#e2e8f0,_#f8fafc_45%)] p-4">
      <form onSubmit={submit} className="card w-full max-w-md p-8">
        <BrandLogo variant="auth" />
        <h2 className="mt-8 text-2xl font-bold">Redefinir senha</h2>
        <p className="mt-2 text-sm text-slate-500">Crie uma nova senha para acessar sua conta.</p>

        {error && <div className="mt-5 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        <label className="mt-6 block text-sm font-medium">Nova senha</label>
        <div className="relative mt-2">
          <input className="input pr-12" value={password} onChange={(e) => setPassword(e.target.value)} type={showPassword ? "text" : "password"} required />
          <button type="button" className="absolute inset-y-0 right-3 my-auto text-sm font-semibold text-slate-600" onClick={() => setShowPassword((value) => !value)}>
            {showPassword ? "🙈" : "👁️"}
          </button>
        </div>

        <label className="mt-4 block text-sm font-medium">Confirmar senha</label>
        <input className="input mt-2" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} type={showPassword ? "text" : "password"} required />

        <button className="btn-primary mt-6 w-full" disabled={loading}>
          {loading ? "Salvando..." : "Salvar nova senha"}
        </button>

        <p className="mt-5 text-center text-sm text-slate-600">
          <Link className="font-semibold text-slate-950 underline" to="/login">Voltar ao login</Link>
        </p>
      </form>
    </div>
  );
}
