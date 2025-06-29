from abc import ABC, abstractmethod
from typing import List


class BaseLlm(ABC):
    @abstractmethod
    def generate_response(self, query: str, chunks: List[str], context: dict) -> str:
        """Gera uma resposta da LLM com base na consulta e nos trechos de contexto."""
        pass
