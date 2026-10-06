"""Gemini client wrapper with safe, actionable provider errors."""

import logging

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMConfigurationError(Exception):
    """Raised when Gemini credentials are missing or rejected."""


class LLMProviderError(Exception):
    """Raised when Gemini cannot complete a request."""


class LLMService:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY.strip()
        self.client = genai.Client(api_key=api_key) if api_key else None

    def _generate_content(self, contents) -> str:
        if self.client is None:
            raise LLMConfigurationError(
                "Gemini API key is missing. Set GEMINI_API_KEY in .env and restart the API."
            )

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
            )
        except genai.errors.APIError as exc:
            error_text = str(exc).lower()
            if "api_key_invalid" in error_text or "api key not valid" in error_text:
                logger.warning("Gemini rejected the configured API key (HTTP %s)", exc.code)
                raise LLMConfigurationError(
                    "Gemini rejected GEMINI_API_KEY. Create or select a valid key in Google AI Studio, "
                    "replace the value in .env, then restart the API."
                ) from exc

            logger.exception("Gemini request failed with HTTP %s", exc.code)
            raise LLMProviderError(
                f"Gemini request failed with HTTP {exc.code}. Check the API process log."
            ) from exc
        except Exception as exc:
            logger.exception("Gemini request failed")
            raise LLMProviderError(
                "Gemini request failed. Check the API process log for details."
            ) from exc

        text = getattr(response, "text", None)
        if not text:
            raise LLMProviderError("Gemini returned an empty response.")
        return text

    def generate_completion(self, prompt: str) -> str:
        return self._generate_content(prompt)

    def generate_document_completion(self, prompt: str, content: bytes, mime_type: str) -> str:
        file_part = types.Part.from_bytes(data=content, mime_type=mime_type)
        return self._generate_content([prompt, file_part])


llm_service = LLMService()
