#!/usr/bin/env python3
"""Compare Italian vs English chapter lengths."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
IT = ROOT / "italian"
EN = ROOT / "english"

def words(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^#.*$", "", text, flags=re.M)
    return len(text.split())

print(f"{'ch':>4} {'IT':>6} {'EN':>6} {'ratio':>7} status")
missing = []
short = []
for i in range(1, 51):
    it = IT / f"chapter_{i:02d}.txt"
    en = EN / f"chapter_{i:02d}.md"
    if not en.exists():
        print(f"{i:4d} {words(it):6d} {'—':>6} {'—':>7} MISSING")
        missing.append(i)
        continue
    iw, ew = words(it), words(en)
    ratio = ew / iw if iw else 0
    flag = "ok"
    if ratio < 0.75:
        flag = "SHORT"
        short.append(i)
    elif ratio > 1.45:
        flag = "LONG"
    print(f"{i:4d} {iw:6d} {ew:6d} {ratio:7.2f} {flag}")

print()
print("missing:", missing or "none")
print("short:", short or "none")
