import { FileText, Layers3, Sparkles, Wand2 } from "lucide-react";
import { Link } from "react-router-dom";
import { MiniFeature, PremiumCTA, PremiumHero, PremiumMetric, PremiumPanel, PremiumTimeline } from "../components/Premium";

export function AdvancedCV() {
  return (
    <div className="space-y-6">
      <PremiumHero
        eyebrow="CV Pro Engine"
        title="Geração avançada de currículo com narrativa, ATS e variações por vaga."
        description="Uma camada comercial para transformar perfil, LinkedIn, histórico e vagas em currículos mais fortes, exportáveis e posicionados para recrutadores."
        icon={FileText}
      >
        <div className="rounded-3xl border border-white/15 bg-white/10 p-4 text-white backdrop-blur lg:min-w-[360px]">
          <p className="text-xs font-black uppercase tracking-wide text-blue-100">Preview ATS</p>
          <p className="mt-2 text-4xl font-black">91%</p>
          <p className="mt-1 text-sm text-blue-100">Template executivo otimizado</p>
        </div>
      </PremiumHero>

      <div className="grid gap-4 md:grid-cols-3">
        <PremiumMetric label="Templates" value="3" helper="ATS, executivo e técnico" />
        <PremiumMetric label="Exportação" value="PDF/DOCX" helper="Estrutura preparada" />
        <PremiumMetric label="IA" value="Contextual" helper="Resumo e experiências por vaga" trend="Pro" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
        <PremiumPanel title="Fluxo CV Pro" subtitle="Como a geração avançada deve funcionar dentro do Applymize.">
          <PremiumTimeline items={[
            { title: "Selecionar vaga ou objetivo", description: "O usuário escolhe uma vaga real ou um cargo alvo para orientar a narrativa.", status: "Input" },
            { title: "Cruzar currículo, LinkedIn e perfil", description: "O motor usa dados existentes para evitar inventar experiências e manter consistência.", status: "Contexto" },
            { title: "Gerar versão otimizada", description: "Resumo, experiências, skills e palavras-chave são organizados para ATS e RH.", status: "IA" },
            { title: "Exportar e comparar", description: "Usuário acompanha score, melhorias e versão pronta para PDF/DOCX.", status: "Pro" },
          ]} />
        </PremiumPanel>

        <PremiumPanel title="Preview visual" subtitle="Demonstração do valor comercial sem depender de geração real nesta tela.">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <div className="rounded-2xl bg-white p-5 shadow-sm">
              <p className="text-xs font-black uppercase tracking-wide text-blue-700">Resumo otimizado</p>
              <h3 className="mt-2 text-xl font-black text-slate-950">Analista de Dados & Automação</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">Profissional com experiência em automação, BI, SQL e pipelines de dados, focado em reduzir tempo operacional e transformar dados em decisões estratégicas.</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {['Python', 'SQL', 'Power BI', 'ETL', 'Automação'].map((tag) => <span key={tag} className="badge">{tag}</span>)}
              </div>
            </div>
          </div>
        </PremiumPanel>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <MiniFeature icon={FileText} title="Template executivo ATS" description="Visual limpo, compatível com leitura automática e recrutadores." />
        <MiniFeature icon={Wand2} title="Resumo por vaga" description="Narrativa adaptada ao cargo sem inventar experiência." />
        <MiniFeature icon={Layers3} title="Versões salvas" description="Base para histórico de currículos, comparação e evolução." />
      </div>

      <PremiumCTA>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-2xl font-black">Próximo passo: geração real com exportação.</h2>
            <p className="mt-2 text-sm leading-6 text-blue-100">A prévia moderna atual já está disponível no Meu Perfil. Esta página organiza a evolução premium do módulo.</p>
          </div>
          <Link to="/profile" className="rounded-xl bg-white px-5 py-3 text-center font-black text-slate-950">Ir para Meu Perfil</Link>
        </div>
      </PremiumCTA>
    </div>
  );
}
