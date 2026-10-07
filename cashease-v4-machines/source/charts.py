"""Charts for the bank-backed machine study. Labels match the model."""

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
    s = results["structures"]

    order = [
        ("managed", "Managed service\nCashEase fee only"),
        ("v3", "v3 owner-pays"),
        ("s60", "60/40 off-site"),
        ("s50", "50/50 off-site"),
        ("concession", "Concession\n50/30/20"),
        ("gallery", "Bank gallery\non-site"),
    ]
    labels = [lab for _, lab in order]
    vals = [s[k]["be_full"] for k, _ in order]
    colors = [GREEN, NAVY, NAVY, GOLD, RED, RED]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.barh(labels[::-1], vals[::-1], color=colors[::-1], height=0.62)
    ax.axvline(150, color=GOLD, ls="--", lw=1, label="150 tx a day")
    ax.axvline(250, color=NAVY, ls="--", lw=1, label="250 tx a day")
    ax.axvline(400, color=GREEN, ls="--", lw=1, label="400 tx a day")
    for y, v in enumerate(vals[::-1]):
        ax.text(v + 30, y, f"{v:,.0f}", va="center", fontsize=8, color=INK)
    ax.set_xlim(0, max(vals) * 1.32)
    ax.set_xlabel("Transactions per scheduled open day to cover CashEase’s full cost")
    ax.set_title("Full-cost break-even against the three test volumes")
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    p = folder / "fig_breakeven.png"
    _save(fig, p)
    paths["breakeven"] = p.name

    groups = [("s60", "60/40"), ("concession", "Concession"), ("gallery", "Gallery"), ("managed", "Managed")]
    import numpy as np

    x = np.arange(len(groups))
    width = 0.24
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    for i, tx in enumerate(("150", "250", "400")):
        heights = [s[k]["at"][tx]["ce_cash_profit"] / 1_000_000 for k, _ in groups]
        bars = ax.bar(x + (i - 1) * width, heights, width, label=f"{tx} tx a day",
                      color=[RED, GOLD, GREEN][i])
        for b, h in zip(bars, heights):
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + (0.35 if h >= 0 else -0.35),
                f"{h:.1f}",
                ha="center",
                va="bottom" if h >= 0 else "top",
                fontsize=7,
                color=INK,
            )
    ax.axhline(0, color=NAVY, lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([lab for _, lab in groups])
    ax.set_ylabel("CashEase cash profit, ₦ million per machine per year")
    ax.set_title("CashEase cash profit per machine at the three test volumes")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_ylim(-10.6, 3.6)
    p = folder / "fig_cash_profit.png"
    _save(fig, p)
    paths["profit"] = p.name

    sites = results["sites"]
    names = ["Listed public\naddresses", "Active ATMs\nH1 2024", "20,000-machine\ntarget"]
    counts = [sites["listed_sum"], sites["atms"], sites["target"]]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.bar(names, counts, color=[NAVY, GOLD, RED], width=0.62)
    for i, v in enumerate(counts):
        ax.text(i, v + 350, f"{v:,.0f}", ha="center", fontsize=9, color=INK)
    ax.set_ylim(0, max(counts) * 1.22)
    ax.set_ylabel("Count")
    ax.set_title("Listed addresses, the mid-2024 ATM stock, and the 20,000 target")
    p = folder / "fig_sites.png"
    _save(fig, p)
    paths["sites"] = p.name
    return paths
