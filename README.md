# Applymize

Plataforma autoral de inteligência de carreira criada como **portfólio full-stack e ferramenta de uso pessoal**.

O projeto reúne descoberta de vagas, filtro de relevância, matching, análise ATS, acompanhamento de candidaturas, automações e alertas em uma experiência construída com **FastAPI, PostgreSQL, React, Vite e Docker Compose**.

## O que o portfólio demonstra

- Engenharia de produto aplicada a um problema real.
- Backend multi-tenant com autenticação, migrations e serviços especializados.
- Ingestão de vagas em múltiplos provedores.
- Regras explicáveis de relevância, elegibilidade e matching.
- Processamento de currículo em PDF, DOCX e TXT.
- Interface responsiva com área autenticada privada e demonstração pública interativa.
- Automação agendada e integração pessoal com WhatsApp.
- Testes de regressão para problemas encontrados em uso real.

O frontend público foi desenhado para permitir que uma pessoa recrutadora navegue pelos principais fluxos, execute ações de teste e entenda a arquitetura sem precisar acessar o ambiente privado.

## Experiência pública

| Rota | Finalidade |
|---|---|
| `/` | Apresentação do projeto e dos recursos |
| `/como-funciona` | Arquitetura, pipeline, decisões, limites e evidências no código |
| `/laboratorio-ats` | Experimento ATS real executado no navegador |
| `/linkedin-analyzer` | Demonstração transparente da análise de LinkedIn |
| `/demo` | Produto interativo com vagas, matching, candidaturas, ATS, perfil e automações |

A demo usa dados ilustrativos e estado temporário no navegador. Busca, salvar vaga, candidatura, avanço de pipeline, otimização de perfil e controles de automação podem ser testados sem login ou backend.

O laboratório ATS aceita PDF, DOCX, TXT ou texto colado, compara o currículo com um cargo ou uma vaga e apresenta estrutura, clareza, experiência, senioridade, palavras-chave e aderência. Todo o processamento dessa página acontece localmente no navegador.

## Como o sistema funciona

```text
Currículo + objetivo profissional
                ↓
     Descoberta multi-provider
                ↓
      Normalização e deduplicação
                ↓
Relevância por cargo + elegibilidade
                ↓
      Matching e análise ATS/RH
                ↓
 Dashboard, candidaturas e alertas
```

### Descoberta e relevância de vagas

O cargo alvo de cada usuário gera termos de busca próprios. Depois da ingestão, o sistema valida família profissional, título, senioridade, modalidade e localização antes de exibir ou notificar uma oportunidade.

Isso evita, por exemplo, que uma busca por **Automação de Processos** seja preenchida principalmente por vagas genéricas de **Analista de Dados**.

Cada execução preserva o provedor e o termo que originou a descoberta para facilitar auditoria e explicação.

### Principais módulos

- **Ingestão multi-provider** — RemoteOK, Gupy, Vagas.com, JobSpy, LinkedIn e InfoJobs.
- **Deduplicação** — evita repetição entre provedores e novas execuções.
- **Filtro de relevância** — valida cargo e família profissional.
- **Filtro de elegibilidade** — localização, escolaridade, senioridade e requisitos.
- **Matching Engine** — score de compatibilidade entre vaga e perfil.
- **ATS/RH Analyzer** — estrutura, palavras-chave, clareza, experiência e senioridade.
- **Application Agent** — fila assistida de candidaturas.
- **Notification Center** — alertas pessoais por WhatsApp ou Telegram.
- **Cover Letter e Follow-up** — mensagens de candidatura e acompanhamento.
- **Skill Gap Roadmap** — lacunas de competência priorizadas.

## Transparência: real, demonstração e privado

- O **laboratório ATS público** é real, determinístico e processado localmente.
- A página **Por trás do projeto** representa o pipeline implementado e leva às evidências no repositório.
- A **demo interativa** utiliza dados ilustrativos, identificados na tela e descartados ao recarregar.
- A **área autenticada** depende do backend local e do banco de dados.
- Login, cadastro e recuperação de senha publicados exibem um aviso de ambiente privado e levam à demo.
- O LinkedIn **não é coletado por scraping de URL**. O usuário fornece PDF, DOCX, TXT ou texto.
- O botão público de WhatsApp abre uma mensagem preenchida; não envia nada automaticamente.

## Rodando localmente

```bash
cp .env.example .env
docker compose up -d --build
```

No Windows PowerShell:

```powershell
copy .env.example .env
docker compose up -d --build
```

```text
Frontend: http://localhost:5173
API Docs: http://localhost:8001/docs
Health:   http://localhost:8001/health
```

Os containers usam `restart: unless-stopped`. Depois da primeira execução, voltam com o Docker Desktop desde que não tenham sido removidos com `docker compose down`.

Instruções operacionais completas estão em [`SETUP.md`](SETUP.md).

## Frontend público no Netlify

O arquivo [`netlify.toml`](netlify.toml) configura:

- diretório base `frontend`;
- build `npm run build`;
- publicação de `frontend/dist`;
- fallback SPA para rotas diretas;
- Node.js 22;
- headers básicos de segurança.

As páginas públicas não precisam do backend. O deploy de portfólio não deve receber `VITE_API_BASE_URL`; assim, acessos diretos às rotas de autenticação mostram a alternativa segura da demo.

Para uma instalação privada que também hospede o backend, configure:

```env
VITE_API_BASE_URL=https://endereco-https-do-backend
```

## Validação

```bash
docker compose exec api pytest -q
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
```

Na validação mais recente:

- 123 testes de backend aprovados;
- TypeScript/lint aprovado;
- build de produção aprovado;
- PostCSS atualizado para corrigir a vulnerabilidade de leitura de source map;
- auditoria npm registra duas ocorrências altas no React Router, ligadas ao modo RSC não utilizado por esta SPA;
- upload e extração de PDF validados no navegador;
- rotas públicas e responsividade validadas em Chrome headless.

## Bugs reais corrigidos

- Deduplicação entre execuções com URLs diferentes.
- Bloqueio de vagas estrangeiras que estava desativado silenciosamente.
- Escolaridade em andamento interpretada incorretamente como inelegível.
- Buscas genéricas retornando famílias profissionais incompatíveis.
- Automação reutilizando termos antigos em vez do cargo alvo atual.
- Rankings e métricas contando vagas irrelevantes.

Os testes principais dessas regras estão em:

- `tests/test_job_eligibility_filter.py`
- `tests/test_job_ingestion_dedup.py`
- `tests/test_job_role_relevance.py`

## Stack

Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic · Redis · React · TypeScript · Vite · Tailwind CSS · Docker Compose · Evolution API

## Estrutura do repositório

```text
backend/       API, modelos, regras e integrações
frontend/      aplicação React e experiência pública
migrations/    migrations Alembic
tests/         testes automatizados
scripts/       seed e utilitários operacionais
docs/          auditorias, decisões e caderno do projeto
legacy/        protótipo Streamlit preservado
```

O produto atual é FastAPI + React. `app.py`, `run.py`, `core/`, `automation/`, `intelligence/` e parte de `legacy/` pertencem ao protótipo anterior e não participam do Docker Compose atual.

## Memória e continuidade

O estado consolidado, decisões, histórico recente e instruções para futuras sessões ficam em [`docs/CADERNO_DO_PROJETO.md`](docs/CADERNO_DO_PROJETO.md).
