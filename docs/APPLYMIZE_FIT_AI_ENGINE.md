# Applymize Fit — AI Engine

Este patch transforma o Applymize Fit em um módulo privado premium de preparação comportamental.

## O que foi adicionado

- Botão **Iniciar treino**.
- Campo de empresa alvo.
- Campo de cargo alvo.
- Foco do treino: Gupy, RH, comunicação, colaboração, liderança etc.
- Geração de perguntas personalizadas usando o contexto do usuário.
- Avaliação de cada resposta com leitura de RH.
- Score por resposta.
- Pontos fortes, pontos de atenção e resposta melhorada.
- Fallback interno caso Groq/Ollama falhe.

## Custos e limites

O módulo usa IA real apenas dentro do sistema logado.

Variável opcional:

```env
APPLYMIZE_FIT_DAILY_LIMIT=8
```

Esse limite controla o número diário de chamadas de IA do Applymize Fit por usuário.

## Endpoints

```http
POST /api/applymize-fit/start
POST /api/applymize-fit/evaluate
```

Ambos exigem autenticação.
