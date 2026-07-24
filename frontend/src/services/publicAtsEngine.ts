import type { AtsAnalysis } from "../types";

const GENERIC_TERMS = [
  "proativo",
  "dinamico",
  "responsavel",
  "comunicativo",
  "trabalho em equipe",
  "facil aprendizado",
  "pontual",
  "dedicado",
  "comprometido",
  "sou uma pessoa",
  "em busca de oportunidade",
];

const ATS_SECTIONS = {
  summary: ["resumo", "objetivo", "perfil", "profile", "summary"],
  skills: ["skills", "habilidades", "competencias", "tecnologias", "ferramentas"],
  experience: ["experiencia", "experience", "historico profissional", "carreira"],
  projects: ["projetos", "projeto", "projects", "portfolio", "github"],
  education: ["educacao", "formacao", "graduacao", "education"],
  certifications: ["certificacoes", "certifications", "certificates", "cursos"],
} as const;

const KNOWN_SKILLS = [
  "Python", "SQL", "FastAPI", "Django", "Flask", "PostgreSQL", "MySQL", "SQLite",
  "Docker", "Kubernetes", "Power BI", "Excel", "VBA", "Machine Learning",
  "Scikit-learn", "Pandas", "NumPy", "APIs", "REST", "GraphQL", "ETL", "Airflow",
  "Spark", "React", "TypeScript", "JavaScript", "Node.js", "AWS", "Azure", "GCP",
  "Git", "GitHub", "Selenium", "Playwright", "Automação", "Data Engineering",
  "Análise de Dados", "DAX", "Power Query", "SQLAlchemy", "Alembic", "Pytest",
  "CI/CD", "Linux", "Postman", "Streamlit", "Scraping", "BeautifulSoup",
  "RPA", "UiPath", "Power Automate", "n8n", "Zapier", "Make", "BPMN",
  "Lean", "Six Sigma", "Mapeamento de Processos", "Melhoria Contínua", "Kanban",
  "Scrum", "Jira", "SAP", "TOTVS", "Salesforce", "Tableau", "Looker", "Qlik",
  "Java", "C#", ".NET", "Go", "PHP", "Ruby", "Figma", "Google Analytics",
];

const STOPWORDS = new Set([
  "a", "as", "ao", "aos", "com", "como", "da", "das", "de", "do", "dos", "e",
  "em", "entre", "essa", "esse", "esta", "este", "para", "pela", "pelas", "pelo",
  "pelos", "por", "que", "se", "sem", "ser", "sua", "suas", "seu", "seus", "um",
  "uma", "na", "nas", "no", "nos", "ou", "mais", "muito", "ter", "tem", "vaga",
  "cargo", "empresa", "area", "anos", "experiencia", "conhecimento", "responsavel",
  "atividades", "requisitos", "desejavel", "buscamos", "profissional", "trabalho",
  "the", "and", "for", "with", "from", "this", "that", "you", "your", "our",
]);

type SectionKey = keyof typeof ATS_SECTIONS;

export type LocalAtsAnalysis = AtsAnalysis & {
  detected_skills: string[];
  found_sections: SectionKey[];
  local_only: true;
};

export type PublicAtsInput = {
  resumeText: string;
  targetRole?: string;
  jobDescription?: string;
};

function normalize(text: string) {
  return (text || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

function clamp(value: number) {
  return Math.max(0, Math.min(100, Math.round(value * 100) / 100));
}

function unique<T>(items: T[]) {
  return [...new Set(items)];
}

function tokenize(text: string) {
  return normalize(text)
    .replace(/[^a-z0-9+#.]+/g, " ")
    .split(/\s+/)
    .filter((token) => token.length > 2 && !STOPWORDS.has(token));
}

function includesTerm(corpus: string, term: string) {
  const normalizedTerm = normalize(term);
  if (!normalizedTerm) return false;
  const escaped = normalizedTerm.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(^|[^a-z0-9])${escaped}([^a-z0-9]|$)`, "i").test(corpus);
}

function detectSkills(text: string) {
  const corpus = normalize(text);
  return KNOWN_SKILLS.filter((skill) => includesTerm(corpus, skill));
}

function detectSections(text: string) {
  const corpus = normalize(text);
  const found: SectionKey[] = [];
  const missing: SectionKey[] = [];

  (Object.entries(ATS_SECTIONS) as [SectionKey, readonly string[]][]).forEach(([section, aliases]) => {
    if (aliases.some((alias) => corpus.includes(normalize(alias)))) found.push(section);
    else missing.push(section);
  });

  return { found, missing, score: clamp((found.length / Object.keys(ATS_SECTIONS).length) * 100) };
}

function extractJobKeywords(jobText: string) {
  if (!jobText.trim()) return [];

  const skillTerms = detectSkills(jobText);
  const counts = new Map<string, number>();
  tokenize(jobText).forEach((token) => counts.set(token, (counts.get(token) || 0) + 1));

  const frequentTerms = [...counts.entries()]
    .filter(([term]) => term.length >= 4 && !skillTerms.some((skill) => normalize(skill).includes(term)))
    .sort((a, b) => b[1] - a[1] || b[0].length - a[0].length)
    .slice(0, 16)
    .map(([term]) => term);

  return unique([...skillTerms, ...frequentTerms]).slice(0, 24);
}

function gradeFromScore(score: number) {
  if (score >= 95) return "A+";
  if (score >= 85) return "A";
  if (score >= 72) return "B";
  if (score >= 58) return "C";
  if (score >= 42) return "D";
  return "F";
}

function probabilityFromScore(score: number) {
  if (score >= 85) return "Alta probabilidade de passar em uma triagem inicial baseada nestes critérios.";
  if (score >= 70) return "Boa probabilidade, com ajustes pontuais recomendados.";
  if (score >= 55) return "Probabilidade moderada; revise palavras-chave, clareza e evidências.";
  return "Baixa probabilidade; o currículo precisa de ajustes importantes antes da candidatura.";
}

function inferSeniority(text: string) {
  const corpus = normalize(text);
  if (["lead", "lider", "principal", "especialista", "senior", "sr"].some((term) => includesTerm(corpus, term))) return 3;
  if (["junior", "jr", "estagio", "estagiario", "trainee"].some((term) => includesTerm(corpus, term))) return 1;
  return 2;
}

function seniorityScore(resumeText: string, jobText: string) {
  if (!jobText.trim()) return 80;
  const resumeLevel = inferSeniority(resumeText);
  const jobLevel = inferSeniority(jobText);
  if (resumeLevel === jobLevel) return 95;
  if (resumeLevel > jobLevel) return 86;
  return clamp(95 - Math.abs(resumeLevel - jobLevel) * 25);
}

export function analyzePublicResume({
  resumeText,
  targetRole = "",
  jobDescription = "",
}: PublicAtsInput): LocalAtsAnalysis {
  const text = resumeText.trim();
  const corpus = normalize(text);
  const lines = text.split(/\r?\n/).filter((line) => line.trim());
  const skills = detectSkills(text);
  const sections = detectSections(text);
  const emailDetected = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/.test(text);
  const phoneDetected = /(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9?\d{4}[-\s]?\d{4}/.test(text);
  const linkedInDetected = /linkedin\.com\/in\//i.test(text);
  const githubDetected = /github\.com\//i.test(text);

  const warnings: string[] = [];
  let clarity = 70;
  if (text.length >= 1200 && text.length <= 6500) clarity += 18;
  else if (text.length < 600) {
    clarity -= 25;
    warnings.push("Currículo muito curto para uma avaliação robusta.");
  } else if (text.length > 8500) {
    clarity -= 15;
    warnings.push("Currículo muito longo; pode dificultar a leitura de RH e ATS.");
  }
  if (lines.length >= 12) clarity += 8;
  else {
    clarity -= 8;
    warnings.push("Poucas linhas ou seções detectadas; organize melhor o currículo.");
  }
  const genericHits = GENERIC_TERMS.filter((term) => corpus.includes(term));
  if (genericHits.length >= 4) {
    clarity -= 15;
    warnings.push("Há excesso de termos genéricos sem evidência prática.");
  } else if (genericHits.length >= 2) clarity -= 8;
  if (emailDetected) clarity += 3;
  else {
    clarity -= 8;
    warnings.push("E-mail não detectado.");
  }
  if (phoneDetected) clarity += 3;
  else {
    clarity -= 5;
    warnings.push("Telefone não detectado.");
  }
  if (linkedInDetected || githubDetected) clarity += 4;
  clarity = clamp(clarity);

  const contactScore =
    (emailDetected ? 35 : 0)
    + (phoneDetected ? 25 : 0)
    + (linkedInDetected ? 20 : 0)
    + (githubDetected ? 20 : 0);
  const ats = clamp(
    sections.score * 0.42
    + contactScore * 0.2
    + clamp(skills.length * 8) * 0.28
    + (text.length > 1000 ? 10 : 0),
  );

  const impactEvidence = (text.match(/\b\d+(?:[.,]\d+)?\s*(?:%|x|mil|milhao|milhões|horas|dias|meses)?\b/gi) || []).length;
  const actionEvidence = [
    "implementei", "desenvolvi", "automatizei", "reduzi", "aumentei", "criei",
    "liderei", "otimizei", "estruturei", "entreguei", "built", "developed",
  ].filter((term) => corpus.includes(term)).length;
  let experience = 35;
  if (sections.found.includes("experience")) experience += 25;
  if (sections.found.includes("projects")) experience += 10;
  experience += Math.min(impactEvidence * 4, 16);
  experience += Math.min(actionEvidence * 3, 14);
  experience = clamp(experience);

  const jobText = `${targetRole}\n${jobDescription}`.trim();
  const jobKeywords = extractJobKeywords(jobText);
  const missingKeywords = jobKeywords.filter((term) => !includesTerm(corpus, term));
  const matchedKeywords = jobKeywords.filter((term) => includesTerm(corpus, term));
  const keywordScore = jobKeywords.length
    ? clamp((matchedKeywords.length / jobKeywords.length) * 100)
    : skills.length >= 12 ? 90 : skills.length >= 7 ? 78 : skills.length >= 4 ? 62 : 38;

  if (!jobKeywords.length && skills.length < 4) {
    missingKeywords.push("skills técnicas específicas");
  }

  const seniority = seniorityScore(text, jobText);
  const resumeTokens = new Set(tokenize(text));
  const jobTokens = unique(tokenize(jobText));
  const textOverlap = jobTokens.length
    ? clamp((jobTokens.filter((token) => resumeTokens.has(token)).length / jobTokens.length) * 100)
    : keywordScore;
  const match = jobText
    ? clamp(keywordScore * 0.55 + textOverlap * 0.2 + seniority * 0.15 + experience * 0.1)
    : clamp(keywordScore * 0.45 + experience * 0.35 + seniority * 0.2);

  const summaryPresent = sections.found.includes("summary");
  const rh = clamp(
    clarity * 0.35
    + experience * 0.4
    + (summaryPresent ? 12 : 0)
    + (sections.found.includes("projects") ? 8 : 0)
    + (sections.found.includes("education") || sections.found.includes("certifications") ? 5 : 0),
  );
  const final = clamp(
    ats * 0.24
    + rh * 0.2
    + match * 0.22
    + keywordScore * 0.16
    + experience * 0.1
    + clarity * 0.08,
  );

  const strengths: string[] = [];
  if (skills.length) strengths.push(`Skills detectadas: ${skills.slice(0, 10).join(", ")}.`);
  if (linkedInDetected || githubDetected) strengths.push("Links profissionais detectados no currículo.");
  if (experience >= 70) strengths.push("Experiências ou projetos apresentam evidências de impacto.");
  if (keywordScore >= 75) strengths.push("Boa cobertura das palavras-chave avaliadas.");
  if (!strengths.length) strengths.push("Existe uma base inicial, mas faltam evidências profissionais mais específicas.");

  const weaknesses: string[] = [];
  if (sections.missing.length) weaknesses.push(`Seções ausentes ou pouco claras: ${sections.missing.join(", ")}.`);
  if (missingKeywords.length && jobText) weaknesses.push("Algumas palavras-chave relevantes da vaga não aparecem no currículo.");
  if (clarity < 70) weaknesses.push("Clareza e objetividade podem melhorar.");
  if (experience < 65) weaknesses.push("Experiências precisam de ações, resultados e métricas mais explícitas.");

  const suggestions: AtsAnalysis["suggestions"] = [];
  if (ats < 70) {
    suggestions.push({
      priority: "alta",
      title: "Reforçar estrutura ATS",
      description: "Use títulos claros para Resumo, Skills, Experiência, Projetos, Educação e Certificações.",
    });
  }
  if (missingKeywords.length && jobText) {
    suggestions.push({
      priority: "alta",
      title: "Adicionar palavras-chave verdadeiras da vaga",
      description: `Considere incluir naturalmente: ${missingKeywords.slice(0, 8).join(", ")}.`,
    });
  }
  if (experience < 65) {
    suggestions.push({
      priority: "alta",
      title: "Evidenciar experiência com impacto",
      description: "Reescreva os bullets com ação, ferramenta, resultado e uma métrica verificável.",
    });
  }
  if (clarity < 70) {
    suggestions.push({
      priority: "média",
      title: "Melhorar clareza",
      description: "Reduza termos genéricos e deixe o resumo direto e orientado ao cargo desejado.",
    });
  }
  if (sections.missing.length) {
    suggestions.push({
      priority: "média",
      title: "Completar seções ausentes",
      description: `Seções não identificadas: ${sections.missing.join(", ")}.`,
    });
  }
  if (!suggestions.length) {
    suggestions.push({
      priority: "baixa",
      title: "Fazer ajuste fino",
      description: "A estrutura está boa. Personalize palavras-chave e resultados para cada vaga.",
    });
  }

  return {
    ats_score: ats,
    rh_score: rh,
    match_score: match,
    keyword_score: keywordScore,
    experience_score: experience,
    clarity_score: clarity,
    seniority_score: seniority,
    final_score: final,
    grade: gradeFromScore(final),
    probability: probabilityFromScore(final),
    strengths,
    weaknesses,
    missing_keywords: unique(missingKeywords).slice(0, 18),
    suggestions,
    warnings,
    compared_job_id: null,
    detected_skills: skills,
    found_sections: sections.found,
    local_only: true,
  };
}
