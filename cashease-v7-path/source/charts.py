"""Charts for the path to ₦50 billion."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#1c3144"
GOLD = "#8a6a2f"
RED = "#8d2b2b"
GREEN = "#1f6b4a"
GRID = "#e6e1d8"


def _style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)


def draw(results: dict, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "Liberation Sans"
    order = [
        ("low_100_200", "Low invoice\n200 a day, keep all"),
        ("high_100_200", "High band\n200 a day, keep all"),
        ("high_70_200", "High band\n200 a day, bank takes 30%"),
        ("high_100_120", "High band\n120 a day, keep all"),
    ]
    labels = [label for _, label in order]
    vals = [results["cases"][key]["machines"] for key, _ in order]
    colors = [GREEN, NAVY, GOLD, RED]
    fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=150)
    bars = ax.barh(labels[::-1], vals[::-1], color=colors[::-1], zorder=2)
    for bar, val in zip(bars, vals[::-1]):
        ax.text(val + 80, bar.get_y() + bar.get_height() / 2, f"{val:,}", va="center", fontsize=9)
    ax.set_xlabel("Machines that produce a ₦50 billion value")
    ax.set_xlim(0, max(vals) * 1.18)
    _style(ax)
    fig.tight_layout()
    fig.savefig(dest / "fig_machines.png")
    plt.close()

    tranches = results["tranches"]
    labels = [f"{t['n']:,}" for t in tranches]
    vals = [t["npv"] / 1e9 for t in tranches]
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=150)
    bars = ax.bar(labels, vals, color=NAVY, zorder=2)
    ax.axhline(50, color=GOLD, linewidth=1.2, linestyle="--", zorder=1)
    ax.text(0, 53.2, "₦50 billion", color=GOLD, fontsize=9, ha="left")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.2, f"{val:.1f}", ha="center", fontsize=9)
    ax.set_xlabel("Opening fleet, machines")
    ax.set_ylabel("Value at 28%, ₦ billion")
    ax.set_ylim(0, 62)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(dest / "fig_tranches.png")
    plt.close()
