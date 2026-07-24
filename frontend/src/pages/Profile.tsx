import { FormEvent, useEffect, useState } from "react";
import { api } from "../services/api";
import { Upload } from "lucide-react";
import { PageLoading, Spinner } from "../components/Loading";
import { SectionCard } from "../components/SectionCard";
import { useToast } from "../context/ToastContext";
import { getApiError } from "../services/api";
import { addSkill, getModernResumeHtml, getProfile, parseResume, updateProfile, uploadResume } from "../services/profile";
import { UserProfile } from "../types";
import { useAuth } from "../context/AuthContext";

export function Profile() {
  const toast = useToast();
  const { reloadUser } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [skill, setSkill] = useState("");
  const [extractedText, setExtractedText] = useState("");
  const [modernResumeHtml, setModernResumeHtml] = useState("");
  const [resumePreviewLoading, setResumePreviewLoading] = useState(false);

  async function load() {
    setLoading(true);
    try { setProfile(await getProfile()); }
    catch (err) { toast.error("Erro ao carregar perfil", getApiError(err)); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (!profile) return;
    try {
      setProfile(await updateProfile({ ...profile, job_cities: profile.job_all_cities ? [] : profile.job_cities }));
      await reloadUser();
      toast.success("Perfil salvo");
    }
    catch (err) { toast.error("Erro ao salvar", getApiError(err)); }
  }

  async function submitSkill() {
    if (!skill.trim()) return;
    try { setProfile(await addSkill(skill.trim())); setSkill(""); toast.success("Skill adicionada"); }
    catch (err) { toast.error("Erro", getApiError(err)); }
  }

  async function handleUpload(file: File | null) {
    if (!file) return;
    try {
      const upload = await uploadResume(file);
      setExtractedText(upload.extracted_text || "");
      await load();
      await loadModernResumePreview();
      toast.success("Currículo importado", "Template moderno gerado automaticamente.");
    } catch (err) {
      toast.error("Erro no upload", getApiError(err));
    }
  }

  async function analyze() {
    try {
      const result = await parseResume();
      setExtractedText(result.extracted_text || "");
      setProfile(result.profile);
      toast.success("Currículo analisado");
      await loadModernResumePreview();
    } catch (err) {
      toast.error("Erro", getApiError(err));
    }
  }

  async function loadModernResumePreview() {
    setResumePreviewLoading(true);
    try {
      const html = await getModernResumeHtml();
      setModernResumeHtml(html);
    } catch (err) {
      toast.error("Erro ao gerar currículo moderno", getApiError(err));
    } finally {
      setResumePreviewLoading(false);
    }
  }

  function downloadModernResume() {
    if (!modernResumeHtml) return;
    const blob = new Blob([modernResumeHtml], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "curriculo_applymize_moderno.html";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function printModernResume() {
    if (!modernResumeHtml) return;
    const win = window.open("", "_blank");
    if (!win) {
      toast.error("Pop-up bloqueado", "Permita pop-ups para imprimir o currículo.");
      return;
    }
    win.document.open();
    win.document.write(modernResumeHtml);
    win.document.close();
    setTimeout(() => win.print(), 500);
  }

  if (loading || !profile) return <PageLoading label="Carregando perfil..." />;
  async function deleteAccount() {
    const confirmation = window.prompt("Digite EXCLUIR para remover sua conta permanentemente.");
    if (confirmation !== "EXCLUIR") return;
    try {
      await api.delete("/api/user/delete-account");
      localStorage.clear();
      sessionStorage.clear();
      window.location.href = "/";
    } catch (err) {
      toast.error("Erro ao excluir conta", getApiError(err));
    }
  }


  return (
    <div className="space-y-6" data-tour="profile-page">
      <section className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-6 text-slate-950 shadow-sm">
        <p className="text-sm text-slate-500">Meu Perfil</p>
        <h1 className="mt-2 text-3xl font-bold">Meu currículo e perfil profissional</h1>
        <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-800">
          <div className="h-full bg-emerald-400" style={{ width: `${profile.completeness}%` }} />
        </div>
        <p className="mt-2 text-sm text-slate-500">{profile.completeness}% completo • Perfil incompleto afeta recomendações</p>
      </section>

      <SectionCard title="Dados principais">
        <form onSubmit={save} className="grid gap-4 md:grid-cols-2">
          {["full_name", "professional_title", "location", "work_preferences", "phone", "email"].map((field) => (
            <label key={field} className="text-sm font-medium">
              {field}
              <input className="input mt-2" value={(profile as any)[field] || ""} onChange={(e) => setProfile({ ...profile, [field]: e.target.value })} />
            </label>
          ))}
          <label className="text-sm font-medium">
            salary_expectation
            <input className="input mt-2" type="number" value={profile.salary_expectation || 0} onChange={(e) => setProfile({ ...profile, salary_expectation: Number(e.target.value) })} />
          </label>
          <label className="text-sm font-medium md:col-span-2">
            summary
            <textarea className="input mt-2 min-h-32" value={profile.summary || ""} onChange={(e) => setProfile({ ...profile, summary: e.target.value })} />
          </label>
          <button className="btn-primary md:col-span-2">Salvar perfil</button>
        </form>
      </SectionCard>

      <SectionCard title="Formação e idiomas" subtitle="Use esses campos para melhorar o matching ATS, filtros de vagas e recomendações do Applymize.">
        <form onSubmit={save} className="grid gap-4 md:grid-cols-3">
          <label className="text-sm font-medium">Escolaridade
            <select className="input mt-2" value={profile.education_level || "Superior completo"} onChange={(e) => setProfile({ ...profile, education_level: e.target.value })}>
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
            <select className="input mt-2" value={profile.english_level || "Intermediário"} onChange={(e) => setProfile({ ...profile, english_level: e.target.value })}>
              <option value="Nenhum">Nenhum</option>
              <option value="Básico">Básico</option>
              <option value="Intermediário">Intermediário</option>
              <option value="Avançado">Avançado</option>
              <option value="Fluente">Fluente</option>
            </select>
          </label>
          <label className="text-sm font-medium">Espanhol
            <select className="input mt-2" value={profile.spanish_level || "Nenhum"} onChange={(e) => setProfile({ ...profile, spanish_level: e.target.value })}>
              <option value="Nenhum">Nenhum</option>
              <option value="Básico">Básico</option>
              <option value="Intermediário">Intermediário</option>
              <option value="Avançado">Avançado</option>
              <option value="Fluente">Fluente</option>
            </select>
          </label>
          <button className="btn-primary md:col-span-3">Salvar formação e idiomas</button>
        </form>
      </SectionCard>


      <SectionCard title="Preferências de busca" subtitle="Defina onde o Applymize deve focar as vagas de todos os providers e da automação.">
        <form onSubmit={save} className="grid gap-4 md:grid-cols-2">
          <label className="text-sm font-medium">País
            <input className="input mt-2" value={profile.job_country || "Brasil"} onChange={(e) => setProfile({ ...profile, job_country: e.target.value })} />
          </label>
          <label className="text-sm font-medium">Estado
            <input className="input mt-2" value={profile.job_state || "São Paulo"} onChange={(e) => setProfile({ ...profile, job_state: e.target.value })} />
          </label>
          <label className="text-sm font-medium">UF
            <input className="input mt-2" value={profile.job_state_code || "SP"} onChange={(e) => setProfile({ ...profile, job_state_code: e.target.value })} />
          </label>
          <label className="text-sm font-medium">Modalidade
            <select className="input mt-2" value={profile.job_remote_preference || "any"} onChange={(e) => setProfile({ ...profile, job_remote_preference: e.target.value })}>
              <option value="any">Presencial, híbrido ou remoto</option>
              <option value="hybrid">Priorizar híbrido</option>
              <option value="remote">Priorizar remoto</option>
              <option value="onsite">Priorizar presencial</option>
            </select>
          </label>
          <label className="text-sm font-medium md:col-span-2">Cidades
            <input
              className="input mt-2"
              disabled={profile.job_all_cities}
              value={(profile.job_cities || []).join(", ")}
              onChange={(e) => setProfile({ ...profile, job_cities: e.target.value.split(",").map((city) => city.trim()).filter(Boolean) })}
              placeholder="São Paulo, Santo André, São Bernardo do Campo"
            />
            <span className="mt-1 block text-xs text-slate-500">Separe por vírgula. Se marcar todas as cidades, o sistema usa estado/país como foco principal.</span>
          </label>
          <label className="flex items-center gap-2 text-sm font-medium md:col-span-2">
            <input type="checkbox" checked={Boolean(profile.job_all_cities)} onChange={(e) => setProfile({ ...profile, job_all_cities: e.target.checked })} />
            Buscar em todas as cidades do estado selecionado
          </label>
          <label className="text-sm font-medium md:col-span-2">Código de cidade InfoJobs
            <input className="input mt-2" value={profile.job_city_code || "5211323"} onChange={(e) => setProfile({ ...profile, job_city_code: e.target.value })} />
            <span className="mt-1 block text-xs text-slate-500">Opcional. São Paulo usa 5211323. Mantido para precisão do InfoJobs.</span>
          </label>
          <button className="btn-primary md:col-span-2">Salvar preferências de busca</button>
        </form>
      </SectionCard>

      <SectionCard title="Skills" action={<button className="btn-secondary" onClick={submitSkill}>Adicionar</button>}>
        <div className="mb-4 flex gap-2"><input className="input" value={skill} onChange={(e) => setSkill(e.target.value)} placeholder="Python, SQL..." /></div>
        <div className="flex flex-wrap gap-2">{profile.skills.map((item) => <span className="badge" key={item.id}>{item.name}</span>)}</div>
      </SectionCard>

      <SectionCard title="📄 Upload de currículo" subtitle="PDF, DOCX ou TXT. Extração local. Detecta LinkedIn/GitHub, idiomas e certificações quando existirem.">
        <div className="flex flex-wrap gap-3">
          <label className="btn-secondary cursor-pointer"><Upload className="mr-2 h-4 w-4" /> Enviar currículo
            <input className="hidden" type="file" accept=".pdf,.docx,.txt" onChange={(e) => handleUpload(e.target.files?.[0] || null)} />
          </label>
          <button className="btn-primary" onClick={analyze}>Analisar currículo</button>
        </div>
        {(extractedText || profile.resume_text) && <pre className="mt-4 max-h-96 overflow-auto rounded-2xl bg-slate-50 p-4 text-sm text-slate-700 ring-1 ring-slate-200 whitespace-pre-wrap">{extractedText || profile.resume_text}</pre>}
      </SectionCard>

      <SectionCard title="Currículo moderno Applymize" subtitle="Gera automaticamente um currículo visual em HTML A4 a partir do currículo importado e dos dados do perfil.">
        <div className="flex flex-wrap gap-3">
          <button className="btn-primary" onClick={loadModernResumePreview} disabled={resumePreviewLoading}>
            {resumePreviewLoading ? <Spinner label="Gerando..." /> : "Gerar prévia moderna"}
          </button>
          <button className="btn-secondary" onClick={printModernResume} disabled={!modernResumeHtml}>Imprimir / Salvar PDF</button>
          <button className="btn-secondary" onClick={downloadModernResume} disabled={!modernResumeHtml}>Baixar HTML</button>
        </div>
        {modernResumeHtml ? (
          <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
            <iframe title="Prévia do currículo moderno" className="h-[760px] w-full bg-white" srcDoc={modernResumeHtml} />
          </div>
        ) : (
          <p className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">Importe ou analise um currículo e clique em gerar prévia moderna.</p>
        )}
      </SectionCard>

      <SectionCard title="Privacidade e LGPD" subtitle="Gerencie permanentemente os dados da sua conta.">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
          <h3 className="text-lg font-bold text-red-700">Excluir conta permanentemente</h3>
          <p className="mt-2 text-sm text-red-600">Essa ação remove sua conta, preferências e dados associados do Applymize.</p>
          <button className="mt-4 rounded-2xl bg-red-600 px-5 py-3 text-sm font-bold text-white" onClick={deleteAccount}>Excluir minha conta</button>
        </div>
      </SectionCard>

    </div>
  );
}
