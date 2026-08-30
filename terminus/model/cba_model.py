#!/usr/bin/env python3
"""Cost-benefit model: interstate coach terminus as landlord (not a fleet).

Planning document, August 2026. Figures are illustrative on stated assumptions.
"""
from __future__ import annotations

import json
from pathlib import Path

TAX = 0.321  # 30% CIT + 3% education tax on PBT
DISCOUNT = 0.22
DAYS = 365
HORIZON = 10
RAMP = [0.55, 0.80, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00]

# Works (not land) depreciated straight-line over 20 years.
WORKS_LIFE = 20

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)


def naira_bn(x: float) -> float:
    return round(x / 1e9, 3)


def naira_m(x: float) -> float:
    return round(x / 1e6, 1)


SCENARIOS = {
    "stress": {
        "label": "Stress",
        "site_m2": 18_000,
        "land_per_m2": 80_000,  # inner-corridor Lagos, freehold
        "pave_m2": 14_000,
        "pave_per_m2": 32_000,
        "build_m2": 2_200,
        "build_per_m2": 380_000,
        "utilities": 380_000_000,
        "fitout": 180_000_000,
        "soft_pct": 0.18,
        "preopen_wc": 120_000_000,
        "bays": 32,
        "bay_occ": 0.48,
        "bay_rent_month": 1_200_000,
        "casual_departures_day": 6,
        "casual_fee": 35_000,
        "layover_buses": 10,
        "layover_night": 8_000,
        "retail_m2": 700,
        "retail_occ": 0.50,
        "retail_m2_month": 8_000,
        "parking_year": 18_000_000,
        "ads_year": 12_000_000,
        "staff_year": 160_000_000,
        "security_year": 60_000_000,
        "power_year": 95_000_000,
        "maint_pct_works": 0.035,
        "insurance_pct_assets": 0.018,
        "rates_year": 48_000_000,
        "admin_year": 55_000_000,
        "land_apprec": 0.04,
        "exit_ebitda_yield": 0.14,
    },
    "planning": {
        "label": "Planning",
        "site_m2": 20_000,
        "land_per_m2": 38_000,  # highway-edge Lagos–Ogun
        "pave_m2": 16_000,
        "pave_per_m2": 24_000,
        "build_m2": 2_500,
        "build_per_m2": 300_000,
        "utilities": 260_000_000,
        "fitout": 120_000_000,
        "soft_pct": 0.14,
        "preopen_wc": 80_000_000,
        "bays": 36,
        "bay_occ": 0.72,
        "bay_rent_month": 1_800_000,
        "casual_departures_day": 12,
        "casual_fee": 45_000,
        "layover_buses": 18,
        "layover_night": 12_000,
        "retail_m2": 900,
        "retail_occ": 0.75,
        "retail_m2_month": 12_000,
        "parking_year": 36_000_000,
        "ads_year": 24_000_000,
        "staff_year": 135_000_000,
        "security_year": 48_000_000,
        "power_year": 72_000_000,
        "maint_pct_works": 0.028,
        "insurance_pct_assets": 0.015,
        "rates_year": 36_000_000,
        "admin_year": 40_000_000,
        "land_apprec": 0.07,
        "exit_ebitda_yield": 0.11,
    },
    "upside": {
        "label": "Upside",
        "site_m2": 20_000,
        "land_per_m2": 12_000,  # long concession / ground rent capitalised
        "pave_m2": 16_000,
        "pave_per_m2": 22_000,
        "build_m2": 2_800,
        "build_per_m2": 280_000,
        "utilities": 240_000_000,
        "fitout": 140_000_000,
        "soft_pct": 0.12,
        "preopen_wc": 70_000_000,
        "bays": 40,
        "bay_occ": 0.86,
        "bay_rent_month": 2_400_000,
        "casual_departures_day": 18,
        "casual_fee": 55_000,
        "layover_buses": 24,
        "layover_night": 15_000,
        "retail_m2": 1_200,
        "retail_occ": 0.88,
        "retail_m2_month": 18_000,
        "parking_year": 55_000_000,
        "ads_year": 48_000_000,
        "staff_year": 145_000_000,
        "security_year": 52_000_000,
        "power_year": 68_000_000,
        "maint_pct_works": 0.025,
        "insurance_pct_assets": 0.014,
        "rates_year": 40_000_000,
        "admin_year": 42_000_000,
        "land_apprec": 0.09,
        "exit_ebitda_yield": 0.09,
    },
}


def capex(p: dict) -> dict:
    land = p["site_m2"] * p["land_per_m2"]
    pave = p["pave_m2"] * p["pave_per_m2"]
    build = p["build_m2"] * p["build_per_m2"]
    hard = pave + build + p["utilities"] + p["fitout"]
    soft = hard * p["soft_pct"]
    works = hard + soft
    total = land + works + p["preopen_wc"]
    return {
        "land": land,
        "pave": pave,
        "build": build,
        "utilities": p["utilities"],
        "fitout": p["fitout"],
        "soft": soft,
        "works": works,
        "wc": p["preopen_wc"],
        "total": total,
    }


def steady_gross(p: dict) -> dict:
    contracted = p["bays"] * p["bay_occ"]
    bay = contracted * p["bay_rent_month"] * 12
    casual = p["casual_departures_day"] * p["casual_fee"] * 330
    layover = p["layover_buses"] * p["layover_night"] * 300
    retail = p["retail_m2"] * p["retail_occ"] * p["retail_m2_month"] * 12
    parking = p["parking_year"]
    ads = p["ads_year"]
    gross = bay + casual + layover + retail + parking + ads
    return {
        "contracted_bays": contracted,
        "bay": bay,
        "casual": casual,
        "layover": layover,
        "retail": retail,
        "parking": parking,
        "ads": ads,
        "gross": gross,
    }


def opex_at(p: dict, cx: dict, scale: float) -> dict:
    # Power, security, rates, admin partly sticky; staff and maint scale a little.
    sticky = (
        p["security_year"]
        + p["power_year"] * 0.7
        + p["rates_year"]
        + p["admin_year"]
        + cx["works"] * p["maint_pct_works"] * 0.6
        + cx["total"] * p["insurance_pct_assets"]
    )
    variable = (
        p["staff_year"]
        + p["power_year"] * 0.3
        + cx["works"] * p["maint_pct_works"] * 0.4
    ) * scale
    return {"opex": sticky + variable, "sticky": sticky, "variable": variable}


def npv(cashflows: list[float], r: float) -> float:
    return sum(cf / ((1 + r) ** t) for t, cf in enumerate(cashflows))


def irr(cashflows: list[float]) -> float | None:
    # Newton on NPV = 0. None if no sign change.
    if cashflows[0] >= 0 or all(c <= 0 for c in cashflows[1:]):
        return None
    r = 0.15
    for _ in range(80):
        f = npv(cashflows, r)
        df = sum(-t * cf / ((1 + r) ** (t + 1)) for t, cf in enumerate(cashflows))
        if abs(df) < 1e-9:
            break
        r2 = r - f / df
        if r2 <= -0.95:
            r2 = -0.9
        if abs(r2 - r) < 1e-7:
            return r2
        r = r2
    return r


def run_scenario(key: str) -> dict:
    p = SCENARIOS[key]
    cx = capex(p)
    sg = steady_gross(p)
    da_year = cx["works"] / WORKS_LIFE
    years = []
    cash = []
    # t=0: invest
    cash.append(-cx["total"])
    for y in range(1, HORIZON + 1):
        scale = RAMP[y - 1]
        g = sg["gross"] * scale
        mix = {k: sg[k] * scale for k in ("bay", "casual", "layover", "retail", "parking", "ads")}
        op = opex_at(p, cx, scale)
        ebitda = g - op["opex"]
        ebit = ebitda - da_year
        tax = max(0.0, ebit * TAX)
        npat = ebit - tax
        fcf = npat + da_year  # unlevered, no further capex in horizon
        years.append(
            {
                "year": y,
                "scale": scale,
                "gross": g,
                **mix,
                "opex": op["opex"],
                "ebitda": ebitda,
                "da": da_year,
                "ebit": ebit,
                "tax": tax,
                "npat": npat,
                "fcf": fcf,
                "ebitda_margin": ebitda / g if g else 0.0,
                "npat_margin": npat / g if g else 0.0,
            }
        )

    y10 = years[-1]
    land_exit = cx["land"] * ((1 + p["land_apprec"]) ** HORIZON)
    ebitda_exit = y10["ebitda"] / p["exit_ebitda_yield"] if y10["ebitda"] > 0 else 0.0
    # Residual: max of capitalised operations and appreciated land + remaining works book.
    works_book = cx["works"] * (1 - HORIZON / WORKS_LIFE)
    ops_plus_land = ebitda_exit
    residual = max(ops_plus_land, land_exit + works_book * 0.5)
    # Conservative: blend 70% ops capitalisation with 30% land floor when ops positive
    if y10["ebitda"] > 0:
        residual = 0.7 * ebitda_exit + 0.3 * (land_exit + works_book)
    years[-1]["residual"] = residual
    years[-1]["fcf"] = y10["fcf"] + residual
    cash.extend(row["fcf"] for row in years[:-1])
    cash.append(years[-1]["fcf"])

    be = break_even(p, cx, sg)
    return {
        "key": key,
        "label": p["label"],
        "capex": cx,
        "steady": sg,
        "years": years,
        "npv22": npv(cash, DISCOUNT),
        "npv18": npv(cash, 0.18),
        "npv15": npv(cash, 0.15),
        "irr": irr(cash),
        "cash": cash,
        "be": be,
        "payback": payback_years(cash),
        "y10_ebitda": y10["ebitda"],
        "y10_npat": y10["npat"] - 0,  # residual not in NPAT
        "y10_npat_ops": years[-1]["npat"],
        "residual": residual,
        "simple_y3_yield": years[2]["ebitda"] / cx["total"] if cx["total"] else 0,
    }


def payback_years(cash: list[float]) -> float | None:
    acc = 0.0
    for t, cf in enumerate(cash):
        acc += cf
        if t > 0 and acc >= 0:
            prev = acc - cf
            return (t - 1) + (-prev / cf if cf else 0)
    return None


def break_even(p: dict, cx: dict, sg: dict) -> dict:
    """Occupancy at which Y3-run-rate EBITDA is zero. All volume lines scale with occ; ads stay."""
    best = None
    for occ in [i / 100 for i in range(5, 99)]:
        q = dict(p)
        q["bay_occ"] = occ
        q["casual_departures_day"] = p["casual_departures_day"] * occ / max(p["bay_occ"], 0.01)
        q["layover_buses"] = p["layover_buses"] * occ / max(p["bay_occ"], 0.01)
        q["retail_occ"] = p["retail_occ"] * occ / max(p["bay_occ"], 0.01)
        q["parking_year"] = p["parking_year"] * occ / max(p["bay_occ"], 0.01)
        g = steady_gross(q)["gross"]
        op = opex_at(q, cx, max(occ / max(p["bay_occ"], 0.01), 0.4))["opex"]
        if g - op >= 0:
            best = occ
            break
    return {
        "bay_occ_ebitda": best,
        "contracted_bays": p["bays"] * best if best else None,
        "note": "Volume lines scale with occupancy. Opex only partly variable. Ads held.",
    }


def fleet_comparison() -> dict:
    """Same order of capital, as operator of coaches — for contrast, not underwriting."""
    coaches = 25
    unit = 95_000_000
    wc = 280_000_000
    capex = coaches * unit + wc
    # One revenue trip per coach per day, 280 days, 42 pax, ₦42,000 fare
    gross = coaches * 280 * 42 * 42_000
    ebitda_margin = 0.11  # after fuel, crew, maint, insurance, park fees
    ebitda = gross * ebitda_margin
    da = coaches * unit / 8  # 8-year life
    ebit = ebitda - da
    npat = ebit * (1 - TAX) if ebit > 0 else ebit
    return {
        "coaches": coaches,
        "unit": unit,
        "capex": capex,
        "gross": gross,
        "ebitda": ebitda,
        "ebitda_margin": ebitda_margin,
        "da": da,
        "npat": npat,
        "npat_margin": npat / gross if gross else 0,
        "note": "Illustrative. Empty legs, accidents, FX parts and fare wars can wipe the 11% EBITDA. No land residual.",
    }


def main() -> None:
    results = {k: run_scenario(k) for k in SCENARIOS}
    fleet = fleet_comparison()
    payload = {
        "tax": TAX,
        "discount": DISCOUNT,
        "horizon": HORIZON,
        "ramp": RAMP,
        "scenarios": results,
        "fleet": fleet,
        "verdict_planning": results["planning"]["npv22"] > 0
        and (results["planning"]["irr"] or 0) > 0.18,
    }
    # JSON-friendly
    def conv(o):
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, list):
            return [conv(v) for v in o]
        if isinstance(o, float):
            return o
        return o

    (OUT / "cba_results.json").write_text(json.dumps(conv(payload), indent=2))
    # CSV planning
    import csv

    with (OUT / "planning_annual.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "year",
                "scale",
                "gross",
                "opex",
                "ebitda",
                "npat",
                "fcf",
                "ebitda_margin",
            ],
        )
        w.writeheader()
        for row in results["planning"]["years"]:
            w.writerow({k: row[k] for k in w.fieldnames})

    p = results["planning"]
    print("PLANNING")
    print(f"  CapEx  ₦{p['capex']['total']/1e9:.2f}bn  (land {p['capex']['land']/1e9:.2f} + works {p['capex']['works']/1e9:.2f})")
    print(f"  Steady gross ₦{p['steady']['gross']/1e6:.0f}m")
    print(f"  Y3 EBITDA ₦{p['years'][2]['ebitda']/1e6:.0f}m  NPAT ₦{p['years'][2]['npat']/1e6:.0f}m")
    print(f"  NPV@22% ₦{p['npv22']/1e9:.2f}bn  @18% ₦{p['npv18']/1e9:.2f}bn  @15% ₦{p['npv15']/1e9:.2f}bn")
    print(f"  IRR {100*(p['irr'] or 0):.1f}%  payback {p['payback']}")
    print(f"  BE bay occ {p['be']['bay_occ_ebitda']}  bays {p['be']['contracted_bays']}")
    print("STRESS NPV22", f"₦{results['stress']['npv22']/1e9:.2f}bn", "IRR", f"{100*(results['stress']['irr'] or 0):.1f}%", "payback", results["stress"]["payback"])
    print("UPSIDE NPV22", f"₦{results['upside']['npv22']/1e9:.2f}bn", "IRR", f"{100*(results['upside']['irr'] or 0):.1f}%")
    print("FLEET capex", f"₦{fleet['capex']/1e9:.2f}bn", "NPAT", f"₦{fleet['npat']/1e6:.0f}m")


if __name__ == "__main__":
    main()
