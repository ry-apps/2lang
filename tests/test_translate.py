import pytest
from markdown_it import MarkdownIt
from markdown_it.token import Token
from translate import get_parser, get_tokens_to_translate


@pytest.fixture
def parser() -> MarkdownIt:
    return get_parser()


@pytest.fixture
def sample(parser: MarkdownIt) -> list[Token]:
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


def test_get_tokens_to_translate(sample: list[Token]):
    selected = get_tokens_to_translate(sample)
    assert len(list(selected)) == 7
