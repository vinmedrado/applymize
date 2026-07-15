# WhatsApp / Evolution — estabilização de sessão

Este patch reduz chamadas desnecessárias para a Evolution API quando a sessão já está conectada.

## O que mudou

- Se a sessão está `connected`, o backend usa cache de status por padrão.
- A tela WhatsApp não força reconexão ao abrir.
- Botões de QR/conectar não chamam `/instance/connect` quando a sessão já está aberta.
- Estados transitórios da Evolution como `connecting/syncing/unknown` não derrubam uma sessão já conectada.
- Se a Evolution falhar temporariamente ao consultar status, o Applymize mantém o último estado conectado.

## Variáveis opcionais

```env
WHATSAPP_CONNECTED_CACHE_SECONDS=600
WHATSAPP_STATUS_FORCE_REFRESH_SECONDS=1800
```

## Logs novos

- `whatsapp_status_cache_hit`
- `whatsapp_transient_status_ignored`
- `whatsapp_status_refresh_failed_preserving_connected`
- `whatsapp_connect_skipped_already_connected`
- `whatsapp_qrcode_skipped_already_connected`
- `whatsapp_create_skipped_already_connected`

## Resultado esperado

Depois que conectou, o sistema para de provocar sincronizações frequentes no WhatsApp. Reconexão/QR só acontece quando o usuário força ação ou quando a sessão realmente está desconectada.
