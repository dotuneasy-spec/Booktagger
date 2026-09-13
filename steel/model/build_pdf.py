#!/usr/bin/env python3
"""Build the Ashlar Steel CBA as a print-ready A4 PDF."""
from __future__ import annotations

from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "Billet_Semifinished_Steel_CBA.md"
OUT_PDF = ROOT / "Billet_Semifinished_Steel_CBA.pdf"
OUT_HTML = ROOT / "build" / "study.html"

CSS = r"""
@page {
  size: A4;
  margin: 16mm 14mm 18mm 14mm;
  @top-left {
    content: "Ashlar Steel  ·  Billet & Semi-Finished CBA  ·  September 2026";
    font-family: "DejaVu Sans", "Noto Sans", sans-serif;
    font-size: 7.5pt;
    color: #5c6b73;
  }
  @top-right {
    content: "CONFIDENTIAL";
    font-family: "DejaVu Sans", "Noto Sans", sans-serif;
    font-size: 7.5pt;
    font-weight: 700;
    color: #8a1f1f;
    letter-spacing: 0.08em;
  }
  @bottom-left {
    content: "Longs first  ·  captive melt second  ·  1.0 Mt is a gate";
    font-family: "DejaVu Sans", "Noto Sans", sans-serif;
    font-size: 7.5pt;
    color: #5c6b73;
  }
  @bottom-right {
    content: "Page " counter(page);
    font-family: "DejaVu Sans", "Noto Sans", sans-serif;
    font-size: 7.5pt;
    color: #1a242b;
  }
}
@page :first {
  margin: 0;
  @top-left { content: none; }
  @top-right { content: none; }
  @bottom-left { content: none; }
  @bottom-right { content: none; }
}

:root {
  --ink: #1a242b;
  --muted: #4e5b62;
  --rule: #d5dde2;
  --navy: #1b3a4b;
  --teal: #2a6f7f;
  --gold: #c5922a;
  --paper: #f7f5f0;
}

html, body {
  font-family: "DejaVu Sans", "Noto Sans", sans-serif;
  font-size: 9.4pt;
  line-height: 1.42;
  color: var(--ink);
  background: white;
}

.cover {
  page-break-after: always;
  break-after: page;
  min-height: 297mm;
  background: #1b3a4b;
  color: #f4efe4;
  padding: 22mm 20mm 18mm 20mm;
  box-sizing: border-box;
  position: relative;
}
.cover .eyebrow {
  font-size: 8.5pt;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 600;
  margin: 0 0 28mm 0;
}
.cover h1 {
  font-size: 26pt;
  line-height: 1.08;
  font-weight: 700;
  margin: 0 0 6mm 0;
  color: #fff;
  border: 0;
  padding: 0;
}
.cover h1 span {
  display: block;
  font-size: 14pt;
  font-weight: 500;
  color: #d4e4ea;
  margin-top: 4mm;
}
.cover .rule {
  width: 28mm;
  height: 2.5pt;
  background: var(--gold);
  margin: 8mm 0 10mm 0;
}
.cover .lede {
  font-size: 11.5pt;
  line-height: 1.4;
  max-width: 155mm;
  color: #e7eef1;
  margin: 0 0 16mm 0;
}
.cover dl {
  display: grid;
  grid-template-columns: 42mm 1fr;
  gap: 2.5mm 6mm;
  font-size: 9.5pt;
  margin: 0;
}
.cover dt { color: var(--gold); font-weight: 600; }
.cover dd { margin: 0; color: #eef3f5; }
.cover .foot {
  position: absolute;
  left: 20mm;
  right: 20mm;
  bottom: 18mm;
  display: flex;
  justify-content: space-between;
  font-size: 8.5pt;
  color: #b8c9d0;
  letter-spacing: 0.04em;
}

h1 {
  font-size: 16pt;
  color: var(--navy);
  border-bottom: 1.5pt solid var(--navy);
  padding-bottom: 2mm;
  margin: 8mm 0 4mm 0;
}
h2 {
  font-size: 12.5pt;
  color: var(--navy);
  margin: 6mm 0 2.5mm 0;
}
h3 {
  font-size: 10.5pt;
  color: var(--teal);
  margin: 4mm 0 2mm 0;
}
p { margin: 0 0 2.6mm 0; }
ul, ol { margin: 0 0 3mm 1.2em; padding: 0; }
li { margin: 0 0 1mm 0; }
strong { color: var(--navy); }
a { color: var(--teal); text-decoration: none; }
hr { border: 0; border-top: 0.5pt solid var(--rule); margin: 5mm 0; }
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 3mm auto 2mm auto;
}
em { color: var(--muted); }

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 8.1pt;
  margin: 0 0 4mm 0;
  page-break-inside: avoid;
}
th {
  background: var(--navy);
  color: white;
  text-align: left;
  padding: 1.6mm 2.2mm;
  font-weight: 600;
}
td {
  border-bottom: 0.4pt solid var(--rule);
  padding: 1.5mm 2.2mm;
  vertical-align: top;
}
tr:nth-child(even) td { background: #f3f6f8; }
code, pre {
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 8pt;
}
pre {
  background: #f3f6f8;
  padding: 3mm;
  white-space: pre-wrap;
}
blockquote {
  margin: 0 0 3mm 0;
  padding: 2mm 0 2mm 4mm;
  border-left: 2.5pt solid var(--gold);
  color: var(--muted);
}
"""

COVER = """
<section class="cover">
  <p class="eyebrow">Confidential  ·  Promoters, DFIs, banks and industrial partners</p>
  <h1>Ashlar Steel<span>Billet and Semi-Finished Steel<br/>Nigeria Plan &amp; Cost–Benefit Analysis</span></h1>
  <div class="rule"></div>
  <p class="lede">Two companies, one holding, one corridor. Ashlar Longs rolls TMT, wire rod and merchant bar. Ashlar Billets melts scrap and DRI only to feed that mill. Raise Phase 1 — 150 kt, ₦82 billion plant — then earn a captive melt. One million tonnes is a gate, not the opening cheque.</p>
  <dl>
    <dt>Prepared</dt><dd>September 2026  ·  v1.0</dd>
    <dt>Horizon</dt><dd>10 years (2028–2037)  ·  FX ₦1,500 / USD</dd>
    <dt>Phase 1</dt><dd>₦28.7 billion equity  ·  ₦53.3 billion DFI/bank  ·  150 kt longs</dd>
    <dt>Phase 2 (gated)</dt><dd>200 kt captive EAF  ·  ₦163 billion plant  ·  after 70% utilisation</dd>
    <dt>Planning Y10</dt><dd>₦159bn sales  ·  ₦7.9bn NPAT  ·  IRR 5.3% with residual</dd>
    <dt>₦100bn profit</dt><dd>Only the gated 1.0 Mt option (₦135bn NPAT, ₦692bn plant)</dd>
    <dt>Classification</dt><dd>Planning document — not financial, legal, tax or investment advice</dd>
  </dl>
  <div class="foot">
    <span>Ogun industrial corridor  →  West Africa offtake later</span>
    <span>CONFIDENTIAL</span>
  </div>
</section>
"""


def md_to_body_html(text: str) -> str:
    lines = text.splitlines()
    # Drop the two H1 title lines — the cover carries the title
    while lines and (lines[0].startswith("# ") or lines[0].strip() == ""):
        if lines[0].startswith("# "):
            lines = lines[1:]
            continue
        lines = lines[1:]
    text = "\n".join(lines)
    return markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "toc", "nl2br"],
        extension_configs={"toc": {"permalink": False}},
    )


def main() -> None:
    source = MD_PATH.read_text(encoding="utf-8")
    body = md_to_body_html(source)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Ashlar Steel — Billet and Semi-Finished Steel CBA (September 2026)</title>
  <style>{CSS}</style>
</head>
<body>
{COVER}
<main>
{body}
</main>
</body>
</html>
"""
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    HTML(string=html, base_url=str(ROOT)).write_pdf(OUT_PDF)
    size_kb = OUT_PDF.stat().st_size / 1024
    print(f"Wrote {OUT_PDF} ({size_kb:.0f} KB)")
    print(f"HTML preview: {OUT_HTML}")


if __name__ == "__main__":
    main()
