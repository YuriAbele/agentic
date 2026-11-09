#!/usr/bin/env python3
"""
markdown_to_html.py - convert a Markdown file into one self-contained HTML page.

Page: dark header (title, search with Ctrl+K, print button, theme switcher
System / Light / Dark, full-width toggle), collapsible and hideable left
navigation with scroll spy, sections as cards, print styles, responsive slide-in menu on small screens.

Usage:
    python markdown_to_html.py <markdown-file> <language-code> [output-file]

Requires the Python package "markdown" (pip install markdown).
Optional front matter at the top of the Markdown file:
    ---
    title: Horizon / Phase 0
    subtitle: MI Hub - Anforderungen v03
    ---
"""
import base64
import datetime
import html
import json
import mimetypes
import re
import sys
from pathlib import Path

try:
    import markdown
    from markdown.extensions.toc import TocExtension, slugify_unicode
except ImportError:
    print("ERROR: Python package 'markdown' is missing. Install it with: pip install markdown")
    sys.exit(3)

USAGE = "USAGE: markdown_to_html.py <markdown-file> <language-code> [output-file]"

LABELS = {
    "en": {"search": "Search term or ID …", "kbd": "Ctrl K", "clear": "Clear search",
           "print": "Print / PDF", "toc": "In this document", "no_results": "No results",
           "menu": "Table of contents", "theme": "Theme", "system": "System", "light": "Light",
           "dark": "Dark", "permalink": "Link to this section", "toggle": "Expand or collapse",
           "diagram": "Diagram", "enlarge": "Enlarge", "close": "Close", "diagram_error": "Diagram could not be rendered",
           "print_blocked": "Printing is blocked by the app that shows this page. Open the HTML file directly in a web browser to print or save it as PDF.",
           "nav_hide": "Hide navigation", "nav_show": "Show navigation", "full_width": "Full width"},
    "de": {"search": "Begriff oder ID suchen …", "kbd": "Strg K", "clear": "Suche leeren",
           "print": "Drucken / PDF", "toc": "Im Dokument", "no_results": "Keine Treffer",
           "menu": "Inhaltsverzeichnis", "theme": "Darstellung", "system": "System", "light": "Hell",
           "dark": "Dunkel", "permalink": "Link zu diesem Abschnitt", "toggle": "Auf- oder zuklappen",
           "diagram": "Diagramm", "enlarge": "Vergrößern", "close": "Schließen", "diagram_error": "Diagramm konnte nicht dargestellt werden",
           "print_blocked": "Die Anwendung, die diese Seite anzeigt, blockiert das Drucken. Öffnen Sie die HTML-Datei direkt im Browser, um sie zu drucken oder als PDF zu speichern.",
           "nav_hide": "Navigation ausblenden", "nav_show": "Navigation einblenden", "full_width": "Volle Breite"},
    "ru": {"search": "Поиск по тексту или ID …", "kbd": "Ctrl K", "clear": "Очистить поиск",
           "print": "Печать / PDF", "toc": "В документе", "no_results": "Ничего не найдено",
           "menu": "Оглавление", "theme": "Тема", "system": "Системная", "light": "Светлая",
           "dark": "Тёмная", "permalink": "Ссылка на раздел", "toggle": "Развернуть или свернуть",
           "diagram": "Диаграмма", "enlarge": "Увеличить", "close": "Закрыть", "diagram_error": "Не удалось отрисовать диаграмму",
           "print_blocked": "Приложение, в котором открыта страница, блокирует печать. Откройте HTML-файл напрямую в браузере, чтобы распечатать его или сохранить в PDF.",
           "nav_hide": "Скрыть навигацию", "nav_show": "Показать навигацию", "full_width": "На всю ширину"},
    "uk": {"search": "Пошук за текстом або ID …", "kbd": "Ctrl K", "clear": "Очистити пошук",
           "print": "Друк / PDF", "toc": "У документі", "no_results": "Нічого не знайдено",
           "menu": "Зміст", "theme": "Тема", "system": "Системна", "light": "Світла",
           "dark": "Темна", "permalink": "Посилання на розділ", "toggle": "Розгорнути або згорнути",
           "diagram": "Діаграма", "enlarge": "Збільшити", "close": "Закрити", "diagram_error": "Не вдалося відобразити діаграму",
           "print_blocked": "Застосунок, у якому відкрито сторінку, блокує друк. Відкрийте HTML-файл безпосередньо в браузері, щоб надрукувати його або зберегти у PDF.",
           "nav_hide": "Сховати навігацію", "nav_show": "Показати навігацію", "full_width": "На всю ширину"},
    "fr": {"search": "Rechercher un terme ou un ID …", "kbd": "Ctrl K", "clear": "Effacer la recherche",
           "print": "Imprimer / PDF", "toc": "Dans ce document", "no_results": "Aucun résultat",
           "menu": "Table des matières", "theme": "Thème", "system": "Système", "light": "Clair",
           "dark": "Sombre", "permalink": "Lien vers cette section", "toggle": "Déplier ou replier",
           "diagram": "Diagramme", "enlarge": "Agrandir", "close": "Fermer", "diagram_error": "Impossible d’afficher le diagramme",
           "print_blocked": "L’application qui affiche cette page bloque l’impression. Ouvrez le fichier HTML directement dans un navigateur pour l’imprimer ou l’enregistrer en PDF.",
           "nav_hide": "Masquer la navigation", "nav_show": "Afficher la navigation", "full_width": "Pleine largeur"},
    "es": {"search": "Buscar término o ID …", "kbd": "Ctrl K", "clear": "Borrar búsqueda",
           "print": "Imprimir / PDF", "toc": "En este documento", "no_results": "Sin resultados",
           "menu": "Índice", "theme": "Tema", "system": "Sistema", "light": "Claro",
           "dark": "Oscuro", "permalink": "Enlace a esta sección", "toggle": "Expandir o contraer",
           "diagram": "Diagrama", "enlarge": "Ampliar", "close": "Cerrar", "diagram_error": "No se pudo mostrar el diagrama",
           "print_blocked": "La aplicación que muestra esta página bloquea la impresión. Abra el archivo HTML directamente en un navegador para imprimirlo o guardarlo como PDF.",
           "nav_hide": "Ocultar navegación", "nav_show": "Mostrar navegación", "full_width": "Ancho completo"},
    "it": {"search": "Cerca termine o ID …", "kbd": "Ctrl K", "clear": "Cancella ricerca",
           "print": "Stampa / PDF", "toc": "In questo documento", "no_results": "Nessun risultato",
           "menu": "Indice", "theme": "Tema", "system": "Sistema", "light": "Chiaro",
           "dark": "Scuro", "permalink": "Link a questa sezione", "toggle": "Espandi o comprimi",
           "diagram": "Diagramma", "enlarge": "Ingrandisci", "close": "Chiudi", "diagram_error": "Impossibile visualizzare il diagramma",
           "print_blocked": "L’applicazione che mostra questa pagina blocca la stampa. Apri il file HTML direttamente in un browser per stamparlo o salvarlo come PDF.",
           "nav_hide": "Nascondi navigazione", "nav_show": "Mostra navigazione", "full_width": "Larghezza piena"},
}

# Names of hand-written tables of contents; such a section is dropped
# because the sidebar replaces it.
MANUAL_TOC_NAMES = re.compile(
    r"^\s*(table of contents|contents|toc|inhalt|inhaltsverzeichnis|оглавление|содержание|зміст|"
    r"sommaire|table des matières|índice|indice|sommario)\s*$", re.I)


def fail(msg, code=1):
    print(f"ERROR: {msg}")
    sys.exit(code)


def split_front_matter(text):
    meta = {}
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n(?:---|\.\.\.)[ \t]*\r?\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip().lower()] = value.strip().strip("'\"")
        text = text[m.end():]
    return meta, text


def plain(name):
    """toc_tokens names are HTML-escaped; return clean escaped text."""
    return html.escape(html.unescape(name), quote=False)


def flatten(tokens):
    for t in tokens:
        yield t
        yield from flatten(t["children"])


def inline_images(body, base_dir):
    def repl(m):
        src = html.unescape(m.group(2))
        if re.match(r"^(?:[a-z]+:|//|#)", src, re.I):
            return m.group(0)
        path = (base_dir / src.split("?")[0].split("#")[0]).resolve()
        if not path.is_file() or path.stat().st_size > 15 * 1024 * 1024:
            return m.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'{m.group(1)}data:{mime};base64,{data}{m.group(3)}'
    return re.sub(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', repl, body)


MERMAID_BLOCK = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.S)
MERMAID_ASSET = Path(__file__).resolve().parent.parent / "assets" / "mermaid.min.js"


def mermaid_figures(body, label):
    """Replace ```mermaid code blocks with figures that the page script renders."""
    count = 0

    def repl(m):
        nonlocal count
        count += 1
        return (f'<figure class="diagram"><div class="diagram-bar"><span>{label} {count}</span>'
                f'<button class="diagram-zoom" type="button" hidden>__L_ENLARGE__</button></div>'
                f'<pre class="diagram-src">{m.group(1)}</pre><div class="diagram-out" hidden></div></figure>')
    return MERMAID_BLOCK.sub(repl, body), count


def mermaid_script():
    """Inline the bundled Mermaid library; fall back to a data: URI if it contains a closing script tag."""
    code = MERMAID_ASSET.read_text(encoding="utf-8")
    if re.search(r"</script", code, re.I):
        data = base64.b64encode(code.encode("utf-8")).decode("ascii")
        return f'<script src="data:text/javascript;base64,{data}"></script>'
    return f"<script>{code}</script>"


ICON_CHEVRON = ('<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">'
                '<path d="M6 3.5 10.5 8 6 12.5" fill="none" stroke="currentColor" stroke-width="1.6" '
                'stroke-linecap="round" stroke-linejoin="round"/></svg>')
ICON_SYSTEM = ('<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><rect x="2.5" y="3.5" '
               'width="15" height="10" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/>'
               '<path d="M7 17h6M10 13.5V17" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>')
ICON_LIGHT = ('<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><circle cx="10" cy="10" r="3.5" '
              'fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 1.8v2M10 16.2v2M1.8 10h2M16.2 10h2'
              'M4.2 4.2l1.4 1.4M14.4 14.4l1.4 1.4M4.2 15.8l1.4-1.4M14.4 5.6l1.4-1.4" stroke="currentColor" '
              'stroke-width="1.5" stroke-linecap="round"/></svg>')
ICON_DARK = ('<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><path d="M16.5 12.4A7 7 0 0 1 7.6 3.5'
             'a7 7 0 1 0 8.9 8.9Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>')
ICON_PRINT = ('<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><path d="M5.5 7V2.5h9V7M5.5 14.5h-2'
              'a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1h13a1 1 0 0 1 1 1v5.5a1 1 0 0 1-1 1h-2M5.5 11.5h9v6h-9z" fill="none" '
              'stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>')
ICON_MENU = ('<svg viewBox="0 0 20 20" width="20" height="20" aria-hidden="true"><path d="M3 5.5h14M3 10h14M3 14.5h14" '
             'stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>')
ICON_CLOSE = ('<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8" '
              'stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>')
ICON_NAV_HIDE = ('<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><rect x="2.5" y="3.5" width="15" '
                 'height="13" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M7.5 3.5v13'
                 'M13.5 7.5 11 10l2.5 2.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
                 'stroke-linejoin="round"/></svg>')
ICON_NAV_SHOW = ('<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><rect x="2.5" y="3.5" width="15" '
                 'height="13" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M7.5 3.5v13'
                 'M11 7.5l2.5 2.5-2.5 2.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
                 'stroke-linejoin="round"/></svg>')
ICON_WIDTH = ('<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><path d="M2.5 4v12M17.5 4v12M5.5 10h9'
              'M8 7.5 5.5 10 8 12.5M12 7.5l2.5 2.5-2.5 2.5" fill="none" stroke="currentColor" stroke-width="1.5" '
              'stroke-linecap="round" stroke-linejoin="round"/></svg>')

LIGHT_TOKENS = """
  color-scheme: light;
  --bg: #edf2f5;
  --surface: #ffffff;
  --sidebar: #f7f9fb;
  --border: #dce4ea;
  --text: #22313f;
  --muted: #5d6d7b;
  --heading: #16304a;
  --strong: #14212e;
  --link: #1a6b8f;
  --accent: #2a8574;
  --accent-text: #1c5e52;
  --accent-soft: #dcefe8;
  --hover: #e9eff3;
  --header-bg: #17364b;
  --header-text: #ffffff;
  --header-muted: #bfd0dc;
  --header-line: rgba(255, 255, 255, 0.32);
  --header-chip: rgba(255, 255, 255, 0.16);
  --input-bg: #ffffff;
  --input-text: #22313f;
  --input-muted: #6b7a87;
  --code-bg: #f1f5f8;
  --zebra: #f8fafb;
  --mark: #ffe38a;
  --mark-text: #22313f;
  --mark-current: #ffb547;
  --backdrop: rgba(12, 24, 36, 0.38);
  --danger: #b3261e;
"""

DARK_TOKENS = """
  color-scheme: dark;
  --bg: #0f171f;
  --surface: #16212b;
  --sidebar: #121c25;
  --border: #253443;
  --text: #d6e0e8;
  --muted: #8fa1b1;
  --heading: #eaf1f6;
  --strong: #f3f7fa;
  --link: #7cc3e6;
  --accent: #5fc2ad;
  --accent-text: #8edbc9;
  --accent-soft: rgba(95, 194, 173, 0.15);
  --hover: #1c2935;
  --header-bg: #0c1924;
  --header-text: #eef4f8;
  --header-muted: #8ea5b8;
  --header-line: rgba(255, 255, 255, 0.2);
  --header-chip: rgba(255, 255, 255, 0.12);
  --input-bg: #182532;
  --input-text: #e3ebf2;
  --input-muted: #8193a3;
  --code-bg: #101a23;
  --zebra: #19252f;
  --mark: #6d5513;
  --mark-text: #fff4cc;
  --mark-current: #b9761c;
  --backdrop: rgba(0, 0, 0, 0.55);
  --danger: #f2a39b;
"""

CSS = """
:root {__LIGHT__
  --header-h: 76px;
  --sidebar-w: 320px;
  --font: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Roboto, Arial, sans-serif;
  --mono: "Cascadia Code", Consolas, "SFMono-Regular", Menlo, "Liberation Mono", monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {__DARK__}
  :root:not([data-theme="light"]) .mm-light { display: none; }
  :root:not([data-theme="light"]) .mm-dark { display: block; }
}
:root[data-theme="dark"] {__DARK__}
:root[data-theme="dark"] .mm-light { display: none; }
:root[data-theme="dark"] .mm-dark { display: block; }

*, *::before, *::after { box-sizing: border-box; }
html { scroll-padding-top: calc(var(--header-h) + 20px); -webkit-text-size-adjust: 100%; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
body { margin: 0; background: var(--bg); color: var(--text); font: 17px/1.65 var(--font); }
button, input { font: inherit; color: inherit; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* Header */
.topbar { position: sticky; top: 0; z-index: 30; display: flex; align-items: center; gap: 20px;
  padding: 14px 28px; background: var(--header-bg); color: var(--header-text);
  border-bottom: 1px solid var(--header-line); }
.menu-btn { display: none; flex: none; width: 42px; height: 42px; align-items: center; justify-content: center;
  border: 1px solid var(--header-line); border-radius: 8px; background: transparent; cursor: pointer; }
.brand { min-width: 0; flex: 0 1 auto; }
.doc-title { margin: 0; font-size: 1.6rem; line-height: 1.2; font-weight: 700; letter-spacing: -0.01em;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.doc-sub { margin: 2px 0 0; font-size: 0.88rem; color: var(--header-muted); white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; }
.search { position: relative; flex: 1 1 380px; max-width: 700px; margin-left: auto; display: flex; align-items: center; }
.search input { width: 100%; height: 46px; padding: 0 150px 0 16px; border: 1px solid transparent; border-radius: 8px;
  background: var(--input-bg); color: var(--input-text); outline: none; }
.search input::placeholder { color: var(--input-muted); }
.search input::-webkit-search-cancel-button, .search input::-webkit-search-decoration { -webkit-appearance: none; appearance: none; }
.search input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
.search-meta { position: absolute; right: 8px; display: flex; align-items: center; gap: 6px; color: var(--input-muted);
  font-size: 0.85rem; pointer-events: none; }
.search-meta > * { pointer-events: auto; }
.kbd { padding: 1px 6px; border: 1px solid var(--border); border-radius: 5px; font-size: 0.78rem; white-space: nowrap; }
.search.has-value .kbd, .search input:focus ~ .search-meta .kbd { display: none; }
.count { white-space: nowrap; }
.clear { display: none; width: 30px; height: 30px; align-items: center; justify-content: center; border: 0; border-radius: 6px;
  background: transparent; color: var(--input-muted); cursor: pointer; }
.search.has-value .clear { display: inline-flex; }
.clear:hover { background: var(--hover); color: var(--input-text); }
.actions { display: flex; align-items: center; gap: 12px; flex: none; }
.btn-print { display: inline-flex; align-items: center; gap: 8px; height: 46px; padding: 0 16px;
  border: 1px solid var(--header-line); border-radius: 8px; background: transparent; cursor: pointer; white-space: nowrap; }
.btn-width { width: 46px; height: 46px; display: inline-flex; align-items: center; justify-content: center;
  border: 1px solid var(--header-line); border-radius: 8px; background: transparent; cursor: pointer; }
.btn-width[aria-pressed="true"] { background: var(--header-chip); border-color: var(--header-muted); }
.btn-print:hover, .menu-btn:hover, .btn-width:hover { background: var(--header-chip); }
.theme-switch { display: inline-flex; gap: 2px; padding: 3px; border: 1px solid var(--header-line); border-radius: 9px; }
.theme-switch button { width: 38px; height: 38px; display: inline-flex; align-items: center; justify-content: center;
  border: 0; border-radius: 6px; background: transparent; color: var(--header-muted); cursor: pointer; }
.theme-switch button:hover { color: var(--header-text); }
.theme-switch button[aria-checked="true"] { background: var(--header-chip); color: var(--header-text); }

/* Layout */
.layout { display: grid; grid-template-columns: var(--sidebar-w) minmax(0, 1fr); }
.sidebar { position: sticky; top: var(--header-h); height: calc(100vh - var(--header-h)); overflow-y: auto;
  padding: 26px 14px 48px 22px; background: var(--sidebar); border-right: 1px solid var(--border);
  scrollbar-width: thin; scrollbar-color: var(--border) transparent; }
.toc-top { position: sticky; top: -26px; z-index: 2; display: flex; align-items: center; justify-content: space-between;
  gap: 8px; margin: -26px -14px 6px -22px; padding: 14px 10px 8px 36px; background: var(--sidebar); }
.toc-head { margin: 0; font-size: 0.92rem; color: var(--muted); }
.nav-hide { flex: none; width: 36px; height: 36px; display: inline-flex; align-items: center; justify-content: center;
  border: 0; border-radius: 6px; background: transparent; color: var(--muted); cursor: pointer; }
.nav-hide:hover { background: var(--hover); color: var(--text); }
.nav-show { display: none; position: fixed; z-index: 15; left: 0; top: calc(var(--header-h) + 16px); width: 42px; height: 42px;
  align-items: center; justify-content: center; padding: 0; background: var(--surface); color: var(--muted);
  border: 1px solid var(--border); border-left: 0; border-radius: 0 8px 8px 0; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer; }
.nav-show:hover { background: var(--hover); color: var(--text); }
.toc-list { list-style: none; margin: 0; padding: 0; }
.toc-list .toc-list { display: none; margin: 4px 0 10px 26px; padding-left: 8px; border-left: 1px solid var(--border); }
li.open > .toc-list { display: block; }
.toc-row { display: flex; align-items: flex-start; gap: 2px; }
.toc-link { flex: 1; min-width: 0; display: block; padding: 9px 12px 9px 13px; border-left: 3px solid transparent;
  border-radius: 6px; color: var(--text); text-decoration: none; line-height: 1.4; font-size: 0.98rem; }
.toc-list .toc-list .toc-link { padding: 7px 10px; font-size: 0.9rem; color: var(--muted); }
.toc-link:hover { background: var(--hover); }
.toc-link.in-trail { color: var(--accent-text); }
.toc-link.active { background: var(--accent-soft); border-left-color: var(--accent); color: var(--accent-text); font-weight: 600; }
.toc-toggle { flex: none; width: 34px; height: 40px; display: inline-flex; align-items: center; justify-content: center;
  border: 0; border-radius: 6px; background: transparent; color: var(--muted); cursor: pointer; }
.toc-toggle:hover { background: var(--hover); color: var(--text); }
.toc-toggle svg { transition: transform 0.15s ease; }
li.open > .toc-row > .toc-toggle svg { transform: rotate(90deg); }
.toc-empty { margin: 8px 14px; color: var(--muted); font-size: 0.92rem; }
.backdrop { display: none; }

/* Content */
main { min-width: 0; padding: 30px 36px 90px; }
.card { max-width: 920px; margin: 0 auto 28px; padding: 32px 44px 36px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 12px; }
main h1, main h2, main h3, main h4, main h5, main h6 { color: var(--heading); line-height: 1.25; font-weight: 700;
  margin: 1.6em 0 0.6em; }
.card > :first-child { margin-top: 0; }
[data-top="1"] main h1, [data-top="2"] main h2 { font-size: 2.15rem; letter-spacing: -0.015em; margin-bottom: 0.7em; }
[data-top="1"] main h2, [data-top="2"] main h3 { font-size: 1.55rem; }
[data-top="1"] main h3, [data-top="2"] main h4 { font-size: 1.22rem; }
main h5, main h6, [data-top="2"] main h5 { font-size: 1.05rem; }
.headerlink { margin-left: 0.35em; color: var(--muted); text-decoration: none; font-weight: 400; opacity: 0; }
main :is(h1, h2, h3, h4, h5, h6):hover .headerlink, .headerlink:focus-visible { opacity: 1; }
main p { margin: 0.8em 0; }
main a { color: var(--link); text-underline-offset: 0.15em; }
main strong { color: var(--strong); font-weight: 650; }
main ul, main ol { padding-left: 1.6em; margin: 0.8em 0; }
main li { margin: 0.4em 0; padding-left: 0.2em; }
main li::marker { color: var(--muted); }
main hr { border: 0; border-top: 1px solid var(--border); margin: 2em 0; }
main img { max-width: 100%; height: auto; border-radius: 6px; }
main code { font-family: var(--mono); font-size: 0.86em; padding: 0.1em 0.35em; background: var(--code-bg);
  border: 1px solid var(--border); border-radius: 5px; }
main pre { margin: 1.2em 0; padding: 14px 18px; overflow-x: auto; background: var(--code-bg);
  border: 1px solid var(--border); border-radius: 10px; line-height: 1.5; }
main pre code { padding: 0; border: 0; background: none; font-size: 0.84em; }
main blockquote { margin: 1.2em 0; padding: 0.5em 1.1em; border-left: 4px solid var(--accent);
  background: var(--accent-soft); border-radius: 0 8px 8px 0; }
.table-wrap { margin: 1.2em 0; overflow-x: auto; border: 1px solid var(--border); border-radius: 10px; }
main table { width: 100%; border-collapse: collapse; font-size: 0.93em; }
main th, main td { padding: 0.6em 0.85em; text-align: left; vertical-align: top; border-bottom: 1px solid var(--border); }
main th { background: var(--sidebar); color: var(--heading); font-weight: 650; }
main tbody tr:nth-child(even) { background: var(--zebra); }
main tbody tr:last-child td { border-bottom: 0; }
main dt { font-weight: 650; color: var(--heading); }
main dd { margin: 0.2em 0 0.8em 1.4em; }
.footnote { font-size: 0.9em; color: var(--muted); }
figure.diagram { margin: 1.4em 0; overflow: hidden; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; }
.diagram-bar { display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 38px;
  padding: 4px 6px 4px 14px; background: var(--sidebar); border-bottom: 1px solid var(--border); color: var(--muted); font-size: 0.85rem; }
.diagram-zoom { padding: 3px 10px; border: 1px solid var(--border); border-radius: 6px; background: transparent;
  color: var(--text); font-size: 0.85rem; cursor: pointer; }
.diagram-zoom:hover { background: var(--hover); }
figure.diagram .diagram-src { margin: 0; border: 0; border-radius: 0; }
.diagram-out { padding: 20px 16px; overflow-x: auto; }
.diagram-out svg { display: block; margin: 0 auto; max-width: 100%; height: auto; }
.mm-dark { display: none; }
.diagram-error { padding: 8px 14px; border-top: 1px solid var(--border); color: var(--danger); font-size: 0.85rem; }
dialog.diagram-dialog { width: 96vw; max-width: none; max-height: 92vh; padding: 0; overflow: hidden;
  background: var(--surface); color: var(--text); border: 1px solid var(--border); border-radius: 12px; }
dialog.diagram-dialog[open] { display: flex; flex-direction: column; }
dialog.diagram-dialog::backdrop { background: var(--backdrop); }
.dialog-bar { display: flex; align-items: center; justify-content: space-between; padding: 8px 8px 8px 18px;
  border-bottom: 1px solid var(--border); color: var(--muted); font-size: 0.9rem; }
.dialog-close { width: 36px; height: 36px; display: inline-flex; align-items: center; justify-content: center;
  border: 0; border-radius: 6px; background: transparent; color: var(--muted); cursor: pointer; }
.dialog-close:hover { background: var(--hover); color: var(--text); }
.dialog-body { overflow: auto; padding: 24px; flex: 1; min-height: 0; }
.dialog-body .diagram-out { padding: 0; overflow: visible; }
.dialog-body .diagram-out svg { max-width: none !important; width: 100% !important; height: auto; }
.print-notice { position: fixed; z-index: 40; left: 50%; bottom: 20px; transform: translateX(-50%);
  width: max-content; max-width: calc(100vw - 32px); display: flex; align-items: center; gap: 10px;
  padding: 10px 8px 10px 16px; background: var(--surface); color: var(--text); border: 1px solid var(--border);
  border-left: 4px solid var(--accent); border-radius: 10px; box-shadow: 0 6px 24px rgba(0, 0, 0, 0.18);
  font-size: 0.92rem; line-height: 1.4; }
.print-notice[hidden] { display: none; }
.print-notice-close { flex: none; width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center;
  border: 0; border-radius: 6px; background: transparent; color: var(--muted); cursor: pointer; }
.print-notice-close:hover { background: var(--hover); color: var(--text); }
mark.hit { background: var(--mark); color: var(--mark-text); border-radius: 3px; padding: 0 1px; }
mark.hit.current { background: var(--mark-current); box-shadow: 0 0 0 2px var(--mark-current); }

/* Full-width cards; hidden navigation (wide screens only, the slide-in menu is unaffected) */
:root[data-width="full"] .card { max-width: none; }
@media screen and (min-width: 901px) {
  :root[data-nav="closed"] .layout { grid-template-columns: minmax(0, 1fr); }
  :root[data-nav="closed"] .sidebar { display: none; }
  :root[data-nav="closed"] .nav-show { display: inline-flex; }
  :root[data-nav="closed"] main { padding-left: 64px; padding-right: 64px; }
}

/* Small screens */
@media (max-width: 1100px) {
  .btn-print .label { display: none; }
  .btn-print { width: 46px; justify-content: center; padding: 0; }
}
@media (max-width: 900px) {
  .topbar { flex-wrap: wrap; gap: 10px 12px; padding: 10px 14px; }
  .menu-btn { display: inline-flex; }
  .brand { flex: 1 1 0; }
  .doc-title { font-size: 1.2rem; }
  .doc-sub { font-size: 0.8rem; }
  .actions { gap: 8px; }
  .btn-print { height: 42px; width: 42px; }
  .btn-width { display: none; }
  .theme-switch button { width: 34px; height: 34px; }
  .search { order: 5; flex: 1 1 100%; max-width: none; margin-left: 0; }
  .search input { padding-right: 110px; }
  .kbd { display: none; }
  .layout { display: block; }
  .sidebar { position: fixed; z-index: 25; top: var(--header-h); bottom: 0; left: 0; height: auto;
    width: min(88vw, 340px); transform: translateX(-100%); transition: transform 0.2s ease;
    box-shadow: 0 0 24px rgba(0, 0, 0, 0.18); }
  body.menu-open .sidebar { transform: none; }
  .backdrop { display: block; position: fixed; z-index: 20; inset: var(--header-h) 0 0 0; background: var(--backdrop);
    opacity: 0; pointer-events: none; transition: opacity 0.2s ease; }
  body.menu-open .backdrop { opacity: 1; pointer-events: auto; }
  main { padding: 16px 12px 70px; }
  .card { padding: 22px 20px 26px; border-radius: 10px; }
  [data-top="1"] main h1, [data-top="2"] main h2 { font-size: 1.7rem; }
}
@media (prefers-reduced-motion: reduce) { .sidebar, .backdrop, .toc-toggle svg { transition: none; } }

/* Print: always light, no chrome */
@media print {
  html:root:not(.x) {__LIGHT__}
  body { background: #fff; font-size: 11pt; }
  .topbar, .sidebar, .backdrop, .nav-show { display: none !important; }
  .layout { display: block; }
  main { padding: 0; }
  .card { max-width: none; margin: 0 0 1.5em; padding: 0; border: 0; border-radius: 0; }
  main :is(h1, h2, h3, h4) { break-after: avoid; }
  main :is(table, pre, blockquote, img, .table-wrap) { break-inside: avoid; }
  .table-wrap { overflow: visible; }
  .headerlink, .diagram-bar, dialog, .print-notice { display: none !important; }
  html:root:not(.x) .mm-light { display: block; }
  html:root:not(.x) .mm-dark { display: none; }
  figure.diagram { border: 0; break-inside: avoid; }
  .diagram-out { padding: 0; }
  mark.hit, mark.hit.current { background: none; color: inherit; box-shadow: none; }
  main a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 0.85em; color: #555; word-break: break-all; }
}
"""

JS = r"""
(function () {
  "use strict";
  var L = JSON.parse(document.getElementById("labels").textContent);
  var root = document.documentElement;
  /* Pristine copy of the page (before diagrams, search marks etc.), only kept when the
     page is embedded in a frame, where printing may be blocked. */
  var framed = true;
  try { framed = window.self !== window.top; } catch (e) {}
  var autoPrint = location.hash === "#md2html-print";
  var snapshot = framed && !autoPrint ? "<!DOCTYPE html>\n" + root.outerHTML : null;
  var KEY = "md2html-theme";

  /* Theme */
  var themeButtons = Array.prototype.slice.call(document.querySelectorAll(".theme-switch button"));
  function applyTheme(value) {
    if (value === "light" || value === "dark") root.setAttribute("data-theme", value);
    else { value = "system"; root.removeAttribute("data-theme"); }
    themeButtons.forEach(function (b) {
      var on = b.getAttribute("data-value") === value;
      b.setAttribute("aria-checked", String(on));
      b.tabIndex = on ? 0 : -1;
    });
    return value;
  }
  function saveTheme(value) {
    try { if (value === "system") localStorage.removeItem(KEY); else localStorage.setItem(KEY, value); } catch (e) {}
  }
  var stored = null;
  try { stored = localStorage.getItem(KEY); } catch (e) {}
  applyTheme(stored);
  themeButtons.forEach(function (b, i) {
    b.addEventListener("click", function () { saveTheme(applyTheme(b.getAttribute("data-value"))); });
    b.addEventListener("keydown", function (e) {
      var d = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      var next = themeButtons[(i + d + themeButtons.length) % themeButtons.length];
      saveTheme(applyTheme(next.getAttribute("data-value")));
      next.focus();
    });
  });

  /* Header height -> CSS variable */
  var header = document.querySelector(".topbar");
  function syncHeader() { root.style.setProperty("--header-h", header.offsetHeight + "px"); }
  syncHeader();
  if (window.ResizeObserver) new ResizeObserver(syncHeader).observe(header);
  else window.addEventListener("resize", syncHeader);

  /* Localised date, shortcut hint */
  document.querySelectorAll("time[datetime]").forEach(function (t) {
    try {
      var p = t.getAttribute("datetime").split("-");
      t.textContent = new Date(+p[0], +p[1] - 1, +p[2]).toLocaleDateString(root.lang, { year: "numeric", month: "2-digit", day: "2-digit" });
    } catch (e) {}
  });
  if (/Mac|iPhone|iPad/.test(navigator.platform || "")) {
    var k = document.querySelector(".kbd"); if (k) k.textContent = "⌘ K";
  }

  /* Navigation */
  var nav = document.querySelector(".sidebar");
  var navLinks = Array.prototype.slice.call(nav.querySelectorAll(".toc-link"));
  var pairs = navLinks.map(function (a) { return { link: a, head: document.getElementById(a.getAttribute("data-id")) }; })
    .filter(function (p) { return p.head; });
  var heads = pairs.map(function (p) { return p.head; });

  function setOpen(li, open, flag) {
    li.classList.toggle("open", open);
    var t = li.querySelector(":scope > .toc-row > .toc-toggle");
    if (t) t.setAttribute("aria-expanded", String(open));
    if (flag) li.setAttribute(flag, "1");
  }
  function hasChildren(li) { return !!li.querySelector(":scope > .toc-list"); }

  var mqMobile = window.matchMedia("(max-width: 900px)");
  var menuBtn = document.querySelector(".menu-btn");
  function openMenu() { document.body.classList.add("menu-open"); menuBtn.setAttribute("aria-expanded", "true"); }
  function closeMenu() { document.body.classList.remove("menu-open"); menuBtn.setAttribute("aria-expanded", "false"); }
  menuBtn.addEventListener("click", function () {
    document.body.classList.contains("menu-open") ? closeMenu() : openMenu();
  });
  document.querySelector(".backdrop").addEventListener("click", closeMenu);

  nav.addEventListener("click", function (e) {
    var toggle = e.target.closest(".toc-toggle");
    if (toggle) {
      var li = toggle.closest("li");
      var open = !li.classList.contains("open");
      setOpen(li, open);
      if (open) li.setAttribute("data-user", "1"); else li.removeAttribute("data-user");
      li.removeAttribute("data-auto");
      return;
    }
    if (e.target.closest(".toc-link") && mqMobile.matches) closeMenu();
  });

  /* Scroll spy */
  var current = null;
  function pathOf(li) {
    var path = [];
    while (li && nav.contains(li)) { path.push(li); li = li.parentElement ? li.parentElement.closest("li") : null; }
    return path;
  }
  function setActive(link) {
    if (link === current) return;
    if (current) { current.classList.remove("active"); current.removeAttribute("aria-current"); }
    nav.querySelectorAll(".in-trail").forEach(function (x) { x.classList.remove("in-trail"); });
    current = link;
    if (!link) return;
    link.classList.add("active");
    link.setAttribute("aria-current", "location");
    var path = pathOf(link.closest("li"));
    path.slice(1).forEach(function (li) { li.querySelector(":scope > .toc-row > .toc-link").classList.add("in-trail"); });
    if (!searching) {
      nav.querySelectorAll("li.open[data-auto]").forEach(function (li) {
        if (path.indexOf(li) < 0 && !li.hasAttribute("data-user")) { setOpen(li, false); li.removeAttribute("data-auto"); }
      });
      path.forEach(function (li) {
        if (hasChildren(li) && !li.classList.contains("open")) setOpen(li, true, "data-auto");
      });
    }
    reveal(link);
  }
  function reveal(link) {
    if (!link || !nav.offsetHeight) return;
    var nr = nav.getBoundingClientRect(), lr = link.getBoundingClientRect();
    var sticky = nav.querySelector(".toc-top").offsetHeight - 26; /* part of the nav header that covers the list */
    if (lr.top < nr.top + sticky + 8 || lr.bottom > nr.bottom - 40) nav.scrollTop += lr.top - nr.top - Math.max(sticky + 24, nr.height / 3);
  }

  /* Hide / show the navigation and full-width cards; both remembered in the browser.
     On narrow screens the hide button simply closes the slide-in menu. */
  var navHide = nav.querySelector(".nav-hide"), navShow = document.querySelector(".nav-show");
  var widthBtn = document.querySelector(".btn-width");
  function remember(key, value) {
    try { if (value) localStorage.setItem(key, value); else localStorage.removeItem(key); } catch (e) {}
  }
  function setNavClosed(closed) {
    if (closed) root.setAttribute("data-nav", "closed"); else root.removeAttribute("data-nav");
    remember("md2html-nav", closed ? "closed" : "");
  }
  navHide.addEventListener("click", function () {
    if (mqMobile.matches) { closeMenu(); menuBtn.focus(); return; }
    setNavClosed(true);
    navShow.focus();
  });
  navShow.addEventListener("click", function () {
    setNavClosed(false);
    navHide.focus({ preventScroll: true });
    reveal(current);
  });
  function setWide(on) {
    if (on) root.setAttribute("data-width", "full"); else root.removeAttribute("data-width");
    widthBtn.setAttribute("aria-pressed", String(on));
  }
  setWide(root.getAttribute("data-width") === "full");
  widthBtn.addEventListener("click", function () {
    var on = root.getAttribute("data-width") !== "full";
    setWide(on);
    remember("md2html-width", on ? "full" : "");
  });
  var ticking = false;
  function spy() {
    ticking = false;
    if (!pairs.length) return;
    var limit = header.offsetHeight + 28, lo = 0, hi = heads.length - 1, idx = 0;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (heads[mid].getBoundingClientRect().top <= limit) { idx = mid; lo = mid + 1; } else hi = mid - 1;
    }
    if (window.innerHeight + window.scrollY >= root.scrollHeight - 4) {
      for (var j = heads.length - 1; j > idx; j--) { if (heads[j].getBoundingClientRect().top < window.innerHeight) { idx = j; break; } }
    }
    setActive(pairs[idx].link);
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(spy); } }, { passive: true });
  window.addEventListener("resize", spy);

  /* Search */
  var main = document.querySelector("main");
  var box = document.querySelector(".search");
  var input = document.getElementById("search-input");
  var countEl = document.querySelector(".count");
  var emptyEl = document.querySelector(".toc-empty");
  var LIMIT = 1000;
  var marks = [], pos = -1, timer = null, searching = false, capped = false;

  function clearMarks() {
    var parents = [];
    marks.forEach(function (m) {
      var p = m.parentNode; if (!p) return;
      p.replaceChild(document.createTextNode(m.textContent), m);
      if (parents.indexOf(p) < 0) parents.push(p);
    });
    parents.forEach(function (p) { p.normalize(); });
    marks = []; pos = -1; capped = false;
  }
  function updateCount() {
    if (!searching) { countEl.textContent = ""; return; }
    countEl.textContent = marks.length ? (pos + 1) + " / " + marks.length + (capped ? "+" : "") : L.no_results;
  }
  function filterNav() {
    var hit = {}, j = 0;
    marks.forEach(function (m) {
      while (j + 1 < heads.length && (heads[j + 1].compareDocumentPosition(m) & Node.DOCUMENT_POSITION_FOLLOWING)) j++;
      if (heads.length && (heads[j] === m || heads[j].compareDocumentPosition(m) & Node.DOCUMENT_POSITION_FOLLOWING)) {
        hit[heads[j].id] = true;
      }
    });
    var lis = Array.prototype.slice.call(nav.querySelectorAll("li")).reverse();
    lis.forEach(function (li) {
      var childHit = !!li.querySelector(":scope > .toc-list > li:not([hidden])");
      var visible = !!hit[li.getAttribute("data-id")] || childHit;
      li.hidden = !visible;
      if (childHit && !li.classList.contains("open")) setOpen(li, true, "data-search");
    });
    emptyEl.hidden = marks.length > 0;
  }
  function resetNav() {
    nav.querySelectorAll("li").forEach(function (li) {
      li.hidden = false;
      if (li.hasAttribute("data-search")) {
        li.removeAttribute("data-search");
        if (!li.hasAttribute("data-user")) setOpen(li, false);
      }
    });
    emptyEl.hidden = true;
    current = null;
    spy();
  }
  function go(i) {
    if (!marks.length) return;
    if (pos >= 0) marks[pos].classList.remove("current");
    pos = (i + marks.length) % marks.length;
    var m = marks[pos];
    m.classList.add("current");
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    m.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" });
    updateCount();
  }
  function runSearch() {
    timer = null;
    clearMarks();
    var q = input.value.trim();
    box.classList.toggle("has-value", input.value.length > 0);
    if (q.length < 2) {
      if (searching) { searching = false; resetNav(); }
      updateCount();
      return;
    }
    searching = true;
    var needle = q.toLowerCase();
    var walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        var p = n.parentElement;
        if (!p || !n.nodeValue.trim() || p.closest(".headerlink, script, style, .diagram")) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (var i = 0; i < nodes.length && !capped; i++) {
      var node = nodes[i], text = node.nodeValue, lower = text.toLowerCase(), at = lower.indexOf(needle);
      if (at < 0) continue;
      var frag = document.createDocumentFragment(), last = 0;
      while (at >= 0) {
        if (marks.length >= LIMIT) { capped = true; break; }
        if (at > last) frag.appendChild(document.createTextNode(text.slice(last, at)));
        var m = document.createElement("mark");
        m.className = "hit";
        m.textContent = text.slice(at, at + needle.length);
        frag.appendChild(m);
        marks.push(m);
        last = at + needle.length;
        at = lower.indexOf(needle, last);
      }
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    }
    filterNav();
    if (marks.length) go(0); else updateCount();
  }
  input.addEventListener("input", function () {
    box.classList.toggle("has-value", input.value.length > 0);
    clearTimeout(timer);
    timer = setTimeout(runSearch, 220);
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      if (timer) { clearTimeout(timer); runSearch(); return; }
      go(pos + (e.shiftKey ? -1 : 1));
    } else if (e.key === "Escape") {
      e.preventDefault();
      input.value = ""; runSearch(); input.blur();
    }
  });
  document.querySelector(".clear").addEventListener("click", function () {
    input.value = ""; runSearch(); input.focus();
  });
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && !e.altKey && (e.key === "k" || e.key === "K")) {
      e.preventDefault(); input.focus(); input.select();
    } else if (e.key === "Escape" && document.body.classList.contains("menu-open")) {
      closeMenu(); menuBtn.focus();
    }
  });
  /* Print. Inside a sandboxed iframe without "allow-modals" (editor previews, chat
     viewers) the browser silently ignores window.print(); "beforeprint" then never
     fires. In that case the page is reopened as a standalone tab that prints itself,
     and if popups are blocked too, a notice explains what to do. */
  var printStarted = false;
  window.addEventListener("beforeprint", function () { printStarted = true; });
  var notice = document.querySelector(".print-notice");
  notice.querySelector(".print-notice-close").addEventListener("click", function () { notice.hidden = true; });
  function tryPrint(onBlocked) {
    printStarted = false;
    try { window.print(); } catch (e) {}
    if (printStarted) return;
    setTimeout(function () { if (!printStarted) onBlocked(); }, 250);
  }
  function openStandalone() {
    if (!snapshot) return false;
    try {
      var url = URL.createObjectURL(new Blob([snapshot], { type: "text/html" }));
      var w = window.open(url + "#md2html-print", "_blank");
      setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
      return !!w;
    } catch (e) { return false; }
  }
  document.querySelector(".btn-print").addEventListener("click", function () {
    notice.hidden = true;
    tryPrint(function () { if (!openStandalone()) notice.hidden = false; });
  });

  /* Mermaid diagrams: each one is rendered twice (light and dark) so that switching
     the theme or printing never needs a re-render. */
  var figures = Array.prototype.slice.call(document.querySelectorAll("figure.diagram"));
  var dialog = document.querySelector(".diagram-dialog");
  function effectiveDark() {
    var t = root.getAttribute("data-theme");
    return t === "dark" || (t !== "light" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
  function mermaidConfig(dark) {
    var v = dark ? {
      darkMode: true, background: "#16212b", primaryColor: "#1d3833", primaryTextColor: "#e6eef4",
      primaryBorderColor: "#5fc2ad", secondaryColor: "#1f2e3b", secondaryTextColor: "#e6eef4",
      secondaryBorderColor: "#6f8aa0", tertiaryColor: "#131d26", tertiaryTextColor: "#d6e0e8",
      tertiaryBorderColor: "#2f4152", lineColor: "#8fa1b1", textColor: "#d6e0e8", mainBkg: "#1d3833",
      nodeBorder: "#5fc2ad", clusterBkg: "#131d26", clusterBorder: "#2f4152", edgeLabelBackground: "#16212b",
      noteBkgColor: "#3a3420", noteTextColor: "#f3ead0", noteBorderColor: "#8a7a3e"
    } : {
      darkMode: false, background: "#ffffff", primaryColor: "#e3f1ec", primaryTextColor: "#16304a",
      primaryBorderColor: "#2a8574", secondaryColor: "#e8eff5", secondaryTextColor: "#16304a",
      secondaryBorderColor: "#7d97ab", tertiaryColor: "#f6f8fa", tertiaryTextColor: "#22313f",
      tertiaryBorderColor: "#c8d3dc", lineColor: "#5d6d7b", textColor: "#22313f", mainBkg: "#e3f1ec",
      nodeBorder: "#2a8574", clusterBkg: "#f6f8fa", clusterBorder: "#c8d3dc", edgeLabelBackground: "#ffffff",
      noteBkgColor: "#fff6d6", noteTextColor: "#22313f", noteBorderColor: "#e0c36a"
    };
    v.fontFamily = getComputedStyle(document.body).fontFamily;
    v.fontSize = "15px";
    return {
      startOnLoad: false, securityLevel: "strict", theme: "base", themeVariables: v, suppressErrorRendering: true,
      flowchart: { htmlLabels: true, useMaxWidth: true }, sequence: { useMaxWidth: true },
      er: { useMaxWidth: true }, gantt: { useMaxWidth: true }, class: { useMaxWidth: true }, state: { useMaxWidth: true }
    };
  }
  /* Sequence-diagram `rect rgb(...)` blocks carry a hard-coded light inline fill that theme
     variables cannot override. In the dark render, keep the hue but turn it into a faint
     translucent tint so the light text stays readable. */
  function darkenRects(svg) {
    var box = document.createElement("div");
    box.innerHTML = svg;
    var probe = document.createElement("span");
    probe.style.display = "none";
    document.body.appendChild(probe);
    box.querySelectorAll("rect.rect").forEach(function (r) {
      var fill = r.style.fill || r.getAttribute("fill");
      if (!fill) return;
      probe.style.color = "";
      probe.style.color = fill;
      var m = getComputedStyle(probe).color.match(/[\d.]+/g);
      if (!m || m.length < 3) return;
      var R = m[0] / 255, G = m[1] / 255, B = m[2] / 255;
      var mx = Math.max(R, G, B), mn = Math.min(R, G, B), d = mx - mn, h = 0;
      if (d > 0) {
        h = mx === R ? ((G - B) / d) % 6 : mx === G ? (B - R) / d + 2 : (R - G) / d + 4;
        h = Math.round(((h * 60) + 360) % 360);
      }
      /* same hue, forced saturation, low lightness: clearly colored but dark */
      r.style.fill = "hsl(" + h + ",55%,21%)";
    });
    probe.remove();
    return box.innerHTML;
  }
  var diagramSeq = 0;
  async function renderSvg(src, dark) {
    window.mermaid.initialize(mermaidConfig(dark));
    var id = "mmd-" + (++diagramSeq);
    try { var svg = (await window.mermaid.render(id, src)).svg; return dark ? darkenRects(svg) : svg; }
    finally { ["d" + id, id].forEach(function (x) { var el = document.getElementById(x); if (el && !el.closest("figure")) el.remove(); }); }
  }
  async function renderDiagrams() {
    for (var i = 0; i < figures.length; i++) {
      var fig = figures[i], srcEl = fig.querySelector(".diagram-src"), out = fig.querySelector(".diagram-out");
      var src = srcEl.textContent, first = effectiveDark();
      try {
        var svg = await renderSvg(src, first);
        out.innerHTML = '<div class="mm-light"></div><div class="mm-dark"></div>';
        out.querySelector(first ? ".mm-dark" : ".mm-light").innerHTML = svg;
        srcEl.hidden = true;
        out.hidden = false;
        fig.querySelector(".diagram-zoom").hidden = false;
      } catch (e) {
        var cap = document.createElement("figcaption");
        cap.className = "diagram-error";
        cap.textContent = L.diagram_error + (e && e.message ? ": " + String(e.message).split("\n")[0] : "");
        fig.appendChild(cap);
        continue;
      }
      try { out.querySelector(first ? ".mm-light" : ".mm-dark").innerHTML = await renderSvg(src, !first); } catch (e) {}
      out.querySelectorAll("svg").forEach(function (s) {
        s.setAttribute("role", "img");
        s.setAttribute("aria-label", fig.querySelector(".diagram-bar span").textContent);
      });
    }
  }
  var diagramsReady = figures.length && window.mermaid ? renderDiagrams() : Promise.resolve();
  if (autoPrint) {
    diagramsReady.catch(function () {}).then(function () {
      setTimeout(function () { tryPrint(function () { notice.hidden = false; }); }, 300);
    });
  }

  var zoomed = null;
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".diagram-zoom");
    if (!btn || !dialog || !dialog.showModal) return;
    var fig = btn.closest("figure");
    var out = fig.querySelector(".diagram-out");
    zoomed = { fig: fig, out: out };
    dialog.querySelector(".dialog-title").textContent = fig.querySelector(".diagram-bar span").textContent;
    dialog.querySelector(".dialog-body").appendChild(out);
    dialog.showModal();
  });
  if (dialog) {
    dialog.addEventListener("close", function () {
      if (zoomed) { zoomed.fig.insertBefore(zoomed.out, zoomed.fig.querySelector(".diagram-src").nextSibling); zoomed = null; }
    });
    dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
    dialog.querySelector(".dialog-close").addEventListener("click", function () { dialog.close(); });
  }

  spy();
})();
"""

PAGE = """<!DOCTYPE html>
<html lang="__LANG__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="markdown_to_html.py">
<title>__TITLE_TEXT__</title>
<script>(function(){try{var d=document.documentElement,s=localStorage,t=s.getItem("md2html-theme");if(t==="light"||t==="dark")d.setAttribute("data-theme",t);if(s.getItem("md2html-nav")==="closed")d.setAttribute("data-nav","closed");if(s.getItem("md2html-width")==="full")d.setAttribute("data-width","full");}catch(e){}})();</script>
<style>__CSS__</style>
</head>
<body data-top="__TOP__">
<header class="topbar">
  <button class="menu-btn" type="button" aria-controls="sidebar" aria-expanded="false" aria-label="__L_MENU__">__ICON_MENU__</button>
  <div class="brand">
    <p class="doc-title">__TITLE__</p>
    <p class="doc-sub">__SUBTITLE__</p>
  </div>
  <div class="search" role="search">
    <input id="search-input" type="search" autocomplete="off" spellcheck="false" placeholder="__L_SEARCH__" aria-label="__L_SEARCH__">
    <div class="search-meta">
      <span class="count" aria-live="polite"></span>
      <span class="kbd">__L_KBD__</span>
      <button class="clear" type="button" aria-label="__L_CLEAR__" title="__L_CLEAR__">__ICON_CLOSE__</button>
    </div>
  </div>
  <div class="actions">
    <button class="btn-width" type="button" aria-pressed="false" aria-label="__L_FULL_WIDTH__" title="__L_FULL_WIDTH__">__ICON_WIDTH__</button>
    <button class="btn-print" type="button" title="__L_PRINT__">__ICON_PRINT__<span class="label">__L_PRINT__</span></button>
    <div class="theme-switch" role="radiogroup" aria-label="__L_THEME__">
      <button type="button" role="radio" data-value="system" aria-checked="true" aria-label="__L_SYSTEM__" title="__L_SYSTEM__">__ICON_SYSTEM__</button>
      <button type="button" role="radio" data-value="light" aria-checked="false" aria-label="__L_LIGHT__" title="__L_LIGHT__">__ICON_LIGHT__</button>
      <button type="button" role="radio" data-value="dark" aria-checked="false" aria-label="__L_DARK__" title="__L_DARK__">__ICON_DARK__</button>
    </div>
  </div>
</header>
<button class="nav-show" type="button" aria-controls="sidebar" aria-label="__L_NAV_SHOW__" title="__L_NAV_SHOW__">__ICON_NAV_SHOW__</button>
<div class="layout">
  <nav class="sidebar" id="sidebar" aria-label="__L_MENU__">
    <div class="toc-top">
      <p class="toc-head">__L_TOC__</p>
      <button class="nav-hide" type="button" aria-controls="sidebar" aria-label="__L_NAV_HIDE__" title="__L_NAV_HIDE__">__ICON_NAV_HIDE__</button>
    </div>
    __NAV__
    <p class="toc-empty" hidden>__L_NO_RESULTS__</p>
  </nav>
  <div class="backdrop" aria-hidden="true"></div>
  <main>
__BODY__
  </main>
</div>
<dialog class="diagram-dialog" aria-label="__L_DIAGRAM__">
  <div class="dialog-bar"><span class="dialog-title"></span><button class="dialog-close" type="button" aria-label="__L_CLOSE__" title="__L_CLOSE__">__ICON_CLOSE__</button></div>
  <div class="dialog-body"></div>
</dialog>
<div class="print-notice" role="status" hidden><span>__L_PRINT_BLOCKED__</span><button class="print-notice-close" type="button" aria-label="__L_CLOSE__" title="__L_CLOSE__">__ICON_CLOSE__</button></div>
<script type="application/json" id="labels">__LABELS_JSON__</script>
__MERMAID__
<script>__JS__</script>
</body>
</html>
"""


def build_nav(items, top, toggle_label, depth=0):
    rows = []
    for t in items:
        if t["level"] > top + 2:
            continue
        kids = [c for c in t["children"] if c["level"] <= top + 2]
        rid = html.escape(t["id"])
        rows.append(f'<li data-id="{rid}"><div class="toc-row">'
                    f'<a class="toc-link" href="#{rid}" data-id="{rid}">{plain(t["name"])}</a>')
        if kids:
            rows.append(f'<button class="toc-toggle" type="button" aria-expanded="false" '
                        f'aria-label="{toggle_label}">{ICON_CHEVRON}</button>')
        rows.append("</div>")
        if kids:
            rows.append(build_nav(kids, top, toggle_label, depth + 1))
        rows.append("</li>")
    return f'<ul class="toc-list">{"".join(rows)}</ul>' if rows else ""


def convert(src, lang, dst):
    labels = dict(LABELS["en"])
    labels.update(LABELS.get(lang, {}))

    raw = src.read_text(encoding="utf-8-sig")
    meta, text = split_front_matter(raw)
    text = re.sub(r"(?im)^[ \t]*\[TOC\][ \t]*$", "", text)

    md = markdown.Markdown(extensions=[
        TocExtension(permalink="#", permalink_title=labels["permalink"], slugify=slugify_unicode,
                     marker="[[__no_toc_marker__]]"),
        "extra", "sane_lists",
    ])
    body = md.convert(text)
    tokens = md.toc_tokens
    flat = list(flatten(tokens))

    # Title: a single leading H1 becomes the page title; its children form the navigation.
    title = meta.get("title", "")
    h1s = [t for t in flat if t["level"] == 1]
    if len(h1s) == 1 and flat and flat[0] is h1s[0]:
        title = title or html.unescape(h1s[0]["name"])
        body = re.sub(r"<h1\b[^>]*>.*?</h1>", "", body, count=1, flags=re.S)
        tokens = h1s[0]["children"]
        flat = list(flatten(tokens))
    elif not title and h1s:
        title = html.unescape(h1s[0]["name"])
    title = title or src.stem
    top = min((t["level"] for t in flat), default=1)

    # Drop a hand-written table of contents (the sidebar replaces it).
    for t in [t for t in tokens if t["level"] == top and MANUAL_TOC_NAMES.match(html.unescape(t["name"]))]:
        pattern = rf'<h{top}\b[^>]*\bid="{re.escape(t["id"])}"[^>]*>.*?(?=<h[1-{top}]\b|\Z)'
        body = re.sub(pattern, "", body, count=1, flags=re.S)
        tokens = [x for x in tokens if x is not t]

    body, diagrams = mermaid_figures(body, html.escape(labels["diagram"]))
    mermaid_note = ""
    if diagrams and not MERMAID_ASSET.is_file():
        mermaid_note = f" ({diagrams} Mermaid diagram(s) left as code: {MERMAID_ASSET.as_posix()} not found)"

    body = re.sub(r"<table>", '<div class="table-wrap"><table>', body)
    body = re.sub(r"</table>", "</table></div>", body)
    body = inline_images(body, src.parent)

    # Each top-level section becomes a card.
    cards = []
    for part in re.split(rf"(?=<h{top}[\s>])", body):
        if part.strip():
            cards.append(f'<section class="card">\n{part.strip()}\n</section>')

    modified = datetime.date.fromtimestamp(src.stat().st_mtime).isoformat()
    if meta.get("subtitle"):
        subtitle = html.escape(meta["subtitle"])
    else:
        subtitle = f'{html.escape(src.name)} · <time datetime="{modified}">{modified}</time>'

    lab = {k: html.escape(v) for k, v in labels.items()}
    nav = build_nav(tokens, top, lab["toggle"])
    labels_json = json.dumps({k: labels[k] for k in ("no_results", "diagram_error")},
                             ensure_ascii=False).replace("</", "<\\/")

    css = CSS.replace("__LIGHT__", LIGHT_TOKENS).replace("__DARK__", DARK_TOKENS)
    out = PAGE
    for key, value in {
        "__CSS__": css, "__JS__": JS, "__LANG__": lang, "__TOP__": str(top),
        "__TITLE_TEXT__": html.escape(title), "__TITLE__": html.escape(title), "__SUBTITLE__": subtitle,
        "__NAV__": nav, "__LABELS_JSON__": labels_json,
        "__ICON_MENU__": ICON_MENU, "__ICON_CLOSE__": ICON_CLOSE, "__ICON_PRINT__": ICON_PRINT,
        "__ICON_SYSTEM__": ICON_SYSTEM, "__ICON_LIGHT__": ICON_LIGHT, "__ICON_DARK__": ICON_DARK,
        "__L_MENU__": lab["menu"], "__L_SEARCH__": lab["search"], "__L_KBD__": lab["kbd"],
        "__L_CLEAR__": lab["clear"], "__L_PRINT__": lab["print"], "__L_THEME__": lab["theme"],
        "__L_SYSTEM__": lab["system"], "__L_LIGHT__": lab["light"], "__L_DARK__": lab["dark"],
        "__L_TOC__": lab["toc"], "__L_NO_RESULTS__": lab["no_results"],
        "__L_DIAGRAM__": lab["diagram"], "__L_CLOSE__": lab["close"],
        "__L_PRINT_BLOCKED__": lab["print_blocked"],
        "__ICON_NAV_HIDE__": ICON_NAV_HIDE, "__ICON_NAV_SHOW__": ICON_NAV_SHOW, "__ICON_WIDTH__": ICON_WIDTH,
        "__L_NAV_HIDE__": lab["nav_hide"], "__L_NAV_SHOW__": lab["nav_show"], "__L_FULL_WIDTH__": lab["full_width"],
    }.items():
        out = out.replace(key, value)
    body_html = "\n".join(cards).replace("__L_ENLARGE__", lab["enlarge"])
    lib = mermaid_script() if diagrams and not mermaid_note else ""
    # Body and library are inserted last, by splitting, so their content is never scanned for placeholders.
    head, _, tail = out.partition("__BODY__")
    tail_a, _, tail_b = tail.partition("__MERMAID__")
    out = head + body_html + tail_a + lib + tail_b

    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    nav_count = sum(1 for t in flatten(tokens) if t["level"] <= top + 2)
    note = "" if lang in LABELS else " (UI labels in English: language not in LABELS)"
    diag = f", {diagrams} diagrams" if diagrams else ""
    print(f"OK: {dst.as_posix()} ({len(cards)} sections, {nav_count} navigation entries{diag}, "
          f"lang={lang}, {dst.stat().st_size // 1024} KB){note}{mermaid_note}")


def main(argv):
    args = [a for a in argv[1:]]
    while args and not args[-1].strip():
        args.pop()
    if len(args) < 2 or len(args) > 3:
        print(USAGE)
        return 2
    src = Path(args[0])
    lang = args[1].strip().lower()
    if not re.fullmatch(r"[a-z]{2}", lang):
        fail(f"language code must be two letters, got '{args[1]}'", 2)
    if not src.is_file():
        fail(f"Markdown file not found: {src}", 2)
    dst = Path(args[2]) if len(args) == 3 and args[2].strip() else src.with_suffix(".html")
    if dst.resolve() == src.resolve():
        fail("output file must differ from the Markdown file", 2)
    convert(src, lang, dst)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except SystemExit:
        raise
    except Exception as exc:  # report on stdout so the slash command sees it
        print(f"ERROR: {type(exc).__name__}: {exc}")
        sys.exit(1)
