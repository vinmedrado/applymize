"""CareerLens v3 - AI Analyzer (ALL modules)"""
import json, re
from core.experience import calcular_experiencia_total

def _groq(api_key, system, user, max_tokens=3000, temp=0.3):
    try:
        from groq import Groq
        r = Groq(api_key=api_key).chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            max_tokens=max_tokens, temperature=temp,
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"ERRO:{e}"

def _json(raw):
    try:
        clean = re.sub(r'```json|```','',raw).strip()
        clean = re.sub(r',\s*}','}',clean)
        clean = re.sub(r',\s*]',']',clean)
        return json.loads(clean)
    except Exception as e:
        return {"_parse_error": str(e), "raw": raw[:1000]}
    
# ── 1. ATS Analysis ──
def analyze_ats(cv, key, target=""):
    exp = calcular_experiencia_total(cv)

    sys = f"""
Você é um avaliador sênior de currículos, ATS e empregabilidade para o mercado brasileiro.

Experiência calculada pelo sistema:
{exp}

Regras obrigatórias:
- Use anos_experiencia_total exatamente como veio em "anos".
- Não estime anos.
- Se anos for null, mantenha null.
- NÃO deduza baseado em cargos.
- Não assuma que o candidato é de tecnologia, dados ou escritório.
- Analise o currículo conforme o histórico real da pessoa.
- Não invente informações.
- Não transforme experiência operacional em experiência analítica se isso não estiver no currículo.
- Responda somente JSON válido.
- Não use markdown.
- Não use ```json.
"""

    ctx = f"Vaga alvo: {target}" if target else "Análise geral."

    usr = f"""Analise profundamente. {ctx}

CV:
{cv[:6000]}

Experiência detectada pelo sistema:
{exp}

IMPORTANTE:
- Use exatamente exp["anos"] no campo anos_experiencia_total.
- Não modifique esse valor.
- Se exp["anos"] for null, mantenha null.

JSON:
{{
  "score_geral": <0-100>,
  "scores_detalhados": {{
    "formatacao": <0-20>,
    "palavras_chave": <0-20>,
    "experiencia_relevante": <0-20>,
    "resultados_quantificados": <0-20>,
    "completude_secoes": <0-20>
  }},
  "nivel_perfil": "<Júnior|Pleno|Sênior|Especialista>",
  "anos_experiencia_total": null,
  "confianca_anos_experiencia": "Alta|Média|Baixa",
  "motivo_anos_experiencia": "",
  "area_principal_detectada": "",
  "areas_secundarias_detectadas": [],
  "cargos_ideais": ["c1","c2","c3","c4","c5"],
  "areas_recomendadas": ["a1","a2","a3"],
  "palavras_chave_encontradas": ["k1","k2","k3","k4","k5"],
  "palavras_chave_faltando": ["k1","k2","k3","k4","k5"],
  "tecnologias_identificadas": ["t1","t2","t3"],
  "soft_skills": ["s1","s2","s3"],
  "pontos_fortes": ["p1","p2","p3"],
  "problemas_criticos": ["p1","p2","p3"],
  "melhorias_prioritarias": ["m1","m2","m3"],
  "compatibilidade_ats": "<Alta|Média|Baixa>",
  "veredicto_rh": "<3-4 linhas>",
  "resumo_executivo": "<2 linhas diretas>",
  "score_empregabilidade": <0-100>,
  "gap_skills": ["skill1","skill2","skill3"],
  "proximos_passos": ["passo1","passo2","passo3"]
}}"""

    raw = _groq(key, sys, usr, 2500)
    r = _json(raw)

    if not isinstance(r, dict) or r.get("_parse_error"):
        return {
            "score_geral": 0,
            "error": "Falha ao converter resposta da IA em JSON",
            "raw": raw[:1000]
        }

    r["anos_experiencia_total"] = exp.get("anos")
    r["confianca_anos_experiencia"] = exp.get("confianca")
    r["motivo_anos_experiencia"] = exp.get("motivo")

    return r

# ── 2. Job Match ──
def analyze_job_match(cv, desc, title, company, key):
    sys = """
    Você é um recrutador sênior especialista em match candidato x vaga no Brasil.

    Regras:
    - Baseie a experiência relevante apenas em evidências do CV.
    - Não invente experiência para encaixar na vaga.
    - Não assuma área do candidato.
    - Compare somente o currículo com a vaga.
    - Diferencie experiência total de experiência relevante para ESTA vaga.
    - Se uma informação não estiver clara, indique como incerteza.
    - Responda somente JSON válido.
    - Não use markdown.
    """
    usr = f"""Compare CV com vaga.
CV: {cv[:3500]}
VAGA: {title} — {company}
DESC: {desc[:2000]}

JSON:
{{
  "match_score":<0-100>,
  "nivel_compatibilidade":"<Excelente|Boa|Razoável|Baixa>",
  "deve_aplicar":<true|false>,
  "motivo_decisao":"<2 linhas>",
  "requisitos_atendidos":["r1","r2","r3"],
  "requisitos_faltando":["r1","r2","r3"],
  "diferenciais_candidato":["d1","d2"],
  "palavras_chave_vaga":["k1","k2","k3","k4","k5"],
  "adicionar_no_cv":["k1","k2","k3"],
  "ajustes_rapidos":["a1","a2","a3"],
  "probabilidade_entrevista":"<Alta|Média|Baixa>",
  "dica_candidatura":"<2 linhas personalizadas>",
  "experiencia_relevante_para_vaga": {{
    "anos_estimados": null,
    "confianca": "Alta|Média|Baixa",
    "motivo": ""
  }}
}}"""
    raw = _groq(key, sys, usr, 1500)
    r = _json(raw)
    return r if r else {
        "match_score": 0,
        "error": "Falha ao converter resposta da IA em JSON",
        "raw": raw[:1000]
    }

# ── 3. CV Optimize ──
def optimize_cv(cv, ats, key):
    sys = "Especialista em currículos ATS-friendly para o mercado brasileiro. Mantenha APENAS dados reais."
    cargos = ", ".join(ats.get("cargos_ideais",[])[:3])
    probs  = "\n".join(f"- {p}" for p in ats.get("problemas_criticos",[]))
    kws    = ", ".join(ats.get("palavras_chave_faltando",[]))
    usr = f"""Reescreva otimizado.
ORIGINAL: {cv[:4000]}
Cargos alvo: {cargos}
Problemas: {probs}
Keywords: {kws}

FORMATO:
NOME
email | telefone | linkedin | github

RESUMO PROFISSIONAL
[3-4 linhas impactantes com keywords]

EXPERIÊNCIA PROFISSIONAL
[Cargo | Empresa | Período]
• [Resultado quantificado]
• [Resultado quantificado]

HABILIDADES TÉCNICAS
[Linguagens]: ...
[Ferramentas]: ...

PROJETOS DE DESTAQUE
[Nome] — [Impacto + tecnologias]

FORMAÇÃO ACADÊMICA
[Curso | Instituição | Período]

CERTIFICAÇÕES
• [Nome | Plataforma | Ano]

IDIOMAS
• [Idioma — Nível]"""
    return _groq(key, sys, usr, 3000)

# ── 4. CV tailored for specific job ──
def tailor_cv_for_job(cv, job_title, job_desc, keywords, key):
    sys = "Especialista em personalização de CV para vagas específicas. Mantenha dados reais, adapte linguagem e destaque pontos relevantes."
    usr = f"""Adapte este CV especificamente para a vaga abaixo.
CV ORIGINAL: {cv[:3500]}
VAGA: {job_title}
DESCRIÇÃO: {job_desc[:1500]}
KEYWORDS DA VAGA: {', '.join(keywords)}

Regras:
- Reordene experiências para priorizar as mais relevantes para ESTA vaga
- Inclua as keywords naturalmente
- Ajuste o resumo para mencionar especificamente o cargo/empresa
- Mantenha APENAS dados reais
- Use o mesmo formato estruturado com seções em MAIÚSCULAS"""
    return _groq(key, sys, usr, 2500)

# ── 5. Cover Letter ──
def gen_cover_letter(cv, title, company, desc, key, tone="profissional"):
    sys = f"Especialista em cartas de apresentação para o mercado brasileiro. Tom: {tone}. Autêntico, direto, nunca genérico."
    usr = f"""Escreva carta personalizada.
VAGA: {title} — {company}
DESC: {desc[:1500]}
CV: {cv[:2500]}

Estrutura:
1. Abertura impactante (NÃO comece com 'Venho por meio desta')
2. Por que esta empresa especificamente
3. 2-3 realizações mais relevantes (com números)
4. Proposta de valor única
5. Fechamento confiante com call-to-action
Máx 4 parágrafos. 1ª pessoa."""
    return _groq(key, sys, usr, 1000, 0.6)

# ── 6. LinkedIn ──
def optimize_linkedin(cv, ats, key):
    sys = """
    Você é um especialista em LinkedIn, personal branding e recrutamento tech no Brasil.
    Responda SOMENTE com JSON válido.
    Não use markdown.
    Não use ```json.
    Não escreva explicações fora do JSON.
    """
    usr = f"""Gere otimizações LinkedIn.
CV: {cv[:3000]}
Nível: {ats.get('nivel_perfil','')} | Cargos: {', '.join(ats.get('cargos_ideais',[])[:3])}

JSON:
{{
  "headline":"<até 120 chars>",
  "headline_alternativas":["alt1","alt2"],
  "about":"<seção Sobre completa, 3 parágrafos, máx 2600 chars>",
  "skills_top10":["s1","s2","s3","s4","s5","s6","s7","s8","s9","s10"],
  "palavras_chave_seo":["k1","k2","k3","k4","k5"],
  "dicas_perfil":["d1","d2","d3","d4"],
  "score_estimado":<0-100>,
  "url_sugestao":"<slug>"
}}"""
    raw = _groq(key, sys, usr, 2000)
    r = _json(raw)
    return r if r else {
        "error": "Falha ao converter resposta da IA em JSON",
        "raw": raw[:1500]
    }

# ── 7. Interview Prep ──
def gen_interview_prep(cv, title, company, desc, key):
    sys = """
    Você é um especialista em entrevistas técnicas e comportamentais para o mercado brasileiro.
    Responda SOMENTE com JSON válido.
    Não use markdown.
    Não use ```json.
    Não escreva nenhuma explicação fora do JSON.
    """
    usr = f"""Gere preparação completa para entrevista.
VAGA: {title} — {company}
DESC: {desc[:1500]}
CV: {cv[:2500]}

JSON:
{{
  "perguntas_rh":[
    {{"pergunta":"...","dica":"...","armadilha":"..."}},
    {{"pergunta":"...","dica":"...","armadilha":"..."}},
    {{"pergunta":"...","dica":"...","armadilha":"..."}},
    {{"pergunta":"...","dica":"...","armadilha":"..."}},
    {{"pergunta":"...","dica":"...","armadilha":"..."}}
  ],
  "perguntas_tecnicas":[
    {{"pergunta":"...","contexto":"...","nivel":"..."}},
    {{"pergunta":"...","contexto":"...","nivel":"..."}},
    {{"pergunta":"...","contexto":"...","nivel":"..."}},
    {{"pergunta":"...","contexto":"...","nivel":"..."}}
  ],
  "fraqueza_sugerida":"...",
  "pretensao_dica":"...",
  "perguntas_para_empresa":["p1","p2","p3"],
  "red_flags":["r1","r2","r3"],
  "dica_geral":"..."
}}"""
    raw = _groq(key, sys, usr, 2500)
    r = _json(raw)
    return r if r else {
        "error": "Falha ao converter resposta da IA em JSON",
        "raw": raw[:1500]
    }

# ── 8. Career Diagnosis ──
def career_diagnosis(cv, ats, target_role, key):
    sys = "Career coach sênior especialista no mercado brasileiro de tecnologia. APENAS JSON válido."
    usr = f"""Faça diagnóstico completo de carreira.
CV: {cv[:3000]}
Score ATS: {ats.get('score_geral',0)}
Nível: {ats.get('nivel_perfil','')}
Gap skills: {', '.join(ats.get('gap_skills',[]))}
Cargo alvo: {target_role}

JSON:
{{
  "score_empregabilidade":<0-100>,
  "posicao_mercado":"<como este profissional está posicionado vs mercado BR>",
  "meses_para_senior":<estimativa>,
  "gap_para_proximo_nivel":["gap1","gap2","gap3"],
  "plano_desenvolvimento":[
    {{"acao":"...","prazo":"...","impacto":"Alto|Médio|Baixo","recurso":"..."}},
    {{"acao":"...","prazo":"...","impacto":"Alto|Médio|Baixo","recurso":"..."}},
    {{"acao":"...","prazo":"...","impacto":"Alto|Médio|Baixo","recurso":"..."}},
    {{"acao":"...","prazo":"...","impacto":"Alto|Médio|Baixo","recurso":"..."}}
  ],
  "certificacoes_recomendadas":["cert1","cert2","cert3"],
  "cursos_gratuitos":["curso1","curso2","curso3"],
  "salario_atual_mercado":"R$X.XXX – R$Y.YYY",
  "salario_senior_mercado":"R$X.XXX – R$Y.YYY",
  "dica_aceleracao":"<conselho único e personalizado de 2 linhas>"
}}"""
    raw = _groq(key, sys, usr, 2000)
    r = _json(raw)
    return r if r else {"error":"Falha","score_empregabilidade":0}

# ── 9. Market Intelligence ──
def market_intelligence(cargo, cidade, nivel, key):
    sys = "Analista de mercado de trabalho brasileiro especialista em dados salariais e tendências. APENAS JSON válido."
    usr = f"""Gere inteligência de mercado para: {cargo} | {cidade} | {nivel}

JSON:
{{
  "demanda_atual":"<Alta|Média|Baixa>",
  "tendencia":"<Crescendo|Estável|Diminuindo>",
  "salario_minimo":"R$X.XXX",
  "salario_mediano":"R$X.XXX",
  "salario_maximo":"R$X.XXX",
  "empresas_contratando":["emp1","emp2","emp3","emp4","emp5"],
  "setores_demandantes":["setor1","setor2","setor3"],
  "skills_mais_pedidas":["skill1","skill2","skill3","skill4","skill5"],
  "skills_emergentes":["skill1","skill2","skill3"],
  "modalidades":{{"presencial":<pct>,"hibrido":<pct>,"remoto":<pct>}},
  "insight":"<observação única sobre o mercado para este perfil>",
  "melhor_momento_candidatura":"<quando e como maximizar chances>"
}}"""
    raw = _groq(key, sys, usr, 1500)
    r = _json(raw)
    return r if r else {"error":"Falha"}

# ── 10. Networking Email ──
def gen_networking_email(cv, target_company, target_role, contact_name, key):
    sys = "Especialista em networking e outreach profissional para o mercado brasileiro. Tom: direto, humano, não-corporativo."
    usr = f"""Escreva email de networking para pedido de indicação/conversa.
MINHA ÁREA: {cv[:1500]}
EMPRESA ALVO: {target_company}
CARGO DESEJADO: {target_role}
CONTATO: {contact_name or 'profissional da empresa'}

Regras:
- Assunto: curto e que gera curiosidade (não genérico)
- Corpo: máx 5 linhas
- Mencione algo específico da empresa
- Peça 15 minutos de conversa, não o emprego
- Tom humano e direto
- Termine com pergunta específica

Formato: ASSUNTO: [assunto]\n\n[corpo do email]"""
    return _groq(key, sys, usr, 500, 0.7)

# ── 11. Job Search Terms ──
def get_search_terms(cv, ats, key):
    sys = "Headhunter especialista no mercado brasileiro. APENAS JSON válido."
    usr = f"""Gere termos de busca otimizados.
Cargos: {ats.get('cargos_ideais',[])}
Nível: {ats.get('nivel_perfil','')}
CV: {cv[:1500]}

JSON:
{{
  "termos_busca":[
    {{"termo":"...","nivel":"...","variacoes":["v1","v2"]}},
    {{"termo":"...","nivel":"...","variacoes":["v1","v2"]}},
    {{"termo":"...","nivel":"...","variacoes":["v1","v2"]}}
  ],
  "keywords_tecnicas":["k1","k2","k3","k4"],
  "areas_recomendadas":["a1","a2","a3"],
  "dica":"..."
}}"""
    raw = _groq(key, sys, usr, 800)
    r = _json(raw)
    return r if r else {"termos_busca":[{"termo":t,"nivel":"Pleno","variacoes":[]} for t in ats.get("cargos_ideais",[])[:3]]}
