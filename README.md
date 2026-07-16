# 2lang

[![CI](https://github.com/yushkou/2lang/actions/workflows/ci.yml/badge.svg)](https://github.com/yushkou/2lang/actions/workflows/ci.yml)

Convert documents to Markdown with [MinerU](https://github.com/opendatalab/mineru), then translate
the prose to a target language — keeping code blocks, formulas, links and table structure intact.

## How it works

1. **Convert** — the input document (pdf, image, docx, pptx, xlsx) is converted to Markdown via
   MinerU's Python API (`hybrid-engine` backend, same defaults as the `mineru` CLI). If the input
   is already a `.md` file, conversion is skipped.
2. **Detect** — the source language comes from `-sl/--source-lang`, or is auto-detected with
   `langdetect` (the detected language is printed in the log).
3. **Translate** — the Markdown is parsed with `markdown-it-py`; a generator picks out only the
   tokens that carry prose, and they are translated concurrently (`asyncio.TaskGroup`, at most 5
   requests in flight, retries with exponential backoff via `tenacity`). Code fences, inline code,
   `$...$` / `$$...$$` math and link targets live in other token types and never reach the
   translator; text inside MinerU's raw HTML tables is translated too. The result is rendered back
   to Markdown with `mdformat`.

Translation is done by `deep-translator` through Google Translate's free web endpoint, so any
language pair Google supports works (e.g. `lv`, `pl`, `de`, `ru`, `zh-CN`).

> Note: translated text segments are sent to Google's free translate endpoint. Nothing else
> (images, code, formulas, the original file) leaves the machine.

## Usage

```bash
# Convert a PDF and translate it to Russian (source language auto-detected)
2lang -p inputs/document.pdf -tl ru

# Explicit source language, translate to Polish
2lang -p inputs/document.pdf -sl en -tl pl

# Already have markdown? Conversion is skipped
2lang -p notes.md -tl lv
```

| Option | Description |
| --- | --- |
| `-p, --path` | (mandatory) input document or `.md` file |
| `-tl, --target-lang` | (mandatory) language to translate into, e.g. `lv`, `pl`, `de`, `zh-CN` |
| `-sl, --source-lang` | (optional) source language; auto-detected when omitted |

MinerU's output goes to `<name>.md/` next to the input file; the translation is saved alongside
the converted Markdown as `<name>.<target-lang>.md`.

## Example

Input (`report.md`, or a PDF that converts to it):

````markdown
# Quarterly Report

The company grew revenue by 12% compared to the previous quarter.

Key formula: $R = P \cdot (1 + g)^t$

| Metric | Value |
| --- | --- |
| Revenue | 4.2M EUR |

```python
revenue = 4_200_000  # keep this code intact
```
````

Output of `2lang -p report.md -tl lv` (`report.lv.md`):

````markdown
# Ceturkšņa pārskats

Uzņēmums palielināja ieņēmumus par 12%, salīdzinot ar iepriekšējo ceturksni.

Galvenā formula: $R = P \cdot (1 + g)^t$

| Metrika  | Vērtība          |
| -------- | ---------------- |
| Ieņēmumi | 4,2 miljoni eiro |

```python
revenue = 4_200_000  # keep this code intact
```
````

The prose is translated; the formula, the code block and the table layout survive untouched.

## Requirements

- Python ≥ 3.14.2 and [uv](https://docs.astral.sh/uv/)
- The first conversion downloads MinerU's models (several GB); on Apple Silicon the `mlx` engine
  is installed automatically

## Development

```bash
uv sync                        # install dependencies (incl. dev group)
uv run pre-commit install      # ruff + ty on every commit
uv run pytest                  # unit tests (offline)
uv run pytest -m integration   # tests that hit the real translate endpoint
```
