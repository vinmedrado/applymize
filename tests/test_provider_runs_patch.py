from backend.services import job_ingestion


class DummyProvider:
    provider_name = "dummy"
    enabled = True
    calls = 0

    def fetch_jobs(self, limit=25, **kwargs):
        self.calls += 1
        if self.calls < 2:
            raise RuntimeError("temporary")
        return []


def test_provider_retry_recovers(monkeypatch):
    monkeypatch.setattr(job_ingestion, "BASE_BACKOFF_SECONDS", 0)
    provider = DummyProvider()
    jobs, errors = job_ingestion._fetch_provider_with_retry(provider, 1, {})
    assert jobs == []
    assert len(errors) == 1
    assert provider.calls == 2
