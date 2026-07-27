# Caderno do Projeto — Applymize

> Fonte de memória permanente para desenvolvimento, auditorias e futuras conversas.

**Última atualização:** 27 de julho de 2026
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

A página também informa o que é funcional, local, demonstrativo e futuro. Desde 27 de julho de 2026, funciona como a área **Por trás do projeto**, com stack, decisões de arquitetura e links diretos para arquivos que comprovam a implementação.

### `/demo`

Demonstração pública interativa, sem login e sem backend.

Permite testar no navegador:

- descoberta demonstrativa de vagas;
- salvar vagas e iniciar uma candidatura;
- avançar etapas do pipeline;
- executar o motor ATS público real;
- otimizar headline e skills de um perfil ilustrativo;
- ativar, pausar e executar uma automação simulada;
- simular a conexão do canal de WhatsApp.

Os dados são explicitamente ilustrativos e o estado é descartado ao recarregar a página. A demonstração não acessa banco, contas, provedores ou integrações pessoais.

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

Site público: `https://applymize.netlify.app`

O frontend público está preparado pelo `netlify.toml`:

- base `frontend`;
- comando `npm run build`;
- publicação `dist`;
- Node 22;
- rewrite `/* → /index.html`;
- headers básicos.

As páginas públicas funcionam sem backend. No host público, rotas de login, cadastro e recuperação de senha exibem um aviso de ambiente privado com acesso à demo e à documentação técnica.

Para usar login e recursos privados em uma hospedagem pública, seria necessário configurar `VITE_API_BASE_URL`. Isso não é necessário para o objetivo atual de portfólio.

Commit principal: `eb16c60 feat: add public ATS lab and product architecture`.

Em 27 de julho de 2026:

- projeto `applymize` criado na conta pessoal Netlify;
- pasta local vinculada ao projeto;
- primeiro deploy de produção publicado e inspecionado;
- build conectado ao repositório público `vinmedrado/applymize`;
- branch de produção configurada como `main`;
- webhook GitHub ativo para `push`, `pull_request` e `delete`;
- backend e variáveis privadas não foram publicados.

## 9. Validação mais recente

Estado auditado em 27 de julho de 2026 no commit `4a92772`:

- `main` local e `origin/main` sincronizadas;
- 123 testes de backend aprovados;
- `pip check`, compilação Python e Alembic head aprovados;
- frontend TypeScript/lint aprovado com as dependências locais;
- build Vite de produção aprovado;
- rotas públicas, `/health` e `/docs` respondendo HTTP 200;
- cinco containers ativos e saudáveis;
- nenhum segredo real encontrado pelos padrões verificados no estado atual e histórico Git;
- `npm audit` encontrou 3 vulnerabilidades altas em PostCSS e React Router;
- `pip-audit` encontrou 67 ocorrências em 8 pacotes, nem todas aplicáveis à arquitetura usada;
- container frontend com volume `node_modules` antigo, embora o build limpo passe;
- zero workflows de GitHub Actions e zero testes automatizados TypeScript/TSX;
- site Applymize ainda não existe na conta Netlify autenticada e a pasta não está vinculada.

Auditoria detalhada: `docs/AUDIT_2026-07-27.md`.

Validação adicional da experiência pública em 27 de julho de 2026, commit `9ab4d73`:

- demo pública convertida de showcase estático em produto interativo;
- landing e CTAs realinhados de SaaS comercial para portfólio full-stack;
- página Por trás do projeto ampliada com arquitetura e evidências no código;
- rotas de autenticação protegidas no deploy estático;
- carregamento das páginas separado por rota;
- PostCSS atualizado de `8.4.49` para `8.5.23`;
- TypeScript/lint e build Vite de produção aprovados;
- `/`, `/demo`, `/como-funciona`, `/laboratorio-ats` e `/login` respondendo HTTP 200 no preview;
- landing, demo e página técnica inspecionadas em Chrome headless;
- layout responsivo da demo validado em 500 px, largura mínima efetiva do Chrome headless usado.
- deploy de produção `https://applymize.netlify.app` respondendo HTTP 200 nas cinco rotas críticas;
- headers `X-Frame-Options`, `X-Content-Type-Options` e `Referrer-Policy` confirmados em produção;
- descrição, homepage e tópicos públicos do repositório GitHub atualizados.

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

### `9ab4d73` — demonstração interativa para recrutadores

- navegação pública orientada à avaliação do portfólio;
- demo com estado local e ações funcionais;
- área Por trás do projeto com stack e links para o código;
- login público substituído por aviso seguro quando não há backend configurado;
- landing sem cadastro, planos ou promessa de SaaS;
- lazy loading por rota e metadados públicos;
- atualização do PostCSS vulnerável;
- site de produção criado em `https://applymize.netlify.app`.

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

- A demo usa dados ilustrativos e estado temporário; ela reproduz os fluxos, mas não executa provedores, banco ou integrações reais.
- Login e dashboard permanecem privados. No Netlify estático, as rotas de autenticação mostram o aviso e encaminham à demo.
- `/pricing` existe apenas como redirecionamento legado para `/como-funciona`.
- GitHub ainda não possui workflow próprio de CI; a integração Netlify executa o build do frontend.
- Não há testes automatizados do frontend ou do motor ATS público.
- O `npm audit` registra duas ocorrências altas do mesmo advisory de CSRF no modo RSC do React Router. A aplicação é uma SPA client-side e não usa RSC/actions; não há versão atual sem conflito com advisories anteriores.
- A auditoria Python ainda registra dependências vulneráveis que precisam de atualização com regressão de uploads e autenticação.
- PostgreSQL, Redis, Evolution, API e frontend locais estão publicados em todas as interfaces; segredos JWT e Evolution ainda usam valores de exemplo.
- JobSpy/Google sofre bloqueios HTTP 429 frequentes e torna a automação pouco eficiente.
- O ATS público usa heurísticas próprias e não representa todos os fornecedores de ATS.
- PDF com texto convertido em imagem pode exigir OCR, que não está implementado no navegador.
- Checkout e billing não processam pagamentos reais.
- O painel Recruiter privado é demonstrativo e não é um ATS empresarial.
- O build contém chunks grandes dos leitores PDF/DOCX, carregados sob demanda.

## 13. Próximos passos recomendados

Somente executar mudanças ou publicação com pedido do proprietário:

1. proteger o ambiente local: trocar segredos de exemplo e restringir portas internas;
2. atualizar dependências Python com regressão de uploads e autenticação;
3. criar CI e testes automatizados do motor ATS público;
4. corrigir cooldown e eficiência do JobSpy diante de HTTP 429;
9. adicionar SEO, autoria, contato e metadados sociais;
10. otimizar code splitting e compatibilidade futura.

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
- Auditoria atual: `docs/AUDIT_2026-07-27.md`
- Auditoria anterior: `docs/AUDIT_2026-07-15.md`
- Rotas frontend: `frontend/src/App.tsx`
- Elegibilidade: `backend/services/job_eligibility_filter.py`
- Relevância por cargo: `backend/services/job_role_relevance.py`
- Ingestão: `backend/services/job_ingestion.py`
- ATS privado: `backend/services/ats_analyzer.py`
- ATS público: `frontend/src/services/publicAtsEngine.ts`
- Automação: `backend/services/automation_scheduler.py`
- Netlify: `netlify.toml`
