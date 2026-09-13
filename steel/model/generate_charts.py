#!/usr/bin/env python3
"""Charts for the Ashlar Steel billet and longs CBA."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "charts"
OUT.mkdir(parents=True, exist_ok=True)
R = json.loads((ROOT / "model" / "outputs" / "model_results.json").read_text())
ST = R["scenarios"]["stress"]
PL = R["scenarios"]["planning"]
UP = R["scenarios"]["upside"]
CO = R["scenarios"]["concession"]
LO = R["longs_only"]
MT = R["one_mt"]
LABELS = R["year_labels"]

NAVY = "#1B3A4B"
TEAL = "#2A6F7F"
GOLD = "#C5922A"
COPPER = "#B87333"
RUST = "#B94A48"
SLATE = "#5C6B73"
INK = "#1A242B"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Noto Sans", "Liberation Sans"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#C9D0D4",
        "axes.labelcolor": INK,
        "xtick.color": "#3A4A44",
        "ytick.color": "#3A4A44",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.titleweight": "bold",
        "axes.titlesize": 11.5,
        "axes.titlecolor": NAVY,
        "figure.dpi": 140,
    }
)


def bn(n: float) -> float:
    return n / 1_000_000_000


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def fig_volume() -> None:
    x = np.arange(len(LABELS))
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.plot(x, [y["roll_t"] / 1000 for y in PL["years"]], "o-", color=TEAL, lw=2.2, label="Planning longs")
    ax.plot(x, [y["melt_t"] / 1000 for y in PL["years"]], "s--", color=COPPER, lw=2, label="Planning billets")
    ax.plot(x, [y["roll_t"] / 1000 for y in ST["years"]], "o-", color=RUST, lw=1.4, alpha=0.8, label="Stress longs")
    ax.plot(x, [y["roll_t"] / 1000 for y in UP["years"]], "o-", color=GOLD, lw=1.6, label="Upside longs")
    ax.set_xticks(x, [lb.replace(" ", "\n") for lb in LABELS], fontsize=7.5)
    ax.set_ylabel("Thousand tonnes / year")
    ax.set_title("Output path — longs first, captive melt from Year 5")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_volume.png")


def fig_npat() -> None:
    x = np.arange(len(LABELS))
    w = 0.22
    fig, ax = plt.subplots(figsize=(8.8, 4.3))
    ax.bar(x - 1.5 * w, [bn(y["npat"]) for y in ST["years"]], w, color=RUST, label="Stress")
    ax.bar(x - 0.5 * w, [bn(y["npat"]) for y in PL["years"]], w, color=TEAL, label="Planning")
    ax.bar(x + 0.5 * w, [bn(y["npat"]) for y in CO["years"]], w, color=NAVY, label="Concession power")
    ax.bar(x + 1.5 * w, [bn(y["npat"]) for y in UP["years"]], w, color=GOLD, label="Upside")
    ax.axhline(0, color=SLATE, lw=0.7)
    ax.set_xticks(x, [lb.split()[0] for lb in LABELS])
    ax.set_ylabel("NPAT (NGN billion)")
    ax.set_title("Net profit — melt only helps if power is cheap")
    ax.legend(frameon=False, ncols=2, fontsize=8)
    save(fig, "fig_npat.png")


def fig_npv() -> None:
    labels = ["Stress", "Longs only", "Planning\nfull", "Concession\npower", "Upside", "1.0 Mt\ngated"]
    v18 = [
        bn(ST["npv_18_resid"]),
        bn(LO["npv_18_resid"]),
        bn(PL["npv_18_resid"]),
        bn(CO["npv_18_resid"]),
        bn(UP["npv_18_resid"]),
        bn(MT["npv_18_resid"]),
    ]
    v12 = [
        bn(ST["npv_12_resid"]),
        bn(LO["npv_12_resid"]),
        bn(PL["npv_12_resid"]),
        bn(CO["npv_12_resid"]),
        bn(UP["npv_12_resid"]),
        bn(MT["npv_12_resid"]),
    ]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.6, 4.3))
    ax.bar(x - 0.18, v18, 0.36, color=TEAL, label="NPV @ 18% + residual")
    ax.bar(x + 0.18, v12, 0.36, color=GOLD, label="NPV @ 12% + residual (DFI)")
    ax.axhline(0, color=SLATE, lw=0.8)
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylabel("NGN billion")
    ax.set_title("Value shows up at a DFI hurdle or with concession power")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_npv.png")


def fig_spread() -> None:
    u = R["unit"]["planning"]
    labels = [
        "Import billet\n+ roll",
        "Own billet\n+ roll",
        "Melt vs\nimport billet",
    ]
    vals = [
        u["longs_spread_import"] / 1000,
        u["longs_spread_own"] / 1000,
        u["melt_vs_import"] / 1000,
    ]
    colors = [SLATE, TEAL, COPPER]
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    bars = ax.bar(labels, vals, color=colors, width=0.55)
    ax.set_ylabel("NGN thousand per tonne")
    ax.set_title("Planning cash spread — melt doubles the longs margin")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 6, f"{v:,.0f}k", ha="center", fontsize=9, color=NAVY)
    ax.set_ylim(0, max(vals) * 1.2)
    save(fig, "fig_spread.png")


def fig_capex() -> None:
    labels = ["LongsCo\nPhase 1", "BilletCo\n+ power", "Full\nplanning", "Concession\npower", "1.0 Mt\ngated"]
    vals = [
        bn(LO["total_plant"]),
        bn(PL["total_plant"] - LO["total_plant"]),
        bn(PL["total_plant"]),
        bn(CO["total_plant"]),
        bn(MT["total_plant"]),
    ]
    colors = [TEAL, COPPER, NAVY, GOLD, RUST]
    fig, ax = plt.subplots(figsize=(8.4, 4.1))
    ax.bar(labels, vals, color=colors, width=0.6)
    ax.set_ylabel("Plant capex (NGN billion)")
    ax.set_title("Capital committed — 1.0 Mt is a different company")
    for i, v in enumerate(vals):
        ax.text(i, v + 8, f"{v:.0f}bn", ha="center", fontsize=8, color=NAVY)
    ax.set_ylim(0, max(vals) * 1.15)
    save(fig, "fig_capex.png")


def fig_hundred() -> None:
    labels = ["Longs\nonly", "Planning\nfull", "Concession\npower", "Upside", "1.0 Mt\ngated"]
    npat = [
        bn(LO["y10_npat"]),
        bn(PL["y10_npat"]),
        bn(CO["y10_npat"]),
        bn(UP["y10_npat"]),
        bn(MT["y10_npat"]),
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    colors = [TEAL, NAVY, GOLD, COPPER, RUST]
    ax.bar(labels, npat, color=colors, width=0.55)
    ax.axhline(100, color=RUST, ls="--", lw=1.2)
    ax.text(4.15, 103, "NGN 100bn NPAT", color=RUST, fontsize=8, ha="right")
    ax.set_ylabel("Year-10 NPAT (NGN billion)")
    ax.set_title("The profit bar is a 1.0 Mt crude programme, not Phase 1")
    save(fig, "fig_hundred.png")


def fig_phases() -> None:
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    stages = ["Phase 1\nLongsCo\n150 kt", "Gate", "Phase 2\nBilletCo\n200 kt captive", "Gate", "Option\n1.0 Mt"]
    vals = [82, 0, 163, 0, 692]
    xs = [0, 1.1, 2.2, 3.3, 4.4]
    ax.bar([xs[0]], [82], color=TEAL, width=0.7)
    ax.bar([xs[2]], [163], color=COPPER, width=0.7)
    ax.bar([xs[4]], [692], color=NAVY, width=0.7)
    ax.set_xticks(xs, stages, fontsize=8)
    ax.set_ylabel("NGN billion plant")
    ax.set_title("Commit Phase 1. Earn Phase 2. Do not buy 1.0 Mt on a slide.")
    ax.text(xs[0], 95, "82bn", ha="center", color=NAVY, fontsize=8)
    ax.text(xs[2], 180, "163bn", ha="center", color=NAVY, fontsize=8)
    ax.text(xs[4], 720, "692bn", ha="center", color=NAVY, fontsize=8)
    ax.set_ylim(0, 820)
    save(fig, "fig_phases.png")


if __name__ == "__main__":
    fig_volume()
    fig_npat()
    fig_npv()
    fig_spread()
    fig_capex()
    fig_hundred()
    fig_phases()
