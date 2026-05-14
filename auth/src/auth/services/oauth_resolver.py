from auth.exceptions.oauth import OAuthProviderNotSupported
from auth.ports.provider.oauth import IOAuthProvider


class OAuthProviderResolver:
    def __init__(self, providers: list[IOAuthProvider]):
        self.providers = {provider.name: provider for provider in providers}

    def get_provider(self, provider_name: str) -> IOAuthProvider:
        provider = self.providers.get(provider_name)
        if provider is None:
            raise OAuthProviderNotSupported()
        return provider
