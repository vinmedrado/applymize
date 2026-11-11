# QA e revisão de dependências — novembro de 2026

## Escopo verificado
A integração contínua executa backend Python (compilação e pytest, incluindo isolamento entre tenants) e frontend React/TypeScript (checagem estática e build).

A auditoria de dependências de produção com `npm audit --omit=dev --audit-level=high` foi incorporada ao CI. Uma execução de correção instalou a versão **7.18.5** de `react-router-dom`, aplicou atualizações compatíveis às dependências transitivas, reproduziu o build com `npm ci` e encerrou a auditoria de produção com **0 vulnerabilidades reportadas**.

## Limites
- `npm audit --omit=dev` não inclui dependências de desenvolvimento; há alertas de segurança nessa árvore e ela não deve ser exposta em um servidor de desenvolvimento público.
- A suíte de testes não substitui pentest de autenticação/tenancy nem testes de integrações reais (WhatsApp, plataformas de vagas, provedores de IA).
- O CI usa valores fictícios e não deve receber segredos reais. A demonstração pública não deve conter dados de candidatos.

## Próximas verificações sob demanda
Validar o deploy real, e revisar atualizações major de dependências de desenvolvimento em branch separada, com regressão de UI antes do merge.
