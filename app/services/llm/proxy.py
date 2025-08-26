from app.core.config import settings
from .cohere_provider import CohereProvider
from .openai_provider import OpenAIProvider
import logging

logger = logging.getLogger(__name__)


_provider = None


def get_provider() -> object:
    """Return an instantiated provider based on settings."""
    global _provider
    if _provider is not None:
        return _provider

    provider_name = getattr(settings, "DEFAULT_LLM_PROVIDER", "cohere").lower()
    if provider_name == "cohere":
        _provider = CohereProvider()
    elif provider_name == "openai":
        _provider = OpenAIProvider()
    else:
        logger.warning("Unknown DEFAULT_LLM_PROVIDER '%s', falling back to Cohere", provider_name)
        _provider = CohereProvider()

    return _provider


def generate(prompt: str, max_tokens: int = 500, temperature: float = 0.1) -> str:
    p = get_provider()
    return p.generate(prompt, max_tokens=max_tokens, temperature=temperature)
