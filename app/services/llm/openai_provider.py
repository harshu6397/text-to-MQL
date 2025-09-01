from typing import Optional
import openai
from app.core.config import settings
from app.utils.logger import logger



class OpenAIProvider:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or getattr(settings, "OPENAI_MODEL", "gpt-4o")
        openai.api_key = self.api_key

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.1) -> str:
        # Use text generation endpoint compatible with this codebase
        response = openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False,
        )

        logger.debug(f"OpenAI response: {response.choices[0].message.content}")
        # response.choices[0].text is the typical structure
        return response.choices[0].message.content.strip()
