# Applymize — Next Level Visual Polish

Este patch foi aplicado sobre o último ZIP `applymize_NEXT_LEVEL_SAAS_STRIPE_RECRUITER_ADMIN.zip`.

## Objetivo
Elevar a percepção visual das novas áreas SaaS sem recriar o projeto e sem quebrar backend, autenticação, IA, ATS, WhatsApp, scheduler ou providers.

## Principais melhorias

- Criação de componentes premium reutilizáveis:
  - `PremiumHero`
  - `PremiumMetric`
  - `PremiumPanel`
  - `PremiumTimeline`
  - `MiniFeature`
  - `PremiumCTA`
- Polimento visual do layout privado.
- Refinamento das páginas:
  - Billing
  - Pricing
  - Admin Analytics
  - Recruiter Panel
  - CV Pro
- Cards mais premium, melhor hierarquia visual, hero escuro, métricas executivas e experiência mais próxima de SaaS comercial.

## Observações

- Não altera regras de negócio.
- Não muda schema do banco.
- Não mexe em IA real.
- Não altera custos de Groq/Ollama.
- Mantém o sistema rodando localmente via Docker.

## Rodar

```bash
docker compose down
docker compose up --build
```
