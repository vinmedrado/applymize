# PATCH — Landing Page Premium + LinkedIn Analyzer

Este patch evolui o Applymize com uma camada pública de apresentação SaaS e um analisador de perfil LinkedIn.

## Incluído

- Landing page pública em `/`
- Demo pública em `/demo`
- LinkedIn Analyzer público em `/linkedin-analyzer`
- Endpoint `POST /api/linkedin-analyzer/analyze`
- Motor determinístico de análise com boas práticas de ATS, LinkedIn SEO e recrutamento
- Score por categorias: headline, sobre, experiência, palavras-chave, clareza, ATS readiness e senioridade percebida
- Sugestões de headline, sobre, palavras-chave e melhorias

## Segurança

- O sistema não faz scraping agressivo do LinkedIn.
- A URL é usada apenas como referência.
- A análise é baseada no texto fornecido pelo usuário.

## Rotas privadas

O dashboard principal agora fica em `/dashboard`.
A landing pública ocupa a rota `/`.

## Rodar

```bash
docker compose down
docker compose up --build
```
