# markdown-to-html

An [Agent Skill](https://agentskills.io) that converts a Markdown file into one self-contained HTML page with a navigation sidebar, full-text search, rendered Mermaid diagrams, print/PDF styles and a System/Light/Dark theme switcher. All CSS, JavaScript and local images are embedded, so the page opens with a double click and can be sent by email.

- [markdown-to-html](#markdown-to-html)
  - [Contents](#contents)
  - [Usage](#usage)
  - [Features](#features)
  - [Document conventions](#document-conventions)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Claude Code](#claude-code)
    - [Claude apps (claude.ai, Desktop)](#claude-apps-claudeai-desktop)
    - [Other agents](#other-agents)
    - [Migrating from the earlier slash command](#migrating-from-the-earlier-slash-command)
    - [Validation](#validation)
  - [Running without an agent](#running-without-an-agent)
  - [Output and errors](#output-and-errors)
  - [Licenses](#licenses)
  - [Customizing](#customizing)

## Contents

```
markdown-to-html/
├── SKILL.md                  # instructions for the agent
├── README.md                 # this file (for people)
├── scripts/
│   └── markdown_to_html.py   # the converter
└── assets/
    ├── mermaid.min.js        # Mermaid 11.17.2, embedded only when needed
    └── mermaid.LICENSE.txt   # Mermaid's MIT license
```

## Usage

In Claude Code, call the skill directly:

```
/markdown-to-html <markdown-file> <language-code> [output-file]
```

or just ask, e.g. "Convert docs/requirements.md to HTML, German". The agent picks the skill on its own.

| Parameter | Required | Description |
|---|---|---|
| `markdown-file` | yes | Relative path to the source Markdown file. |
| `language-code` | yes | Two-letter language code (`de`, `en`, `ru` …). Sets the page's `lang` attribute, the UI labels and the date format. The document text is not translated. |
| `output-file` | no | Relative path to the HTML file. Default: next to the source file, same name, extension `.html`. Missing folders are created; an existing file is overwritten. |

Examples:

```
/markdown-to-html docs/requirements.md de
/markdown-to-html docs/requirements.md en build/requirements-en.html
```

## Features

- **Header** with title, subtitle, search field, print button and theme switcher.
- **Themes:** System (default), Light, Dark. The choice is remembered in the browser; printing always uses the light theme.
- **Sidebar** built from three heading levels: collapsible sections, current section highlighted while scrolling, permalink anchors. The button at its top right hides it, and the content then uses the full window width; a button pinned to the left edge below the header shows it again. The choice is remembered in the browser.
- **Search** across the whole text: highlighted matches, counter, Enter / Shift+Enter between matches, sidebar filtered to matching sections. Ctrl+K focuses, Esc clears.
- **Cards** for top-level sections; styled tables (horizontal scroll when wide), code blocks and quotes. The **Full width** button in the header widens the cards from reading width to the whole content area (remembered in the browser).
- **Mobile:** the sidebar becomes a slide-in menu.
- **Print / PDF:** no header or sidebar, no breaks inside tables and code, external links printed with their URL. When the page is shown in a sandboxed frame that blocks printing (editor previews, chat viewers), the button reopens it in a new tab that prints itself, or, if popups are blocked as well, shows a hint to open the file in a browser.
- **Mermaid diagrams:** ` ```mermaid ` code blocks become diagrams, drawn in matching colors for the light and the dark theme, with an Enlarge button that opens the diagram full width. The library is embedded only when the document contains diagrams (about 3.5 MB extra), so the page still works offline. A diagram with a syntax error is shown as code with an error note.
- **Images** from local paths are embedded.
- **UI languages:** `de`, `en`, `ru`, `uk`, `fr`, `es`, `it`; other codes fall back to English.

## Document conventions

- A single leading `#` heading becomes the page title and the `##` sections become cards; otherwise the `#` headings are the cards.
- A hand-written table of contents ("Contents", "Inhalt", "Inhaltsverzeichnis", "Оглавление" …) and the `[TOC]` marker are removed, since the sidebar replaces them.
- Title and subtitle can be set with front matter:

  ```
  ---
  title: Horizon / Phase 0
  subtitle: MI Hub · Anforderungen v03 · 03.11.2026
  ---
  ```

  Without it, the subtitle shows the file name and its last modification date.

## Installation

### Requirements

- Python 3.8 or newer, available as `python` (on Windows `py` also works).
- The `markdown` package, installed once:

  ```
  pip install "markdown>=3.4"
  ```

### Claude Code

Copy the whole `markdown-to-html` folder into your personal skills folder, so that the file ends up at `~/.claude/skills/markdown-to-html/SKILL.md` (on Windows `C:\Users\<name>\.claude\skills\markdown-to-html\SKILL.md`).

Windows (PowerShell), from the folder that contains `markdown-to-html`:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force markdown-to-html "$HOME\.claude\skills\"
```

macOS / Linux:

```bash
mkdir -p ~/.claude/skills
cp -R markdown-to-html ~/.claude/skills/
```

For a single project only, use `<project>/.claude/skills/markdown-to-html/` instead; the folder can then be committed to the repository and shared with the team.

Start a new Claude Code session afterwards. Check that `/markdown-to-html` appears when you type `/`, or ask "Which skills do you have?".

### Claude apps (claude.ai, Desktop)

Zip the `markdown-to-html` folder (the zip must contain the folder itself) and upload it under Settings → Capabilities → Skills. Note that there the agent works in a cloud sandbox, so the Markdown file has to be uploaded to the chat.

### Other agents

Any agent that supports the Agent Skills format and can run shell commands can use the folder as is. Put it into that agent's skills directory; see the [client showcase](https://agentskills.io/clients.md) and the agent's own documentation for the location.

### Migrating from the earlier slash command

If you installed the previous `/markdown-to-html` command, remove it so that it does not clash with the skill of the same name:

- `~/.claude/commands/markdown-to-html.md`
- `~/.claude/scripts/markdown_to_html.py`

### Validation

The folder follows the [Agent Skills specification](https://agentskills.io/specification.md) and can be checked with the reference validator:

```
skills-ref validate ./markdown-to-html
```

## Running without an agent

The script also works on its own, without any token usage:

```
python markdown-to-html/scripts/markdown_to_html.py docs/requirements.md de
```

## Output and errors

| Output | Meaning |
|---|---|
| `OK: <path> (…)` | File created; the brackets show sections, navigation entries, diagrams, language and size. |
| `… left as code: … mermaid.min.js not found` | The `assets` folder is missing; diagrams stay as code. Reinstall the complete skill folder. |
| `ERROR: Markdown file not found` | The source path is wrong. |
| `ERROR: language code must be two letters` | The language code is not two letters. |
| `ERROR: Python package 'markdown' is missing` | Run `pip install markdown`. |
| `USAGE: …` | Required parameters are missing. |

## Licenses

Mermaid is © Knut Sveidqvist and contributors, MIT license; see `assets/mermaid.LICENSE.txt`.

## Customizing

Colors are in `LIGHT_TOKENS` and `DARK_TOKENS`, layout and typography in `CSS`, behaviour in `JS` and UI texts in `LABELS` inside `scripts/markdown_to_html.py`. You can also ask the agent to change the design; the skill tells it where to look.
