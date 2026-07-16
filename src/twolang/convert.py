"""Convert a document to Markdown via MinerU's Python API."""

import asyncio
import shutil
from pathlib import Path

from loguru import logger
from mineru.cli.backend_options import DEFAULT_BACKEND
from mineru.cli.client import run_orchestrated_cli


def convert(source_path: Path) -> list[Path]:
    """Convert a document to Markdown."""

    if source_path.suffix.lower() == ".md" and source_path.is_file():
        logger.info("Input is already markdown, skipping conversion")
        return [source_path]

    output_dir = source_path.parent / f"{source_path.stem}.md"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    md_files = run_mineru(source_path, output_dir)

    if not md_files:
        raise ValueError(f"No markdown files to process under {output_dir}")

    return md_files


def run_mineru(path: Path, output: Path) -> list[Path]:
    logger.info(f"Converting {path} with mineru ({DEFAULT_BACKEND} backend)")
    # Same call the `mineru` CLI makes, with its defaults
    asyncio.run(
        run_orchestrated_cli(
            input_path=path,
            output_dir=output,
            method="auto",
            backend=DEFAULT_BACKEND,
            lang="ch",
            server_url=None,
            api_url=None,
            start_page_id=0,
            end_page_id=None,
            formula_enable=True,
            table_enable=True,
        )
    )

    return sorted(output.rglob("*.md"))
