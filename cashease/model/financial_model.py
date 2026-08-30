#!/usr/bin/env python3
"""
CashEase Nigeria — six-year three-case financial model.

Scenarios
---------
stress    Conservative haircut: weaker traffic, higher opex, slower fleet.
planning  Feasibility case used for go / no-go (this study's planning case).
promoter  Midpoint of the progressed Grok plan's "realistic" ranges.

The promoter case is the conversation's stated plan. The planning case
applies a feasibility haircut so the document is not a reprint of
optimistic desktop estimates.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

YEARS = [1, 2, 3, 4, 5, 6]
YEAR_LABELS = ["Y1 2027", "Y2 2028", "Y3 2029", "Y4 2030", "Y5 2031", "Y6 2032"]
DAYS = 365
TAX = 0.321  # 30% CIT + 3% education tax on PBT (conservative stacking)
DISCOUNT = 0.22  # payments / cash-handling risk rate
WACC_NOTE = 0.22

# Central G&A (₦) by year-end fleet band — HQ, monitoring, compliance, insurance desk
def central_ga(avg_machines: float, year: int) -> float:
    base = 90_000_000 * (1.12 ** (year - 1))
    variable = 18_000 * 12 * avg_machines  # ₦18k / machine / month allocated HQ
    return base + variable


def field_staff(avg_machines: float) -> float:
    techs = max(2.0, avg_machines / 40.0)
    monitors = max(1.0, avg_machines / 80.0)
    return (techs * 280_000 + monitors * 220_000) * 12


SCENARIOS = {
    "stress": {
        "label": "Stress",
        "tx_per_day": 110,
        "uptime": 0.85,
        "blended_fee": 70.0,
        "bank_share_rate": 0.38,
        "eligible_share": 0.70,
        "logistics_pct": 0.32,
        "rent_month": 120_000,
        "maint_year": 350_000,
        "connect_year": 90_000,
        "insurance_pct_assets": 0.022,
        "unit_capex": 4_500_000,
        "setup_per": 450_000,
        "float_per": 1_500_000,
        "self_float": [1.00, 0.55, 0.45, 0.40, 0.35, 0.35],
        "fleet_end": [200, 1_200, 2_500, 5_000, 8_000, 12_000],
        "bank_share_from_year": 2,
        "theft_loss_pct": 0.035,
    },
    "planning": {
        "label": "Planning",
        "tx_per_day": 180,
        "uptime": 0.92,
        "blended_fee": 100.0,
        "bank_share_rate": 0.32,
        "eligible_share": 0.55,
        "logistics_pct": 0.24,
        "rent_month": 80_000,
        "maint_year": 250_000,
        "connect_year": 72_000,
        "insurance_pct_assets": 0.016,
        "unit_capex": 3_500_000,
        "setup_per": 350_000,
        "float_per": 1_200_000,
        "self_float": [1.00, 0.35, 0.25, 0.20, 0.15, 0.15],
        "fleet_end": [350, 2_000, 5_000, 10_000, 15_000, 20_000],
        "bank_share_from_year": 2,
        "theft_loss_pct": 0.012,
    },
    "promoter": {
        "label": "Promoter (Grok plan)",
        "tx_per_day": 225,
        "uptime": 0.93,
        "blended_fee": 115.0,
        "bank_share_rate": 0.30,
        "eligible_share": 0.50,
        "logistics_pct": 0.22,
        "rent_month": 70_000,
        "maint_year": 200_000,
        "connect_year": 60_000,
        "insurance_pct_assets": 0.014,
        "unit_capex": 3_000_000,
        "setup_per": 300_000,
        "float_per": 1_200_000,
        "self_float": [1.00, 0.30, 0.20, 0.15, 0.10, 0.10],
        "fleet_end": [500, 2_000, 5_000, 10_000, 16_000, 20_000],
        "bank_share_from_year": 2,
        "theft_loss_pct": 0.008,
    },
}


def unit_gross_year(p: dict) -> float:
    return p["tx_per_day"] * p["uptime"] * DAYS * p["blended_fee"]


def run_scenario(name: str, fleet_end: list[int] | None = None) -> dict:
    p = dict(SCENARIOS[name])
    fleet = fleet_end if fleet_end is not None else p["fleet_end"]
    p["fleet_end"] = fleet
    rows = []
    opening = 0
    cash = 0.0
    cumulative_capex = 0.0
    cumulative_npat = 0.0
    # Opening equity for Y1: machines + setup + self-funded float + ₦80m working / licenses
    y1_add = fleet[0]
    opening_uses = (
        y1_add * (p["unit_capex"] + p["setup_per"])
        + y1_add * p["float_per"] * p["self_float"][0]
        + 80_000_000
    )
    cash = opening_uses  # funded by equity at t=0; then spent in Y1
    opening_equity = opening_uses

    for i, year in enumerate(YEARS):
        end = fleet[i]
        added = end - opening
        avg = (opening + end) / 2.0 if end else 0.0
        if avg <= 0:
            avg = end / 2.0

        gross = unit_gross_year(p) * avg
        bank_share = 0.0
        if year >= p["bank_share_from_year"]:
            bank_share = gross * p["eligible_share"] * p["bank_share_rate"]
        logistics = gross * p["logistics_pct"]
        rent = avg * p["rent_month"] * 12
        maint = avg * p["maint_year"]
        connect = avg * p["connect_year"]
        ga = central_ga(avg, year)
        staff = field_staff(avg)
        assets_at_risk = end * (p["unit_capex"] + p["float_per"])
        insurance = assets_at_risk * p["insurance_pct_assets"]
        theft = gross * p["theft_loss_pct"]
        licenses = 40_000_000 * (1.10 ** (year - 1)) + added * 12_000

        opex = (
            bank_share
            + logistics
            + rent
            + maint
            + connect
            + ga
            + staff
            + insurance
            + theft
            + licenses
        )
        ebitda = gross - opex
        # Straight-line 5-year on machines + setup
        dep_base = end * (p["unit_capex"] + p["setup_per"])
        da = dep_base / 5.0
        ebit = ebitda - da
        pbt = ebit  # no interest in unlevered run
        tax = max(0.0, pbt) * TAX
        npat = pbt - tax

        # Y1 machines, setup, float and HQ are funded at t=0. Later years
        # fund only incremental machines / setup / self-funded float.
        if year == 1:
            capex = opening_uses
            dwc_float = 0.0
            fcf = npat + da
        else:
            capex = added * (p["unit_capex"] + p["setup_per"])
            self_float_end = end * p["float_per"] * p["self_float"][i]
            self_float_open = opening * p["float_per"] * p["self_float"][i - 1]
            dwc_float = self_float_end - self_float_open
            fcf = npat + da - capex - dwc_float

        self_float_end = end * p["float_per"] * p["self_float"][i]
        cash = cash + fcf if year > 1 else (npat + da)

        cumulative_capex += capex
        cumulative_npat += npat

        rows.append(
            {
                "year": year,
                "label": YEAR_LABELS[i],
                "opening_fleet": opening,
                "closing_fleet": end,
                "added": added,
                "avg_fleet": avg,
                "gross": gross,
                "bank_share": bank_share,
                "logistics": logistics,
                "rent": rent,
                "maint": maint,
                "connect": connect,
                "ga": ga,
                "staff": staff,
                "insurance": insurance,
                "theft": theft,
                "licenses": licenses,
                "opex": opex,
                "ebitda": ebitda,
                "da": da,
                "ebit": ebit,
                "pbt": pbt,
                "tax": tax,
                "npat": npat,
                "capex": capex,
                "self_float": self_float_end,
                "dwc_float": dwc_float,
                "fcf": fcf,
                "cash": cash,
                "ebitda_margin": ebitda / gross if gross else 0.0,
                "npat_margin": npat / gross if gross else 0.0,
                "gross_per_machine_month": (gross / avg / 12.0) if avg else 0.0,
                "npat_per_machine_month": (npat / avg / 12.0) if avg else 0.0,
            }
        )
        opening = end

    # NPV of unlevered FCF, t=0 equity as negative FCF at t=0
    npv = -opening_equity
    for i, r in enumerate(rows):
        npv += r["fcf"] / ((1 + DISCOUNT) ** r["year"])

    # IRR (simple Newton)
    def npv_at(rate: float) -> float:
        v = -opening_equity
        for r in rows:
            v += r["fcf"] / ((1 + rate) ** r["year"])
        return v

    irr = None
    lo, hi = -0.5, 3.0
    if npv_at(lo) * npv_at(hi) < 0:
        for _ in range(80):
            mid = (lo + hi) / 2
            if npv_at(mid) > 0:
                lo = mid
            else:
                hi = mid
        irr = (lo + hi) / 2

    # Payback on opening equity from cumulative FCF
    cum = 0.0
    payback = None
    for r in rows:
        cum += r["fcf"]
        if payback is None and cum >= opening_equity:
            payback = r["year"]

    # Unit snapshot at mature kiosk (Y3 avg)
    y3 = rows[2]
    unit_annual_gross = unit_gross_year(p)

    return {
        "name": name,
        "label": p["label"],
        "params": {
            k: v
            for k, v in p.items()
            if k != "label"
        },
        "unit_annual_gross": unit_annual_gross,
        "unit_monthly_gross": unit_annual_gross / 12.0,
        "opening_equity": opening_equity,
        "opening_uses": {
            "machines_setup": y1_add * (p["unit_capex"] + p["setup_per"]),
            "self_float": y1_add * p["float_per"] * p["self_float"][0],
            "hq_licenses": 80_000_000,
        },
        "years": rows,
        "npv_22": npv,
        "irr": irr,
        "payback_year": payback,
        "cumulative_npat": cumulative_npat,
        "y6_fleet": fleet[-1],
        "y6_npat": rows[-1]["npat"],
        "y6_gross": rows[-1]["gross"],
        "y2_npat": rows[1]["npat"],
        "y2_fleet": fleet[1],
        "y3_npat": rows[2]["npat"],
        "y3_fleet": fleet[2],
    }


def naira(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000:
        return f"{sign}₦{n/1_000_000_000:,.2f}bn"
    if n >= 1_000_000:
        return f"{sign}₦{n/1_000_000:,.1f}m"
    if n >= 1_000:
        return f"{sign}₦{n/1_000:,.0f}k"
    return f"{sign}₦{n:,.0f}"


def lever_with_boi(unlev: dict, draws: list[float], rate: float = 0.09) -> dict:
    """Apply a ₦90bn-class BOI facility: interest-only Y1–Y2 of each draw window,
    then 6-year principal amortisation from Y3 of the model (year 3).
    draws is a 6-length list of new drawings in each year (Y1 usually 0).
    """
    years = [dict(r) for r in unlev["years"]]
    debt = 0.0
    equity_fcf = []
    for i, r in enumerate(years):
        drawn = draws[i]
        debt += drawn
        interest = debt * rate
        # principal: after year 2, amortise outstanding over remaining years through Y8
        # within the 6-year window, start amortising in Y3 over 6 years
        principal = 0.0
        if r["year"] >= 3 and debt > 0:
            remaining_years = 6 - (r["year"] - 3)  # 6,5,4,3
            # 8-year tenor from first major draw (Y2): 6 amortising years Y3–Y8
            principal = debt / max(remaining_years + 2, 1)  # leave tail beyond Y6
            principal = min(principal, debt)
        debt = max(0.0, debt - principal)
        pbt = r["ebit"] - interest
        tax = max(0.0, pbt) * TAX
        npat = pbt - tax
        # equity FCF: unlevered FCF - interest*(1-t) - principal + draws
        # simpler: npat + da - capex - dwc + draws - principal
        # Reconstruct capex+dwc from unlevered identity: fcf_u = npat_u + da - capex - dwc
        capex_plus_dwc = r["npat"] + r["da"] - r["fcf"]
        efcf = npat + r["da"] - capex_plus_dwc + drawn - principal
        r["interest"] = interest
        r["principal"] = principal
        r["drawn"] = drawn
        r["debt_end"] = debt
        r["pbt"] = pbt
        r["tax"] = tax
        r["npat"] = npat
        r["equity_fcf"] = efcf
        equity_fcf.append(efcf)

    opening_equity = unlev["opening_equity"]
    npv = -opening_equity
    for i, r in enumerate(years):
        npv += r["equity_fcf"] / ((1 + DISCOUNT) ** r["year"])

    def npv_at(rate_: float) -> float:
        v = -opening_equity
        for r in years:
            v += r["equity_fcf"] / ((1 + rate_) ** r["year"])
        return v

    irr = None
    lo, hi = -0.5, 5.0
    if npv_at(lo) * npv_at(hi) < 0:
        for _ in range(80):
            mid = (lo + hi) / 2
            if npv_at(mid) > 0:
                lo = mid
            else:
                hi = mid
        irr = (lo + hi) / 2

    dscr = []
    for r in years:
        service = r["interest"] + r["principal"]
        dscr.append(None if service <= 0 else r["ebitda"] / service)

    return {
        "years": years,
        "npv_22": npv,
        "irr": irr,
        "opening_equity": opening_equity,
        "total_drawn": sum(draws),
        "min_dscr": min((d for d in dscr if d is not None), default=None),
        "dscr": dscr,
        "y6_npat": years[-1]["npat"],
        "y6_debt": years[-1]["debt_end"],
    }


def unit_breakeven(name: str) -> dict:
    """Daily transactions needed for EBITDA = 0 on one mature kiosk with bank share on."""
    p = SCENARIOS[name]
    # opex = a * gross + fixed
    # gross = tx * uptime * 365 * fee
    # a = logistics + theft + eligible*bank_share
    a = p["logistics_pct"] + p["theft_loss_pct"] + p["eligible_share"] * p["bank_share_rate"]
    fixed = (
        p["rent_month"] * 12
        + p["maint_year"]
        + p["connect_year"]
        + 18_000 * 12
        + (280_000 / 40 + 220_000 / 80) * 12
        + (p["unit_capex"] + p["float_per"]) * p["insurance_pct_assets"]
        + 12_000
    )
    # (1-a)*gross = fixed => gross = fixed/(1-a)
    gross_be = fixed / (1 - a)
    tx_be = gross_be / (p["uptime"] * DAYS * p["blended_fee"])
    return {
        "fixed_annual": fixed,
        "variable_ratio": a,
        "gross_be": gross_be,
        "tx_per_day_be": tx_be,
        "planned_tx": p["tx_per_day"],
        "margin_of_safety": 1 - tx_be / p["tx_per_day"] if p["tx_per_day"] else None,
    }


def main() -> None:
    results = {name: run_scenario(name) for name in SCENARIOS}
    hold_2k = run_scenario("planning", fleet_end=[350, 2_000, 2_000, 2_000, 2_000, 2_000])
    hold_2k["name"] = "planning_hold_2k"
    hold_2k["label"] = "Planning — hold at 2,000"
    hold_5k = run_scenario("planning", fleet_end=[350, 2_000, 5_000, 5_000, 5_000, 5_000])
    hold_5k["name"] = "planning_hold_5k"
    hold_5k["label"] = "Planning — hold at 5,000"
    phase1 = run_scenario("planning", fleet_end=[350, 350, 350, 350, 350, 350])
    phase1["name"] = "planning_phase1"
    phase1["label"] = "Planning — Phase 1 hold (350)"

    # BOI ₦90bn: ₦25bn Y2, ₦35bn Y3, ₦30bn Y4
    boi_draws = [0.0, 25_000_000_000, 35_000_000_000, 30_000_000_000, 0.0, 0.0]
    boi_planning = lever_with_boi(results["planning"], boi_draws)
    boi_promoter = lever_with_boi(results["promoter"], boi_draws)
    boi_25 = lever_with_boi(
        hold_5k, [0.0, 25_000_000_000, 0.0, 0.0, 0.0, 0.0]
    )
    boi_30_phased = lever_with_boi(
        hold_5k, [0.0, 15_000_000_000, 15_000_000_000, 0.0, 0.0, 0.0]
    )
    boi_10_on_2k = lever_with_boi(
        hold_2k, [0.0, 8_000_000_000, 0.0, 0.0, 0.0, 0.0]
    )

    breakeven = {name: unit_breakeven(name) for name in SCENARIOS}

    payload = {
        "discount": DISCOUNT,
        "tax": TAX,
        "days": DAYS,
        "year_labels": YEAR_LABELS,
        "scenarios": results,
        "planning_hold_2k": hold_2k,
        "planning_hold_5k": hold_5k,
        "planning_phase1": phase1,
        "boi_planning": boi_planning,
        "boi_promoter": boi_promoter,
        "boi_25_on_5k": boi_25,
        "boi_30_phased_on_5k": boi_30_phased,
        "boi_8_on_2k": boi_10_on_2k,
        "breakeven": breakeven,
    }
    (OUT / "model_results.json").write_text(json.dumps(payload, indent=2))

    # CSV extracts
    for name, res in results.items():
        lines = [
            "year,label,closing_fleet,avg_fleet,gross,opex,ebitda,npat,capex,fcf,npat_margin"
        ]
        for r in res["years"]:
            lines.append(
                f"{r['year']},{r['label']},{r['closing_fleet']},{r['avg_fleet']:.1f},"
                f"{r['gross']:.0f},{r['opex']:.0f},{r['ebitda']:.0f},{r['npat']:.0f},"
                f"{r['capex']:.0f},{r['fcf']:.0f},{r['npat_margin']:.4f}"
            )
        (OUT / f"{name}_annual.csv").write_text("\n".join(lines) + "\n")

    print("CashEase three-case model")
    print(f"{'':20} {'Stress':>16} {'Planning':>16} {'Promoter':>16}")
    for key, fmt in [
        ("opening_equity", "equity t=0"),
        ("y2_npat", "Y2 NPAT"),
        ("y3_npat", "Y3 NPAT"),
        ("y6_npat", "Y6 NPAT"),
        ("cumulative_npat", "6y cum NPAT"),
        ("npv_22", "NPV @ 22%"),
    ]:
        cells = [naira(results[s][key]) for s in SCENARIOS]
        print(f"{fmt:20} {cells[0]:>16} {cells[1]:>16} {cells[2]:>16}")
    irrs = [
        f"{results[s]['irr']*100:.1f}%" if results[s]["irr"] is not None else "n/m"
        for s in SCENARIOS
    ]
    print(f"{'IRR':20} {irrs[0]:>16} {irrs[1]:>16} {irrs[2]:>16}")
    for s, res in results.items():
        print(f"\n{res['label']} fleet:", [y["closing_fleet"] for y in res["years"]])
        print(
            f"  unit monthly gross {naira(res['unit_monthly_gross'])} | "
            f"Y1 equity {naira(res['opening_equity'])}"
        )

    print("\nHold / BOI extras")
    print(
        f"  Phase 1 hold NPV {naira(phase1['npv_22'])}  IRR "
        f"{phase1['irr']*100:.1f}%" if phase1["irr"] else f"  Phase 1 hold NPV {naira(phase1['npv_22'])}"
    )
    print(
        f"  Hold 2k NPV {naira(hold_2k['npv_22'])}  IRR "
        f"{(hold_2k['irr']*100):.1f}%" if hold_2k["irr"] else f"  Hold 2k NPV {naira(hold_2k['npv_22'])}"
    )
    print(
        f"  BOI planning equity NPV {naira(boi_planning['npv_22'])}  "
        f"min DSCR {boi_planning['min_dscr']:.2f}x  Y6 debt {naira(boi_planning['y6_debt'])}"
        if boi_planning["min_dscr"]
        else f"  BOI planning equity NPV {naira(boi_planning['npv_22'])}"
    )
    print(
        f"  BOI promoter equity NPV {naira(boi_promoter['npv_22'])}  "
        f"min DSCR {boi_promoter['min_dscr']:.2f}x"
        if boi_promoter["min_dscr"]
        else f"  BOI promoter equity NPV {naira(boi_promoter['npv_22'])}"
    )
    print(
        f"  Hold 5k NPV {naira(hold_5k['npv_22'])}  IRR "
        f"{(hold_5k['irr']*100):.1f}%" if hold_5k["irr"] else f"  Hold 5k NPV {naira(hold_5k['npv_22'])}"
    )
    print(
        f"  ₦8bn BOI on 2k hold NPV {naira(boi_10_on_2k['npv_22'])}  "
        f"min DSCR {boi_10_on_2k['min_dscr']:.2f}x  Y6 debt {naira(boi_10_on_2k['y6_debt'])}"
    )
    print(
        f"  ₦25bn BOI on 5k hold NPV {naira(boi_25['npv_22'])}  "
        f"min DSCR {boi_25['min_dscr']:.2f}x  Y6 debt {naira(boi_25['y6_debt'])}"
    )
    print(
        f"  ₦30bn phased on 5k hold NPV {naira(boi_30_phased['npv_22'])}  "
        f"min DSCR {boi_30_phased['min_dscr']:.2f}x  Y6 debt {naira(boi_30_phased['y6_debt'])}"
    )
    print("\nBreak-even tx/day (mature kiosk, bank share on)")
    for name, b in breakeven.items():
        print(
            f"  {name:10} {b['tx_per_day_be']:.0f} tx/day vs plan {b['planned_tx']}  "
            f"MoS {b['margin_of_safety']*100:.0f}%"
        )
    print("\nwrote", OUT / "model_results.json")


if __name__ == "__main__":
    main()
