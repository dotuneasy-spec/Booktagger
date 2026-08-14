#!/usr/bin/env python3
from pathlib import Path
ORDER = """00-front-matter.md
01-preface.md
02-introduction.md
02b-how-to-read.md
28-ethics-note.md
03-ch01-tool-self.md
04-ch02-surface-depth.md
05-ch03-mapping.md
06-ch04-nodes.md
07-ch05-animation.md
08-ch06-plan-first.md
09-ch07-problems.md
10-ch08-dialectic.md
11-ch09-contrapuntal.md
12-ch10-conversation.md
13-ch11-umwelt.md
14-ch12-making-do.md
15-ch13-flights.md
16-ch14-self-differing.md
17-ch15-intuition.md
18-ch16-agency.md
19-ch17-one-being.md
20-ch18-poetic.md
27-singular-specific.md
26-bergson.md
23-studies.md
34-father.md
37-school.md
31-invisibility.md
32-memory.md
33-freedom.md
24-ordinary-life.md
29-a-day.md
39-language.md
38-remainders.md
36-intuitive-reason.md
40-winning.md
41-image-of-thought.md
25-spine.md
42-simplicity.md
35-objections.md
43-recap.md
21-coda.md
30-afterword.md
22-glossary.md""".strip().splitlines()
root = Path(__file__).parent
parts = []
for i, name in enumerate(ORDER):
    parts.append((root / name).read_text().rstrip())
    if i != len(ORDER) - 1:
        parts.append("\n\n---\n\n")
(root / "FULL-MANUSCRIPT.md").write_text("".join(parts) + "\n")
print("wrote FULL-MANUSCRIPT.md", len("".join(parts).split()), "words")
