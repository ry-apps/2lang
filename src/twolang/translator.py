"""Translation backend: Google Translate free web endpoint via deep-translator."""

import time

from deep_translator import GoogleTranslator
from langdetect import DetectorFactory, detect
from loguru import logger

DetectorFactory.seed = 0  # deterministic language detection

_MAX_CHARS = 4500  # Google web endpoint rejects requests over ~5000 chars
_RETRIES = 3


def to_google_code(code: str) -> str:
    code_lower = code.lower()
    return {
        "zh-cn": "zh-CN",
        "zh-tw": "zh-TW",
        "he": "iw",
        "jw": "jv",
    }.get(code_lower, code_lower)


def detect_language(sample: str) -> str:
    """Detect the language of a text sample, returning a Google-compatible code."""
    return to_google_code(detect(sample))


class Translator:
    """Cached, retrying wrapper around deep-translator's GoogleTranslator."""

    def __init__(self, *, target_lang: str, source_lang: str | None = None) -> None:
        self.source_lang = to_google_code(source_lang) if source_lang else "auto"
        self.target_lang = to_google_code(target_lang)
        self._cache: dict[str, str] = {}
        self.segments = 0

    def translate(self, text: str) -> str:
        core = text.strip()
        if not core:
            return text
        if core not in self._cache:
            self._cache[core] = self._translate(core)
            self.segments += 1
            if self.segments % 50 == 0:
                logger.info("translated {} segments...", self.segments)
        # re-attach the original surrounding whitespace
        head = text[: len(text) - len(text.lstrip())]
        tail = text[len(text.rstrip()) :]
        return head + self._cache[core] + tail

    def _translate(self, text: str) -> str:
        if len(text) > _MAX_CHARS:
            half = text.rfind(" ", 0, _MAX_CHARS)
            half = half if half > 0 else _MAX_CHARS
            return self._translate(text[:half]) + " " + self._translate(text[half:])
        last_error: Exception | None = None
        for attempt in range(1, _RETRIES + 1):
            google_translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)
            try:
                result = google_translator.translate(text)
                return result if result is not None else text
            except Exception as e:  # network hiccups / transient endpoint errors
                last_error = e
                logger.warning("translation attempt {}/{} failed: {}", attempt, _RETRIES, e)
                time.sleep(attempt)
        raise RuntimeError(f"translation failed after {_RETRIES} attempts") from last_error
