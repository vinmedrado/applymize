import requests
from datetime import datetime
from typing import List

from backend.core.config import settings


def format_job_whatsapp_message(job, strategy=None) -> str:
    title = job.title or "Não informado"
    company = job.company or "Não informado"
    location = job.location or "Não informado"
    model = "Remoto" if job.remote else "Presencial/Híbrido"
    url = job.url or ""

    score = getattr(strategy, "strategy_score", None)
    priority = getattr(strategy, "priority", None)

    score_line = f"\n⭐ Score Applymize: {score:.2f}" if score else ""
    priority_line = f"\n🔥 Prioridade: {priority}" if priority else ""

    return f"""🎯 VAGA APPLYMIZE - {'HOME OFFICE' if job.remote else 'OPORTUNIDADE'}!

💼 Vaga: {title}
🏢 Empresa: {company}
📍 Local: {location}
💻 Modelo: {model}
📄 Tipo: {getattr(job, 'employment_type', 'Não informado')}
♿ PCD: Não informado
📅 Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}{score_line}{priority_line}

🔗 Clique aqui para aplicar:
{url}
"""


def send_whatsapp_message(number: str, message: str):
    url = f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance_id}"

    payload = {
        "number": number,
        "text": message,
    }

    headers = {
        "Content-Type": "application/json",
        "apikey": settings.evolution_api_key,
    }

    response = requests.post(url, json=payload, headers=headers, timeout=20)

    if response.status_code not in (200, 201):
        raise Exception(f"Erro ao enviar WhatsApp: {response.text}")


def send_job_alerts(jobs: List, strategy_map: dict):
    if not settings.whatsapp_enabled:
        return

    number = settings.evolution_target_number
    max_items = settings.notification_max_per_run

    sent = 0

    for job in jobs:
        strategy = strategy_map.get(job.id)

        if not strategy:
            continue

        if strategy.priority != settings.notification_min_priority:
            continue

        message = format_job_whatsapp_message(job, strategy)

        try:
            send_whatsapp_message(number, message)
            sent += 1
        except Exception as e:
            print(f"[WHATSAPP ERROR] {e}")

        if sent >= max_items:
            break
