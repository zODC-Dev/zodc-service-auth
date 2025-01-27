from abc import ABC, abstractmethod

from src.domain.entities.auth import MicrosoftIdentity


class IMicrosoftSSOService(ABC):
    @abstractmethod
    async def generate_microsoft_auth_url(self, code_challenge: str) -> str:
        """Generate Microsoft SSO authentication URL"""
        pass

    @abstractmethod
    async def exchange_microsoft_code(
        self,
        code: str,
        code_verifier: str
    ) -> MicrosoftIdentity:
        """Exchange authorization code for Microsoft user information"""
        pass
