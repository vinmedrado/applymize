"""
CareerLens v3 - Intelligence Engine
Market Score · Employability Score · Alerts · A/B CV Test · Weekly Report
"""
from datetime import datetime, date
import json


def calc_employability_score(ats_result: dict, funnel: dict, history: list) -> dict:
    """
    Calcula score de empregabilidade 0-100 com base em múltiplos fatores.
    Sobe conforme usuário melhora CV, LinkedIn, aplica vagas, etc.
    """
    score = 0
    breakdown = {}

    # CV quality (40 pts)
    cv_score = ats_result.get("score_geral", 0)
    cv_pts = int((cv_score / 100) * 40)
    score += cv_pts
    breakdown["cv_quality"] = {"pts": cv_pts, "max": 40, "label": "Qualidade do CV"}

    # Activity (30 pts) — based on funnel
    total_apps = sum(len(v) for v in funnel.values())
    interviews = len(funnel.get("Entrevista", []))
    offers = len(funnel.get("Oferta", []))
    act_pts = min(30, total_apps * 2 + interviews * 5 + offers * 10)
    score += act_pts
    breakdown["activity"] = {"pts": act_pts, "max": 30, "label": "Atividade de candidatura"}

    # Profile completeness (20 pts)
    ats = ats_result
    comp_pts = 0
    if ats.get("tecnologias_identificadas"): comp_pts += 5
    if ats.get("soft_skills"):               comp_pts += 5
    if ats.get("anos_experiencia_estimados"): comp_pts += 5
    if ats.get("cargos_ideais"):             comp_pts += 5
    score += comp_pts
    breakdown["profile"] = {"pts": comp_pts, "max": 20, "label": "Completude do perfil"}

    # History momentum (10 pts)
    recent = [h for h in history if h.get("date","") >= str(date.today())[:7]]  # this month
    mom_pts = min(10, len(recent) * 2)
    score += mom_pts
    breakdown["momentum"] = {"pts": mom_pts, "max": 10, "label": "Momentum recente"}

    level = "🔥 Excelente" if score>=80 else "💪 Bom" if score>=60 else "📈 Em desenvolvimento" if score>=40 else "🚀 Iniciando"
    return {
        "score": min(score, 100),
        "level": level,
        "breakdown": breakdown,
        "tips": _employability_tips(breakdown),
    }


def _employability_tips(breakdown):
    tips = []
    if breakdown["cv_quality"]["pts"] < 25:
        tips.append("Melhore seu CV — baixo score ATS reduz visibilidade")
    if breakdown["activity"]["pts"] < 15:
        tips.append("Aumente o número de candidaturas — meta: 10+ por semana")
    if breakdown["profile"]["pts"] < 15:
        tips.append("Complete seu perfil: adicione tecnologias, soft skills e anos de experiência")
    if breakdown["momentum"]["pts"] < 5:
        tips.append("Você está inativo este mês — retome as candidaturas")
    if not tips:
        tips.append("Você está no caminho certo! Continue aplicando consistentemente.")
    return tips


def check_alerts(jobs: list, alerts: list, cv_keywords: list) -> list:
    """
    Verifica vagas novas contra alertas configurados.
    Retorna lista de vagas que ativaram alertas.
    """
    triggered = []
    for alert in alerts:
        min_match = alert.get("min_match", 70)
        keywords  = alert.get("keywords", [])
        cargo     = alert.get("cargo", "").lower()

        for job in jobs:
            match_score = job.get("match_score", 0)
            title_lower = job.get("title", "").lower()

            kw_hit = any(k.lower() in title_lower for k in keywords) if keywords else True
            cargo_hit = cargo in title_lower if cargo else True

            if match_score >= min_match and kw_hit and cargo_hit:
                triggered.append({
                    "alert_name": alert.get("name", "Alerta"),
                    "job": job,
                    "match_score": match_score,
                })
    return triggered


def generate_weekly_report(funnel: dict, history: list, ats_result: dict, emp_score: dict) -> dict:
    """Gera relatório semanal de progresso."""
    from datetime import timedelta

    today = date.today()
    week_ago = today - timedelta(days=7)

    recent_apps = [
        h for h in history
        if h.get("date","") >= str(week_ago)
    ]

    total = sum(len(v) for v in funnel.values())
    aplicado = len(funnel.get("Aplicado",[]))
    entrevistas = len(funnel.get("Entrevista",[]))
    ofertas = len(funnel.get("Oferta",[]))
    recusados = len(funnel.get("Recusado",[]))

    conversion = round((entrevistas / max(aplicado,1)) * 100, 1)

    return {
        "week": str(today),
        "total_no_funil": total,
        "aplicadas_semana": len(recent_apps),
        "entrevistas": entrevistas,
        "ofertas": ofertas,
        "recusados": recusados,
        "taxa_conversao": conversion,
        "score_empregabilidade": emp_score.get("score", 0),
        "score_cv": ats_result.get("score_geral", 0),
        "destaque": _weekly_highlight(entrevistas, ofertas, conversion, len(recent_apps)),
        "proxima_meta": _next_goal(aplicado, entrevistas, ofertas),
    }


def _weekly_highlight(ent, offers, conv, apps):
    if offers > 0:   return f"🎉 Você tem {offers} oferta(s) ativa(s)! Hora de negociar."
    if ent > 0:      return f"🎤 {ent} entrevista(s) — prepare-se bem com o módulo de prep."
    if conv > 10:    return f"📈 Taxa de conversão de {conv}% — excelente!"
    if apps >= 10:   return f"💪 {apps} candidaturas essa semana — consistência é a chave."
    return "📌 Meta da semana: aplicar em pelo menos 10 vagas compatíveis."


def _next_goal(apps, ent, offers):
    if offers == 0 and ent > 0: return "Transformar entrevista em oferta — use o prep de entrevista"
    if ent == 0 and apps > 5:   return "Conseguir 1ª entrevista — revise o CV e personalize por vaga"
    if apps < 10:               return f"Chegar em 10 candidaturas ({10 - apps} faltam)"
    return "Manter ritmo e diversificar plataformas de busca"


def abtest_compare(results_a: list, results_b: list) -> dict:
    """Compara performance de dois currículos por match score."""
    avg_a = sum(j.get("match_score",0) for j in results_a) / max(len(results_a),1)
    avg_b = sum(j.get("match_score",0) for j in results_b) / max(len(results_b),1)
    winner = "A" if avg_a >= avg_b else "B"
    diff = abs(avg_a - avg_b)
    return {
        "avg_a": round(avg_a,1),
        "avg_b": round(avg_b,1),
        "winner": winner,
        "diff": round(diff,1),
        "confidence": "Alta" if diff > 10 else "Média" if diff > 5 else "Baixa",
        "recommendation": f"Use o CV {winner} — {round(diff,1)} pontos de match a mais em média." if diff > 3
                         else "Desempenho similar — escolha o que você prefere.",
    }
