"""Charts for the China-kiosk addendum."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
    labels = [f"${row['fob']:,.0f}" for row in results["rows"]]
    vals = [row["cases"]["high"]["landed"]["all_in_ngn"] / 1_000_000 for row in results["rows"]]
    us = results["us_reference"]["all_in"] / 1_000_000
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.bar(labels, vals, color=NAVY, width=0.62, label="China listing, high freight band")
    ax.axhline(us, color=RED, ls="--", lw=1.2, label=f"v4 US reference, ₦{us:.1f}m, before duty")
    for i, v in enumerate(vals):
        ax.text(i, v + 1.2, f"{v:.1f}", ha="center", fontsize=8, color=INK)
    ax.set_ylim(0, max(us, max(vals)) * 1.08)
    ax.set_ylabel("All-in cost, ₦ million")
    ax.set_xlabel("Published FOB, US dollars")
    ax.set_title("Landed cost of the listed Chinese machines, with the v4 site-works assumption")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    p = folder / "fig_china_landed.png"
    _save(fig, p)
    paths["landed"] = p.name

    be = [row["cases"]["high"]["be_full"] for row in results["rows"]]
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.bar(labels, be, color=GOLD, width=0.62)
    ax.axhline(150, color=NAVY, ls="--", lw=1, label="150 tx a day")
    ax.axhline(250, color=GREEN, ls="--", lw=1, label="250 tx a day")
    ax.axhline(400, color=RED, ls="--", lw=1, label="400 tx a day")
    for i, v in enumerate(be):
        ax.text(i, v + 8, f"{v:.0f}", ha="center", fontsize=8, color=INK)
    ax.set_ylim(0, max(be) * 1.25)
    ax.set_ylabel("Transactions per scheduled open day")
    ax.set_xlabel("Published FOB, US dollars")
    ax.set_title("Full-cost break-even if sites, notes and cash-in-transit are free")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    p = folder / "fig_china_breakeven.png"
    _save(fig, p)
    paths["breakeven"] = p.name
    return paths
