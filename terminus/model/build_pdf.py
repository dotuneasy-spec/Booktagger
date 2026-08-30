#!/usr/bin/env python3
"""Build the interstate terminus CBA as a print-ready A4 PDF."""
from __future__ import annotations

from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "Interstate_Terminus_CBA.md"
OUT_PDF = ROOT / "Interstate_Terminus_CBA.pdf"
OUT_HTML = ROOT / "build" / "study.html"

CSS = r"""
@page {
  size: A4;
  margin: 16mm 14mm 18mm 14mm;
  @top-left {
    content: "Interstate coach terminus  ·  Cost–benefit  ·  August 2026";
    font-family: "DejaVu Sans", "Noto Sans", sans-serif;
    font-size: 7.5pt;
    color: #5c6b73;
  }
  @top-right {
    content: "PLANNING NOTE";
    font-family: "DejaVu Sans", "Noto Sans", sans-serif;
    font-size: 7.5pt;
    font-weight: 700;
    color: #8a1f1f;
    letter-spacing: 0.06em;
  }
  @bottom-left {
    content: "Rent the station  ·  do not buy the buses";
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
  --muted: #5c6b73;
  --gold: #b8860b;
  --paper: #f7f4ee;
}
html, body {
  font-family: "DejaVu Sans", "Noto Sans", sans-serif;
  font-size: 9.4pt;
  line-height: 1.38;
  color: var(--ink);
}
.cover {
  background: var(--paper);
  min-height: 277mm;
  padding: 28mm 18mm 16mm 18mm;
  box-sizing: border-box;
}
.cover h1 {
  font-size: 26pt;
  font-weight: 700;
  margin: 8mm 0 2mm 0;
  letter-spacing: -0.02em;
}
.cover h1 span {
  display: block;
  font-size: 14pt;
  font-weight: 500;
  color: var(--muted);
  margin-top: 2mm;
}
.cover .lede {
  font-size: 10.5pt;
  color: var(--muted);
  max-width: 165mm;
  border-left: 2.5pt solid var(--gold);
  padding: 2mm 0 2mm 4mm;
  margin: 8mm 0 10mm 0;
}
.cover dl {
  display: grid;
  grid-template-columns: 42mm 1fr;
  gap: 1.5mm 4mm;
  font-size: 9pt;
}
.cover dt { color: var(--muted); }
.cover dd { margin: 0; font-weight: 600; }
.cover .foot {
  position: absolute;
  bottom: 16mm;
  left: 18mm;
  right: 18mm;
  display: flex;
  justify-content: space-between;
  font-size: 8pt;
  color: var(--muted);
}
h1 { font-size: 16pt; margin: 6mm 0 3mm; }
h2 { font-size: 12.5pt; margin: 5mm 0 2mm; border-bottom: 0.6pt solid #d8d0c4; padding-bottom: 1mm; }
h3 { font-size: 10.5pt; margin: 4mm 0 1.5mm; }
p { margin: 0 0 2.2mm 0; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 8.4pt;
  margin: 0 0 3.5mm 0;
}
th, td {
  border: 0.4pt solid #cfc6b8;
  padding: 1.4mm 2mm;
  text-align: left;
  vertical-align: top;
}
th { background: #efe8dc; font-weight: 700; }
tr:nth-child(even) td { background: #fbf9f5; }
blockquote {
  margin: 0 0 3mm 0;
  padding: 2mm 0 2mm 4mm;
  border-left: 2.5pt solid var(--gold);
  color: var(--muted);
}
ul, ol { margin: 0 0 2.5mm 4mm; }
code { font-size: 8pt; }
hr { border: none; border-top: 0.4pt solid #d8d0c4; margin: 4mm 0; }
a { color: var(--ink); }
"""

COVER = """
<section class="cover">
  <p style="letter-spacing:0.12em;font-size:8pt;color:#5c6b73;font-weight:700;">PLANNING NOTE  ·  PROMOTERS AND ADVISORS</p>
  <h1>Interstate coach terminus<span>Cost–benefit analysis</span></h1>
  <div style="height:2pt;width:28mm;background:#b8860b;margin:4mm 0 8mm;"></div>
  <p class="lede">Private state-to-state station. Rent bays and night slots to private fleets. Do not buy the buses. Take rent plus shops, parking and ads — not the ticket. Everyday waves on the same concrete.</p>
  <dl>
    <dt>Prepared</dt><dd>August 2026</dd>
    <dt>Planning capital</dt><dd>₦2.57 billion · ~2 ha highway-edge Lagos–Ogun</dd>
    <dt>Y3 run-rate</dt><dd>₦960m gross · ₦542m EBITDA · ₦310m NPAT</dd>
    <dt>Unlevered IRR</dt><dd>16% planning · −9% stress · 43% if land is a concession</dd>
    <dt>NPV @ 22%</dt><dd>Planning −₦0.71bn · clears ~15% property hurdle</dd>
    <dt>Versus fleet</dt><dd>Same ~₦2.6bn buys 25 coaches; higher paper NPAT, worse residual</dd>
  </dl>
  <div class="foot">
    <span>Rent the station  ·  do not buy the buses</span>
    <span>ILLUSTRATIVE</span>
  </div>
</section>
"""


def main() -> None:
    md = MD_PATH.read_text(encoding="utf-8")
    # Cover already has the title; drop the markdown H1 block through the first rule.
    cut = md.find("A private **state-to-state**")
    if cut > 0:
        md = md[cut:]
    body = markdown.markdown(
        md,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{COVER}<article class="doc">{body}</article></body></html>"""
    OUT_HTML.parent.mkdir(exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    HTML(filename=str(OUT_HTML), base_url=str(ROOT)).write_pdf(str(OUT_PDF))
    print(f"Wrote {OUT_PDF} ({OUT_PDF.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
