# PATCH — Alertas inteligentes WhatsApp

Implementado:

- Preferências por usuário para alertas de vagas.
- Prioridade em português: Alta, Alta + Média, Alta + Média + Baixa.
- Filtro opcional de vagas remotas.
- Frequência configurável: imediato, diário ou semanal.
- Resumo Top vagas em uma mensagem única.
- Histórico de alertas por usuário/tenant para evitar repetir a mesma vaga.
- Envio em background após ingestão para não travar a importação.
- Fallback por e-mail quando WhatsApp falhar, se SMTP estiver configurado.
- Tela de Notificações atualizada com preferências e histórico.

Migração adicionada:

- `migrations/versions/0012_job_alert_preferences.py`

Validação executada:

```bash
python -m compileall backend
```

Observação:

- Frequências diária/semanal ficam salvas como preferência. O envio imediato é executado após ingestão. Para rotina diária/semanal real, basta conectar essas preferências ao scheduler/cron do projeto.
