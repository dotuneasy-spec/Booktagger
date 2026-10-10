"""Charts for the China-machine path."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#1c3144"
GOLD = "#8a6a2f"
RED = "#8d2b2b"
GREEN = "#1f6b4a"
GRID = "#e6e1d8"


def draw(results: dict, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "Liberation Sans"
    labels = [
        "Hongzhou US$4,800\nno adder",
        "Hongzhou US$4,800\nplus US$1,800",
        "Hongzhou US$5,500\nplus US$1,800",
        "Listing high band\nUS$7,850 plus US$1,800",
    ]
    keys = ("hz4800_plain", "hz4800_custom", "hz5500_custom", "high_band")
    vals = [results["boxes"][k]["all_in_ngn"] / 1e6 for k in keys]
    colors = [GREEN, NAVY, GOLD, RED]
    fig, ax = plt.subplots(figsize=(7.4, 4.0), dpi=150)
    bars = ax.barh(labels[::-1], vals[::-1], color=colors[::-1], zorder=2)
    for bar, val in zip(bars, vals[::-1]):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2, f"₦{val:.1f}m", va="center", fontsize=9)
    ax.set_xlabel("Landed cost, first machine, ₦ million")
    ax.set_xlim(0, max(vals) * 1.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(dest / "fig_landed.png")
    plt.close()

    order = [
        ("plain_100_200", "US$4,800 plain\n200 a day, keep all"),
        ("custom_100_200", "US$4,800 plus adder\n200 a day, keep all"),
        ("high_100_200", "High band\n200 a day, keep all"),
        ("custom_70_200", "US$4,800 plus adder\n200 a day, bank takes 30%"),
    ]
    labels = [label for _, label in order]
    vals = [results["cases"][key]["machines"] for key, _ in order]
    colors = [GREEN, NAVY, GOLD, RED]
    fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=150)
    bars = ax.barh(labels[::-1], vals[::-1], color=colors[::-1], zorder=2)
    for bar, val in zip(bars, vals[::-1]):
        ax.text(val + 30, bar.get_y() + bar.get_height() / 2, f"{val:,}", va="center", fontsize=9)
    ax.set_xlabel("Machines that produce a ₦50 billion value")
    ax.set_xlim(0, max(vals) * 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(dest / "fig_fleets.png")
    plt.close()
