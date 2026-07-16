"""
Markdown-aware translation built on markdown-it-py + mdformat.

The document is parsed into a token stream; a generator yields the tokens that
carry prose (inline text and raw HTML blocks, e.g. MinerU's HTML tables).
Everything else that must survive verbatim — code fences, inline code,
$...$ / $$...$$ math, link targets — lives in other token types and never reaches
the translator.
"""

import asyncio
from pathlib import Path
from typing import Generator

import mdformat_tables
from loguru import logger
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdformat.renderer import MDRenderer
from mdit_py_plugins.dollarmath import dollarmath_plugin
from tqdm import tqdm

from twolang.translator import Translator, detect_language


async def translate(md_files: list[Path], target_lang: str, source_lang: str | None):
    suffix = f".{target_lang}.md"
    for md_file in md_files:
        md_text = md_file.read_text(encoding="utf-8")

        if source_lang is None:
            source_lang = detect_language(sample=md_text)
            logger.info(f"{md_file.name}: auto-detected source language: {source_lang}")

        translator = Translator(source_lang=source_lang, target_lang=target_lang)
        logger.info(f"{md_file.name}: translating {source_lang} -> {target_lang}")
        translated = await translate_markdown(md_text, translator)

        translation_file = md_file.parent / (md_file.stem + suffix)
        translation_file.write_text(translated, encoding="utf-8")
        logger.info(f"saved {translation_file}")


def get_parser() -> MarkdownIt:
    return MarkdownIt("commonmark").enable("table").use(dollarmath_plugin)


def get_tokens_to_translate(tokens: list[Token]) -> Generator[Token]:
    for token in tokens:
        match token.type:
            case "html_block":
                yield token
            case "inline":
                yield from (child for child in token.children or [] if child.type == "text")


class _MathExtension:
    """
    mdformat renderer extension for dollarmath tokens.
    """

    RENDERERS = {  # noqa: RUF012
        "math_inline": lambda node, ctx: f"${node.content}$",
        "math_block": lambda node, ctx: f"$${node.content}$$",
    }


async def translate_markdown(md_text: str, translator: Translator) -> str:
    parser = get_parser()
    tokens = parser.parse(md_text, {})

    async with asyncio.TaskGroup() as tg:
        to_translate = list(get_tokens_to_translate(tokens))
        pbar = tqdm(total=len(to_translate), desc="translating", unit="token")

        async def translate_token(token: Token, translator: Translator) -> None:
            token.content = await translator.translate(token.content)
            pbar.update(1)

        for token in to_translate:
            tg.create_task(translate_token(token, translator))

    options = dict(parser.options) | {"parser_extension": [mdformat_tables, _MathExtension]}
    return MDRenderer().render(tokens, options, {})
