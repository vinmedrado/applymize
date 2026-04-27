# 🚀 Applymize — Plataforma Inteligente de Empregabilidade

## 📌 Visão Geral
O **Applymize** é uma plataforma inteligente que combina **IA + Engenharia de Dados + Scraping** para ajudar usuários a:

- 📄 Analisar currículos (ATS realista)
- 🎯 Medir compatibilidade com vagas
- 🔎 Buscar vagas automaticamente
- 📊 Priorizar oportunidades com inteligência
- 💾 Salvar perfil do usuário (currículo persistente)

---

## 🧠 Principais Funcionalidades

### 🎯 Análise ATS (nível profissional)
- Score geral (0–100)
- Avaliação detalhada:
  - Formatação
  - Palavras-chave
  - Experiência relevante
  - Resultados
  - Completude
- Veredicto de RH
- Score de empregabilidade

---

### 🤖 Match Inteligente com Vagas
- Compatibilidade real (sem invenção de dados)
- Requisitos atendidos / faltantes
- Ajustes rápidos no CV
- Probabilidade de entrevista
- Experiência relevante específica da vaga

---

### 📊 Parser de Experiência (diferencial)
- Detecta datas automaticamente no CV
- Calcula anos reais de experiência
- Remove sobreposição de períodos
- Não depende de IA (mais preciso)

---

### 🔎 Sistema de Busca de Vagas
- Integra múltiplas fontes:
  - Gupy
  - Vagas.com
  - Catho
  - InfoJobs
  - Indeed (limitado)
- Normalização de dados
- Deduplicação
- Enriquecimento de descrição
- Filtro por localização

---

### 🧠 Score Inteligente de Vagas
Cada vaga recebe:

- `match_score` → compatibilidade com o usuário
- `quality_score` → qualidade da vaga
- `ghost_score` → risco de vaga fake/baixa qualidade

---

### 🧪 Ghost Job Detector
Detecta vagas suspeitas:

- Empresa oculta
- Descrição genérica
- Linguagem vaga
- Vagas antigas
- Padrões suspeitos

---

### 💾 Persistência de Currículo (UX profissional)
- Upload feito **uma única vez**
- Salvo localmente
- Recarregado automaticamente
- Opção de atualizar

---

### ⚡ Otimização de IA
- Limite de chamadas (custo controlado)
- Cache possível
- Fallback para rate limit
- Redução de tokens

---

## 🏗️ Arquitetura

```
APPLYMIZE/
│
├── app.py
├── run.py
├── requirements.txt
├── README.md
│
├── automation/
│   ├── __init__.py
│   └── auto_apply.py
│
├── core/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── auth.py
│   ├── cv_exporter.py
│   ├── cv_parser.py
│   ├── experience.py
│   └── profile_store.py
│
├── intelligence/
│   ├── __init__.py
│   └── engine.py
│
└── scrapers/
    ├── __init__.py
    └── scrapers.py
```

---

## ⚙️ Tecnologias

- Python
- Streamlit
- BeautifulSoup
- Requests
- Selenium (opcional)
- Groq API (LLM)
- JSON / Regex

---

## 🚀 Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔑 Configuração

Defina sua API key:

```bash
GROQ_API_KEY=your_key_here
```

---

## ⚠️ Limitações

- Scraping pode falhar por bloqueio dos sites
- LinkedIn não é confiável sem login
- Rate limit da IA pode ocorrer
- Algumas vagas não possuem descrição completa

---

## 🧠 Roadmap

- [ ] Ranking automático de vagas
- [ ] Engine de decisão (aplicar ou não)
- [ ] Histórico do usuário
- [ ] Dashboard de carreira
- [ ] Multi-IA fallback
- [ ] API própria

---

## 🏆 Diferenciais

- IA controlada (não inventa dados)
- Parser próprio de experiência
- Sistema híbrido (IA + regras)
- Foco em empregabilidade real
- Arquitetura pronta para escalar

---

## 👨‍💻 Autor

**Vinicius Medrado**  
Analista de Dados & Automação  

---

## ⚡ Frase do projeto

> Isso não é só um analisador de currículo.  
> É um motor de decisão de carreira.

---

## 🔥 Status

🟢 Em evolução — já funcional e pronto para portfólio

