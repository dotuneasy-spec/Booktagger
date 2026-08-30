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


def overlay(base: dict, **kw) -> dict:
    q = dict(base)
    q.update(kw)
    return q


PLAN = SCENARIOS["planning"]

HUBS = [
    {
        "id": "lagos",
        "name": "Lagos–Ogun hub",
        "phase": 1,
        "open_t": 0,
        "params": overlay(PLAN),
    },
    {
        "id": "abuja",
        "name": "Abuja hub (pair)",
        "phase": 2,
        "open_t": 3,
        "params": overlay(
            PLAN,
            site_m2=18_000,
            land_per_m2=48_000,
            pave_m2=14_500,
            build_m2=2_300,
            bays=32,
            bay_occ=0.68,
            bay_rent_month=1_900_000,
            casual_departures_day=10,
            layover_buses=16,
            retail_m2=800,
            parking_year=32_000_000,
            staff_year=128_000_000,
            power_year=70_000_000,
        ),
    },
    {
        "id": "ph",
        "name": "Port Harcourt hub",
        "phase": 3,
        "open_t": 5,
        "params": overlay(
            PLAN,
            site_m2=15_000,
            land_per_m2=28_000,
            pave_m2=12_000,
            build_m2=1_800,
            utilities=200_000_000,
            fitout=90_000_000,
            bays=28,
            bay_occ=0.65,
            bay_rent_month=1_500_000,
            casual_departures_day=8,
            layover_buses=12,
            retail_m2=650,
            retail_m2_month=10_000,
            parking_year=22_000_000,
            ads_year=16_000_000,
            staff_year=110_000_000,
            security_year=40_000_000,
            power_year=58_000_000,
            rates_year=28_000_000,
            admin_year=28_000_000,
        ),
    },
    {
        "id": "kano",
        "name": "Kano hub",
        "phase": 3,
        "open_t": 6,
        "params": overlay(
            PLAN,
            site_m2=15_000,
            land_per_m2=22_000,
            pave_m2=12_000,
            build_m2=1_800,
            utilities=190_000_000,
            fitout=85_000_000,
            bays=28,
            bay_occ=0.62,
            bay_rent_month=1_350_000,
            casual_departures_day=7,
            layover_buses=12,
            retail_m2=600,
            retail_m2_month=9_000,
            parking_year=18_000_000,
            ads_year=14_000_000,
            staff_year=105_000_000,
            security_year=38_000_000,
            power_year=55_000_000,
            rates_year=24_000_000,
            admin_year=26_000_000,
        ),
    },
    {
        "id": "enugu",
        "name": "Enugu / Onitsha hub",
        "phase": 3,
        "open_t": 7,
        "params": overlay(
            PLAN,
            site_m2=14_000,
            land_per_m2=20_000,
            pave_m2=11_000,
            build_m2=1_600,
            utilities=180_000_000,
            fitout=80_000_000,
            bays=24,
            bay_occ=0.60,
            bay_rent_month=1_300_000,
            casual_departures_day=7,
            layover_buses=10,
            retail_m2=550,
            retail_occ=0.70,
            retail_m2_month=9_000,
            parking_year=16_000_000,
            ads_year=12_000_000,
            staff_year=98_000_000,
            security_year=36_000_000,
            power_year=52_000_000,
            rates_year=22_000_000,
            admin_year=24_000_000,
        ),
    },
    {
        "id": "ibadan",
        "name": "Ibadan hub",
        "phase": 3,
        "open_t": 8,
        "params": overlay(
            PLAN,
            site_m2=14_000,
            land_per_m2=26_000,
            pave_m2=11_000,
            build_m2=1_600,
            utilities=185_000_000,
            fitout=80_000_000,
            bays=24,
            bay_occ=0.64,
            bay_rent_month=1_400_000,
            casual_departures_day=8,
            layover_buses=10,
            retail_m2=550,
            parking_year=20_000_000,
            ads_year=14_000_000,
            staff_year=100_000_000,
            security_year=36_000_000,
            power_year=54_000_000,
            rates_year=24_000_000,
            admin_year=24_000_000,
        ),
    },
]

PHASE_HORIZON = 12  # years of calendar after t=0 Lagos spend


def hub_year_fcf(p: dict, cx: dict, years_open: int) -> tuple[float, float, float, float]:
    """Gross, EBITDA, FCF, NPAT for a hub in its Nth operating year (1-indexed)."""
    scale = RAMP[min(years_open - 1, len(RAMP) - 1)]
    g = steady_gross(p)["gross"] * scale
    op = opex_at(p, cx, scale)["opex"]
    ebitda = g - op
    da = cx["works"] / WORKS_LIFE
    ebit = ebitda - da
    tax = max(0.0, ebit * TAX)
    npat = ebit - tax
    fcf = npat + da
    return g, ebitda, fcf, npat


def hub_residual(p: dict, cx: dict, last_ebitda: float) -> float:
    land_exit = cx["land"] * ((1 + p["land_apprec"]) ** PHASE_HORIZON)
    works_book = cx["works"] * max(1 - PHASE_HORIZON / WORKS_LIFE, 0.3)
    if last_ebitda > 0:
        return 0.7 * (last_ebitda / p["exit_ebitda_yield"]) + 0.3 * (land_exit + works_book)
    return land_exit * 0.5


def run_phased() -> dict:
    cash = [0.0] * (PHASE_HORIZON + 1)
    hubs_out = []
    annual = [
        {"year": y, "capex": 0.0, "gross": 0.0, "ebitda": 0.0, "npat": 0.0, "fcf_ops": 0.0}
        for y in range(1, PHASE_HORIZON + 1)
    ]
    for h in HUBS:
        p = h["params"]
        cx = capex(p)
        sg = steady_gross(p)
        t0 = h["open_t"]
        cash[t0] -= cx["total"]
        last_e = 0.0
        last_npat = 0.0
        ops_years = 0
        for cal in range(t0 + 1, PHASE_HORIZON + 1):
            ops_years = cal - t0
            g, ebitda, fcf, npat = hub_year_fcf(p, cx, ops_years)
            cash[cal] += fcf
            row = annual[cal - 1]
            row["gross"] += g
            row["ebitda"] += ebitda
            row["npat"] += npat
            row["fcf_ops"] += fcf
            last_e = ebitda
            last_npat = npat
        res = hub_residual(p, cx, last_e) if ops_years else 0.0
        cash[PHASE_HORIZON] += res
        hubs_out.append(
            {
                "id": h["id"],
                "name": h["name"],
                "phase": h["phase"],
                "open_t": t0,
                "capex": cx["total"],
                "land": cx["land"],
                "works": cx["works"],
                "bays": p["bays"],
                "bay_occ": p["bay_occ"],
                "steady_gross": sg["gross"],
                "y12_ebitda": last_e,
                "y12_npat": last_npat,
                "residual": res,
            }
        )

    phase_capex = {1: 0.0, 2: 0.0, 3: 0.0}
    for ho, h in zip(hubs_out, HUBS):
        phase_capex[h["phase"]] += ho["capex"]

    copies36 = {
        "n": 36,
        "capex": 36 * capex(PLAN)["total"],
        "note": "36 × planning Lagos yard. Most would run at stress occupancy or worse.",
        "stress_y3_ebitda_if_all_stress": 36 * run_scenario("stress")["years"][2]["ebitda"],
    }

    spoke = overlay(
        PLAN,
        site_m2=8_000,
        land_per_m2=18_000,
        pave_m2=6_000,
        build_m2=900,
        utilities=90_000_000,
        fitout=40_000_000,
        soft_pct=0.12,
        preopen_wc=40_000_000,
        bays=12,
        bay_occ=0.70,
        bay_rent_month=1_100_000,
        casual_departures_day=4,
        layover_buses=6,
        retail_m2=250,
        retail_occ=0.65,
        parking_year=8_000_000,
        ads_year=6_000_000,
        staff_year=48_000_000,
        security_year=18_000_000,
        power_year=28_000_000,
        rates_year=12_000_000,
        admin_year=12_000_000,
    )
    spoke_cx = capex(spoke)
    spoke_g = steady_gross(spoke)["gross"]
    spoke_op = opex_at(spoke, spoke_cx, 1.0)["opex"]
    spokes = {
        "bays": 12,
        "capex_each": spoke_cx["total"],
        "steady_gross": spoke_g,
        "steady_ebitda": spoke_g - spoke_op,
        "eight_cities_capex": 8 * spoke_cx["total"],
        "cities_example": "Jos, Kaduna, Calabar, Warri, Benin, Maiduguri, Uyo, Asaba — only with pre-lets",
    }

    return {
        "horizon": PHASE_HORIZON,
        "hubs": hubs_out,
        "phase_capex": phase_capex,
        "cumulative_capex": sum(phase_capex.values()),
        "annual": annual,
        "npv22": npv(cash, DISCOUNT),
        "npv18": npv(cash, 0.18),
        "npv15": npv(cash, 0.15),
        "irr": irr(cash),
        "cash": cash,
        "y12_gross": annual[-1]["gross"],
        "y12_ebitda": annual[-1]["ebitda"],
        "y12_npat": annual[-1]["npat"],
        "copies36": copies36,
        "spokes": spokes,
        "gates": {
            "phase2": "Lagos median occupancy ≥ 65% for 12 months; ≥20 bays contracted; designation clean",
            "phase3": "Pair (Lagos+Abuja) both ≥ 60% occ; cash to fund next hub without emptying float",
            "spokes": "Named operator LOI for ≥8 of 12 bays; no spoke without that paper",
            "never": "36 identical 2 ha copies; a capital with no originating volume",
        },
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
    phased = run_phased()
    payload = {
        "tax": TAX,
        "discount": DISCOUNT,
        "horizon": HORIZON,
        "ramp": RAMP,
        "scenarios": results,
        "fleet": fleet,
        "phased": phased,
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
    ph = phased
    print("PHASED 6 hubs capex", f"₦{ph['cumulative_capex']/1e9:.2f}bn", "Y12 NPAT", f"₦{ph['y12_npat']/1e6:.0f}m", "IRR", f"{100*(ph['irr'] or 0):.1f}%", "NPV22", f"₦{ph['npv22']/1e9:.2f}bn")
    print("  phase capex", {k: round(v/1e9, 2) for k, v in ph['phase_capex'].items()})
    print("  36 copies", f"₦{ph['copies36']['capex']/1e9:.1f}bn")
    print("  spoke each", f"₦{ph['spokes']['capex_each']/1e6:.0f}m", "x8", f"₦{ph['spokes']['eight_cities_capex']/1e9:.2f}bn")


if __name__ == "__main__":
    main()
