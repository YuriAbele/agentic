---
name: markdown-to-html
description: Converts a Markdown file into one self-contained HTML page with a collapsible navigation sidebar, full-text search, rendered Mermaid diagrams, print/PDF styles and a System/Light/Dark theme switcher. Use whenever the user wants to turn a .md file into HTML, a readable or shareable page, or a documentation page with navigation, or asks to render, publish, export or convert Markdown to HTML, even if they don't name this skill.
compatibility: Requires Python 3.8+ with the "markdown" package (pip install markdown) and an agent that can run shell commands.
allowed-tools: Bash(python:*) Bash(py:*) Bash(pip:*)
metadata:
  author: yuab
  version: "1.1"
---

# Markdown to HTML

The bundled script `scripts/markdown_to_html.py` does the whole conversion. Your job is to pick the parameters, run it once, and report the result. The script is deterministic and already tested, so there is no need to read the Markdown file, read or rewrite the script, or open the generated HTML: that would only spend tokens without improving the result.

## Parameters

| Parameter | Required | Meaning |
|---|---|---|
| `markdown-file` | yes | Relative path to the source Markdown file. |
| `language-code` | yes | Two-letter code (`de`, `en`, `ru` …): page `lang`, UI labels, date format. The text itself is not translated. |
| `output-file` | no | Relative path to the HTML file. Default: same path as the Markdown file with the extension `.html`. |

When invoked as `/markdown-to-html <markdown-file> <language-code> [output-file]`, the arguments come in this order. In a natural-language request, take them from the wording ("convert docs/req.md to HTML, German" → `docs/req.md de`).

If the language is not stated, infer it from the request; if that is not possible, look at the first 20 lines of the file only. If the Markdown file is not named or is ambiguous, ask one short question.

## Run

From the user's working directory (so relative paths resolve), with `<skill-dir>` being the folder that contains this SKILL.md:

```bash
python "<skill-dir>/scripts/markdown_to_html.py" "<markdown-file>" "<language-code>" "<output-file>"
```

Leave out the third argument when no output file was given. On Windows, use `py` if `python` is not found. For several files, run the script once per file.

## Report

The script prints exactly one line:

- `OK: <path> (…)` → tell the user the path in one sentence.
- `ERROR: Python package 'markdown' is missing` → run `pip install markdown`, then run the script again.
- `ERROR: …` or `USAGE: …` → explain the problem in one sentence and fix the parameters if the cause is obvious (e.g. a typo in the path).

## What the page contains

Use this to answer questions about the output without opening it:

- Dark header with title, subtitle, search (Ctrl+K, Enter / Shift+Enter between matches, Esc clears), Print / PDF button and a System / Light / Dark theme switcher (System is the default; the choice is remembered in the browser).
- Left sidebar built from three heading levels, collapsible, highlights the current section while scrolling; slide-in menu on narrow screens.
- Each top-level section as a card; styled tables, code, quotes; local images embedded; print styles without header and sidebar.
- ` ```mermaid ` code blocks rendered as diagrams in matching light and dark colors, with an Enlarge button. The bundled `assets/mermaid.min.js` (Mermaid 11.17.2, MIT) is embedded only when the document has diagrams, adding about 3.5 MB. A diagram with a syntax error stays visible as code with an error note; the `OK:` line reports the number of diagrams.
- UI labels for `de en ru uk fr es it`; other codes fall back to English.

## Document conventions

- A single leading `#` heading becomes the page title, and `##` sections become cards; otherwise `#` headings are the cards.
- Optional front matter sets the header text:

  ```
  ---
  title: Horizon / Phase 0
  subtitle: MI Hub · Anforderungen v03
  ---
  ```

- A hand-written table of contents ("Contents", "Inhalt", "Оглавление" …) and `[TOC]` are dropped, because the sidebar replaces them.

## Changing the design

Only when the user asks to change how the page looks or behaves: edit `scripts/markdown_to_html.py`. Colors are in `LIGHT_TOKENS` and `DARK_TOKENS`, layout and typography in `CSS`, behaviour in `JS`, UI texts in `LABELS`. Make the smallest edit that does the job and rerun the conversion.
