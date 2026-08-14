#!/usr/bin/env python3
"""Build Thinking as One Being as a typeset PDF with a graphic cover."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path("/workspace/book")
ASSETS = ROOT / "assets"
SRC = ROOT / "FULL-MANUSCRIPT.md"
BODY_MD = ROOT / "_pdf_body.md"
BODY_TYP = ROOT / "_pdf_body.typ"
PREAMBLE = ROOT / "_pdf_preamble.typ"
OUT_TYP = ROOT / "book.typ"
OUT_PDF = ROOT / "Thinking-as-One-Being.pdf"


def prepare_markdown(text: str) -> str:
    # Drop the opening title block; the cover carries title and subtitle.
    text = re.sub(
        r"^# Thinking as One Being\n\n## The Mind of Ayanokoji\n\n"
        r"A study of singular thought, intuition, and the quiet machinery of a tool-self\.\n+",
        "",
        text,
        count=1,
    )
    # Chapter file separators become page breaks later; keep a blank line.
    text = text.replace("\n\\newpage\n", "\n\n")
    return text


def wrap_typst(body: str) -> str:
    # Chapter separators from the assembled manuscript.
    body = body.replace("#horizontalrule", "#pagebreak(weak: true)")
    # Soften raw heading anchors looking noisy — leave pandoc anchors; Typst uses them.
    return PREAMBLE.read_text() + "\n\n" + body + "\n"


PREAMBLE.write_text(
    r'''
#set document(
  title: "Thinking as One Being",
  author: "A study of singular thought",
  keywords: ("singular thought", "Ayanokoji", "image of thought"),
)

#set page(
  width: 6in,
  height: 9in,
  margin: (inside: 0.85in, outside: 0.7in, top: 0.75in, bottom: 0.8in),
  numbering: none,
)

#set text(
  font: "Liberation Serif",
  size: 11pt,
  lang: "en",
  hyphenate: true,
)

#set par(justify: true, leading: 0.72em, first-line-indent: 1.15em, spacing: 0.72em)
#set heading(numbering: none)

#show heading: it => {
  set par(first-line-indent: 0em, justify: false)
  set text(font: "Liberation Sans", weight: "bold", hyphenate: false)
  v(1.35em, weak: true)
  if it.level == 1 {
    pagebreak(weak: true)
    block(spacing: 0.55em)[
      #text(size: 20pt, tracking: 0.4pt, fill: rgb("#1a1a1a"))[#it.body]
    ]
    v(0.85em)
  } else if it.level == 2 {
    block(spacing: 0.45em)[
      #text(size: 14.5pt, fill: rgb("#222"))[#it.body]
    ]
    v(0.45em)
  } else {
    block(spacing: 0.35em)[
      #text(size: 12pt, fill: rgb("#333"))[#it.body]
    ]
    v(0.3em)
  }
}

#show emph: it => text(style: "italic", it.body)
#show strong: it => text(weight: "bold", it.body)
#show link: it => underline(it)

#show outline.entry.where(level: 1): it => {
  v(0.35em, weak: true)
  strong(it)
}

// ---------- Cover ----------
#page(margin: 0pt, numbering: none)[
  #block(width: 100%, height: 100%, clip: true)[
    #image("assets/cover-ayanokoji.png", width: 100%, height: 100%, fit: "cover")
  ]
  #place(bottom + left)[
    #block(
      width: 6in,
      fill: gradient.linear(
        rgb(0, 0, 0, 0%),
        rgb(0, 0, 0, 78%),
        rgb(0, 0, 0, 92%),
        angle: 90deg,
      ),
      inset: (x: 1.15cm, top: 2.4cm, bottom: 1.35cm),
    )[
      #set par(first-line-indent: 0em, justify: false, leading: 0.95em)
      #set text(fill: rgb("#f4efe6"), font: "Liberation Serif")
      #text(size: 11pt, tracking: 3.2pt, fill: rgb("#c9b896"))[A STUDY OF SINGULAR THOUGHT]
      #v(0.55em)
      #text(size: 32pt, weight: "bold")[Thinking as#linebreak()One Being]
      #v(0.45em)
      #text(size: 15pt, fill: rgb("#e6d7b8"))[The Mind of Ayanokoji]
    ]
  ]
]

// ---------- Half title ----------
#page(numbering: none)[
  #align(center + horizon)[
    #set par(first-line-indent: 0em, justify: false)
    #text(size: 11pt, tracking: 2.8pt, font: "Liberation Sans", fill: rgb("#666"))[SINGULAR THOUGHT]
    #v(1.1em)
    #text(size: 26pt, font: "Liberation Serif")[Thinking as One Being]
    #v(0.55em)
    #line(length: 28%, stroke: 0.5pt + rgb("#888"))
    #v(0.55em)
    #text(size: 13pt, fill: rgb("#444"))[The Mind of Ayanokoji]
  ]
]

#pagebreak()
#set page(numbering: "1", number-align: center)
#counter(page).update(1)
'''.lstrip()
)

def main() -> None:
    md = prepare_markdown(SRC.read_text())
    BODY_MD.write_text(md)
    subprocess.run(
        [
            "pandoc",
            str(BODY_MD),
            "-t",
            "typst",
            "-o",
            str(BODY_TYP),
            "--wrap=none",
        ],
        check=True,
    )
    body = BODY_TYP.read_text()
    OUT_TYP.write_text(wrap_typst(body))
    subprocess.run(
        ["typst", "compile", "--root", str(ROOT), str(OUT_TYP), str(OUT_PDF)],
        check=True,
    )
    print("wrote", OUT_PDF, "size", OUT_PDF.stat().st_size)


if __name__ == "__main__":
    main()
