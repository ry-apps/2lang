"""Translation backend: Google Translate via deep-translator."""

import asyncio
import logging

from deep_translator import GoogleTranslator
from langdetect import DetectorFactory, detect
from loguru import logger
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

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
    def __init__(self, *, target_lang: str, source_lang: str | None = None, max_threads: int = 5) -> None:
        self.source_lang = to_google_code(source_lang) if source_lang else "auto"
        self.target_lang = to_google_code(target_lang)
        self._semaphore = asyncio.Semaphore(max_threads)

    async def translate(self, text: str) -> str:
        head = text[: len(text) - len(text.lstrip())]
        tail = text[len(text.rstrip()) :]
        core = text.strip()
        if not core:
            return text

        sentences = list(split_by_sentences(core, max_chars=4500))
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(self._translate(s)) for s in sentences]
        return head + " ".join(task.result() for task in tasks) + tail

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _translate(self, text: str) -> str:
        async with self._semaphore:
            result = await asyncio.to_thread(
                GoogleTranslator(
                    source=self.source_lang,
                    target=self.target_lang,
                ).translate,
                text,
            )
        return result if result is not None else text
