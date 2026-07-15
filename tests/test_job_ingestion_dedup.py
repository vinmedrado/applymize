"""Regression tests for the job deduplication logic in job_ingestion.py.

Bug that was fixed: `_find_existing_fallback` matched an existing job by
title + company, but also required the URL to be identical. Since an
identical URL is already handled by the check right above it, that made
the title+company fallback unreachable in practice -- the exact scenario
that causes duplicated jobs when the same posting reappears with a new
URL (re-scraped daily, or mirrored across sources).
"""

import uuid

from backend.core.database import SessionLocal
from backend.models.tenant import Tenant
from backend.services.job_ingestion import _insert_job, _find_existing_fallback


def _make_tenant(db) -> int:
    tenant = Tenant(name="Test Tenant", slug=f"test-tenant-{uuid.uuid4().hex[:12]}")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant.id


def _base_payload(**overrides) -> dict:
    payload = {
        "source": "linkedin",
        "external_id": "abc123",
        "title": "Analista de Dados Pleno",
        "title_original": "Analista de Dados Pleno",
        "company": "Empresa X",
        "location": "São Paulo, SP",
        "url": "https://linkedin.com/jobs/1",
        "description": "Descrição da vaga",
        "description_original": "Descrição da vaga",
        "requirements": "",
        "seniority": "mid",
        "employment_type": "full_time",
        "salary_min": 0.0,
        "salary_max": 0.0,
        "remote": False,
    }
    payload.update(overrides)
    return payload


def test_same_source_and_external_id_is_skipped():
    db = SessionLocal()
    try:
        tenant_id = _make_tenant(db)
        inserted, job = _insert_job(db, tenant_id, _base_payload())
        assert inserted is True

        inserted_again, existing = _insert_job(db, tenant_id, _base_payload())
        assert inserted_again is False
        assert existing.id == job.id
    finally:
        db.close()


def test_same_title_and_company_with_different_url_is_detected_as_duplicate():
    # This is the bug scenario: same job, re-scraped with a new external_id
    # and a different URL (e.g. tracking params, or mirrored on another
    # board). It must be recognized as the same posting, not a new one.
    db = SessionLocal()
    try:
        tenant_id = _make_tenant(db)
        first_payload = _base_payload(external_id="run-1", url="https://linkedin.com/jobs/1")
        inserted, job = _insert_job(db, tenant_id, first_payload)
        assert inserted is True

        second_payload = _base_payload(
            external_id="run-2",  # different id from a later scrape
            url="https://linkedin.com/jobs/1?ref=email",  # different url
        )
        inserted_again, existing = _insert_job(db, tenant_id, second_payload)

        assert inserted_again is False, "duplicate with a different URL must not be inserted again"
        assert existing.id == job.id

        fallback = _find_existing_fallback(db, tenant_id, second_payload)
        assert fallback is not None
        assert fallback.id == job.id
    finally:
        db.close()


def test_different_company_is_not_treated_as_duplicate():
    db = SessionLocal()
    try:
        tenant_id = _make_tenant(db)
        inserted, job = _insert_job(db, tenant_id, _base_payload())
        assert inserted is True

        other_payload = _base_payload(
            external_id="run-2",
            company="Empresa Y",  # different company, same title
            url="https://linkedin.com/jobs/999",
        )
        inserted_again, other_job = _insert_job(db, tenant_id, other_payload)
        assert inserted_again is True
        assert other_job.id != job.id
    finally:
        db.close()


def test_duplicate_is_scoped_per_tenant():
    # The same job posting for two different tenants must not collide.
    db = SessionLocal()
    try:
        tenant_a = _make_tenant(db)
        tenant_b = _make_tenant(db)
        payload = _base_payload()

        inserted_a, job_a = _insert_job(db, tenant_a, payload)
        inserted_b, job_b = _insert_job(db, tenant_b, payload)

        assert inserted_a is True
        assert inserted_b is True
        assert job_a.id != job_b.id
    finally:
        db.close()
