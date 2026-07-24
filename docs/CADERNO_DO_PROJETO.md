# Caderno do Projeto — Applymize

> Fonte de memória permanente para desenvolvimento, auditorias e futuras conversas.

**Última atualização:** 24 de julho de 2026  
**Branch principal:** `main`  
**Último commit funcional registrado:** `eb16c60`  
**Natureza do projeto:** portfólio full-stack e ferramenta de uso pessoal  

## 1. O que é o Applymize

O Applymize é um projeto autoral de inteligência de carreira. Ele foi criado para resolver problemas vividos no uso pessoal:

- buscar oportunidades em vários sites;
- eliminar vagas duplicadas;
- evitar resultados incompatíveis com o cargo desejado;
- entender a aderência entre currículo e vaga;
- acompanhar candidaturas;
- receber alertas pessoais pelo WhatsApp.

O projeto não está sendo tratado como SaaS comercial. O frontend público existe para portfólio e demonstração a recrutadores. O backend completo permanece voltado ao ambiente pessoal/local.

## 2. Regra de apresentação do portfólio

A comunicação pública deve sempre distinguir:

- **real:** algo que executa regras ou integrações implementadas;
- **local:** algo que roda inteiramente no navegador;
- **privado:** algo que depende de login e backend;
- **demonstração:** interface com dados ilustrativos;
- **roadmap:** ideia ainda não implementada.

Não apresentar demonstração como funcionalidade real. Não sugerir que uma URL do LinkedIn é lida quando o conteúdo não é coletado.

## 3. Arquitetura atual

```text
Frontend React/Vite
        ↓
API FastAPI
        ↓
PostgreSQL + Redis
        ↓
Providers, workers, scheduler e Evolution API
```

### Componentes ativos

- `frontend/`: produto React, páginas públicas e dashboard autenticado.
- `backend/`: API, autenticação, modelos, filtros, matching e integrações.
- `migrations/`: histórico Alembic do banco.
- `tests/`: regressão e comportamento do backend.
- `scripts/`: seed e utilitários operacionais.
- `docker-compose.yml`: ambiente local principal.

### Componentes legados

O protótipo Streamlit foi preservado em `app.py`, `run.py`, `core/`, `automation/`, `intelligence/` e `legacy/`. Ele não representa a aplicação atual em Docker Compose.

## 4. Experiência pública do portfólio

### `/`

Landing page do projeto. Apresenta recursos, proposta e links para as experiências públicas.

### `/como-funciona`

Explica para uma pessoa recrutadora:

1. entrada do currículo e objetivo;
2. descoberta multi-provider;
3. normalização e deduplicação;
4. filtros de relevância e elegibilidade;
5. matching e ATS;
6. automação e alertas.

A página também informa o que é funcional, local, demonstrativo e futuro.

### `/laboratorio-ats`

Experimento público real sem login e sem backend.

Aceita:

- PDF;
- DOCX;
- TXT;
- texto colado.

Analisa:

- estrutura ATS;
- leitura de RH;
- aderência ao cargo ou vaga;
- palavras-chave;
- experiência;
- clareza;
- senioridade.

O arquivo é lido na memória do navegador. O resultado oferece uma prévia de WhatsApp e um link `wa.me`; nenhuma mensagem é enviada automaticamente.

Arquivos principais:

- `frontend/src/pages/PublicAtsLab.tsx`
- `frontend/src/services/browserDocument.ts`
- `frontend/src/services/publicAtsEngine.ts`

### `/linkedin-analyzer`

Showcase público com dados ilustrativos e comunicação transparente.

Na área privada:

- foi removido o campo que sugeria análise direta por URL;
- o usuário pode importar PDF, DOCX ou TXT;
- também pode colar o conteúdo do perfil;
- o texto fornecido é analisado pelo endpoint autenticado.

O projeto não faz scraping de perfis do LinkedIn.

## 5. Descoberta e relevância de vagas

### Problema encontrado

Ao configurar **Automação de Processos**, o sistema retornava principalmente vagas de Analista de Dados em diferentes senioridades.

### Causas identificadas

- termos amplos demais na ingestão;
- falta de uma camada explícita de relevância por família profissional;
- automação podendo continuar com termos antigos;
- rankings e métricas contando vagas ingeridas, mesmo quando incompatíveis.

### Correção implementada

- termos de busca derivados do cargo alvo do usuário;
- persistência do termo usado em cada execução;
- serviço `backend/services/job_role_relevance.py`;
- famílias profissionais e sinais positivos/negativos;
- filtro aplicado em listagem, matching, estratégia, analytics, dashboard, recruiter e automação;
- opção de termo explícito na automação;
- migration `0020_automation_role_search.py`;
- testes de regressão em `tests/test_job_role_relevance.py`.

Commit principal: `389c468 fix: personalize job discovery and relevance`.

## 6. ATS: diferença entre público e privado

### ATS público

- TypeScript;
- executado no navegador;
- determinístico e explicável;
- não usa IA generativa;
- não envia currículo;
- adequado para demonstração de portfólio;
- não afirma reproduzir todos os ATS comerciais.

### ATS privado

- executado no backend;
- usa currículo e perfil persistidos;
- pode comparar com vagas existentes no banco;
- retorna score ATS, RH, match, keywords, experiência, clareza e senioridade.

Arquivo principal: `backend/services/ats_analyzer.py`.

## 7. WhatsApp

### Experiência pública

Somente prévia e abertura de mensagem preenchida via `wa.me`.

### Ambiente privado

Integração pessoal pela Evolution API:

- sessão por usuário;
- QR Code;
- status de conexão;
- teste de envio;
- alertas relevantes;
- deduplicação e limites.

Segredos da Evolution ficam somente no backend.

## 8. Netlify

O frontend público está preparado pelo `netlify.toml`:

- base `frontend`;
- comando `npm run build`;
- publicação `dist`;
- Node 22;
- rewrite `/* → /index.html`;
- headers básicos.

As páginas públicas funcionam sem backend.

Para usar login e recursos privados em uma hospedagem pública, seria necessário configurar `VITE_API_BASE_URL`. Isso não é necessário para o objetivo atual de portfólio.

Commit principal: `eb16c60 feat: add public ATS lab and product architecture`.

## 9. Validação mais recente

Estado validado em 24 de julho de 2026:

- 123 testes de backend aprovados;
- frontend TypeScript/lint aprovado;
- build Vite de produção aprovado;
- `npm audit` com zero vulnerabilidades conhecidas;
- rotas `/`, `/como-funciona`, `/laboratorio-ats` e `/linkedin-analyzer` respondendo diretamente;
- responsividade mobile inspecionada;
- fluxo “Usar exemplo → Analisar agora” validado;
- exemplo de Automação de Processos retornando score ATS coerente;
- importação e extração de PDF testadas no navegador.

## 10. Histórico consolidado

### `dc8d11b` — baseline auditado

- consolidação do produto FastAPI + React;
- auditoria full-stack;
- documentação e testes;
- ambiente Docker validado.

### `389c468` — relevância personalizada

- busca orientada ao cargo;
- filtro por família profissional;
- propagação para dashboard, matching e automação;
- correção do caso Automação de Processos;
- testes adicionais.

### `eb16c60` — portfólio público

- configuração Netlify;
- página Como funciona;
- laboratório ATS local;
- PDF/DOCX/TXT no navegador;
- prévia de WhatsApp;
- LinkedIn sem promessa falsa de scraping;
- atualização de segurança do React Router.

## 11. Decisões já tomadas

- O projeto é portfólio e ferramenta pessoal, não SaaS comercial.
- Não expor o backend pessoal apenas para tornar a demonstração pública.
- Priorizar transparência sobre recursos reais e mockados.
- Manter o laboratório ATS inteiramente no navegador.
- Não implementar scraping de URL do LinkedIn.
- Manter a integração real de WhatsApp restrita ao ambiente privado.
- Preservar o código legado, mas deixar explícito que não é o produto atual.
- Não incluir `docs/prints-sistema/` em commits sem solicitação explícita do proprietário.

## 12. Limitações conhecidas

- A demo geral ainda contém dados visuais estáticos identificados como mock.
- Login e dashboard privado não funcionam em um Netlify exclusivamente estático sem backend configurado.
- O ATS público usa heurísticas próprias e não representa todos os fornecedores de ATS.
- PDF com texto convertido em imagem pode exigir OCR, que não está implementado no navegador.
- Checkout e billing não processam pagamentos reais.
- O painel Recruiter privado é demonstrativo e não é um ATS empresarial.
- O build contém chunks grandes dos leitores PDF/DOCX, carregados sob demanda.

## 13. Próximos passos opcionais

Somente executar se houver pedido do proprietário:

1. confirmar visualmente o deploy final do Netlify;
2. adicionar URL pública e screenshots ao README;
3. otimizar code splitting do frontend;
4. ampliar o dicionário de cargos/famílias após novos casos reais;
5. criar testes automatizados do motor ATS público;
6. atualizar este caderno após novas mudanças materiais.

## 14. Procedimento para futuras sessões

Antes de alterar o projeto:

1. ler este caderno por inteiro;
2. ler o README;
3. executar `git status --short`;
4. verificar os commits recentes;
5. preservar arquivos não relacionados e alterações do usuário;
6. confirmar se o pedido é sobre portfólio público ou ambiente privado.

Depois de uma mudança material:

1. atualizar a seção correspondente deste caderno;
2. registrar a data e o commit quando houver;
3. atualizar o README se o visitante do portfólio precisar conhecer a mudança;
4. executar validações proporcionais ao risco;
5. não adicionar `docs/prints-sistema/` automaticamente.

## 15. Referências rápidas

- Visão pública: `README.md`
- Operação local: `SETUP.md`
- Auditoria anterior: `docs/AUDIT_2026-07-15.md`
- Rotas frontend: `frontend/src/App.tsx`
- Elegibilidade: `backend/services/job_eligibility_filter.py`
- Relevância por cargo: `backend/services/job_role_relevance.py`
- Ingestão: `backend/services/job_ingestion.py`
- ATS privado: `backend/services/ats_analyzer.py`
- ATS público: `frontend/src/services/publicAtsEngine.ts`
- Automação: `backend/services/automation_scheduler.py`
- Netlify: `netlify.toml`

