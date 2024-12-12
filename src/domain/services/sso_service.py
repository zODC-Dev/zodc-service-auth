from abc import ABC, abstractmethod

from src.domain.entities.auth import MicrosoftIdentity


class ISSOService(ABC):
    @abstractmethod
    async def generate_auth_url(self, code_challenge: str) -> str:
        """Generate SSO authentication URL"""
        pass

    @abstractmethod
    async def exchange_code(self, code: str, code_verifier: str) -> MicrosoftIdentity:
        """Exchange authorization code for user information"""
        pass
