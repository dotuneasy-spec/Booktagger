#!/usr/bin/env python3
"""Charts for the SNLB Farms comprehensive feasibility study — Regular-first, non-glut planning case."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "charts"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = json.loads((ROOT / "model" / "outputs" / "model_results.json").read_text())
PLAN = RESULTS["credit"]
UP = RESULTS["promoter"]
ST = RESULTS["downside"]
DEBT = RESULTS["credit_debt"]

G0 = "#1B4D3E"
G1 = "#2F6F5B"
G2 = "#5B9A82"
G3 = "#A8CDBB"
OR = "#E07A3D"
RD = "#B94A48"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "DejaVu Sans", "Noto Sans", "Liberation Sans"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#C5CEC8",
        "axes.labelcolor": G0,
        "xtick.color": "#3A4A44",
        "ytick.color": "#3A4A44",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.titleweight": "bold",
        "axes.titlesize": 11.5,
        "axes.titlecolor": G0,
        "figure.dpi": 140,
    }
)


def m(n: float) -> float:
    return n / 1_000_000


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def fig_mechanization() -> None:
    labels = [
        "Stage 0\nManual\n<5 ha",
        "Stage 1\nRented core\n5–24 ha",
        "Stage 2\nBulk + fleet\n25–59 ha",
        "Stage 3\nFull mech.\n≥60 ha",
    ]
    vals = [0, 7, 14, 20]
    colors = [G3, G2, G1, G0]
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    bars = ax.bar(labels, vals, color=colors, width=0.62)
    ax.set_ylabel("Approx. reduction in per-ha\nproduction cost (%)")
    ax.set_ylim(0, 26)
    ax.set_title("Mechanization Roadmap — Unit-Cost Reduction by Scale Stage")
    for b, v in zip(bars, vals):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + 0.6,
            "Baseline" if v == 0 else f"{v}%",
            ha="center",
            fontsize=9,
            color=G0,
            fontweight="bold",
        )
    save(fig, "fig_mechanization.png")


def fig_mile12() -> None:
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    cats = [
        "Deep glut\nJan 2025",
        "Regular\nwindow",
        "Inter-season\nexamples",
        "Peak\nplanning",
        "Scarcity\nJul 2026",
    ]
    obs = {
        0: [13, 15],
        1: [33, 35, 40, 50, 55],
        2: [60, 65, 70, 110],
        3: [145],
        4: [120, 145, 150],
    }
    rng = np.random.default_rng(7)
    for i, ys in obs.items():
        xs = i + rng.uniform(-0.12, 0.12, len(ys))
        ax.scatter(xs, ys, s=42, c=G0, zorder=3, alpha=0.85)
    ax.axhline(33, color=G1, ls="--", lw=1.4, label="Planning Regular (non-glut) ₦33k")
    ax.axhline(145, color=OR, ls="--", lw=1.4, label="Planning Peak ₦145k")
    ax.axhline(15, color=RD, ls=":", lw=1.2, label="Glut crash floor ₦15k")
    ax.set_xticks(range(5))
    ax.set_xticklabels(cats)
    ax.set_ylabel("₦ ’000 per 50 kg big basket")
    ax.set_title("Mile 12 Big-Basket Price Context — Regular Planned as Non-Glut")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_ylim(0, 170)
    save(fig, "fig_mile12_prices.png")


def fig_land() -> None:
    cycles = ["C1", "C2", "C3", "C4", "C5", "C6"]
    ha = [1, 3, 15, 27, 72, 100]
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    ax.bar(cycles, ha, color=G0, width=0.62)
    ax.axhline(45, color=OR, ls="--", lw=1.3, label="45 ha/cycle operational ceiling")
    for x, y in zip(cycles, ha):
        ax.text(x, y + 2.2, f"{y} ha", ha="center", fontsize=8.5, color=G0, fontweight="bold")
    ax.set_ylabel("Cultivated area (ha)")
    ax.set_title("Land Expansion Path — Reinvestment-Driven Growth to 100 ha")
    ax.set_ylim(0, 118)
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_land_expansion.png")


def fig_cycle_pnl() -> None:
    cs = PLAN["cycles"][:6]
    labels = [f"{c['id']}\n{c['season']}" for c in cs]
    rev = np.array([m(c["revenue"]) for c in cs])
    npat = np.array([m(c["npat"]) for c in cs])
    x = np.arange(len(labels))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    ax.bar(x - w / 2, rev, w, color=G0, label="Cycle revenue")
    ax.bar(x + w / 2, npat, w, color=G2, label="Cycle net profit")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("₦ million")
    ax.set_title("Cycle Revenue & Net Profit — Regular-First, Non-Glut Planning Case")
    ax.legend(frameon=False, fontsize=8)
    ax.set_ylim(0, max(rev) * 1.15)
    save(fig, "fig_cycle_pnl.png")


def fig_annual() -> None:
    years = ["Year 1", "Year 2", "Year 3"]
    ys = PLAN["years"][:3]
    rev = [m(y["revenue"]) for y in ys]
    npat = [m(y["npat"]) for y in ys]
    buf = [m(y["cum_buffer"]) for y in ys]
    x = np.arange(3)
    w = 0.25
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    ax.bar(x - w, rev, w, color=G0, label="Revenue")
    ax.bar(x, npat, w, color=G1, label="Net profit")
    ax.bar(x + w, buf, w, color=G3, edgecolor=G0, linewidth=0.6, label="Cumulative buffer")
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylabel("₦ million")
    ax.set_title("Annual Revenue, Net Profit & Cumulative Buffer — Planning Case")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_annual_triple.png")


def fig_buffer() -> None:
    xs = ["Start", "End Y1", "End Y2", "End Y3"]
    ys = [0] + [m(y["cum_buffer"]) for y in PLAN["years"][:3]]
    fig, ax = plt.subplots(figsize=(8.0, 3.6))
    ax.fill_between(xs, ys, color=G3, alpha=0.85)
    ax.plot(xs, ys, color=G0, lw=2.4, marker="o", ms=7)
    for x, y in zip(xs[1:], ys[1:]):
        label = f"₦{y:.0f}m" if y < 1000 else f"₦{y / 1000:.2f}bn"
        ax.text(x, y + max(ys) * 0.04, label, ha="center", fontsize=8.5, color=G0, fontweight="bold")
    ax.set_ylabel("Cumulative buffer (₦ million)")
    ax.set_title("Cumulative Buffer Reserve Growth (50% Retention Policy)")
    ax.set_ylim(0, max(ys) * 1.2)
    save(fig, "fig_buffer.png")


def fig_margins() -> None:
    years = ["Year 1", "Year 2", "Year 3"]
    gm = [y["gross_margin"] * 100 for y in PLAN["years"][:3]]
    nm = [y["net_margin"] * 100 for y in PLAN["years"][:3]]
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.plot(years, gm, color=G0, marker="o", lw=2.2, label="Gross margin")
    ax.plot(years, nm, color=G2, marker="s", lw=2.2, label="Net margin")
    for x, y in zip(years, gm):
        ax.text(x, y + 1.4, f"{y:.1f}%", ha="center", fontsize=8, color=G0)
    for x, y in zip(years, nm):
        ax.text(x, y - 3.2, f"{y:.1f}%", ha="center", fontsize=8, color=G1)
    ax.set_ylabel("Margin %")
    ax.set_ylim(35, 95)
    ax.set_title("Gross & Net Margin Trend — Regular-First Planning Case")
    ax.legend(frameon=False, fontsize=8, loc="center right")
    save(fig, "fig_margins.png")


def fig_breakeven() -> None:
    be = PLAN["break_even"]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    labels = ["Break-even\nprice", "Planning Regular\n(non-glut) price"]
    vals = [be["be_price"], be["c1_price"]]
    bars = ax.bar(labels, vals, color=[OR, G0], width=0.48)
    ax.set_ylabel("₦ per 50 kg basket")
    ax.set_title("Cycle 1 Break-even vs Non-Glut Regular Selling Price")
    ax.set_ylim(0, max(vals) * 1.25)
    for b, v in zip(bars, vals):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + max(vals) * 0.03,
            f"₦{v:,.0f}",
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=G0,
        )
    mos = be["margin_of_safety"] * 100
    ax.annotate(
        f"{mos:.1f}% margin of safety",
        xy=(0.5, (vals[0] + vals[1]) / 2),
        xytext=(0.5, max(vals) * 1.12),
        ha="center",
        color=OR,
        fontsize=9,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=OR),
    )
    save(fig, "fig_breakeven.png")


def fig_sensitivity() -> None:
    base_y3 = PLAN["years"][2]["npat"]
    stress_y3 = ST["years"][2]["npat"]
    stacked = (stress_y3 / base_y3 - 1) * 100
    labels = [
        "Stacked stress\n(glut Regular, weak Peak, yield −25%)",
        "Missed Peak window\n(Peak priced as Regular)",
        "Yield −20%",
        "Regular at Jan 2025 crash ₦15,000",
        "Input cost +30%",
    ]
    vals = [stacked, -35.0, -20.0, -12.0, -5.0]
    colors = [RD if v < -40 else OR for v in vals]
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    y = np.arange(len(labels))
    ax.barh(y, vals, color=colors, height=0.62)
    ax.axvline(0, color=G0, lw=1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Change in Year 3 NPAT vs planning case (%)")
    ax.set_title("Sensitivity — Impact on Year 3 Planning-Case Net Profit")
    ax.set_xlim(-100, 10)
    save(fig, "fig_sensitivity.png")


def fig_three_case() -> None:
    labels = ["Stress case\n(glut floor)", "Planning case\n(Regular first, non-glut)", "Upside case\n(tax holiday)"]
    npv = [
        ST["dcf"]["npv_18_no_tv"] / 1e9,
        PLAN["dcf"]["npv_18_no_tv"] / 1e9,
        UP["dcf"]["npv_18_no_tv"] / 1e9,
    ]
    colors = [OR, G0, G2]
    fig, ax = plt.subplots(figsize=(7.6, 3.7))
    bars = ax.bar(labels, npv, color=colors, width=0.55)
    ax.set_ylabel("5-year NPV @ 18% (₦ billion, no TV)")
    ax.set_title("Scenario Design — Project NPV at 18% Discount")
    for b, v in zip(bars, npv):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + 0.15,
            f"₦{v:.2f}bn",
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=G0,
        )
    ax.set_ylim(0, max(npv) * 1.2)
    save(fig, "fig_three_case_npv.png")


def fig_capex() -> None:
    years = ["Opening\n(t=0)", "Year 1\nincremental", "Year 2", "Year 3"]
    vals = [3.5, 2.0, 38.0, 113.0]
    fig, ax = plt.subplots(figsize=(7.8, 3.6))
    ax.bar(years, vals, color=[G2, G2, G1, G0], width=0.55)
    for x, v in zip(years, vals):
        ax.text(x, v + 2.2, f"₦{v:.1f}m", ha="center", fontsize=8.5, fontweight="bold", color=G0)
    ax.set_ylabel("CapEx (₦ million)")
    ax.set_title("Phased Irrigation, Borehole and Packhouse CapEx")
    ax.set_ylim(0, 135)
    save(fig, "fig_capex.png")


def fig_dscr() -> None:
    rows = [y for y in DEBT["years"] if y["year"] >= 2]
    years = [f"Y{y['year']}" for y in rows]
    dscr = [y["dscr"] for y in rows]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar(years, dscr, color=G0, width=0.5)
    ax.axhline(1.5, color=OR, ls="--", lw=1.3, label="Typical 1.50× agri covenant")
    ax.set_ylabel("DSCR (×)")
    ax.set_title("Optional ₦80m Facility — Debt Service Coverage")
    ax.legend(frameon=False, fontsize=8)
    ax.set_ylim(0, max(dscr) * 1.2)
    save(fig, "fig_dscr.png")


if __name__ == "__main__":
    fig_mechanization()
    fig_mile12()
    fig_land()
    fig_cycle_pnl()
    fig_annual()
    fig_buffer()
    fig_margins()
    fig_breakeven()
    fig_sensitivity()
    fig_three_case()
    fig_capex()
    fig_dscr()
    print("done", OUT)
