from abc import ABC, abstractmethod
from typing import Any, Optional

class RepositoryProvider(ABC):
    @abstractmethod
    def search(self, query: str, language: Optional[str] = None, page: int = 1, per_page: int = 10) -> list[dict[str, Any]]:
        """Search repositories using query and filters."""
        pass

    @abstractmethod
    def getRepository(self, owner: str, repo: str) -> Optional[dict[str, Any]]:
        """Get repository details by owner and name."""
        pass

    @abstractmethod
    def getReadme(self, owner: str, repo: str) -> Optional[str]:
        """Get readme raw text content for a repository."""
        pass

    @abstractmethod
    def getMetadata(self, owner: str, repo: str) -> dict[str, Any]:
        """Get additional metadata for a repository."""
        pass
