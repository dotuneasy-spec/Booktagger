"""Charts for the CashEase feasibility study. Labels match the model."""

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
SAND = "#f4efe4"

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

    # 1. ATM density
    labels = ["Kenya", "Ghana", "Nigeria", "India", "Egypt", "South Africa"]
    vals = [6.42, 10.97, 12.83, 24.47, 37.06, 45.96]
    colors = [NAVY if name != "Nigeria" else GOLD for name in labels]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.barh(labels[::-1], vals[::-1], color=colors[::-1], height=0.62)
    ax.set_xlabel("ATMs per 100,000 adults, 2024")
    ax.set_title("Nigeria’s ATM density sits with Ghana, not with Egypt or South Africa")
    for y, v in enumerate(vals[::-1]):
        ax.text(v + 0.4, y, f"{v:.2f}", va="center", fontsize=8, color=INK)
    ax.set_xlim(0, 58)
    p = folder / "fig_atm_density.png"
    _save(fig, p)
    paths["density"] = p.name

    # 2. Break-even versus a public benchmark
    be = results["breakeven"]
    hurdle = results["hurdle_tx_per_open_day"]["base_fee"]
    names = [
        "Blog high-traffic\nPOS anecdote",
        "Street costs\nonly",
        "Cash costs,\nincluding the machine",
        "Full cost,\nwith depreciation",
        "Volume that\nclears a 28% NPV",
    ]
    heights = [
        80,
        be["street_tx_per_open_day"],
        be["cash_tx_per_open_day"],
        be["full_tx_per_open_day"],
        hurdle,
    ]
    bar_colors = [GREEN, GOLD, NAVY, RED, RED]
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.bar(names, heights, color=bar_colors, width=0.72)
    ax.set_ylabel("Transactions per open day")
    ax.set_title("Break-even sits far above any public traffic benchmark")
    for i, v in enumerate(heights):
        ax.text(i, v + 20, f"{v:,.0f}", ha="center", fontsize=8, color=INK)
    ax.set_ylim(0, max(heights) * 1.18)
    p = folder / "fig_breakeven.png"
    _save(fig, p)
    paths["breakeven"] = p.name

    # 3. One kiosk, 80 tx test case
    u = results["unit_test_80"]
    items = [
        ("Net revenue", u["net_revenue_ngn"] / 1e6, GREEN),
        ("Rent", u["rent_ngn"] / 1e6, NAVY),
        ("Cash logistics", u["cit_ngn"] / 1e6, NAVY),
        ("Security", u["security_ngn"] / 1e6, NAVY),
        ("Power and link", (u["power_ngn"] + u["connectivity_ngn"]) / 1e6, NAVY),
        ("Maintenance", u["maintenance_ngn"] / 1e6, GOLD),
        ("Insurance", u["insurance_ngn"] / 1e6, GOLD),
        ("Depreciation", u["depreciation_ngn"] / 1e6, RED),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.barh([i[0] for i in items][::-1], [i[1] for i in items][::-1], color=[i[2] for i in items][::-1], height=0.62)
    ax.set_xlabel("₦ million per kiosk per year")
    ax.set_title("At 80 transactions a day, revenue does not cover the street, let alone the machine")
    p = folder / "fig_unit_bars.png"
    _save(fig, p)
    paths["unit"] = p.name

    # 4. Hardware versus the only positive ceiling in the grid
    hw = results["hardware"]
    hlabels = [
        "Dispense-only\nATM, $25,000",
        "Recycler\nmedian, $36,000",
        "Deposit ATM\nlow, $40,000",
        "Deposit ATM\nhigh, $55,000",
    ]
    hvals = [
        hw["dispense_low"]["all_in_ngn"] / 1e6,
        hw["recycler_median"]["all_in_ngn"] / 1e6,
        hw["deposit_low"]["all_in_ngn"] / 1e6,
        hw["deposit_high"]["all_in_ngn"] / 1e6,
    ]
    ceiling = results["capex_ceiling_ngn"]["400"] / 1e6
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.bar(hlabels, hvals, color=NAVY, width=0.68)
    ax.axhline(
        ceiling,
        color=RED,
        linewidth=1.2,
        linestyle="--",
        label=f"NPV ceiling at 400 tx/day (₦{ceiling:.1f}m)",
    )
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    ax.set_ylabel("All-in ₦ million per machine")
    ax.set_title("Published machine prices land above the only price that clears a 28% hurdle")
    for i, v in enumerate(hvals):
        ax.text(i, v + 1.2, f"{v:.0f}", ha="center", fontsize=8)
    ax.set_ylim(0, max(hvals) * 1.42)
    p = folder / "fig_hardware.png"
    _save(fig, p)
    paths["hardware"] = p.name

    return paths
