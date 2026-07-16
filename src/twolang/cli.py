"""2lang CLI: MinerU-style document conversion, extended with translation."""

from pathlib import Path
from typing import Annotated

import typer

from twolang.flow import main_flow

cli = typer.Typer(add_completion=False, rich_markup_mode=None)


@cli.command()
def main(
    path: Annotated[
        Path,
        typer.Option(
            "-p",
            "--path",
            exists=True,
            help="...",
        ),
    ],
    target_lang: Annotated[
        str,
        typer.Option(
            "-tl",
            "--target-lang",
            help="Language to translate the converted markdown into (e.g. lv, pl, de)",
        ),
    ],
    source_lang: Annotated[
        str | None,
        typer.Option(
            "-sl",
            "--source-lang",
            help="Language of the converted markdown (auto-detected if not specified)",
        ),
    ] = None,
) -> None:
    main_flow(
        source_path=path,
        source_lang=source_lang,
        target_lang=target_lang,
    )


if __name__ == "__main__":
    cli()
