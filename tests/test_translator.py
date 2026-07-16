import pytest
from langdetect import DetectorFactory, detect

from twolang.translator import Translator, detect_language, split_chunks

DetectorFactory.seed = 0  # deterministic language detection

pytestmark = pytest.mark.integration


def test_detect_language_real_text():
    assert detect_language("Bonjour, comment ça va aujourd'hui ?") == "fr"


def test_translate_basic_translation():
    translator = Translator(source_lang="en", target_lang="pl")
    result = translator.translate("Hello, how are you?")
    assert detect(result) == "pl"



