from twolang.lang import split_by_sentences


def test_split_chunks():
    text = """1 22? 333."""

    result = list(split_by_sentences(text, max_chars=4))
    assert result == [
        "1",
        "22?",
        "333.",
    ]
