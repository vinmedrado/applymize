from backend.models.job import Job
from backend.models.user import User
from backend.services.matching_engine import calculate_match, split_skills


def _stack_questions(skills: list[str]) -> list[str]:
    questions = []
    for skill in skills[:8]:
        questions.append(f"Explique um projeto real em que você usou {skill}, quais decisões tomou e qual resultado gerou.")
        questions.append(f"Quais erros comuns você evitaria trabalhando com {skill} em produção?")
    return questions


def generate_interview_prep(user: User, job: Job, profile_context: str | None = None) -> dict:
    match = calculate_match(user, job, profile_context=profile_context)
    matched = match.matched_skills
    gaps = match.missing_skills[:8]
    required = split_skills(job.requirements)

    technical = _stack_questions(matched or required or ["Python", "SQL", "APIs"])
    behavioral = [
        "Conte uma situação em que você teve prazo curto e precisou priorizar o essencial.",
        "Descreva uma entrega em que você precisou comunicar riscos para alguém não técnico.",
        "Fale sobre um erro técnico que você encontrou e como corrigiu.",
        "Como você organiza documentação, logs e testes para manter um sistema confiável?",
        "Como você mede impacto de uma automação ou melhoria técnica?",
    ]
    gap_questions = [
        f"A vaga pode exigir {gap}. Como você compensaria ou evoluiria rapidamente nesse ponto?"
        for gap in gaps
    ]

    study_plan = []
    for idx, gap in enumerate(gaps, start=1):
        priority = "Alta" if idx <= 3 else "Média"
        study_plan.append(f"{priority}: estudar {gap}, criar exemplo prático e preparar explicação de uso em projeto.")
    if not study_plan:
        study_plan = [
            "Alta: preparar 2 cases técnicos com impacto mensurável.",
            "Alta: revisar descrição da vaga e conectar cada requisito a um projeto real.",
            "Média: treinar perguntas comportamentais usando método STAR.",
        ]

    return {
        "job_id": job.id,
        "role_pitch": (
            f"Sou {user.full_name}, perfil {user.seniority}, com experiência em {user.skills}. "
            f"Para {job.title} na {job.company}, meu foco é entregar soluções práticas, seguras e mensuráveis."
        ),
        "questions": technical + behavioral + gap_questions,
        "weak_points": gaps,
        "study_plan": study_plan,
        "suggested_answers": ["Use contexto, ação, resultado e métrica.", "Para gaps: reconheça, mostre plano e conecte com experiência próxima."],
        "salary_talk": (
            "Antes de informar pretensão, confirme escopo, senioridade, modelo de trabalho, benefícios e faixa interna. "
            "Depois apresente uma faixa coerente com responsabilidade e mercado."
        ),
    }
