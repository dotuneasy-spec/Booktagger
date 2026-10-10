"""Charts for the bank-owned operator addendum."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

NAVY = "#1c3144"
GOLD = "#8a6a2f"
RED = "#8d2b2b"
GREEN = "#1f6b4a"
INK = "#243038"
GRID = "#e6e1d8"

plt.rcParams.update(
    {
        "font.family": "Liberation Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": NAVY,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
    }
)


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def draw(results: dict, folder: Path) -> dict[str, str]:
    folder.mkdir(parents=True, exist_ok=True)
    paths = {}
    labels = ["150", "250", "400"]
    series = [
        ("China, no adder", NAVY, "plain"),
        ("China, US$1,800 adder", GOLD, "custom"),
        ("US reference", RED, "us"),
    ]
    by_id = {row["id"]: row for row in results["rows"]}
    x = np.arange(len(labels))
    width = 0.24

    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    for i, (name, color, key) in enumerate(series):
        vals = [by_id[key]["ce"][tx]["profit"] / 1_000_000 for tx in labels]
        bars = ax.bar(x + (i - 1) * width, vals, width, color=color, label=name)
        for bar, val in zip(bars, vals):
            y = val + (0.12 if val >= 0 else -0.28)
            ax.text(bar.get_x() + bar.get_width() / 2, y, f"{val:.2f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=7, color=INK)
    ax.axhline(0, color=INK, lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(["150 a day", "250 a day", "400 a day"])
    ax.set_ylabel("Cash profit, ₦ million")
    ax.set_title("CashEase profit per machine at a 20% share, before the office")
    lows = [by_id[key]["ce"][tx]["profit"] / 1_000_000 for tx in labels for _, _, key in series]
    ax.set_ylim(min(lows) * 1.28, max(0.2, max(lows) * 1.35))
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    p = folder / "fig_operator_ce.png"
    _save(fig, p)
    paths["ce"] = p.name

    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    for i, (name, color, key) in enumerate(series):
        vals = [by_id[key]["bank"][tx]["cash_profit"] / 1_000_000 for tx in labels]
        bars = ax.bar(x + (i - 1) * width, vals, width, color=color, label=name)
        for bar, val in zip(bars, vals):
            y = val + (0.12 if val >= 0 else -0.28)
            ax.text(bar.get_x() + bar.get_width() / 2, y, f"{val:.2f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=7, color=INK)
    ax.axhline(0, color=INK, lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(["150 a day", "250 a day", "400 a day"])
    ax.set_ylabel("Cash profit, ₦ million")
    ax.set_title("Bank cash profit per machine on its 80%, after rent, CIT and site costs")
    lows = [by_id[key]["bank"][tx]["cash_profit"] / 1_000_000 for tx in labels for _, _, key in series]
    ax.set_ylim(min(lows) * 1.35, max(lows) * 1.28)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    p = folder / "fig_operator_bank.png"
    _save(fig, p)
    paths["bank"] = p.name
    return paths
