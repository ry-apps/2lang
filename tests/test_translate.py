import pytest
from markdown_it import MarkdownIt
from markdown_it.token import Token

from twolang.translate import get_parser, get_tokens_to_translate, translate_markdown
from twolang.translator import Translator

SAMPLE = """# Title

Some *emphasised* text with `inline code` and a [link text](https://example.com/page?a=1).

Formula inline $x_i^2$ and a block:

$$E = mc^2$$

| Col A | Col B |
| --- | --- |
| one | two |

```python
print("do not translate")
```

<table>
<tr><th>Column A</th><th>Column B</th></tr>
<tr><td>html cell</td><td>42</td></tr>
</table>
"""


class UppercaseTranslator(Translator):
    """Offline stand-in for the Google backend: uppercases prose instead of translating."""

    def __init__(self) -> None:
        super().__init__(target_lang="en")

    async def translate(self, text: str) -> str:
        return text.upper()


@pytest.fixture
def parser() -> MarkdownIt:
    return get_parser()


@pytest.fixture
def sample_tokens(parser: MarkdownIt) -> list[Token]:
    md_text = """
# H1 header

Paragraph of text.

* this one
* that one

- this one
- that one

<table>
<tr><th>Column A</th><th>Column B</th></tr>
<tr><td>A1</td><td>B1</td></tr>
</table>
"""
    return parser.parse(md_text)


def test_get_tokens_to_translate(sample_tokens: list[Token]):
    selected = get_tokens_to_translate(sample_tokens)
    assert len(list(selected)) == 7


@pytest.mark.asyncio
async def test_translate_markdown_translates_prose():
    result = await translate_markdown(SAMPLE, UppercaseTranslator())

    assert "# TITLE" in result
    assert "EMPHASISED" in result
    assert "[LINK TEXT]" in result
    assert "| ONE | TWO |".replace(" ", "") in result.replace(" ", "")  # table cells, ignoring padding
    assert "HTML CELL" in result  # text inside raw HTML tables is translated too


@pytest.mark.asyncio
async def test_translate_markdown_preserves_structure():
    result = await translate_markdown(SAMPLE, UppercaseTranslator())

    assert "`inline code`" in result  # inline code
    assert 'print("do not translate")' in result  # code fence body
    assert "$x_i^2$" in result  # inline math
    assert "$$E = mc^2$$" in result  # block math
    assert "(https://example.com/page?a=1)" in result  # link target
    assert "<td>42</td>" in result  # HTML tags and non-prose cells
    assert result.count("|") == SAMPLE.count("|")  # table structure intact
