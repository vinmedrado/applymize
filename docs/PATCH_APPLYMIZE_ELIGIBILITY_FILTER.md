# PATCH Applymize — Filtro de Elegibilidade de Vagas

## Objetivo
Reduzir envio automático de vagas incompatíveis no WhatsApp, especialmente vagas com requisitos obrigatórios que o usuário não atende e vagas internacionais do LinkedIn.

## Arquivos alterados

- `backend/services/job_eligibility_filter.py`
- `backend/services/automation_scheduler.py`
- `backend/services/whatsapp_job_alert_service.py`
- `backend/services/providers/linkedin_guest.py`

## O que foi implementado

### 1. Filtro de elegibilidade
Criado o serviço `evaluate_job_eligibility(job)` retornando:

```python
{
    "eligible": bool,
    "blockers": list[str],
    "penalty": int,
    "warnings": list[str],
}
```

Bloqueia vagas com sinais obrigatórios de:

- ensino superior completo / graduação completa / formação superior completa
- inglês avançado ou fluente
- espanhol avançado ou fluente
- MBA/pós-graduação obrigatória
- certificação/certificações obrigatórias

Quando o requisito aparece como desejável, diferencial, plus, nice to have ou preferencialmente, a vaga continua elegível e recebe warning/penalty leve.

### 2. Scheduler e WhatsApp
O filtro foi aplicado antes do envio automático no scheduler e também no serviço de alertas WhatsApp.

Quando `eligible=false`:

- a vaga não é enviada;
- não é marcada como enviada;
- o fluxo continua analisando as próximas vagas;
- o log `job_blocked_by_eligibility` é registrado com `tenant_id`, `user_id`, `job_id` e blockers.

### 3. LinkedIn Brasil
O provider LinkedIn agora força busca com localização `São Paulo, Brasil` quando cidade/UF não forem informadas.

Também descarta vagas com localização estrangeira, como:

- United States
- USA / US
- Remote US
- North America
- Canada

E mantém vagas com sinais de Brasil/São Paulo/remoto Brasil.

### 4. Logs adicionados

- `job_eligibility_checked`
- `job_blocked_by_eligibility`
- `linkedin_job_discarded_foreign_location`

## Validação executada

```bash
python -m compileall backend
```

Resultado: compilação concluída com sucesso.
