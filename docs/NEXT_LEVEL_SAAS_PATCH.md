# Applymize — Next Level SaaS Patch

Este patch adiciona uma camada comercial e B2B em cima do último Applymize, sem remover as funcionalidades existentes.

## Incluído

- `/pricing`: página pública de planos.
- `/billing`: billing privado com checkout mock seguro e estrutura Stripe-ready.
- `/admin`: analytics admin do tenant.
- `/recruiter`: painel recruiter com pipeline, ranking e visão HRTech.
- `/cv-pro`: vitrine interna para geração avançada de CV.
- APIs:
  - `GET /api/public/billing/plans`
  - `GET /api/billing/plans`
  - `GET /api/billing/subscription`
  - `POST /api/billing/checkout`
  - `GET /api/admin/overview`
  - `GET /api/recruiter/dashboard`

## Stripe

Sem `STRIPE_SECRET_KEY`, o checkout opera em modo demonstrativo e ativa o plano no tenant para demo comercial. Com Stripe real, conectar os Price IDs e webhook.

## Observação

Este patch é incremental e seguro para demonstração. Para produção real, completar webhooks Stripe, termos, política de privacidade, backups e monitoramento.
