# Setup e operação — Applymize

Documentação operacional completa. Para visão geral do projeto, ver o [README](README.md).

## Subir localmente

```bash
cp .env.example .env
docker compose up -d --build
```

Windows PowerShell:

```powershell
copy .env.example .env
docker compose up -d --build
```

Acessos:

```text
Frontend: http://localhost:5173
API Docs: http://localhost:8001/docs
Health:   http://localhost:8001/health
```

> O frontend detecta o hostname atual e usa a API na porta `8001`. Para sobrescrever esse comportamento, configure `VITE_API_BASE_URL`.

Os serviços usam `restart: unless-stopped`; depois desta primeira execução, iniciam com o Docker Desktop. Não use `docker compose down` se quiser preservar os containers para inicialização automática.

## Seed de demonstração

```bash
docker compose exec api python scripts/dev_seed.py
```

Login:

```text
demo@example.com
Demo123!
```

Cria tenant, usuário, perfil completo, skills, experiências, projetos, educação, currículo textual, vagas e candidaturas demo.

## Checklist manual de validação

1. Login no frontend.
2. Abrir `Meu Perfil` — conferir perfil demo e preview do currículo.
3. Importar vagas em `Vagas`.
4. Gerar score/matching.
5. Gerar CV ATS.
6. Gerar entrevista.
7. Conferir recomendações no Dashboard.
8. Abrir `Application Agent` — criar fila, aprovar, pular ou marcar como aplicada.

## Testes

```bash
docker compose exec api pytest -q
```

Suítes principais:

```bash
docker compose exec api pytest -q tests/test_final_refinement.py
docker compose exec api pytest -q tests/test_profile_resume_engine.py
docker compose exec api pytest -q tests/test_application_agent.py
docker compose exec api pytest -q tests/test_strategy_engine.py
docker compose exec api pytest -q tests/test_job_eligibility_filter.py
docker compose exec api pytest -q tests/test_job_ingestion_dedup.py
```

---

## Currículo

Tela: `http://localhost:5173/profile`

Formatos aceitos: PDF, DOCX, TXT.

O parser extrai: nome, email, telefone, LinkedIn, GitHub, skills técnicas, experiências, projetos, educação, idiomas, certificações.

## Providers de vagas

```bash
curl -X POST "http://localhost:8001/api/jobs/ingest?provider=remoteok&limit=25" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X POST "http://localhost:8001/api/jobs/ingest?provider=gupy&term=Analista%20de%20dados&state=São%20Paulo&city=Santo%20André&workplace_types=remote,hybrid&limit=25" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X POST "http://localhost:8001/api/jobs/ingest?provider=vagas&term=Analista%20de%20dados" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Filtros opcionais do provider Gupy: `term`, `state`, `city`, `workplace_types`, `limit`. Sem filtros, a busca é geral.

A ingestão registra cada execução em `provider_runs`, com retry/backoff, logs estruturados e deduplicação (ver README para o histórico do bug de dedup corrigido).

## Strategy Engine

```text
GET /api/strategy/recommendations
```

Retorna `strategy_score`, `priority`, `explanation` e `factors`.

## Application Agent

Tela: `http://localhost:5173/application-agent`

Config (`.env`):

```text
APPLICATION_AGENT_DAILY_LIMIT=10
APPLICATION_AGENT_MIN_PROFILE_COMPLETENESS=35
```

## ATS/RH Analyzer

Tela: `http://localhost:5173/ats-analyzer`

Endpoints:

```text
GET /api/ats/analyze-me
GET /api/ats/analyze-job/{job_id}
```

Scores retornados: ATS Score, RH Score, Match Score, Keyword Score, Experience Score, Clarity Score, Seniority Score. Grades de `A+` a `F`.

Uso recomendado:

1. Complete `Meu Perfil`.
2. Faça upload do currículo.
3. Clique em `Analisar meu currículo`.
4. Para uma vaga específica, selecione a vaga e clique em `Analisar contra vaga`.
5. Aplique os ajustes de prioridade alta antes de se candidatar.

## Link da vaga

O sistema mantém `job.url` em todas as vagas quando o provider disponibiliza o link original. Lista de vagas, detalhe da vaga e Application Agent exibem botão para abrir a vaga original; se não houver URL, o botão fica desabilitado com aviso `Link não disponível`.

## Notification Center

Envio automático fica desativado por padrão.

`.env`:

```text
NOTIFICATIONS_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EVOLUTION_API_URL=
EVOLUTION_API_KEY=
EVOLUTION_INSTANCE_ID=
NOTIFICATION_MAX_PER_RUN=5
NOTIFICATION_MIN_PRIORITY=HIGH
```

Tela: `http://localhost:5173/notifications`

Endpoints:

```text
GET  /api/notifications/settings
POST /api/notifications/test
POST /api/notifications/send-high-priority
```

Regras: o envio é manual enquanto o scheduler estiver desativado. Com `AUTOMATION_SCHEDULER_ENABLED=true` e automação habilitada pelo usuário, pode haver envio automático; continuam válidos prioridade mínima, limite por execução e deduplicação por canal.

## WhatsApp / Pareamento (Evolution API)

Tela: `http://localhost:5173/whatsapp-pairing`

O WhatsApp é multi-tenant: cada usuário tem sua própria sessão (`whatsapp_sessions`).

Rotas:

```text
GET    /api/whatsapp/session
POST   /api/whatsapp/session
POST   /api/whatsapp/session/connect
GET    /api/whatsapp/session/qrcode
GET    /api/whatsapp/session/status
POST   /api/whatsapp/session/test
POST   /api/whatsapp/session/disconnect
DELETE /api/whatsapp/session
```

Configuração `.env`:

```text
EVOLUTION_API_URL=http://evolution:8080
EVOLUTION_API_KEY=applymize_local_key
EVOLUTION_INSTANCE_PREFIX=applymize
EVOLUTION_DEFAULT_COUNTRY_CODE=55
WHATSAPP_ENABLED=true
```

A API key da Evolution fica só no backend — o frontend nunca acessa a Evolution API diretamente nem a expõe.

Fluxo:

1. Configure as variáveis acima.
2. Suba o Applymize.
3. Acesse `WhatsApp / Pareamento`.
4. Informe o telefone no formato DDI + DDD + número (ex: `5511999999999`).
5. Clique em `Criar conexão`.
6. Escaneie o QR Code.
7. Clique em `Verificar conexão`.
8. Envie mensagem teste.

Troubleshooting:

- **QR não aparece**: clique em `Atualizar QR Code` e confirme que o container `applymize_evolution` está ativo (`docker compose logs -f evolution`).
- **Evolution offline**: `docker compose up -d --build` e conferir logs.
- **Telefone inválido**: use somente números, formato `5511999999999`.
- **Instância desconectada**: clique em `Criar conexão` e escaneie o QR novamente.
- **Mensagem teste não envia**: verifique se o status está `Conectado`.

## Normalização e tradução pt-BR

O Applymize normaliza textos de vagas para manter a interface em português.

- Campos originais preservados em `title_original` / `description_original`.
- Campos `title` / `description` exibem a versão traduzida quando o texto está em inglês.
- Termos técnicos (Python, SQL, API, Docker, AWS, etc.) são protegidos e não traduzidos.
- Dicionário editável em `backend/services/translation_service.py` (`TECHNICAL_TERMS`, `PHRASE_TRANSLATIONS`, `WORD_TRANSLATIONS`).
- Fallback seguro: se a tradução falhar, usa o texto original.

Frontend: lista de vagas mostra a versão em português; detalhe da vaga tem toggle `[Português | Original]`.

## Migrations

```bash
docker compose exec api alembic upgrade head
```

No Docker, as migrations são aplicadas automaticamente antes da API iniciar.

## Limites do modo comercial atual

- Sem Stripe configurado, a troca de plano é uma simulação local e não processa pagamento.
- A integração Stripe real ainda precisa criar Checkout Sessions e validar webhooks.
- Os limites de IA são globais por configuração; ainda não há uma matriz completa de permissões por plano.
- O painel Recruiter é uma demonstração funcional sobre os dados do tenant, não um ATS empresarial completo.
- Para internet pública, adicione HTTPS/reverse proxy, backups do PostgreSQL e monitoramento externo.

## Daily Job Radar

Tela: `/radar`

```text
POST /api/radar/run
GET  /api/radar/history
```

Config:

```text
JOB_RADAR_ENABLED=false
JOB_RADAR_INTERVAL=24h
```

## Follow-up Assistant

Tela: `/applications` — gera mensagens de follow-up por candidatura e sugere próxima ação com base em status e tempo desde a última atualização.

## Cover Letter Engine

Endpoint: `GET /api/cover-letter/jobs/{job_id}` — gera mensagem curta, e-mail de candidatura, mensagem LinkedIn e follow-up.

## Analytics pessoal

Tela: `/analytics`

```text
GET /api/analytics/overview
```

## Skill Gap Roadmap

Tela: `/skill-gap`

```text
GET /api/skill-gap/roadmap
```

## Onboarding

Tutorial guiado no primeiro acesso, com status salvo por usuário no backend (tabela `user_settings`) e fallback em `localStorage` (`applymize:onboarding-tour:v1`).

```text
GET  /api/user/onboarding-status
POST /api/user/onboarding-complete
```

Reset manual (console do navegador):

```js
localStorage.removeItem("applymize:onboarding-tour:v1")
```

## Legado

O protótipo antigo em Streamlit foi movido para `legacy/streamlit_app.py`, separado do produto atual (FastAPI + React).
