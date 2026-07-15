from backend.services.providers.base import JobProvider, ProviderJob
from backend.services.providers.gupy import GupyProvider
from backend.services.providers.jobspy_provider import JobSpyProvider
from backend.services.providers.remoteok import RemoteOKProvider
from backend.services.providers.vagas import VagasProvider
from .linkedin_guest import LinkedInGuestProvider
from backend.services.providers.infojobs import InfoJobsProvider

PROVIDERS = {
    "remoteok": RemoteOKProvider,
    "gupy": GupyProvider,
    "vagas": VagasProvider,
    "jobspy": JobSpyProvider,
    "linkedin": LinkedInGuestProvider,
    "infojobs": InfoJobsProvider,
}

__all__ = [
    "JobProvider",
    "ProviderJob",
    "RemoteOKProvider",
    "GupyProvider",
    "VagasProvider",
    "JobSpyProvider",
    "InfoJobsProvider",
    "PROVIDERS",
]
