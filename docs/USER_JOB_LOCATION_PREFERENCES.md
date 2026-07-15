# Applymize — Preferências de localização de vagas

Este patch remove a dependência de filtros hardcoded por São Paulo e passa a usar preferências do usuário.

## Onde configurar

- No cadastro: o usuário informa país, estado, cidades e modalidade.
- No perfil: seção **Preferências de busca** permite alterar depois.

## Campos salvos em `user_profiles`

- `job_country`
- `job_state`
- `job_state_code`
- `job_cities`
- `job_all_cities`
- `job_remote_preference`
- `job_city_code`

## Como os providers usam

O scheduler e a ingestão manual chamam `get_user_job_search_location_preference(...)` e montam `provider_options` com base no perfil do usuário.

- LinkedIn: usa localização montada por cidade/estado/país.
- Gupy: recebe state/city/country/workplaceTypes.
- InfoJobs: recebe `poblacion/city_code` quando disponível.
- JobSpy: recebe location/country/is_remote/workplace types.

## Observação

Quando o usuário escolhe "todas as cidades do estado", o sistema usa estado/país como foco e evita prender a busca em uma única cidade.
