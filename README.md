# Applymize

Sistema de inteligência de carreira: importa vagas de múltiplas fontes, avalia compatibilidade real com o perfil do candidato, analisa o currículo como um ATS faria, e automatiza o acompanhamento das candidaturas.

Construído como projeto autoral, full-stack: **FastAPI + PostgreSQL** no backend, **React (Vite)** no frontend, orquestrado com **Docker Compose**.

## O problema que resolve

Buscar vaga manualmente em múltiplos sites tem três fricções: (1) a mesma vaga aparece repetida em fontes diferentes, (2) vagas fora do seu perfil (localização, senioridade, requisitos que você não atende) misturadas com as relevantes, e (3) nenhum feedback real de por que um currículo não passa de triagem automática. O Applymize automatiza as três etapas: ingestão + deduplicação, filtro de elegibilidade, e análise ATS do currículo contra a vaga.

## Principais módulos

- **Ingestão multi-provider** — RemoteOK, Gupy, Vagas.com, JobSpy, LinkedIn e InfoJobs, com deduplicação entre fontes e execuções (`provider_runs`, retry/backoff, logs estruturados)
- **Filtro de elegibilidade** — bloqueia vagas fora do perfil (localização, escolaridade exigida vs. em andamento, senioridade) antes de chegar ao candidato
- **Matching Engine** — score de compatibilidade vaga × perfil
- **ATS/RH Analyzer** — nota de estrutura, palavras-chave, clareza e senioridade do currículo, com e sem uma vaga específica
- **Application Agent** — fila de candidaturas assistida, com limite diário configurável
- **Notification Center** — alertas de vagas de alta prioridade via WhatsApp (Evolution API) ou Telegram
- **Cover Letter / Follow-up Engine** — geração de mensagens de candidatura e acompanhamento
- **Skill Gap Roadmap** — compara perfil × vagas e prioriza lacunas de skill

## Engenharia — bugs reais corrigidos com teste de regressão

Esse projeto não parou no "funciona na demo". Alguns problemas encontrados em uso real e corrigidos:

- **Deduplicação falha entre execuções** — o fallback de dedup por título+empresa exigia URL idêntica, o que o tornava inalcançável na prática (URL igual já era pega antes). Vagas re-scrapeadas com URL diferente passavam como novas.
- **Filtro de vagas fora do Brasil desativado silenciosamente** — a lógica de bloqueio de vagas estrangeiras do LinkedIn existia no código, mas retornava lista vazia sempre.
- **Filtro de escolaridade bloqueando quem está cursando** — a lista de frases reconhecidas como "exige diploma completo" era estreita demais, e não distinguia "completo obrigatório" de "completo ou cursando".

Os três têm teste de regressão em `tests/test_job_eligibility_filter.py` e `tests/test_job_ingestion_dedup.py`.

## Rodando localmente

```bash
cp .env.example .env
docker compose up -d --build
```

```text
Frontend: http://localhost:5173
API Docs: http://localhost:8001/docs
Health:   http://localhost:8001/health
```

Seed de demonstração e detalhes operacionais completos (providers, WhatsApp, notificações, troubleshooting): ver [`SETUP.md`](SETUP.md).

Os containers usam `restart: unless-stopped`. Depois da primeira execução, eles voltam automaticamente quando o Docker Desktop inicia, desde que não tenham sido removidos com `docker compose down`.
No Windows, deixe habilitada também a opção do Docker Desktop para iniciar junto com o sistema.

## Testes

```bash
docker compose exec api pytest -q
```

## Stack

Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic · Redis · React · Vite · Docker Compose

## Escopo de prontidão

O ambiente Docker está preparado para uso local contínuo e demonstração funcional. A camada comercial ainda não deve ser tratada como cobrança real: sem Stripe, o checkout é demonstrativo; com as chaves atuais, a criação de sessão e o webhook ainda precisam ser implementados. Para exposição pública também faltam proxy HTTPS, política de backup, monitoramento externo e uma imagem estática de produção para o frontend.

O produto atual é FastAPI + React. O código Streamlit em `app.py`, `run.py`, `core/`, `automation/`, `intelligence/` e `legacy/` é legado e não participa do Docker Compose.
