#!/usr/bin/env python3
"""Charts for the CashEase Nigeria feasibility study."""
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
PR = R["scenarios"]["promoter"]
LABELS = R["year_labels"]

NAVY = "#1B3A4B"
TEAL = "#2A6F7F"
GOLD = "#C5922A"
SAND = "#E6D3A3"
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


def fig_fleet() -> None:
    x = np.arange(len(LABELS))
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    ax.plot(x, [y["closing_fleet"] for y in ST["years"]], "o-", color=RUST, label="Stress", lw=2)
    ax.plot(x, [y["closing_fleet"] for y in PL["years"]], "o-", color=TEAL, label="Planning", lw=2.2)
    ax.plot(x, [y["closing_fleet"] for y in PR["years"]], "o-", color=GOLD, label="Promoter plan", lw=2)
    ax.set_xticks(x, LABELS)
    ax.set_ylabel("Kiosks at year-end")
    ax.set_title("Fleet path — three cases")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1000:.0f}k" if v >= 1000 else f"{v:.0f}"))
    ax.legend(frameon=False)
    ax.axhline(2000, color=SLATE, ls="--", lw=0.8, alpha=0.7)
    ax.text(5.05, 2100, "2,000 hold", color=SLATE, fontsize=8, va="bottom")
    save(fig, "fig_fleet.png")


def fig_npat() -> None:
    x = np.arange(len(LABELS))
    w = 0.26
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.bar(x - w, [bn(y["npat"]) for y in ST["years"]], w, color=RUST, label="Stress")
    ax.bar(x, [bn(y["npat"]) for y in PL["years"]], w, color=TEAL, label="Planning")
    ax.bar(x + w, [bn(y["npat"]) for y in PR["years"]], w, color=GOLD, label="Promoter plan")
    ax.axhline(0, color="#888", lw=0.7)
    ax.set_xticks(x, LABELS)
    ax.set_ylabel("NPAT (₦ billion)")
    ax.set_title("Annual net profit after tax")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    save(fig, "fig_npat.png")


def fig_npv() -> None:
    labels = [
        "Stress\n20k path",
        "Planning\n20k path",
        "Planning\nhold 2,000",
        "Planning\nhold 5,000",
        "Promoter\n20k path",
        "₦8bn BOI\non 2,000",
        "₦90bn BOI\non 20k plan",
    ]
    vals = [
        bn(ST["npv_22"]),
        bn(PL["npv_22"]),
        bn(R["planning_hold_2k"]["npv_22"]),
        bn(R["planning_hold_5k"]["npv_22"]),
        bn(PR["npv_22"]),
        bn(R["boi_8_on_2k"]["npv_22"]),
        bn(R["boi_planning"]["npv_22"]),
    ]
    colors = [RUST, TEAL, TEAL, TEAL, GOLD, NAVY, NAVY]
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    bars = ax.bar(labels, vals, color=colors, width=0.68)
    ax.axhline(0, color="#888", lw=0.7)
    ax.set_ylabel("NPV at 22% (₦ billion)")
    ax.set_title("Value at a 22% cash-handling hurdle")
    for b, v in zip(bars, vals):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + (0.6 if v >= 0 else -1.4),
            f"{v:+.1f}",
            ha="center",
            fontsize=8,
            color=INK,
            fontweight="bold",
        )
    save(fig, "fig_npv.png")


def fig_breakeven() -> None:
    names = ["Stress", "Planning", "Promoter"]
    be = [R["breakeven"]["stress"]["tx_per_day_be"], R["breakeven"]["planning"]["tx_per_day_be"], R["breakeven"]["promoter"]["tx_per_day_be"]]
    plan = [110, 180, 225]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    ax.bar(x - 0.18, be, 0.36, color=RUST, label="EBITDA break-even tx/day")
    ax.bar(x + 0.18, plan, 0.36, color=TEAL, label="Assumed tx/day")
    ax.set_xticks(x, names)
    ax.set_ylabel("Transactions per kiosk per day")
    ax.set_title("Mature-kiosk break-even vs assumed traffic")
    ax.legend(frameon=False)
    save(fig, "fig_breakeven.png")


def fig_unit_waterfall() -> None:
    # Planning mature monthly unit, bank share on
    p = PL["params"]
    gross = PL["unit_monthly_gross"]
    bank = gross * p["eligible_share"] * p["bank_share_rate"]
    logi = gross * p["logistics_pct"]
    rent = p["rent_month"]
    maint = p["maint_year"] / 12
    conn = p["connect_year"] / 12
    ga = 18_000
    staff = (280_000 / 40 + 220_000 / 80)
    ins = (p["unit_capex"] + p["float_per"]) * p["insurance_pct_assets"] / 12
    theft = gross * p["theft_loss_pct"]
    ebitda = gross - (bank + logi + rent + maint + conn + ga + staff + ins + theft)
    labels = [
        "Gross\nfees",
        "Bank\nshare",
        "Cash\nlogistics",
        "Site\nrent",
        "Maint /\npower",
        "HQ +\nfield",
        "Insurance\n+ loss",
        "EBITDA",
    ]
    vals = [gross, -bank, -logi, -rent, -(maint + conn), -(ga + staff), -(ins + theft), ebitda]
    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    colors = [TEAL] + [RUST] * 6 + ([GOLD] if ebitda > 0 else [RUST])
    ax.bar(labels, [v / 1000 for v in vals], color=colors, width=0.65)
    ax.axhline(0, color="#888", lw=0.7)
    ax.set_ylabel("₦ thousand / kiosk / month")
    ax.set_title("Planning-case unit waterfall — mature kiosk, bank cash on")
    save(fig, "fig_unit_waterfall.png")


def fig_sources_uses() -> None:
    uses = PL["opening_uses"]
    labels = ["Machines\n+ fit-out", "Self-funded\ncash float", "HQ, licences,\nlegal"]
    vals = [uses["machines_setup"] / 1e6, uses["self_float"] / 1e6, uses["hq_licenses"] / 1e6]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    bars = ax.bar(labels, vals, color=[NAVY, TEAL, GOLD], width=0.55)
    ax.set_ylabel("₦ million")
    ax.set_title("Phase 1 sources & uses — 350 kiosks (planning)")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 20, f"₦{v:,.0f}m", ha="center", fontsize=9, color=INK, fontweight="bold")
    save(fig, "fig_sources_uses.png")


def fig_dscr() -> None:
    labels = LABELS
    d90 = [d if d is not None else 0 for d in R["boi_planning"]["dscr"]]
    d25 = [d if d is not None else 0 for d in R["boi_25_on_5k"]["dscr"]]
    d8 = [d if d is not None else 0 for d in R["boi_8_on_2k"]["dscr"]]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    ax.plot(x, d8, "o-", color=TEAL, lw=2.2, label="₦8bn on 2,000 hold")
    ax.plot(x, d25, "o-", color=GOLD, lw=2, label="₦25bn on 5,000 hold")
    ax.plot(x, d90, "o-", color=RUST, lw=2, label="₦90bn on 20,000 path")
    ax.axhline(1.25, color=NAVY, ls="--", lw=1, label="1.25× comfort")
    ax.set_xticks(x, labels)
    ax.set_ylabel("DSCR (EBITDA / debt service)")
    ax.set_title("Development-bank facilities — debt service coverage")
    ax.set_ylim(0, 3.2)
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_dscr.png")


def fig_revenue_mix() -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.pie(
        [45, 40, 15],
        labels=["Note-breaking\n45%", "POS cash-out\n40%", "Airtime, bills, ads\n15%"],
        colors=[NAVY, TEAL, GOLD],
        startangle=90,
        wedgeprops={"width": 0.45, "edgecolor": "white"},
    )
    ax.set_title("Planning revenue mix — multi-service kiosk")
    save(fig, "fig_revenue_mix.png")


def fig_phases() -> None:
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    stages = ["Phase 1\nProof\n350 kiosks", "Phase 2\nRepeatable\n2,000", "Phase 2b\nNational core\n5,000", "Phase 3\nOnly if earned\n20,000"]
    vals = [350, 2000, 5000, 20000]
    colors = [TEAL, NAVY, GOLD, SAND]
    bars = ax.bar(stages, vals, color=colors, width=0.62)
    ax.set_ylabel("Kiosks")
    ax.set_title("Committed scale vs earned scale")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1000:.0f}k" if v >= 1000 else f"{v:.0f}"))
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.04, f"{v:,}", ha="center", fontsize=9, color=INK, fontweight="bold")
    save(fig, "fig_phases.png")


if __name__ == "__main__":
    fig_fleet()
    fig_npat()
    fig_npv()
    fig_breakeven()
    fig_unit_waterfall()
    fig_sources_uses()
    fig_dscr()
    fig_revenue_mix()
    fig_phases()
