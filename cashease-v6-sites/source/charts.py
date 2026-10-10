"""Charts for the site-partnership study."""

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
    labels = ["100/0", "70/30", "50/50", "Average existing\nATM, all cards"]
    vals = [
        results["be"]["100/0"]["full"],
        results["be"]["70/30"]["full"],
        results["be"]["50/50"]["full"],
        results["per_atm_withdrawals"],
    ]
    colors = [GREEN, GOLD, RED, NAVY]
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=150)
    bars = ax.bar(labels, vals, color=colors, zorder=2)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 6, f"{val:.0f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Withdrawals a day")
    ax.set_title("Full-cost hurdle on the high-band machine, beside the national ATM average")
    ax.set_ylim(0, max(vals) * 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(dest / "fig_hurdle.png")
    plt.close()
