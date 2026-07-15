from __future__ import annotations

import json
import time
from collections import defaultdict
from datetime import datetime
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.logging import get_logger
from backend.models.job import Job
from backend.models.provider_run import ProviderRun
from backend.services.provider_registry import iter_providers
from backend.models.user import User
from backend.services.user_location_preferences import get_user_job_search_location_preference
from backend.services.translation_service import normalize_job_text

logger = get_logger(__name__)

MAX_PROVIDER_ATTEMPTS = 3
BASE_BACKOFF_SECONDS = 1.2


def _provider_options_with_location_defaults(provider_options: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply safe São Paulo defaults when the user did not choose another filter.

    This keeps all providers focused on Brazil/São Paulo without hard-blocking
    LinkedIn results post-fetch. User-supplied filters always win.
    """
    from backend.core.config import settings

    options = dict(provider_options or {})
    options.setdefault("term", settings.automation_default_term)
    options.setdefault("city", settings.automation_default_city)
    options.setdefault("state", settings.automation_default_state)
    options.setdefault("country", settings.automation_default_country)
    options.setdefault("poblacion", settings.automation_default_infojobs_city_code)
    options.setdefault("city_code", settings.automation_default_infojobs_city_code)
    logger.info("provider_location_defaults_applied options=%s", options)
    return options


def _normalize_translation_payload(payload: dict) -> dict:
    title_original = payload.get("title_original") or payload.get("title") or ""
    description_original = payload.get("description_original") or payload.get("description") or ""
    normalized = normalize_job_text(title_original, description_original)
    payload["title_original"] = normalized["title_original"]
    payload["description_original"] = normalized["description_original"]
    payload["title"] = normalized["title"]
    payload["description"] = normalized["description"]
    return payload


def _dedup_key(payload: dict) -> tuple:
    return (
        str(payload.get("source") or "").strip().lower(),
        str(payload.get("external_id") or "").strip().lower(),
        str(payload.get("url") or "").strip().lower(),
        str(payload.get("title") or "").strip().lower(),
        str(payload.get("company") or "").strip().lower(),
    )


def _find_existing_fallback(db: Session, tenant_id: int, payload: dict) -> Job | None:
    url = payload.get("url") or ""
    title = payload.get("title") or ""
    company = payload.get("company") or ""
    query = db.query(Job).filter(Job.tenant_id == tenant_id)
    if url:
        existing = query.filter(Job.url == url).first()
        if existing:
            return existing
    # Catch the same job posted again with a different URL (re-scraped daily,
    # or mirrored across sources) by matching on title + company alone.
    # Requiring an equal URL here made this fallback unreachable, since an
    # equal URL is already caught by the check above.
    if title and company:
        return query.filter(Job.title == title, Job.company == company).first()
    return None


def _insert_job(db: Session, tenant_id: int, payload: dict) -> tuple[bool, Job | None]:
    payload = _normalize_translation_payload(payload)
    existing = db.query(Job).filter(
        Job.tenant_id == tenant_id,
        Job.source == payload["source"],
        Job.external_id == payload["external_id"],
    ).first()
    if existing:
        return False, existing
    fallback = _find_existing_fallback(db, tenant_id, payload)
    if fallback:
        return False, fallback
    job = Job(tenant_id=tenant_id, **payload)
    db.add(job)
    try:
        db.commit()
        db.refresh(job)
        return True, job
    except IntegrityError:
        db.rollback()
        existing = db.query(Job).filter(
            Job.tenant_id == tenant_id,
            Job.source == payload["source"],
            Job.external_id == payload["external_id"],
        ).first()
        return False, existing


def _fetch_provider_with_retry(provider, limit: int, provider_options: dict[str, Any]):
    errors: list[str] = []
    for attempt in range(1, MAX_PROVIDER_ATTEMPTS + 1):
        started = time.perf_counter()
        try:
            logger.info(
                "provider_fetch_attempt provider=%s attempt=%s max_attempts=%s limit=%s options=%s",
                provider.provider_name,
                attempt,
                MAX_PROVIDER_ATTEMPTS,
                limit,
                provider_options,
            )
            jobs = provider.fetch_jobs(limit=limit, **provider_options)
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.info("provider_fetch_success provider=%s attempt=%s elapsed_ms=%s collected=%s", provider.provider_name, attempt, elapsed_ms, len(jobs))
            return jobs, errors
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            message = f"attempt={attempt} elapsed_ms={elapsed_ms} error={exc}"
            errors.append(message)
            logger.warning("provider_fetch_failed provider=%s %s", provider.provider_name, message)
            if attempt < MAX_PROVIDER_ATTEMPTS:
                time.sleep(BASE_BACKOFF_SECONDS * attempt)
    raise RuntimeError("; ".join(errors))


def _create_provider_run(db: Session, tenant_id: int, provider_name: str, limit: int) -> ProviderRun:
    run = ProviderRun(tenant_id=tenant_id, provider=provider_name, requested_limit=limit, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def _finish_provider_run(db: Session, run: ProviderRun, status: str, collected: int, inserted: int, skipped: int, errors: list[str] | str = "") -> None:
    run.status = status
    run.collected = collected
    run.inserted = inserted
    run.skipped = skipped
    run.errors = json.dumps(errors, ensure_ascii=False) if isinstance(errors, list) else str(errors or "")
    run.finished_at = datetime.utcnow()
    db.commit()


def ingest_jobs(db: Session, tenant_id: int, source: str = "remoteok", limit: int = 25, provider_options: dict[str, Any] | None = None, user: User | None = None):
    inserted = 0
    skipped = 0
    saved: list[Job] = []
    errors: dict[str, str] = {}
    collected_by_provider: dict[str, int] = defaultdict(int)
    provider_options = _provider_options_with_location_defaults(provider_options)
    if user is not None:
        provider_options = get_user_job_search_location_preference(db, tenant_id, user).to_provider_options(provider_options)
    providers = iter_providers(source)

    for provider in providers:
        provider_name = provider.provider_name
        run = _create_provider_run(db, tenant_id, provider_name, limit)
        if not provider.enabled:
            logger.warning("provider_disabled provider=%s", provider_name)
            errors[provider_name] = "provider disabled"
            _finish_provider_run(db, run, "disabled", 0, 0, 0, ["provider disabled"])
            continue

        try:
            provider_jobs, provider_fetch_errors = _fetch_provider_with_retry(provider, limit, provider_options)
            seen: set[tuple] = set()
            unique_provider_jobs = []
            for provider_job in provider_jobs:
                key = _dedup_key(provider_job.to_dict())
                if key in seen:
                    continue
                seen.add(key)
                unique_provider_jobs.append(provider_job)
            collected_by_provider[provider_name] = len(unique_provider_jobs)
        except Exception as exc:
            logger.warning("provider_ingestion_failed provider=%s error=%s", provider_name, exc)
            errors[provider_name] = str(exc)
            _finish_provider_run(db, run, "failed", 0, 0, 0, str(exc))
            continue

        before_inserted = inserted
        before_skipped = skipped
        for provider_job in unique_provider_jobs:
            was_inserted, job = _insert_job(db, tenant_id, provider_job.to_dict())
            if was_inserted:
                inserted += 1
            else:
                skipped += 1
            if job:
                saved.append(job)

        run_inserted = inserted - before_inserted
        run_skipped = skipped - before_skipped
        _finish_provider_run(db, run, "success", len(unique_provider_jobs), run_inserted, run_skipped, provider_fetch_errors)
        logger.info(
            "provider_ingestion_done provider=%s collected=%s inserted=%s skipped=%s",
            provider_name,
            len(unique_provider_jobs),
            run_inserted,
            run_skipped,
        )

    logger.info(
        "jobs_ingestion_finished tenant_id=%s provider=%s collected=%s inserted=%s skipped=%s errors=%s",
        tenant_id,
        source,
        dict(collected_by_provider),
        inserted,
        skipped,
        errors,
    )
    return inserted, skipped, saved, dict(collected_by_provider), errors
