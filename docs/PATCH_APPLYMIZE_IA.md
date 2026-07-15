# PATCH — Applymize IA

Patch incremental para incluir uma IA contextual de carreira sem alterar scheduler, WhatsApp, providers, ATS, dashboard ou autenticação.

## Backend

- Novo endpoint autenticado: `POST /api/career-ai/chat`
- Novo serviço: `backend/services/ai/career_ai_service.py`
- Providers híbridos:
  - Groq primeiro
  - Ollama como fallback local
- Prompt builder contextual em `backend/services/ai/prompts/career_prompt_builder.py`
- Contexto leve montado a partir de:
  - perfil/currículo
  - skills
  - experiências
  - projetos
  - formação
  - análise ATS
  - candidaturas recentes
  - vagas recentes

## Frontend

- Bolha flutuante `Applymize IA` no canto inferior direito.
- Chat lateral responsivo.
- Sugestões rápidas.
- Histórico local da sessão.
- Exibição de provider, modelo e fallback ativo.

## Variáveis de ambiente

```env
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
OLLAMA_ENABLED=true
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://host.docker.internal:11434
CAREER_AI_TIMEOUT_SECONDS=25
CAREER_AI_MAX_MESSAGE_CHARS=3000
```

## Validação executada

```bash
python -m compileall backend
cd frontend && npm install && npm run build
```

Resultado: backend compilado e frontend buildado com sucesso.
