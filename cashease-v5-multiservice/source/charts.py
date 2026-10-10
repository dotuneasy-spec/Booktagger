"""Charts for the v5 multi-service study."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#1c3144"
GOLD = "#8a6a2f"
RED = "#8d2b2b"
GREEN = "#1f6b4a"
GRID = "#e6e1d8"


def _style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID, zorder=0)
    ax.set_axisbelow(True)


def draw(results: dict, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "Liberation Sans"
    boxes = results["boxes"]
    order = (
        ("recycler_low", "Recycler\nlow band"),
        ("recycler_high", "Recycler\nhigh band"),
        ("kiosk_low", "Cash-in\nlow band"),
        ("kiosk_high", "Cash-in\nhigh band"),
    )
    vals = [boxes[k]["all_in_ngn"] / 1e6 for k, _ in order]
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=150)
    colors = [NAVY, GOLD, GREEN, RED]
    bars = ax.bar([b[1] for b in order], vals, color=colors, zorder=2)
    ax.set_ylabel("Naira million, first machine")
    ax.set_title("Landed cost, first machine, site works included")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.4, f"{val:.1f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, max(vals) * 1.18)
    _style(ax)
    fig.tight_layout()
    fig.savefig(dest / "fig_landed.png")
    plt.close()

    unit = results["units"]["recycler_high"]
    volumes = (60, 120, 200)
    splits = ("100/0", "70/30", "50/50")
    colors = {"100/0": GREEN, "70/30": GOLD, "50/50": RED}
    import numpy as np

    x = np.arange(len(volumes))
    width = 0.24
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=150)
    for i, split in enumerate(splits):
        heights = [unit["splits"][split][str(wd)]["cash"] / 1e6 for wd in volumes]
        bars = ax.bar(x + (i - 1) * width, heights, width, label=f"CashEase/bank {split}", color=colors[split], zorder=2)
        for bar, h in zip(bars, heights):
            va = "bottom" if h >= 0 else "top"
            off = 0.35 if h >= 0 else -0.35
            ax.text(bar.get_x() + bar.get_width() / 2, h + off, f"{h:.1f}", ha="center", va=va, fontsize=8)
    ax.axhline(0, color=NAVY, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{wd} a day" for wd in volumes])
    ax.set_ylabel("Cash profit, Naira million a year")
    ax.set_title("High-band recycler, surcharge only, bank carries the cash")
    ax.legend(frameon=False, fontsize=8)
    ax.set_ylim(-4, 26)
    _style(ax)
    fig.tight_layout()
    fig.savefig(dest / "fig_cash.png")
    plt.close()

    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=150)
    for i, split in enumerate(splits):
        heights = []
        for wd in volumes:
            irr = unit["splits"][split][str(wd)]["irr"]
            heights.append(None if irr is None else irr * 100)
        ys = [0 if h is None else h for h in heights]
        bars = ax.bar(x + (i - 1) * width, ys, width, label=f"{split}", color=colors[split], zorder=2)
        for bar, h in zip(bars, heights):
            if h is None:
                bar.set_height(0)
                ax.text(bar.get_x() + bar.get_width() / 2, 2, "none", ha="center", va="bottom", fontsize=8, color=RED)
            else:
                va = "bottom" if h >= 0 else "top"
                off = 1.8 if h >= 0 else -1.8
                ax.text(bar.get_x() + bar.get_width() / 2, h + off, f"{h:.0f}%", ha="center", va=va, fontsize=8)
    ax.axhline(28, color=NAVY, linestyle="--", linewidth=1, label="28% hurdle")
    ax.axhline(0, color=NAVY, linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{wd} a day" for wd in volumes])
    ax.set_ylabel("IRR, percent")
    ax.set_title("Return on one high-band recycler")
    ax.legend(frameon=False, fontsize=8)
    ax.set_ylim(-20, 110)
    _style(ax)
    fig.tight_layout()
    fig.savefig(dest / "fig_irr.png")
    plt.close()
