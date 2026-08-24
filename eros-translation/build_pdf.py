#!/usr/bin/env python3
"""Build a typeset English PDF of Verga's Eros from chapter markdown files."""
from __future__ import annotations

import html
import re
from pathlib import Path

from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
EN = ROOT / "english"
OUT = ROOT / "Eros_Giovanni_Verga_English.pdf"

ROMANS = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
    "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX",
    "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI", "XXXVII", "XXXVIII", "XXXIX", "XL",
    "XLI", "XLII", "XLIII", "XLIV", "XLV", "XLVI", "XLVII", "XLVIII", "XLIX", "L",
]


def md_to_paragraphs(text: str) -> tuple[str, list[str]]:
    lines = text.replace("\r\n", "\n").strip().split("\n")
    title = "Chapter"
    body_lines: list[str] = []
    started = False
    for line in lines:
        if not started and line.startswith("#"):
            title = line.lstrip("#").strip()
            started = True
            continue
        started = True
        body_lines.append(line)
    raw = "\n".join(body_lines).strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]
    # unwrap single newlines inside a paragraph
    paras = [re.sub(r"\s*\n\s*", " ", p) for p in paras]
    return title, paras


def p_html(text: str, first: bool = False) -> str:
    t = html.escape(text)
    t = t.replace("---", "—").replace("--", "—")
    t = t.replace("...", "…")
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    cls = ' class="drop"' if first else ""
    return f"<p{cls}>{t}</p>"


def load_note() -> list[str]:
    note = (ROOT / "TRANSLATOR_NOTE.md").read_text(encoding="utf-8")
    _, paras = md_to_paragraphs(note)
    return paras


def chapter_files() -> list[Path]:
    files = []
    for i, rom in enumerate(ROMANS, 1):
        p = EN / f"chapter_{i:02d}.md"
        if not p.exists():
            raise SystemExit(f"Missing translation: {p}")
        files.append(p)
    return files


CSS = r"""
@page {
  size: 6in 9in;
  margin: 0.85in 0.75in 0.9in 0.8in;
  @bottom-center {
    content: counter(page);
    font-family: "Liberation Serif", "DejaVu Serif", serif;
    font-size: 9pt;
    color: #444;
    letter-spacing: 0.08em;
  }
}
@page :first {
  margin: 0;
  @bottom-center { content: none; }
}
@page front {
  @bottom-center { content: none; }
}
html, body {
  font-family: "Liberation Serif", "DejaVu Serif", serif;
  font-size: 11pt;
  line-height: 1.45;
  color: #1a1a1a;
  hyphens: auto;
  text-align: justify;
}
.cover {
  page: first;
  height: 9in;
  background: #2b1d18;
  color: #f3e6c8;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1.4in 0.8in;
}
.cover .rule {
  width: 2.4in;
  border: none;
  border-top: 1px solid #c4a574;
  margin: 0.45in auto;
}
.cover .author {
  font-size: 13pt;
  letter-spacing: 0.38em;
  text-transform: uppercase;
  color: #e8d5a3;
}
.cover h1 {
  font-family: "Liberation Serif", serif;
  font-weight: normal;
  font-size: 56pt;
  letter-spacing: 0.22em;
  margin: 0.15in 0 0 0;
  color: #f7edd4;
}
.cover .sub {
  font-style: italic;
  font-size: 12pt;
  letter-spacing: 0.04em;
  color: #d9c49a;
}
.cover .bottom {
  margin-top: 1.5in;
  font-size: 10pt;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #c4a574;
}
.half-title, .title-page, .colophon, .note, .contents {
  page: front;
}
.half-title {
  page-break-before: always;
  padding-top: 2.6in;
  text-align: center;
}
.half-title h1 {
  font-weight: normal;
  font-size: 28pt;
  letter-spacing: 0.28em;
}
.title-page {
  page-break-before: always;
  padding-top: 1.7in;
  text-align: center;
}
.title-page .author {
  font-size: 13pt;
  letter-spacing: 0.32em;
  text-transform: uppercase;
}
.title-page h1 {
  font-weight: normal;
  font-size: 42pt;
  letter-spacing: 0.24em;
  margin: 0.35in 0 0.2in 0;
}
.title-page .rule {
  width: 1.6in;
  border: none;
  border-top: 1px solid #333;
  margin: 0.35in auto;
}
.title-page .desc {
  font-style: italic;
  font-size: 12pt;
}
.title-page .imprint {
  margin-top: 2.1in;
  font-size: 10pt;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.colophon {
  page-break-before: always;
  padding-top: 2.2in;
  font-size: 10pt;
  line-height: 1.5;
  text-align: left;
  color: #333;
}
.note {
  page-break-before: always;
}
.note h2, .contents h2, .chapter h2 {
  font-weight: normal;
  text-align: center;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 13pt;
  margin: 0.4in 0 0.45in 0;
}
.contents {
  page-break-before: always;
}
.contents ol {
  list-style: none;
  padding: 0;
  margin: 0 auto;
  max-width: 3.6in;
}
.contents li {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dotted #bbb;
  margin: 0.12in 0;
  font-size: 11pt;
  text-align: left;
}
.chapter {
  page-break-before: always;
}
.chapter h2 {
  margin-top: 0.9in;
  margin-bottom: 0.55in;
}
.chapter p {
  margin: 0 0 0.22em 0;
  text-indent: 1.15em;
}
.chapter p.drop {
  text-indent: 0;
  margin-top: 0.1in;
}
.note p {
  text-indent: 1.15em;
  margin: 0 0 0.28em 0;
}
.note p:first-of-type {
  text-indent: 0;
}
"""


def build_html() -> str:
    files = chapter_files()
    note_paras = load_note()
    parts: list[str] = []
    parts.append("<div class='cover'>")
    parts.append("<div class='author'>Giovanni Verga</div>")
    parts.append("<hr class='rule'>")
    parts.append("<h1>EROS</h1>")
    parts.append("<div class='sub'>A novel</div>")
    parts.append("<hr class='rule'>")
    parts.append("<div class='bottom'>Translated from the Italian</div>")
    parts.append("</div>")

    parts.append("<div class='half-title'><h1>EROS</h1></div>")

    parts.append("<div class='title-page'>")
    parts.append("<div class='author'>Giovanni Verga</div>")
    parts.append("<h1>EROS</h1>")
    parts.append("<hr class='rule'>")
    parts.append("<div class='desc'>Translated from the Italian</div>")
    parts.append("<div class='imprint'>From the 1884 Treves edition</div>")
    parts.append("</div>")

    parts.append("<div class='colophon'>")
    parts.append("<p>The original Italian text is in the public domain. First published 1874–75; this translation follows the fifth edition, Milan, Fratelli Treves, 1884, as transcribed on Wikisource.</p>")
    parts.append("<p>English translation prepared 2026. The modern critical apparatus of later copyrighted Italian editions is not included.</p>")
    parts.append("</div>")

    parts.append("<div class='note'><h2>Translator’s Note</h2>")
    for i, p in enumerate(note_paras):
        parts.append(p_html(p, first=(i == 0)))
    parts.append("</div>")

    parts.append("<div class='contents'><h2>Contents</h2><ol>")
    for rom in ROMANS:
        parts.append(f"<li><span>Chapter {rom}</span></li>")
    parts.append("</ol></div>")

    for i, path in enumerate(files, 1):
        title, paras = md_to_paragraphs(path.read_text(encoding="utf-8"))
        if not paras:
            raise SystemExit(f"Empty chapter: {path}")
        parts.append("<section class='chapter'>")
        parts.append(f"<h2>{html.escape(title)}</h2>")
        for j, para in enumerate(paras):
            parts.append(p_html(para, first=(j == 0)))
        parts.append("</section>")

    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>Eros — Giovanni Verga</title><style>{CSS}</style></head>"
        f"<body>{''.join(parts)}</body></html>"
    )


def main() -> None:
    html_doc = build_html()
    (ROOT / "eros_en.html").write_text(html_doc, encoding="utf-8")
    HTML(string=html_doc, base_url=str(ROOT)).write_pdf(str(OUT))
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
