"""Vertex AI powered speech recognition utilities."""
from __future__ import annotations

import logging
import mimetypes
from collections import OrderedDict
from pathlib import Path
from typing import Optional

from google.api_core.exceptions import GoogleAPICallError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part

LOGGER = logging.getLogger("vertex_speech")

_DEFAULT_PROMPT = (
    "You are an automatic speech recognition service. Transcribe the provided "
    "audio into {language} plain text. Return only the transcript with no "
    "additional commentary. If the audio lacks intelligible speech, return an "
    "empty string."
)


class VertexSpeechToText:
    """Speech-to-text helper built on top of Vertex AI Gemini models."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-1.5-flash",
        *,
        language_code: str = "en-US",
        instruction: Optional[str] = None,
        max_retries: int = 3,
        cache_size: int = 64,
    ) -> None:
        self.enabled: bool = False
        self.language_code = language_code
        self.max_retries = max_retries
        self.model_name = model_name
        self.cache: "OrderedDict[str, str]" = OrderedDict()
        self.max_cache_size = max(1, cache_size)
        self._instruction = instruction or _DEFAULT_PROMPT.format(language=self.language_code)
        self._project_id = project_id
        self._location = location

        try:
            aiplatform.init(project=project_id, location=location)
            self.model = GenerativeModel(model_name)
            self.enabled = True
            LOGGER.info(
                "VertexSpeechToText initialised with model=%s language=%s",
                model_name,
                language_code,
            )
        except DefaultCredentialsError as exc:
            self.model = None
            LOGGER.warning("VertexSpeechToText not initialised: %s", exc)
        except Exception as exc:  # pragma: no cover - defensive log
            self.model = None
            LOGGER.warning("VertexSpeechToText encountered unexpected init error: %s", exc)

    @staticmethod
    def _guess_mime_type(path: Path) -> str:
        mime, _ = mimetypes.guess_type(str(path))
        if mime:
            return mime
        # Fallback for raw PCM often used in pipelines
        if path.suffix.lower() in {".wav", ".wave"}:
            return "audio/wav"
        if path.suffix.lower() in {".mp3"}:
            return "audio/mpeg"
        return "application/octet-stream"

    @staticmethod
    def _make_cache_key(path: Path) -> str:
        try:
            stat = path.stat()
            return f"{path.resolve()}:{stat.st_size}:{stat.st_mtime_ns}"
        except OSError:
            return str(path.resolve())

    @staticmethod
    def _create_audio_part(audio_bytes: bytes, mime_type: str) -> Part:
        return Part.from_audio(audio=audio_bytes, mime_type=mime_type)

    def _store_cache(self, key: str, value: str) -> None:
        self.cache[key] = value
        if len(self.cache) > self.max_cache_size:
            self.cache.popitem(last=False)

    def transcribe(
        self,
        filename: str,
        *,
        mime_type: Optional[str] = None,
        instruction: Optional[str] = None,
    ) -> Optional[str]:
        """Transcribe an audio file into text via Vertex AI.

        Returns the transcript string when successful, otherwise ``None``.
        """
        if not self.enabled or not getattr(self, "model", None):
            LOGGER.warning("VertexSpeechToText disabled: no transcription performed")
            return None

        audio_path = Path(filename)
        if not audio_path.exists():
            LOGGER.warning("VertexSpeechToText: file %s not found", filename)
            return None

        cache_key = self._make_cache_key(audio_path)
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            audio_bytes = audio_path.read_bytes()
        except OSError as exc:
            LOGGER.warning("VertexSpeechToText: failed to read %s (%s)", filename, exc)
            return None

        mime = mime_type or self._guess_mime_type(audio_path)
        prompt = instruction or self._instruction
        audio_part = self._create_audio_part(audio_bytes, mime)

        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content([audio_part, prompt])  # type: ignore[call-arg]
                text = getattr(response, "text", "")
                if text:
                    cleaned = text.strip()
                    if cleaned:
                        self._store_cache(cache_key, cleaned)
                        return cleaned
                LOGGER.info(
                    "VertexSpeechToText empty transcript on attempt %d", attempt + 1
                )
            except GoogleAPICallError as exc:
                LOGGER.warning(
                    "VertexSpeechToText failed attempt %d: %s", attempt + 1, exc
                )
            except Exception as exc:  # pragma: no cover - defensive log
                LOGGER.warning(
                    "VertexSpeechToText unexpected error on attempt %d: %s",
                    attempt + 1,
                    exc,
                )

        return None