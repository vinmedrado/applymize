from __future__ import annotations

from backend.services.providers import PROVIDERS, JobProvider


def list_provider_names() -> list[str]:
    return sorted(PROVIDERS.keys())


def get_provider(name: str) -> JobProvider:
    provider_cls = PROVIDERS.get(name)
    if not provider_cls:
        raise ValueError(f"Provider inválido: {name}. Disponíveis: {', '.join(list_provider_names())}, all")
    return provider_cls()


def iter_providers(name: str) -> list[JobProvider]:
    if name == "all":
        return [provider_cls() for provider_cls in PROVIDERS.values()]
    return [get_provider(name)]


def providers_health() -> list[dict]:
    result = []
    for name in list_provider_names():
        try:
            provider = get_provider(name)
            result.append(provider.healthcheck())
        except Exception as exc:
            result.append({
                "provider": name,
                "enabled": False,
                "status": "error",
                "message": "Falha local no healthcheck do provider.",
                "error": str(exc),
            })
    return result


def providers_summary() -> list[dict]:
    return [
        {
            "provider": name,
            "enabled": get_provider(name).enabled,
        }
        for name in list_provider_names()
    ]
