from abc import ABC, abstractmethod

from src.domain.entities.auth import JiraIdentity


class IJiraSSOService(ABC):
    @abstractmethod
    async def generate_jira_auth_url(self) -> str:
        """Generate Jira SSO authentication URL"""
        pass

    @abstractmethod
    async def exchange_jira_code(
        self,
        code: str
    ) -> JiraIdentity:
        """Exchange authorization code for Jira user information"""
        pass
