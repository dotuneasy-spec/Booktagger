#!/usr/bin/env python3
"""Build the CashEase feasibility study as a print-ready A4 PDF."""
from __future__ import annotations

from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "CashEase_Feasibility_Study.md"
OUT_PDF = ROOT / "CashEase_Feasibility_Study.pdf"
OUT_HTML = ROOT / "build" / "study.html"

CSS = r"""
@page {
  size: A4;
  margin: 16mm 14mm 18mm 14mm;
  @top-left {
    content: "CashEase Nigeria  ·  Feasibility Study  ·  August 2026";
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
    content: "Own the kiosk  ·  bank owns the float  ·  follow people, not place-names";
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
  font-size: 28pt;
  line-height: 1.08;
  font-weight: 700;
  margin: 0 0 6mm 0;
  color: #fff;
  border: 0;
  padding: 0;
}
.cover h1 span {
  display: block;
  font-size: 15pt;
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
  font-size: 12pt;
  line-height: 1.4;
  max-width: 155mm;
  color: #e7eef1;
  margin: 0 0 16mm 0;
}
.cover dl {
  display: grid;
  grid-template-columns: 38mm 1fr;
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
  font-size: 8.3pt;
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
  <p class="eyebrow">Confidential  ·  Promoters, advisors, banks and DFIs</p>
  <h1>CashEase Nigeria<span>Feasibility Study</span></h1>
  <div class="rule"></div>
  <p class="lede">Owned multi-service cash kiosks on everyday streets — petty traders, mallams, bus waits. Note-breaking, POS cash-out, airtime and bills. Pain follows people; availability is ATM-like. Destination: an inclusive, holistic stall platform (cash, restock, goods on credit, BNPL) for traders Omni-class apps skip. The company owns the machines; a bank supplies small notes and settlement. One machine per counted pitch. Raise ₦1.85 billion for 350 kiosks, then fund 2,000.</p>
  <dl>
    <dt>Prepared</dt><dd>August 2026  ·  v2.8</dd>
    <dt>Horizon</dt><dd>6 years (2027–2032)  ·  350 → 2,000 → earned scale</dd>
    <dt>Opening equity</dt><dd>₦1.85 billion for 350 kiosks (planning case)</dd>
    <dt>Planning unit</dt><dd>180 tx/day  ·  ₦100 blended fee  ·  break-even 89 tx/day</dd>
    <dt>First operating scale</dt><dd>Hold at 2,000 with an ₦8–12 billion facility (DSCR ~2×)</dd>
    <dt>Classification</dt><dd>Planning document — not financial, legal, tax or investment advice</dd>
  </dl>
  <div class="foot">
    <span>Lagos / Ogun first  →  national hubs later</span>
    <span>CONFIDENTIAL</span>
  </div>
</section>
"""


def md_to_body_html(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    if lines and lines[0].startswith("# "):
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
  <title>CashEase Nigeria — Feasibility Study (August 2026)</title>
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
