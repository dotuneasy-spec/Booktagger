#!/usr/bin/env python3
"""Build the SNLB Farms bankable IM as a print-ready A4 PDF."""
from __future__ import annotations

from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "SNLB_Farms_Comprehensive_Feasibility_Study.md"
OUT_PDF = ROOT / "SNLB_Farms_Comprehensive_Feasibility_Study.pdf"
OUT_HTML = ROOT / "build" / "im.html"

CSS = r"""
@page {
  size: A4;
  margin: 16mm 14mm 18mm 14mm;
  @top-left {
    content: "SNLB Farms  ·  Comprehensive Feasibility Study  ·  August 2026";
    font-family: Inter, "Noto Sans", "DejaVu Sans", sans-serif;
    font-size: 7.5pt;
    color: #5a656c;
  }
  @top-right {
    content: "CONFIDENTIAL";
    font-family: Inter, "Noto Sans", "DejaVu Sans", sans-serif;
    font-size: 7.5pt;
    font-weight: 700;
    color: #8a1f1f;
    letter-spacing: 0.08em;
  }
  @bottom-left {
    content: "August 2026  ·  Ogun State → Mile 12  ·  Two-cycle self-fund model";
    font-family: Inter, "Noto Sans", "DejaVu Sans", sans-serif;
    font-size: 7.5pt;
    color: #5a656c;
  }
  @bottom-right {
    content: "Page " counter(page);
    font-family: Inter, "Noto Sans", "DejaVu Sans", sans-serif;
    font-size: 7.5pt;
    color: #1f2a30;
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
  --ink: #1c2428;
  --muted: #4e5b62;
  --rule: #d5ddd8;
  --green: #1b4d3e;
  --green-2: #2f6f5b;
  --gold: #c4a35a;
  --paper: #fbfaf6;
  --band: #eef4f0;
}

html, body {
  font-family: Inter, "Noto Sans", "DejaVu Sans", sans-serif;
  font-size: 9.4pt;
  line-height: 1.42;
  color: var(--ink);
  background: white;
}

.cover {
  page: first;
  page-break-after: always;
  break-after: page;
  min-height: 297mm;
  background: #14261f;
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
  color: #d9e6df;
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
  max-width: 145mm;
  color: #e7eee9;
  margin: 0 0 16mm 0;
}
.cover dl {
  display: grid;
  grid-template-columns: 38mm 1fr;
  gap: 2.2mm 4mm;
  font-size: 9.5pt;
  margin: 0;
}
.cover dt {
  color: #b7c7bf;
  font-weight: 500;
}
.cover dd {
  margin: 0;
  color: #fff;
  font-weight: 600;
}
.cover .foot {
  position: absolute;
  left: 20mm;
  right: 20mm;
  bottom: 16mm;
  display: flex;
  justify-content: space-between;
  font-size: 8pt;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #b7c7bf;
  border-top: 0.4pt solid #3a554b;
  padding-top: 5mm;
}

h1, h2, h3, h4 {
  color: var(--green);
  font-weight: 700;
  line-height: 1.2;
  page-break-after: avoid;
}
h1 {
  font-size: 16pt;
  margin: 5mm 0 3mm 0;
  padding-bottom: 1.6mm;
  border-bottom: 1.6pt solid var(--green);
}
h2 {
  font-size: 12.2pt;
  margin: 5.5mm 0 2mm 0;
  padding-bottom: 0.8mm;
  border-bottom: 0.4pt solid var(--rule);
}
h3 {
  font-size: 10.4pt;
  margin: 4mm 0 1.5mm 0;
  color: #243832;
}
h4 {
  font-size: 9.6pt;
  margin: 3mm 0 1mm 0;
  color: #2c3c36;
}
p { margin: 0 0 2.4mm 0; }
strong { font-weight: 650; color: #152019; }
em { font-style: italic; }
a { color: var(--green-2); text-decoration: none; }

hr {
  border: 0;
  border-top: 0.4pt solid var(--rule);
  margin: 4mm 0;
}

ul, ol {
  margin: 0 0 2.6mm 4.5mm;
  padding: 0;
}
li { margin: 0 0 1mm 0; }
li ul, li ol { margin-top: 1mm; margin-bottom: 1mm; }

blockquote {
  margin: 0 0 3mm 0;
  padding: 2.2mm 3.5mm;
  background: var(--band);
  border-left: 2.4pt solid var(--green);
  color: #24322c;
}

code {
  font-family: "JetBrains Mono", "Noto Sans Mono", "DejaVu Sans Mono", monospace;
  font-size: 8.2pt;
  background: #f1f3f1;
  padding: 0 1.2pt;
}
pre {
  background: #f3f5f3;
  border: 0.4pt solid var(--rule);
  padding: 2.5mm;
  font-size: 8pt;
  line-height: 1.35;
  white-space: pre-wrap;
  page-break-inside: avoid;
}
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1.5mm auto 3.2mm auto;
  page-break-inside: avoid;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 3.5mm 0;
  font-size: 7.7pt;
  line-height: 1.28;
  page-break-inside: auto;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th {
  background: var(--green);
  color: #fff;
  font-weight: 650;
  text-align: left;
  padding: 1.5mm 1.8mm;
  vertical-align: bottom;
}
td {
  padding: 1.3mm 1.8mm;
  border-bottom: 0.35pt solid var(--rule);
  vertical-align: top;
}
tbody tr:nth-child(even) td { background: #f6f8f6; }

input[type="checkbox"] {
  transform: scale(0.85);
  margin-right: 1.5mm;
}

.toc-cover-skip { display: none; }
"""


def md_to_body_html(text: str) -> str:
    # Cover consumes the two title lines.
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    text = "\n".join(lines)

    # GitHub-style task list → HTML checkboxes (print-safe).
    def tasks(line: str) -> str:
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if stripped.startswith("- [ ] "):
            return f'{indent}- <input type="checkbox"/> {stripped[6:]}'
        if stripped.startswith("- [x] ") or stripped.startswith("- [X] "):
            return f'{indent}- <input type="checkbox" checked/> {stripped[6:]}'
        return line

    text = "\n".join(tasks(ln) for ln in text.splitlines())

    return markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "toc", "nl2br"],
        extension_configs={"toc": {"permalink": False}},
    )


COVER = """
<section class="cover">
  <p class="eyebrow">Confidential  ·  Promoters, advisors, lenders and DFIs</p>
  <h1>SNLB Farms<span>Comprehensive Feasibility Study</span></h1>
  <div class="rule"></div>
  <p class="lede">Commercial tomato farming on a leased 100-hectare master block in Ogun State, Nigeria, supplying Mile 12 International Market, Lagos. A self-funding expansion from 1 hectare to 100 hectares through two-cycle production, 50/50 reinvestment and progressive mechanization.</p>
  <dl>
    <dt>Entity</dt><dd>SNLB ENTERPRISE BN 6922259  ·  proposed SNLB Farms Limited</dd>
    <dt>Horizon</dt><dd>5 years / 10 cycles  ·  1 ha → 100 ha in six cycles (3 years)</dd>
    <dt>Planning case NPV</dt><dd>₦5.78 billion at 18% (Regular first, non-glut, 5-year, no TV)</dd>
    <dt>Opening capital</dt><dd>₦8.0 million (₦3.0m CapEx + ₦5.0m Cycle 1 working capital)</dd>
    <dt>Includes</dt><dd>SWOT · ESG · charts · NPV/IRR · three scenarios · Cycle 1 ₦8m uses · optional ₦80m facility</dd>
  </dl>
  <div class="foot">
    <span>Ogun State  →  Mile 12, Lagos</span>
    <span>Self-fund path  ·  optional external facility</span>
  </div>
</section>
"""


def main() -> None:
    source = MD_PATH.read_text(encoding="utf-8")
    body = md_to_body_html(source)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>SNLB Farms — Comprehensive Feasibility Study (August 2026)</title>
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
