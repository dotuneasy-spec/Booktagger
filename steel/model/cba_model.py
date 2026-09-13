#!/usr/bin/env python3
"""
Ashlar Steel — ten-year cost–benefit model.

Two operating companies under one holding:
  LongsCo   rolling mill (rebar, wire rod, merchant bar)
  BilletCo  EAF + caster (billets sold inside the group, surplus to third parties)

Three cases (stress / planning / upside) plus a Longs-only hold and a
gated 1.0 Mt crude expansion. Figures are in naira unless noted.
Planning FX is ₦1,500 / USD — a conservative capital-goods rate, not a
spot forecast.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

YEARS = list(range(1, 11))
YEAR_LABELS = [
    "Y1 2028",
    "Y2 2029",
    "Y3 2030",
    "Y4 2031",
    "Y5 2032",
    "Y6 2033",
    "Y7 2034",
    "Y8 2035",
    "Y9 2036",
    "Y10 2037",
]
TAX = 0.321  # 30% CIT + education tax, stacked conservatively
DISCOUNT = 0.18  # industrial project rate (Nigeria)
FX = 1_500.0
DAYS = 365
BILLET_PER_T_FINISHED = 1.036  # yield loss on the roll
LIFE_ROLL = 18
LIFE_MELT = 20
LIFE_POWER = 16


def naira(x: float) -> str:
    ax = abs(x)
    sign = "-" if x < 0 else ""
    if ax >= 1e12:
        return f"{sign}₦{ax/1e12:.2f}tn"
    if ax >= 1e9:
        return f"{sign}₦{ax/1e9:.2f}bn"
    if ax >= 1e6:
        return f"{sign}₦{ax/1e6:.1f}m"
    return f"{sign}₦{ax:,.0f}"


def usd(x_naira: float) -> str:
    return f"${x_naira / FX / 1e6:,.1f}m"


def npv_of(cash: list[float], rate: float, t0: float = 0.0) -> float:
    v = -t0
    for i, c in enumerate(cash, start=1):
        v += c / ((1 + rate) ** i)
    return v


def irr_of(cash: list[float], t0: float) -> float | None:
    lo, hi = -0.6, 4.0
    a, b = npv_of(cash, lo, t0), npv_of(cash, hi, t0)
    if a * b > 0:
        return None
    for _ in range(90):
        mid = (lo + hi) / 2
        if npv_of(cash, mid, t0) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------
# Capacities are nameplate tonnes / year. Utilisation is of nameplate.
# Melt starts only if the case builds it (planning and upside do; stress
# starts melt late and under-runs it; longs_only never builds melt).

CASES = {
    "stress": {
        "label": "Stress",
        "roll_kt": 150.0,
        "melt_kt": 200.0,
        "build_melt": True,
        "expand_roll_kt": 0.0,
        "expand_melt_kt": 0.0,
        "roll_util": [0.00, 0.28, 0.42, 0.48, 0.50, 0.50, 0.48, 0.45, 0.45, 0.45],
        "melt_util": [0.00, 0.00, 0.00, 0.00, 0.15, 0.28, 0.32, 0.32, 0.30, 0.30],
        "asp_longs": 820_000,
        "asp_billet_ext": 640_000,
        "import_billet": 800_000,
        "own_billet_cash": 780_000,
        "conv_longs": 140_000,
        "ga_year1": 4.2e9,
        "ga_growth": 1.10,
        "roll_fixed_capex": 96e9,
        "melt_fixed_capex": 155e9,
        "power_capex": 0.0,  # no captive; diesel sits inside own_billet_cash
        "expand_roll_capex": 0.0,
        "expand_melt_capex": 0.0,
        "wc_days_metal": 70,
        "debt_rate_1": 0.16,
        "debt_rate_2": 0.16,
        "equity_share_1": 0.40,
        "equity_share_2": 0.40,
        "theft_yield": 0.015,
        "insure_pct": 0.016,
    },
    "planning": {
        "label": "Planning",
        "roll_kt": 150.0,
        "melt_kt": 200.0,  # sized to the roll mill, not a billet export shop
        "build_melt": True,
        "expand_roll_kt": 0.0,
        "expand_melt_kt": 0.0,
        "roll_util": [0.00, 0.40, 0.70, 0.85, 0.88, 0.90, 0.90, 0.90, 0.90, 0.90],
        "melt_util": [0.00, 0.00, 0.00, 0.00, 0.45, 0.75, 0.88, 0.88, 0.88, 0.88],
        "asp_longs": 990_000,
        "asp_billet_ext": 710_000,
        "import_billet": 750_000,
        "own_billet_cash": 610_000,
        "conv_longs": 80_000,
        "ga_year1": 2.8e9,
        "ga_growth": 1.07,
        "roll_fixed_capex": 82e9,
        "melt_fixed_capex": 125e9,
        "power_capex": 38e9,
        "expand_roll_capex": 0.0,
        "expand_melt_capex": 0.0,
        "wc_days_metal": 50,
        "debt_rate_1": 0.09,
        "debt_rate_2": 0.10,
        "equity_share_1": 0.35,
        "equity_share_2": 0.35,
        "theft_yield": 0.004,
        "insure_pct": 0.008,
    },
    "upside": {
        "label": "Upside",
        "roll_kt": 150.0,
        "melt_kt": 200.0,
        "build_melt": True,
        "expand_roll_kt": 150.0,  # second stand, Y5
        "expand_melt_kt": 200.0,  # merchant + second EAF, Y8 — only with offtake
        "roll_util": [0.00, 0.50, 0.80, 0.90, 0.92, 0.92, 0.92, 0.92, 0.92, 0.92],
        "melt_util": [0.00, 0.00, 0.00, 0.00, 0.60, 0.85, 0.90, 0.90, 0.90, 0.90],
        "asp_longs": 1_080_000,
        "asp_billet_ext": 740_000,
        "import_billet": 720_000,
        "own_billet_cash": 560_000,
        "conv_longs": 70_000,
        "ga_year1": 2.6e9,
        "ga_growth": 1.06,
        "roll_fixed_capex": 78e9,
        "melt_fixed_capex": 118e9,
        "power_capex": 36e9,
        "expand_roll_capex": 68e9,
        "expand_melt_capex": 95e9,
        "wc_days_metal": 42,
        "debt_rate_1": 0.08,
        "debt_rate_2": 0.09,
        "equity_share_1": 0.30,
        "equity_share_2": 0.30,
        "theft_yield": 0.002,
        "insure_pct": 0.007,
    },
    "concession": {
        "label": "Concession power",
        "roll_kt": 150.0,
        "melt_kt": 200.0,
        "build_melt": True,
        "expand_roll_kt": 0.0,
        "expand_melt_kt": 0.0,
        "roll_util": [0.00, 0.45, 0.75, 0.88, 0.90, 0.92, 0.92, 0.92, 0.92, 0.92],
        "melt_util": [0.00, 0.00, 0.00, 0.00, 0.50, 0.80, 0.90, 0.90, 0.90, 0.90],
        "asp_longs": 990_000,
        "asp_billet_ext": 710_000,
        "import_billet": 750_000,
        "own_billet_cash": 540_000,  # firm gas at the fence
        "conv_longs": 68_000,
        "ga_year1": 2.5e9,
        "ga_growth": 1.06,
        "roll_fixed_capex": 64e9,  # industrial park, shared civils
        "melt_fixed_capex": 105e9,
        "power_capex": 18e9,  # IPP wheels; no full captive build
        "expand_roll_capex": 0.0,
        "expand_melt_capex": 0.0,
        "wc_days_metal": 45,
        "debt_rate_1": 0.08,
        "debt_rate_2": 0.09,
        "equity_share_1": 0.30,
        "equity_share_2": 0.30,
        "theft_yield": 0.003,
        "insure_pct": 0.007,
    },
}


def roll_nameplate(p: dict, year: int) -> float:
    extra = p["expand_roll_kt"] if year >= 5 else 0.0
    return (p["roll_kt"] + extra) * 1_000.0


def melt_nameplate(p: dict, year: int) -> float:
    if not p["build_melt"]:
        return 0.0
    extra = p["expand_melt_kt"] if year >= 8 else 0.0
    return (p["melt_kt"] + extra) * 1_000.0


def capex_schedule(p: dict) -> list[float]:
    """Plant cash spend by year (not working capital)."""
    cap = [0.0] * 10
    # Longs: 70% Y1, 30% Y2
    cap[0] += p["roll_fixed_capex"] * 0.70
    cap[1] += p["roll_fixed_capex"] * 0.30
    if p["build_melt"]:
        # Melt + captive power: Y4 40%, Y5 60%
        melt = p["melt_fixed_capex"] + p["power_capex"]
        cap[3] += melt * 0.40
        cap[4] += melt * 0.60
    if p["expand_roll_capex"]:
        cap[4] += p["expand_roll_capex"] * 0.50
        cap[5] += p["expand_roll_capex"] * 0.50
    if p["expand_melt_capex"]:
        cap[7] += p["expand_melt_capex"] * 0.45
        cap[8] += p["expand_melt_capex"] * 0.55
    return cap


def funded_plant(p: dict) -> dict:
    """Split plant capex into equity and debt by phase."""
    longs = p["roll_fixed_capex"]
    melt = (p["melt_fixed_capex"] + p["power_capex"]) if p["build_melt"] else 0.0
    exp_r = p["expand_roll_capex"]
    exp_m = p["expand_melt_capex"]
    e1 = longs * p["equity_share_1"]
    d1 = longs - e1
    e2 = melt * p["equity_share_2"]
    d2 = melt - e2
    e3 = (exp_r + exp_m) * p["equity_share_2"]
    d3 = (exp_r + exp_m) - e3
    return {
        "equity_longs": e1,
        "debt_longs": d1,
        "equity_melt": e2,
        "debt_melt": d2,
        "equity_exp": e3,
        "debt_exp": d3,
        "equity_total": e1 + e2 + e3,
        "debt_total": d1 + d2 + d3,
    }


def run_case(name: str, **override) -> dict:
    p = {**CASES[name], **override}
    capex = capex_schedule(p)
    fund = funded_plant(p)

    # Debt drawn in the same years as the related capex.
    debt_draw = [0.0] * 10
    debt_draw[0] += fund["debt_longs"] * 0.70
    debt_draw[1] += fund["debt_longs"] * 0.30
    if p["build_melt"]:
        melt = p["melt_fixed_capex"] + p["power_capex"]
        share = fund["debt_melt"] / melt if melt else 0.0
        debt_draw[3] += melt * 0.40 * share
        debt_draw[4] += melt * 0.60 * share
    exp = p["expand_roll_capex"] + p["expand_melt_capex"]
    if exp:
        share = fund["debt_exp"] / exp
        if p["expand_roll_capex"]:
            debt_draw[4] += p["expand_roll_capex"] * 0.50 * share
            debt_draw[5] += p["expand_roll_capex"] * 0.50 * share
        if p["expand_melt_capex"]:
            debt_draw[7] += p["expand_melt_capex"] * 0.45 * share
            debt_draw[8] += p["expand_melt_capex"] * 0.55 * share

    equity_draw = [c - d for c, d in zip(capex, debt_draw)]

    # Amortise: longs debt from Y3, 10 years; melt from Y6, 12 years.
    # Simple straight-line principal once amortisation starts.
    debt_bal = 0.0
    rows = []
    prev_wc = 0.0
    cum_capex = 0.0
    fcf_list = []
    eq_fcf_list = []

    for i, year in enumerate(YEARS):
        r_kt = roll_nameplate(p, year) * p["roll_util"][i]
        m_kt = melt_nameplate(p, year) * p["melt_util"][i] if p["build_melt"] else 0.0

        roll_need_billet = r_kt * BILLET_PER_T_FINISHED
        own_used = min(m_kt, roll_need_billet)
        import_used = max(0.0, roll_need_billet - own_used)
        billets_sold = max(0.0, m_kt - own_used)

        rev_longs = r_kt * p["asp_longs"]
        rev_billet = billets_sold * p["asp_billet_ext"]
        revenue = rev_longs + rev_billet

        metal = (
            own_used * p["own_billet_cash"]
            + import_used * p["import_billet"]
            + billets_sold * p["own_billet_cash"]
        )
        conversion = r_kt * p["conv_longs"]
        shrink = revenue * p["theft_yield"]
        cogs = metal + conversion + shrink

        ga = p["ga_year1"] * (p["ga_growth"] ** (year - 1))
        # Insurance ~1.4% of cumulative plant
        cum_capex += capex[i]
        insurance = cum_capex * p["insure_pct"]
        opex = cogs + ga + insurance
        ebitda = revenue - opex

        # Depreciation on commissioned plant (longs from Y2, melt from Y5)
        da = 0.0
        if year >= 2:
            da += p["roll_fixed_capex"] / LIFE_ROLL
        if year >= 5 and p["expand_roll_capex"]:
            da += p["expand_roll_capex"] / LIFE_ROLL
        if year >= 5 and p["build_melt"]:
            da += p["melt_fixed_capex"] / LIFE_MELT
            da += p["power_capex"] / LIFE_POWER
        if year >= 8 and p["expand_melt_capex"]:
            da += p["expand_melt_capex"] / LIFE_MELT

        # Working capital = days of metal on the year's throughput
        metal_t = own_used + import_used + billets_sold
        wc = metal_t * (
            (p["own_billet_cash"] * (own_used + billets_sold) + p["import_billet"] * import_used)
            / metal_t
            if metal_t
            else 0.0
        ) * (p["wc_days_metal"] / DAYS)
        # receivables 25 days of sales
        wc += revenue * (25.0 / DAYS)
        dwc = wc - prev_wc
        prev_wc = wc

        # Debt service
        debt_bal += debt_draw[i]
        # blended rate: longs  vs melt outstanding approximated by current rate
        # Use rate_1 until melt draws (Y4), then blend toward rate_2.
        rate = p["debt_rate_1"] if year < 4 else (
            p["debt_rate_1"] if not p["build_melt"] else (p["debt_rate_1"] + p["debt_rate_2"]) / 2
        )
        if year >= 6 and p["build_melt"]:
            rate = p["debt_rate_2"]
        interest = debt_bal * rate
        principal = 0.0
        if year >= 3 and fund["debt_longs"] > 0:
            principal += fund["debt_longs"] / 10.0
        if year >= 6 and fund["debt_melt"] > 0:
            principal += fund["debt_melt"] / 12.0
        if year >= 7 and fund["debt_exp"] > 0:
            principal += fund["debt_exp"] / 10.0
        principal = min(principal, debt_bal)
        debt_end = max(0.0, debt_bal - principal)

        ebit = ebitda - da
        pbt = ebit - interest
        tax = pbt * TAX if pbt > 0 else 0.0
        npat = pbt - tax

        # Project FCF (unlevered): EBITDA - tax_unlev - capex - dwc
        tax_unlev = (ebit * TAX) if ebit > 0 else 0.0
        fcf = ebitda - tax_unlev - capex[i] - dwc
        # Equity FCF: -equity_draw + (fcf - interest + debt_draw - principal)
        # Standard: EBITDA - tax - capex - dwc - interest - principal + debt_draw
        # and opening equity is t0 separately. Annual equity plug:
        eq_fcf = ebitda - tax - capex[i] - dwc - interest - principal + debt_draw[i]

        dscr = (ebitda / (interest + principal)) if (interest + principal) > 1 else None

        fx_saved = (
            r_kt * p["asp_longs"]  # finished tonnes no longer imported
            + billets_sold * p["asp_billet_ext"]
        )

        # Remaining book value of plant (for residual at Y10)
        nbv = 0.0
        if year >= 2:
            used = min(year - 1, LIFE_ROLL)
            nbv += p["roll_fixed_capex"] * max(0.0, 1 - used / LIFE_ROLL)
        if year >= 5 and p["expand_roll_capex"]:
            used = min(year - 4, LIFE_ROLL)
            nbv += p["expand_roll_capex"] * max(0.0, 1 - used / LIFE_ROLL)
        if year >= 5 and p["build_melt"]:
            used = min(year - 4, LIFE_MELT)
            nbv += p["melt_fixed_capex"] * max(0.0, 1 - used / LIFE_MELT)
            used_p = min(year - 4, LIFE_POWER)
            nbv += p["power_capex"] * max(0.0, 1 - used_p / LIFE_POWER)
        if year >= 8 and p["expand_melt_capex"]:
            used = min(year - 7, LIFE_MELT)
            nbv += p["expand_melt_capex"] * max(0.0, 1 - used / LIFE_MELT)

        rows.append(
            {
                "year": year,
                "label": YEAR_LABELS[i],
                "roll_t": r_kt,
                "melt_t": m_kt,
                "own_used": own_used,
                "import_used": import_used,
                "billets_sold": billets_sold,
                "revenue": revenue,
                "rev_longs": rev_longs,
                "rev_billet": rev_billet,
                "cogs": cogs,
                "metal": metal,
                "conversion": conversion,
                "ga": ga,
                "insurance": insurance,
                "opex": opex,
                "ebitda": ebitda,
                "da": da,
                "ebit": ebit,
                "interest": interest,
                "principal": principal,
                "pbt": pbt,
                "tax": tax,
                "npat": npat,
                "capex": capex[i],
                "wc": wc,
                "dwc": dwc,
                "fcf": fcf,
                "eq_fcf": eq_fcf,
                "debt_draw": debt_draw[i],
                "equity_draw": equity_draw[i],
                "debt_end": debt_end,
                "dscr": dscr,
                "ebitda_margin": ebitda / revenue if revenue else 0.0,
                "npat_margin": npat / revenue if revenue else 0.0,
                "fx_saved": fx_saved,
                "nbv": nbv,
            }
        )
        fcf_list.append(fcf)
        eq_fcf_list.append(eq_fcf)
        debt_bal = debt_end

    residual = rows[-1]["nbv"] + rows[-1]["wc"]
    rows[-1]["residual"] = residual
    fcf_resid = fcf_list[:-1] + [fcf_list[-1] + residual]
    eq_resid = eq_fcf_list[:-1] + [eq_fcf_list[-1] + residual]

    opening_equity = equity_draw[0]
    # t=0 is first-year equity already inside eq_fcf as -equity_draw[0] netted
    # with construction. Unlevered IRR uses project FCF with t0 = 0 because
    # Y1 capex is in fcf_list[0].
    irr_u = irr_of(fcf_list, 0.0)
    irr_e = irr_of(eq_fcf_list, 0.0)
    irr_u_r = irr_of(fcf_resid, 0.0)
    irr_e_r = irr_of(eq_resid, 0.0)

    npv18 = npv_of(fcf_list, DISCOUNT, 0.0)
    npv15 = npv_of(fcf_list, 0.15, 0.0)
    npv12 = npv_of(fcf_list, 0.12, 0.0)
    npv22 = npv_of(fcf_list, 0.22, 0.0)
    npv_e = npv_of(eq_fcf_list, DISCOUNT, 0.0)
    npv18_r = npv_of(fcf_resid, DISCOUNT, 0.0)
    npv15_r = npv_of(fcf_resid, 0.15, 0.0)
    npv12_r = npv_of(fcf_resid, 0.12, 0.0)
    npv22_r = npv_of(fcf_resid, 0.22, 0.0)

    payback = None
    cum = 0.0
    for r in rows:
        cum += r["fcf"]
        if cum >= 0 and payback is None and r["year"] > 1:
            payback = r["year"]

    y10 = rows[-1]
    dscrs = [r["dscr"] for r in rows if r["dscr"] is not None]
    return {
        "name": name,
        "label": p["label"],
        "params": p,
        "fund": fund,
        "years": rows,
        "irr_unlev": irr_u,
        "irr_equity": irr_e,
        "irr_unlev_resid": irr_u_r,
        "irr_equity_resid": irr_e_r,
        "residual": residual,
        "npv_18": npv18,
        "npv_15": npv15,
        "npv_12": npv12,
        "npv_22": npv22,
        "npv_18_resid": npv18_r,
        "npv_15_resid": npv15_r,
        "npv_12_resid": npv12_r,
        "npv_22_resid": npv22_r,
        "npv_equity_18": npv_e,
        "payback_year": payback,
        "opening_equity": opening_equity,
        "total_equity": fund["equity_total"],
        "total_debt": fund["debt_total"],
        "total_plant": sum(capex),
        "y10_npat": y10["npat"],
        "y10_revenue": y10["revenue"],
        "y10_ebitda": y10["ebitda"],
        "y10_roll_t": y10["roll_t"],
        "y10_melt_t": y10["melt_t"],
        "cumulative_npat": sum(r["npat"] for r in rows),
        "cumulative_fx_saved": sum(r["fx_saved"] for r in rows),
        "min_dscr": min(dscrs) if dscrs else None,
        "steady_npat": y10["npat"],
    }


def unit_economics(p: dict) -> dict:
    """Steady-state ₦ / tonne at planning prices, 90% longs / 85% melt."""
    roll_t = p["roll_kt"] * 1_000 * 0.90
    melt_t = p["melt_kt"] * 1_000 * 0.85 if p["build_melt"] else 0.0
    need = roll_t * BILLET_PER_T_FINISHED
    own = min(melt_t, need)
    imp = need - own
    sold = max(0.0, melt_t - own)
    rev = roll_t * p["asp_longs"] + sold * p["asp_billet_ext"]
    metal = own * p["own_billet_cash"] + imp * p["import_billet"] + sold * p["own_billet_cash"]
    conv = roll_t * p["conv_longs"]
    longs_spread_import = p["asp_longs"] - BILLET_PER_T_FINISHED * p["import_billet"] - p["conv_longs"]
    longs_spread_own = p["asp_longs"] - BILLET_PER_T_FINISHED * p["own_billet_cash"] - p["conv_longs"]
    melt_spread = p["import_billet"] - p["own_billet_cash"]
    return {
        "roll_t": roll_t,
        "melt_t": melt_t,
        "revenue": rev,
        "longs_spread_import": longs_spread_import,
        "longs_spread_own": longs_spread_own,
        "melt_vs_import": melt_spread,
        "gross": rev - metal - conv,
    }


def public_cba(res: dict) -> dict:
    """Simple public-account view: FX kept in-country vs private capex."""
    fx = res["cumulative_fx_saved"]
    plant = res["total_plant"]
    return {
        "import_substitution_10y": fx,
        "plant_capex": plant,
        "substitution_per_naira_plant": fx / plant if plant else 0.0,
        "y10_annual_substitution": res["years"][-1]["fx_saved"],
    }


def main() -> None:
    results = {n: run_case(n) for n in ("stress", "planning", "upside", "concession")}
    longs_only = run_case(
        "planning",
        build_melt=False,
        melt_kt=0.0,
        melt_fixed_capex=0.0,
        power_capex=0.0,
        expand_roll_kt=0.0,
        expand_melt_kt=0.0,
        expand_roll_capex=0.0,
        expand_melt_capex=0.0,
        melt_util=[0.0] * 10,
    )
    longs_only["name"] = "longs_only"
    longs_only["label"] = "Planning — Longs only (no melt)"

    mt_expand = run_case(
        "upside",
        expand_melt_kt=800.0,  # 200 + 800 = 1.0 Mt
        expand_melt_capex=310e9,
        expand_roll_kt=350.0,
        expand_roll_capex=150e9,
    )
    mt_expand["name"] = "one_mt"
    mt_expand["label"] = "Upside — gated 1.0 Mt crude"

    units = {
        n: unit_economics(CASES[n] | {"build_melt": True})
        for n in ("stress", "planning", "upside", "concession")
    }
    units["longs_only"] = unit_economics(
        {**CASES["planning"], "build_melt": False, "melt_kt": 0.0}
    )

    public = {n: public_cba(results[n]) for n in results}
    public["longs_only"] = public_cba(longs_only)
    public["one_mt"] = public_cba(mt_expand)

    payload = {
        "fx": FX,
        "tax": TAX,
        "discount": DISCOUNT,
        "year_labels": YEAR_LABELS,
        "scenarios": results,
        "longs_only": longs_only,
        "one_mt": mt_expand,
        "unit": units,
        "public": public,
    }
    (OUT / "model_results.json").write_text(json.dumps(payload, indent=2))

    for name, res in list(results.items()) + [
        ("longs_only", longs_only),
        ("one_mt", mt_expand),
    ]:
        lines = [
            "year,label,roll_t,melt_t,revenue,ebitda,npat,capex,fcf,dscr,npat_margin"
        ]
        for r in res["years"]:
            dscr = f"{r['dscr']:.3f}" if r["dscr"] is not None else ""
            lines.append(
                f"{r['year']},{r['label']},{r['roll_t']:.1f},{r['melt_t']:.1f},"
                f"{r['revenue']:.0f},{r['ebitda']:.0f},{r['npat']:.0f},"
                f"{r['capex']:.0f},{r['fcf']:.0f},{dscr},{r['npat_margin']:.4f}"
            )
        (OUT / f"{name}_annual.csv").write_text("\n".join(lines) + "\n")

    print("Ashlar Steel — ten-year CBA")
    print(
        f"{'':28} {'Stress':>14} {'Planning':>14} {'Upside':>14} "
        f"{'Longs only':>14} {'Concession':>14}"
    )
    rows_print = [
        ("Plant capex", "total_plant"),
        ("Equity committed", "total_equity"),
        ("Y10 revenue", "y10_revenue"),
        ("Y10 EBITDA", "y10_ebitda"),
        ("Y10 NPAT", "y10_npat"),
        ("10y cum NPAT", "cumulative_npat"),
        ("NPV @ 18% (no resid)", "npv_18"),
        ("NPV @ 18% + residual", "npv_18_resid"),
        ("NPV @ 12% + residual", "npv_12_resid"),
    ]
    pack = [
        results["stress"],
        results["planning"],
        results["upside"],
        longs_only,
        results["concession"],
    ]
    for title, key in rows_print:
        cells = [naira(r[key]) for r in pack]
        print(
            f"{title:28} {cells[0]:>14} {cells[1]:>14} {cells[2]:>14} "
            f"{cells[3]:>14} {cells[4]:>14}"
        )
    irrs = []
    irrs_r = []
    for r in pack:
        irrs.append(f"{r['irr_unlev']*100:.1f}%" if r["irr_unlev"] is not None else "n/m")
        irrs_r.append(
            f"{r['irr_unlev_resid']*100:.1f}%" if r["irr_unlev_resid"] is not None else "n/m"
        )
    print(f"{'IRR unlev':28} {irrs[0]:>14} {irrs[1]:>14} {irrs[2]:>14} {irrs[3]:>14} {irrs[4]:>14}")
    print(
        f"{'IRR unlev + residual':28} {irrs_r[0]:>14} {irrs_r[1]:>14} {irrs_r[2]:>14} "
        f"{irrs_r[3]:>14} {irrs_r[4]:>14}"
    )
    print(
        f"{'1.0 Mt gated Y10 NPAT':28} {naira(mt_expand['y10_npat']):>14}  "
        f"NPV18+R {naira(mt_expand['npv_18_resid'])}  plant {naira(mt_expand['total_plant'])}"
    )
    u = units["planning"]
    print(
        f"\nPlanning spread  import-route {naira(u['longs_spread_import'])}/t  "
        f"own-billet {naira(u['longs_spread_own'])}/t  "
        f"melt vs import {naira(u['melt_vs_import'])}/t"
    )
    print("wrote", OUT / "model_results.json")


if __name__ == "__main__":
    main()
