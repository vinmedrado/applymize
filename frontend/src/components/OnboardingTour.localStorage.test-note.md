# OnboardingTour fallback localStorage

Este projeto não possui infraestrutura de testes frontend configurada.
O fallback permanece implementado no componente:

- tenta GET /api/user/onboarding-status
- se falhar, usa localStorage applymize:onboarding-tour:v1
- ao finalizar, salva no backend e também no localStorage
- botão Ver tutorial dispara evento e ignora estado salvo
