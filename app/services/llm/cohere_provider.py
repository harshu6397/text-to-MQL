from typing import Optional
import logging
import cohere
from app.core.config import settings

logger = logging.getLogger(__name__)


class CohereProvider:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.COHERE_API_KEY
        self.model = model or getattr(settings, "COHERE_MODEL", "command-r-plus")
        self.client = None

    def _ensure_client(self):
        if self.client is None:
            self.client = cohere.Client(self.api_key)
            logger.info("Cohere client initialized")

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.1) -> str:
        self._ensure_client()
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.generations[0].text.strip()
