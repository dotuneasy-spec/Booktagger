#!/usr/bin/env python3
"""
SNLB Farms — Bankable financial model (August 2026).

Produces three cases over a 5-year (10-cycle) horizon:
  - promoter: original operating yields/prices, with previously omitted costs filled in
  - credit:   lender underwriting case (haircut prices/yields, full cost stack, fully taxed)
  - downside: stacked stress (yield −25%, glut/scarcity prices, costs +25%)

All figures in Nigerian naira. Run: python3 financial_model.py
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

N = 1_000_000  # millions helper


def fmt(n: float, decimals: int = 1) -> str:
    """Format naira as ₦X.Xm / ₦X.Xb."""
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000:
        return f"{sign}₦{n / 1_000_000_000:.{decimals}f}bn"
    return f"{sign}₦{n / 1_000_000:.{decimals}f}m"


def pct(n: float) -> str:
    return f"{n * 100:.1f}%"


def irr_newton(cashflows: list[float], guess: float = 0.5) -> float:
    """Annual IRR via Newton-Raphson. Returns nan if it fails to converge."""
    r = guess
    for _ in range(80):
        npv = sum(cf / ((1 + r) ** t) for t, cf in enumerate(cashflows))
        d = sum(-t * cf / ((1 + r) ** (t + 1)) for t, cf in enumerate(cashflows) if t)
        if abs(d) < 1e-12:
            break
        r2 = r - npv / d
        if abs(r2 - r) < 1e-10:
            return r2
        r = r2
        if r <= -0.999:
            r = -0.99
    npv = sum(cf / ((1 + r) ** t) for t, cf in enumerate(cashflows))
    return r if abs(npv) < 1.0 else float("nan")


def npv(rate: float, cashflows: list[float]) -> float:
    return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows))


@dataclass
class CaseParams:
    name: str
    yield_reg_t: float
    yield_peak_t: float
    price_reg: float
    price_peak: float
    prod_reg: float
    prod_peak: float
    logistics_per_basket: float
    cost_inflation: float
    tax_mode: str  # "holiday" | "full" | "legacy_bands"
    initial_equity: float
    initial_capex: float


CASES = {
    "promoter": CaseParams(
        name="Upside case (NTA agri tax holiday on the operating plan)",
        yield_reg_t=20.0,
        yield_peak_t=18.0,
        price_reg=33_000,
        price_peak=145_000,
        prod_reg=3_400_000,
        prod_peak=3_800_000,
        logistics_per_basket=900,
        cost_inflation=0.12,
        tax_mode="holiday",
        initial_equity=8_000_000,
        initial_capex=3_500_000,
    ),
    "credit": CaseParams(
        name="Planning case — Peak-first, non-glut Mile 12 prices, full tax",
        yield_reg_t=20.0,
        yield_peak_t=18.0,
        price_reg=33_000,
        price_peak=145_000,
        prod_reg=3_400_000,
        prod_peak=3_800_000,
        logistics_per_basket=900,
        cost_inflation=0.12,
        tax_mode="full",
        initial_equity=8_000_000,
        initial_capex=3_500_000,
    ),
    "downside": CaseParams(
        name="Downside / stacked stress",
        yield_reg_t=15.0,  # −25% vs original 20
        yield_peak_t=13.5,  # −25% vs original 18
        price_reg=15_000,  # Jan 2025 glut floor
        price_peak=55_000,  # below May-2026 trough band
        prod_reg=4_250_000,  # +25% vs original Regular
        prod_peak=4_750_000,
        logistics_per_basket=1_300,
        cost_inflation=0.17,  # near NBS food inflation
        tax_mode="full",
        initial_equity=8_000_000,
        initial_capex=3_500_000,
    ),
}

# Operational expansion path (ha under cultivation at each cycle)
HA_PATH = [1, 3, 15, 27, 72, 100, 100, 100, 100, 100]
# Cycle 1 is timed into Mile 12 scarcity (Peak / non-glut). Regular glut is the second cycle, not the plan.
SEASONS = ["Peak", "Regular"] * 5
YEARS = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
CYCLE_IDS = [f"C{i}" for i in range(1, 11)]
MASTER_HA = 100
LEASE_CULTIVATED_PER_CYCLE = 100_000  # ₦200k/ha/year
LEASE_HOLDING_PER_CYCLE = 12_500  # ₦25k/ha/year on unused block
NAIC_RATE = 0.02
CARGO_RATE = 0.015
CONTINGENCY = 0.05
BULK_FROM_HA = 55
BULK_REV_HAIRCUT = 0.07
DA_YEARS = 6.0  # straight-line on gross irrigation/packhouse stock

# Line-item mix for Regular production cost (shares sum to 1)
PROD_MIX = {
    "Hybrid seed & seedlings": 0.30,
    "Fertilizer & fertigation": 0.20,
    "IPM / crop protection": 0.12,
    "Seasonal labour": 0.18,
    "Irrigation operating cost": 0.08,
    "Staking, twine, mulch": 0.07,
    "Nursery & miscellaneous": 0.05,
}


def mech_discount(ha: int) -> float:
    if ha < 5:
        return 0.0
    if ha < 25:
        return 0.07
    if ha < 60:
        return 0.14
    return 0.20


def management_payroll(ha: int, year: int, inflation: float) -> float:
    if ha < 5:
        monthly = 70_000
    elif ha < 30:
        monthly = 550_000
    else:
        monthly = 2_600_000
    return monthly * 6 * ((1 + inflation) ** (year - 1))


def other_insurance(ha: int, year: int, inflation: float) -> float:
    """Public liability + key-person + product liability, per cycle."""
    base = 180_000 + 8_000 * ha
    return base * ((1 + inflation) ** (year - 1))


def incremental_capex(prev_ha: int, ha: int) -> tuple[float, dict]:
    """Drip extension + shared infrastructure triggered by scale."""
    added = max(0, ha - prev_ha)
    drip = added * 1_000_000
    shared = 0.0
    notes = {}
    if prev_ha < 15 <= ha:
        shared += 6_000_000
        notes["second_borehole"] = 6_000_000
    if prev_ha < 27 <= ha:
        shared += 8_000_000
        notes["packing_shed"] = 8_000_000
    if prev_ha < 72 <= ha:
        shared += 40_000_000
        notes["packhouse_cold_borehole"] = 40_000_000
    notes["drip_extension"] = drip
    return drip + shared, notes


def cit_legacy(turnover: float, ebit: float) -> float:
    if turnover <= 25_000_000:
        rate = 0.0
    elif turnover <= 100_000_000:
        rate = 0.20
    else:
        rate = 0.30
    return max(0.0, ebit) * rate


def cit_nta_full(turnover: float, fixed_assets: float, ebit: float) -> float:
    """NTA 2025: small company 0% if turnover ≤ ₦50m AND FA ≤ ₦250m; else 30% + 4% levy."""
    if turnover <= 50_000_000 and fixed_assets <= 250_000_000:
        return 0.0
    return max(0.0, ebit) * 0.34


def run_case(p: CaseParams, with_debt: bool = False) -> dict:
    baskets_reg = p.yield_reg_t / 0.05  # 50 kg basket
    baskets_peak = p.yield_peak_t / 0.05

    cycles = []
    gross_ppe = p.initial_capex
    accum_da = 0.0
    buffer = 0.0
    expansion = 0.0
    cash = p.initial_equity - p.initial_capex  # residual WC after t=0 CapEx
    prev_ha = 0
    annual = {y: {} for y in range(1, 6)}

    # Optional BOA-style facility drawn at start of Year 2
    debt_principal = 80_000_000 if with_debt else 0.0
    debt_outstanding = 0.0
    debt_rate = 0.09
    mgmt_fee_rate = 0.01

    for i, (cid, year, season, ha) in enumerate(zip(CYCLE_IDS, YEARS, SEASONS, HA_PATH)):
        infl = (1 + p.cost_inflation) ** (year - 1)
        disc = mech_discount(ha)
        bulk = BULK_REV_HAIRCUT if ha >= BULK_FROM_HA else 0.0
        bph = baskets_reg if season == "Regular" else baskets_peak
        price = p.price_reg if season == "Regular" else p.price_peak
        prod_base = p.prod_reg if season == "Regular" else p.prod_peak

        baskets = bph * ha
        tonnes = (p.yield_reg_t if season == "Regular" else p.yield_peak_t) * ha
        revenue = baskets * price * (1 - bulk)

        prod = prod_base * (1 - disc) * infl * ha
        logistics = baskets * p.logistics_per_basket * infl
        lease = ha * LEASE_CULTIVATED_PER_CYCLE * infl + (MASTER_HA - ha) * LEASE_HOLDING_PER_CYCLE * infl
        naic = NAIC_RATE * prod
        cargo = CARGO_RATE * logistics
        ins_other = other_insurance(ha, year, p.cost_inflation)
        insurance = naic + cargo + ins_other
        contingency = CONTINGENCY * prod
        mgmt = management_payroll(ha, year, p.cost_inflation)

        capex_now, capex_notes = incremental_capex(prev_ha, ha)
        if i == 0:
            capex_now += 0.0  # initial CapEx already at t=0
        gross_ppe += capex_now
        da = gross_ppe / DA_YEARS / 2  # two cycles per year
        accum_da += da
        net_ppe = max(0.0, gross_ppe - accum_da)

        # Debt: draw at start of Year 2 (cycle index 2)
        interest = 0.0
        principal_repay = 0.0
        debt_fees = 0.0
        if with_debt:
            if i == 2 and debt_outstanding == 0.0:
                debt_outstanding = debt_principal
                cash += debt_principal
                debt_fees = debt_principal * 0.005  # appraisal, paid once
            if debt_outstanding > 0:
                interest = debt_outstanding * debt_rate / 2  # per cycle
                debt_fees += debt_outstanding * mgmt_fee_rate / 2
                # principal: moratorium through Year 2 (cycles 2-3, i=2,3); amortise Years 3-5
                if year >= 3:
                    principal_repay = min(debt_outstanding, debt_principal / 6)  # 6 remaining cycles
                    debt_outstanding -= principal_repay

        opex = prod + logistics + lease + insurance + contingency + mgmt + da
        ebit = revenue - opex
        ebt = ebit - interest - debt_fees

        cycles.append(
            {
                "id": cid,
                "year": year,
                "season": season,
                "ha": ha,
                "added": ha - prev_ha,
                "mech_discount": disc,
                "bulk_haircut": bulk,
                "baskets": baskets,
                "tonnes": tonnes,
                "revenue": revenue,
                "prod": prod,
                "logistics": logistics,
                "lease": lease,
                "insurance": insurance,
                "contingency": contingency,
                "mgmt": mgmt,
                "da": da,
                "opex": opex,
                "ebit": ebit,
                "interest": interest,
                "debt_fees": debt_fees,
                "principal_repay": principal_repay,
                "ebt": ebt,
                "capex": capex_now if i > 0 else 0.0,
                "capex_notes": capex_notes,
                "gross_ppe": gross_ppe,
                "net_ppe": net_ppe,
            }
        )
        prev_ha = ha

    # Annual tax on summed EBT
    by_year = {y: [c for c in cycles if c["year"] == y] for y in range(1, 6)}
    years_out = []
    cash = p.initial_equity  # reset: t=0 equity in; CapEx of year 1 includes initial
    # Rebuild annual cash from cycle results
    # Initial: equity in, initial capex out
    # We'll compute year-level from cycles

    opening_cash = 0.0
    debt_out_ye = 0.0
    if with_debt:
        pass

    # Recompute debt outstanding year-end from cycles
    # Tax per year then allocate NPAT to cycles pro-rata to EBT for 50/50

    for y in range(1, 6):
        cs = by_year[y]
        rev = sum(c["revenue"] for c in cs)
        prod = sum(c["prod"] for c in cs)
        logistics = sum(c["logistics"] for c in cs)
        lease = sum(c["lease"] for c in cs)
        insurance = sum(c["insurance"] for c in cs)
        contingency = sum(c["contingency"] for c in cs)
        mgmt = sum(c["mgmt"] for c in cs)
        da = sum(c["da"] for c in cs)
        ebit = sum(c["ebit"] for c in cs)
        interest = sum(c["interest"] for c in cs)
        fees = sum(c["debt_fees"] for c in cs)
        ebt = sum(c["ebt"] for c in cs)
        capex = (p.initial_capex if y == 1 else 0.0) + sum(c["capex"] for c in cs)
        tonnes = sum(c["tonnes"] for c in cs)
        ha_end = cs[-1]["ha"]
        net_ppe = cs[-1]["net_ppe"]
        principal = sum(c["principal_repay"] for c in cs)

        if p.tax_mode == "holiday" and y <= 5:
            tax = 0.0
        elif p.tax_mode == "legacy_bands":
            tax = cit_legacy(rev, ebt)
        else:
            tax = cit_nta_full(rev, cs[-1]["gross_ppe"], ebt)

        npat = ebt - tax
        ebitda = ebit + da
        debt_service = interest + fees + principal
        dscr = (ebitda / debt_service) if debt_service > 1 else None

        for c in cs:
            share = c["ebt"] / ebt if ebt else 0.5
            c["tax"] = tax * share
            c["npat"] = c["ebt"] - c["tax"]
            c["buffer"] = c["npat"] * 0.5
            c["reinvest"] = c["npat"] * 0.5

        years_out.append(
            {
                "year": y,
                "ha_end": ha_end,
                "tonnes": tonnes,
                "revenue": rev,
                "prod": prod,
                "logistics": logistics,
                "lease": lease,
                "insurance": insurance,
                "contingency": contingency,
                "mgmt": mgmt,
                "da": da,
                "ebitda": ebitda,
                "ebit": ebit,
                "interest": interest,
                "fees": fees,
                "ebt": ebt,
                "tax": tax,
                "npat": npat,
                "gross_margin": (rev - prod - logistics) / rev if rev else 0,
                "ebit_margin": ebit / rev if rev else 0,
                "net_margin": npat / rev if rev else 0,
                "capex": capex,
                "principal": principal,
                "debt_service": debt_service,
                "dscr": dscr,
                "buffer": npat * 0.5,
                "reinvest": npat * 0.5,
                "fcf": npat + da - capex,  # NWC assumed cash-sales, intra-cycle
                "net_ppe": net_ppe,
            }
        )

    # Cash roll-forward
    cash = 0.0
    cum_buffer = 0.0
    equity = p.initial_equity
    bs = []
    for yrow in years_out:
        y = yrow["year"]
        opening = cash
        cfo = yrow["npat"] + yrow["da"]
        cfi = -yrow["capex"]
        cff = p.initial_equity if y == 1 else 0.0
        if with_debt:
            if y == 2:
                cff += debt_principal
            cff -= yrow["principal"]  # principal is financing outflow (interest already in NPAT)
            # interest already reduced NPAT so CFO is after interest — standard
        cash = opening + cfo + cfi + cff
        yrow["opening_cash"] = opening
        yrow["cfo"] = cfo
        yrow["cfi"] = cfi
        yrow["cff"] = cff
        yrow["closing_cash"] = cash
        cum_buffer += yrow["buffer"]
        yrow["cum_buffer"] = cum_buffer
        # Debt outstanding year-end
        drawn = debt_principal if (with_debt and y >= 2) else 0.0
        repaid = sum(yy["principal"] for yy in years_out if yy["year"] <= y)
        debt_ye = max(0.0, drawn - repaid) if with_debt else 0.0
        yrow["debt_ye"] = debt_ye
        equity = cash + yrow["net_ppe"] - debt_ye
        bs.append(
            {
                "year": y,
                "cash": cash,
                "net_ppe": yrow["net_ppe"],
                "total_assets": cash + yrow["net_ppe"],
                "debt": debt_ye,
                "equity": equity,
            }
        )

    # DCF on project FCF (unlevered approximation: add back after-tax interest)
    fcf = []
    for yrow in years_out:
        tax_rate = 0.0 if (p.tax_mode == "holiday") else 0.34
        nopat = yrow["ebit"] * (1 - tax_rate) if yrow["ebit"] > 0 else yrow["ebit"]
        fcf.append(nopat + yrow["da"] - yrow["capex"])
    # t=0 is before year 1; year 1 FCF already deducts initial capex, but equity contribution
    # is the investment. Project CF: t=0 = -initial equity (or -initial capex - opening WC)
    # We treat t=0 as -initial_equity, and year 1 FCF should NOT double-count initial capex
    # wait: year 1 capex includes initial_capex, and t=0 -equity would double count.
    # Standard: t=0 = -(initial capex + opening WC) = -initial_equity
    # Year 1 FCF = NOPAT + DA - *incremental* capex only (exclude initial)
    fcf[0] = fcf[0] + years_out[0]["capex"] - 0.0  # remove all y1 capex then...
    # Cleaner: t=0 = -initial_equity; Y1+ FCF uses capex AFTER t=0, i.e. exclude initial_capex from Y1
    y1_incr_capex = years_out[0]["capex"] - p.initial_capex
    tax_rate = 0.0 if p.tax_mode == "holiday" else 0.34
    nopat1 = years_out[0]["ebit"] * (1 - tax_rate) if years_out[0]["ebit"] > 0 else years_out[0]["ebit"]
    fcf[0] = nopat1 + years_out[0]["da"] - y1_incr_capex

    dcf_cfs = [-p.initial_equity] + fcf
    # Terminal value on Y5 FCF
    g = 0.03
    tv_10 = fcf[-1] * (1 + g) / (0.10 - g) if fcf[-1] > 0 else 0.0
    tv_18 = fcf[-1] * (1 + g) / (0.18 - g) if fcf[-1] > 0 else 0.0
    cfs_tv_10 = dcf_cfs[:-1] + [dcf_cfs[-1] + tv_10]
    cfs_tv_18 = dcf_cfs[:-1] + [dcf_cfs[-1] + tv_18]

    project_irr = irr_newton(dcf_cfs, guess=1.0)
    # Equity IRR: t=0 -equity; Y1-Y5 = CFO - capex - principal + debt draw = change in cash + distributions
    # If no distributions, equity value at Y5 = closing cash + net PPE - debt
    equity_cfs = [-p.initial_equity] + [0.0] * 4 + [bs[-1]["equity"]]
    # Better equity CF: free cash to equity each year = CFO - capex - principal + draws
    eq = [-p.initial_equity]
    for yrow in years_out:
        draw = debt_principal if (with_debt and yrow["year"] == 2) else 0.0
        fte = yrow["npat"] + yrow["da"] - yrow["capex"] - yrow["principal"] + draw
        eq.append(fte)
    equity_irr = irr_newton(eq, guess=1.0)

    # Cycle 1 break-even against that cycle's selling price (Peak if Peak-first)
    c1 = cycles[0]
    c1_var = c1["prod"] + c1["logistics"] + c1["lease"] + c1["insurance"] + c1["contingency"] + c1["mgmt"] + c1["da"]
    c1_price = p.price_peak if c1["season"] == "Peak" else p.price_reg
    be_price = c1_var / c1["baskets"] if c1["baskets"] else 0
    be_baskets = c1_var / c1_price if c1_price else 0
    mos = 1 - be_price / c1_price if c1_price else 0

    # Payback on initial equity using cumulative FCF
    cum = 0.0
    payback = None
    for t, cf in enumerate(dcf_cfs):
        cum += cf
        if cum >= 0 and t > 0:
            # interpolate
            prev = cum - cf
            frac = -prev / cf if cf else 0
            payback = (t - 1) + frac
            break

    min_dscr = None
    if with_debt:
        dscrs = [y["dscr"] for y in years_out if y["dscr"] is not None]
        min_dscr = min(dscrs) if dscrs else None

    return {
        "params": asdict(p),
        "cycles": cycles,
        "years": years_out,
        "balance_sheet": bs,
        "dcf": {
            "fcf_years": fcf,
            "cfs_no_tv": dcf_cfs,
            "npv_10_no_tv": npv(0.10, dcf_cfs),
            "npv_18_no_tv": npv(0.18, dcf_cfs),
            "npv_10_with_tv": npv(0.10, cfs_tv_10),
            "npv_18_with_tv": npv(0.18, cfs_tv_18),
            "tv_10": tv_10,
            "tv_18": tv_18,
            "project_irr": project_irr,
            "equity_irr_annual": equity_irr,
            "equity_cfs": eq,
            "payback_years": payback,
        },
        "break_even": {
            "c1_cash_cost": c1_var,
            "be_price": be_price,
            "be_baskets": be_baskets,
            "margin_of_safety": mos,
            "c1_baskets": c1["baskets"],
            "c1_price": c1_price,
        },
        "debt": {
            "enabled": with_debt,
            "principal": debt_principal if with_debt else 0,
            "min_dscr": min_dscr,
        },
    }


def line_items_table(p: CaseParams) -> list[dict]:
    rows = []
    for name, share in PROD_MIX.items():
        rows.append(
            {
                "item": name,
                "regular": p.prod_reg * share,
                "peak": p.prod_peak * share,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> None:
    results = {}
    for key, params in CASES.items():
        results[key] = run_case(params, with_debt=False)
        results[f"{key}_debt"] = run_case(params, with_debt=True)

    # Serialize (drop capex_notes objects that are fine in json)
    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(x) for x in obj]
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj

    (OUT / "model_results.json").write_text(json.dumps(clean(results), indent=2), encoding="utf-8")

    # CSVs for credit case (primary underwriting)
    cred = results["credit"]
    write_csv(
        OUT / "credit_cycle_pnl.csv",
        [
            {
                **{k: v for k, v in c.items() if k != "capex_notes"},
            }
            for c in cred["cycles"]
        ],
        [
            "id",
            "year",
            "season",
            "ha",
            "added",
            "tonnes",
            "baskets",
            "revenue",
            "prod",
            "logistics",
            "lease",
            "insurance",
            "contingency",
            "mgmt",
            "da",
            "ebit",
            "tax",
            "npat",
            "capex",
        ],
    )
    write_csv(
        OUT / "credit_annual.csv",
        cred["years"],
        [
            "year",
            "ha_end",
            "tonnes",
            "revenue",
            "ebitda",
            "ebit",
            "tax",
            "npat",
            "net_margin",
            "capex",
            "fcf",
            "closing_cash",
            "cum_buffer",
        ],
    )
    write_csv(
        OUT / "credit_debt_dscr.csv",
        results["credit_debt"]["years"],
        ["year", "ebitda", "interest", "fees", "principal", "debt_service", "dscr", "debt_ye"],
    )

    # Console summary for document authoring
    print("=" * 78)
    print("SNLB FARMS — MODEL SUMMARY")
    print("=" * 78)
    for key in ("promoter", "credit", "downside"):
        r = results[key]
        d = r["dcf"]
        print(f"\n### {r['params']['name']}")
        print(f"  Tax mode: {r['params']['tax_mode']}")
        for y in r["years"]:
            print(
                f"  Y{y['year']}: ha={y['ha_end']:>3}  rev={fmt(y['revenue'])}  "
                f"EBIT={fmt(y['ebit'])} ({pct(y['ebit_margin'])})  "
                f"NPAT={fmt(y['npat'])} ({pct(y['net_margin'])})  "
                f"FCF={fmt(y['fcf'])}  cash={fmt(y['closing_cash'])}  "
                f"gm={pct(y['gross_margin'])}  buf={fmt(y['cum_buffer']) if 'cum_buffer' in y else ''}"
            )
        print(
            f"  NPV 10% no TV {fmt(d['npv_10_no_tv'])} | with TV {fmt(d['npv_10_with_tv'])}"
        )
        print(
            f"  NPV 18% no TV {fmt(d['npv_18_no_tv'])} | with TV {fmt(d['npv_18_with_tv'])}"
        )
        print(f"  Project IRR {pct(d['project_irr']) if d['project_irr']==d['project_irr'] else 'n/a'}")
        print(f"  Equity IRR  {pct(d['equity_irr_annual']) if d['equity_irr_annual']==d['equity_irr_annual'] else 'n/a'}")
        print(f"  Payback {d['payback_years']:.2f} years" if d["payback_years"] else "  Payback n/a")
        be = r["break_even"]
        print(
            f"  C1 BE price ₦{be['be_price']:,.0f} vs ₦{be['c1_price']:,.0f} "
            f"(MoS {pct(be['margin_of_safety'])})  cash cost ₦{be['c1_cash_cost']:,.0f}"
        )
        rd = results[f"{key}_debt"]
        print(f"  Optional ₦80m facility min DSCR: {rd['debt']['min_dscr']:.2f}x" if rd["debt"]["min_dscr"] else "")
        if key == "credit":
            print("  Annual detail:")
            for y in r["years"]:
                print(
                    f"    Y{y['year']} capex={fmt(y['capex'])} ebitda={fmt(y['ebitda'])} "
                    f"tax={fmt(y['tax'])} fcf={fmt(y['fcf'])}"
                )

    print("\nCycle detail — PLANNING case")
    for c in cred["cycles"]:
        print(
            f"  {c['id']} {c['season']:8} {c['ha']:3}ha  rev={fmt(c['revenue'])}  "
            f"EBIT={fmt(c['ebit'])}  NPAT={fmt(c.get('npat', 0))}  capex={fmt(c['capex'])}"
        )

    print("\nWrote", OUT)


if __name__ == "__main__":
    main()
