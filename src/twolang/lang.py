import re
from typing import Generator

_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


def split_by_sentences(text: str, max_chars: int) -> Generator[str]:
    """
    Split text into chunks of at most max_chars, breaking on sentence boundaries.
    Sentences that are themselves too long are broken on word or characters boundaries instead.
    """

    leftover = ""

    for sentence in _SENTENCE_END_RE.split(text):
        while len(sentence) > max_chars:
            pos = sentence.rfind(" ", 0, max_chars)
            if pos == -1:
                pos = max_chars
                yield sentence[:pos]
                sentence = sentence[pos:]
            else:
                yield sentence[:pos]
                sentence = sentence[pos + 1 :]

        chunk = leftover + sentence
        if len(chunk) > max_chars:
            if leftover:
                yield leftover
            leftover = sentence
        else:
            leftover = chunk

    if leftover:
        yield leftover
