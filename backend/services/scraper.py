from backend.core.logging import get_logger
from backend.services.provider_registry import get_provider, list_provider_names

logger = get_logger(__name__)


def available_providers() -> list[str]:
    return list_provider_names()


def fetch_jobs_from_provider(source: str, limit: int = 25) -> list[dict]:
    provider = get_provider(source)
    if not provider.enabled:
        logger.warning("provider_disabled source=%s", source)
        return []

    try:
        return [job.to_dict() for job in provider.fetch_jobs(limit=limit)]
    except Exception as exc:
        logger.warning("provider_fetch_failed source=%s error=%s", source, exc)
        return []


def scrape_remoteok(limit: int = 25) -> list[dict]:
    return fetch_jobs_from_provider("remoteok", limit)
