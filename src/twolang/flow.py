import asyncio
from pathlib import Path

from twolang.convert import convert
from twolang.translate import translate


def main_flow(source_path: Path, target_lang: str, source_lang: str | None):
    md_files = convert(source_path)
    asyncio.run(
        translate(
            md_files=md_files,
            source_lang=source_lang,
            target_lang=target_lang,
        )
    )
