"""Translation backend: Google Translate free web endpoint via deep-translator."""

import logging

from deep_translator import GoogleTranslator
from langdetect import DetectorFactory, detect
from loguru import logger
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

from twolang.lang import split_by_sentences

DetectorFactory.seed = 0  # deterministic language detection


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
    def __init__(self, *, target_lang: str, source_lang: str | None = None) -> None:
        self.source_lang = to_google_code(source_lang) if source_lang else "auto"
        self.target_lang = to_google_code(target_lang)

    def translate(self, text: str) -> str:
        text = text.strip()
        if not text:
            return text

        head = text[: len(text) - len(text.lstrip())]
        tail = text[len(text.rstrip()) :]
        sentences = split_by_sentences(text, max_chars=4500)
        result = []

        for sentence in tqdm(sentences):
            translation = self._translate(sentence)
            result.append(translation)

        return head + " ".join(result) + tail

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _translate(self, segment: str) -> str:
        google_translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)
        result = google_translator.translate(segment)
        return result if result is not None else segment
