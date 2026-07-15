import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getApiError } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { BrandLogo } from "../components/BrandLogo";

export function Register() {
  const { register } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    tenant_name: "Minha Empresa",
    full_name: "",
    email: "",
    password: "Strong123!",
    skills: "Python, SQL, FastAPI, PostgreSQL, Docker, Power BI",
    seniority: "mid",
    target_role: "Analista de Dados e Automação",
    job_country: "Brasil",
    job_state: "São Paulo",
    job_state_code: "SP",
    job_cities_text: "São Paulo",
    job_all_cities: false,
    job_remote_preference: "any",
    job_city_code: "5211323",
    education_level: "Superior completo",
    english_level: "Intermediário",
    spanish_level: "Nenhum"
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(field: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        ...form,
        job_cities: form.job_all_cities ? [] : form.job_cities_text.split(",").map((city) => city.trim()).filter(Boolean),
      };
      await register(payload);
      toast.success("Conta criada", "Seu workspace foi criado com sucesso.");
      window.location.href = "/dashboard";
    } catch (err) {
      const message = getApiError(err);
      setError(message);
      toast.error("Erro ao criar conta", message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_#e2e8f0,_#f8fafc_45%)] p-4">
      <form onSubmit={submit} className="card w-full max-w-2xl p-8">
        <BrandLogo variant="auth" />
        <h2 className="mt-8 text-2xl font-bold">Criar conta</h2>
        <p className="mt-2 text-sm text-slate-500">Crie seu tenant e seu usuário principal.</p>

        {error && <div className="mt-5 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium">Nome</label>
            <input className="input mt-2" value={form.full_name} onChange={(e) => update("full_name", e.target.value)} required />
          </div>
          <div>
            <label className="block text-sm font-medium">Tenant/Empresa</label>
            <input className="input mt-2" value={form.tenant_name} onChange={(e) => update("tenant_name", e.target.value)} required />
          </div>
          <div>
            <label className="block text-sm font-medium">E-mail</label>
            <input className="input mt-2" type="email" value={form.email} onChange={(e) => update("email", e.target.value)} required />
          </div>
          <div>
            <label className="block text-sm font-medium">Senha forte</label>
            <div className="relative mt-2">
              <input className="input pr-12" type={showPassword ? "text" : "password"} value={form.password} onChange={(e) => update("password", e.target.value)} required />
              <button
                type="button"
                className="absolute inset-y-0 right-3 my-auto text-sm font-semibold text-slate-600"
                onClick={() => setShowPassword((value) => !value)}
                aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
              >
                {showPassword ? "🙈" : "👁️"}
              </button>
            </div>
            <p className="mt-1 text-xs text-slate-500">Use maiúscula, minúscula, número e caractere especial.</p>
          </div>
          <div>
            <label className="block text-sm font-medium">Senioridade</label>
            <select className="input mt-2" value={form.seniority} onChange={(e) => update("seniority", e.target.value)}>
              <option value="junior">Junior</option>
              <option value="mid">Pleno/Mid</option>
              <option value="senior">Senior</option>
              <option value="lead">Lead</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium">Cargo alvo</label>
            <input className="input mt-2" value={form.target_role} onChange={(e) => update("target_role", e.target.value)} />
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-blue-100 bg-blue-50/60 p-4">
          <h2 className="text-sm font-bold text-slate-900">Formação e idiomas</h2>
          <p className="mt-1 text-xs text-slate-500">Esses dados melhoram o matching ATS e a leitura do perfil por recrutadores.</p>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <label className="text-sm font-medium">Escolaridade
              <select className="input mt-2" value={form.education_level} onChange={(e) => update("education_level", e.target.value)}>
                <option value="Ensino médio">Ensino médio</option>
                <option value="Técnico">Técnico</option>
                <option value="Superior cursando">Superior cursando</option>
                <option value="Superior completo">Superior completo</option>
                <option value="Pós-graduação">Pós-graduação</option>
                <option value="MBA">MBA</option>
                <option value="Mestrado">Mestrado</option>
                <option value="Doutorado">Doutorado</option>
              </select>
            </label>
            <label className="text-sm font-medium">Inglês
              <select className="input mt-2" value={form.english_level} onChange={(e) => update("english_level", e.target.value)}>
                <option value="Nenhum">Nenhum</option>
                <option value="Básico">Básico</option>
                <option value="Intermediário">Intermediário</option>
                <option value="Avançado">Avançado</option>
                <option value="Fluente">Fluente</option>
              </select>
            </label>
            <label className="text-sm font-medium">Espanhol
              <select className="input mt-2" value={form.spanish_level} onChange={(e) => update("spanish_level", e.target.value)}>
                <option value="Nenhum">Nenhum</option>
                <option value="Básico">Básico</option>
                <option value="Intermediário">Intermediário</option>
                <option value="Avançado">Avançado</option>
                <option value="Fluente">Fluente</option>
              </select>
            </label>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <h2 className="text-sm font-bold text-slate-900">Preferência de busca de vagas</h2>
          <p className="mt-1 text-xs text-slate-500">O Applymize usa isso para focar os providers na sua região.</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <label className="text-sm font-medium">País
              <input className="input mt-2" value={form.job_country} onChange={(e) => update("job_country", e.target.value)} />
            </label>
            <label className="text-sm font-medium">Estado
              <input className="input mt-2" value={form.job_state} onChange={(e) => update("job_state", e.target.value)} />
            </label>
            <label className="text-sm font-medium">UF
              <input className="input mt-2" value={form.job_state_code} onChange={(e) => update("job_state_code", e.target.value)} />
            </label>
            <label className="text-sm font-medium">Modalidade
              <select className="input mt-2" value={form.job_remote_preference} onChange={(e) => update("job_remote_preference", e.target.value)}>
                <option value="any">Presencial, híbrido ou remoto</option>
                <option value="hybrid">Priorizar híbrido</option>
                <option value="remote">Priorizar remoto</option>
                <option value="onsite">Priorizar presencial</option>
              </select>
            </label>
            <label className="text-sm font-medium md:col-span-2">
              Cidades desejadas
              <input className="input mt-2" value={form.job_cities_text} onChange={(e) => update("job_cities_text", e.target.value)} disabled={form.job_all_cities} placeholder="São Paulo, Santo André" />
              <span className="mt-1 block text-xs text-slate-500">Separe por vírgula. Ex.: São Paulo, Santo André, São Bernardo do Campo.</span>
            </label>
            <label className="flex items-center gap-2 text-sm font-medium md:col-span-2">
              <input type="checkbox" checked={form.job_all_cities} onChange={(e) => setForm((prev) => ({ ...prev, job_all_cities: e.target.checked }))} />
              Buscar em todas as cidades do estado selecionado
            </label>
          </div>
        </div>

        <label className="mt-4 block text-sm font-medium">Skills</label>
        <textarea className="input mt-2 min-h-24" value={form.skills} onChange={(e) => update("skills", e.target.value)} />

        <button className="btn-primary mt-6 w-full" disabled={loading}>
          {loading ? "Criando..." : "Criar conta"}
        </button>

        <p className="mt-5 text-center text-sm text-slate-600">
          Já tem conta? <Link className="font-semibold text-slate-950 underline" to="/login">Entrar</Link>
        </p>
      </form>
    </div>
  );
}
