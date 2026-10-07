"""CashEase v4.1 — China-built kiosk scenario.

Does not modify the v4 model. Reuses the v4 fee mix, uptime, street costs and
FX rate. FOB prices are the listings named in LISTINGS. Freight per machine
uses a labeled packing assumption. Duty is a third-party representative rate
for the HS code a manufacturer prints, not a Nigeria Customs ruling.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"

FX = 1331.69
MPR = 0.23
DISCOUNT = 0.28
DAYS = 300 * 0.90  # 270
LIFE = 7
HORIZON = 7

# v4 fee mix. Off-site public site, so the surcharge assumption can apply.
GROSS = 0.55 * 100 + 0.35 * 250 + 0.10 * 30  # 145.50
SHRINK = 0.35 * 12_000 * 0.003  # 12.60
POOL = GROSS - SHRINK  # 132.90
CE_PER_TX = 0.60 * POOL  # 79.74

POWER = 336 * 1810 + 80_000  # 688,160
CONN = 18_000 * 12
SECURITY = 120_000 * 12
CIT_FULL = 40_000 * 4 * 12  # v4 assumption, used only in the half-subsidy case
STREET = POWER + CONN + SECURITY  # rent and CIT removed in this scenario

INSTALL = 6_000_000  # v4 assumption, not a Chinese-kiosk quote
SOFTWARE = 2_000_000
MAINT_RATE = 0.10
INS_RATE = 0.015

# Packing and border charges. The divisor is a choice. The rates are sourced.
PER_CONTAINER = 10
OCEAN_LOW = 2_970  # Shenzhen–Lagos 20ft, low of the published band
OCEAN_HIGH = 3_450
THC_LOW = 250_000  # forwarder range, per container
THC_HIGH = 450_000
CLEAR_LOW = 150_000
CLEAR_HIGH = 350_000
DUTY_RATE = 0.05  # representative 8471.60 rate; not an NCS ruling
VAT_RATE = 0.075
SON_USD = 500 + 350  # PC1 + one SONCAP certificate, per consignment

V4_ALL_IN = 40_000 * FX * 1.08 + INSTALL + SOFTWARE  # 65,529,008 before duty
LISTED_SITES = 774 + 2048 + 30 + 10 + 13 + 12  # 2,887
HQ_ANNUAL = 25_000_000

LISTINGS = [
    {
        "id": "hz4800",
        "name": "Hongzhou cash in/out kiosk, 10+ price",
        "fob": 4_800,
        "role": "Whole kiosk on a manufacturer page",
    },
    {
        "id": "hz5500",
        "name": "Hongzhou cash in/out kiosk, 1–9 price",
        "fob": 5_500,
        "role": "Whole kiosk on a manufacturer page",
    },
    {
        "id": "reseller6",
        "name": "Reseller listing, GRG H68N, bottom of range",
        "fob": 6_000,
        "role": "Reseller, not the GRG factory",
    },
    {
        "id": "ccs9",
        "name": "GRGintech CCS-30 recycler, low FOB",
        "fob": 9_000,
        "role": "Manufacturer showroom, banknote and coin recycler",
    },
    {
        "id": "ccs10",
        "name": "GRGintech CCS-30 recycler, high FOB",
        "fob": 10_000,
        "role": "Manufacturer showroom, banknote and coin recycler",
    },
    {
        "id": "reseller11",
        "name": "Reseller listing, GRG H68N, top of range",
        "fob": 11_000,
        "role": "Reseller, not the GRG factory",
    },
]


def naira(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000:
        return f"{sign}₦{n / 1_000_000_000:.2f} billion"
    if n >= 1_000_000:
        return f"{sign}₦{n / 1_000_000:.2f} million"
    return f"{sign}₦{n:,.0f}"


def npv(rate: float, flows: list[float]) -> float:
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(flows))


def irr(flows: list[float]) -> float | None:
    low, high = -0.99, 5.0
    f_low, f_high = npv(low, flows), npv(high, flows)
    if f_low * f_high > 0:
        return None
    for _ in range(80):
        mid = (low + high) / 2
        f_mid = npv(mid, flows)
        if abs(f_mid) < 1.0:
            return mid
        if f_low * f_mid <= 0:
            high, f_high = mid, f_mid
        else:
            low, f_low = mid, f_mid
    return (low + high) / 2


def payback(flows: list[float]) -> float | None:
    cum = 0.0
    for t, cf in enumerate(flows):
        prev = cum
        cum += cf
        if t and prev < 0 <= cum:
            return (t - 1) + (-prev / cf if cf else 0)
    return None


def landed(fob: float, ocean: float, thc: float, clearing: float, with_site_works: bool) -> dict:
    freight_usd = ocean / PER_CONTAINER
    cif = fob + freight_usd
    duty = DUTY_RATE * cif
    vat = VAT_RATE * (cif + duty)
    son_usd = SON_USD / PER_CONTAINER
    border_usd = cif + duty + vat + son_usd
    border_ngn = border_usd * FX + (thc + clearing) / PER_CONTAINER
    works = (INSTALL + SOFTWARE) if with_site_works else 0.0
    all_in = border_ngn + works
    return {
        "fob_usd": fob,
        "freight_usd": freight_usd,
        "cif_usd": cif,
        "duty_usd": duty,
        "vat_usd": vat,
        "son_usd": son_usd,
        "border_ngn": border_ngn,
        "works_ngn": works,
        "all_in_ngn": all_in,
        "exworks_ngn": fob * FX,
    }


def unit(all_in: float, exworks: float, tx: float, cit: float) -> dict:
    annual_tx = tx * DAYS
    revenue = annual_tx * CE_PER_TX
    maint = MAINT_RATE * exworks
    ins = INS_RATE * all_in
    dep = all_in / LIFE
    cash_cost = STREET + maint + ins + cit
    full_cost = cash_cost + dep
    cash_profit = revenue - cash_cost
    operating = revenue - full_cost
    flows = [-all_in] + [cash_profit] * HORIZON
    return {
        "annual_tx": annual_tx,
        "revenue": revenue,
        "maint": maint,
        "insurance": ins,
        "depreciation": dep,
        "cash_cost": cash_cost,
        "full_cost": full_cost,
        "cash_profit": cash_profit,
        "operating": operating,
        "npv_28": npv(DISCOUNT, flows),
        "npv_mpr": npv(MPR, flows),
        "irr": irr(flows),
        "payback": payback(flows),
    }


def be(annual_cost: float) -> float | None:
    if CE_PER_TX <= 0:
        return None
    return (annual_cost / CE_PER_TX) / DAYS


def rollout(all_in: float, cash_profit: float, hq: float, start: int = 1) -> dict:
    """Buy the next machine only with retained cash. Equity only. No debt."""
    fleet = start
    pot = 0.0
    path = [start]
    for _ in range(HORIZON):
        pot += fleet * cash_profit - hq
        bought = 0
        if pot >= all_in:
            bought = int(pot // all_in)
            room = max(0, LISTED_SITES - fleet)
            bought = min(bought, room)
            pot -= bought * all_in
            fleet += bought
        path.append(fleet)
    return {"path": path, "end": fleet, "retained": pot}


def main() -> dict:
    rows = []
    for item in LISTINGS:
        low = landed(item["fob"], OCEAN_LOW, THC_LOW, CLEAR_LOW, True)
        high = landed(item["fob"], OCEAN_HIGH, THC_HIGH, CLEAR_HIGH, True)
        bare = landed(item["fob"], OCEAN_HIGH, THC_HIGH, CLEAR_HIGH, False)
        cases = {}
        for label, pack in (("low", low), ("high", high), ("bare", bare)):
            ex = pack["exworks_ngn"]
            ain = pack["all_in_ngn"]
            maint = MAINT_RATE * ex
            ins = INS_RATE * ain
            dep = ain / LIFE
            cash_cost = STREET + maint + ins
            full_cost = cash_cost + dep
            at = {str(tx): unit(ain, ex, tx, 0.0) for tx in (150, 250, 400)}
            at_half = {str(tx): unit(ain, ex, tx, CIT_FULL / 2) for tx in (150, 250, 400)}
            cases[label] = {
                "landed": pack,
                "be_cash": be(cash_cost),
                "be_full": be(full_cost),
                "be_cash_half_cit": be(cash_cost + CIT_FULL / 2),
                "be_full_half_cit": be(full_cost + CIT_FULL / 2),
                "at": at,
                "at_half_cit": at_half,
                "roll_400": rollout(ain, at["400"]["cash_profit"], 0.0),
                "roll_400_hq": rollout(ain, at["400"]["cash_profit"], HQ_ANNUAL),
                "roll_250": rollout(ain, at["250"]["cash_profit"], 0.0),
                "roll_250_hq": rollout(ain, at["250"]["cash_profit"], HQ_ANNUAL),
                "roll_150": rollout(ain, at["150"]["cash_profit"], 0.0),
            }
        rows.append({"id": item["id"], "name": item["name"], "role": item["role"], "fob": item["fob"], "cases": cases})

    # v4 US reference machine under the same supports, still before duty.
    us_ex = 40_000 * FX
    us_at = {str(tx): unit(V4_ALL_IN, us_ex, tx, 0.0) for tx in (150, 250, 400)}
    us_maint = MAINT_RATE * us_ex
    us_ins = INS_RATE * V4_ALL_IN
    us_dep = V4_ALL_IN / LIFE
    us = {
        "all_in": V4_ALL_IN,
        "be_cash": be(STREET + us_maint + us_ins),
        "be_full": be(STREET + us_maint + us_ins + us_dep),
        "at": us_at,
    }

    result = {
        "fx": FX,
        "ce_per_tx": CE_PER_TX,
        "pool": POOL,
        "street": STREET,
        "per_container_assumption": PER_CONTAINER,
        "duty_rate": DUTY_RATE,
        "vat_rate": VAT_RATE,
        "listed_sites": LISTED_SITES,
        "hq_annual": HQ_ANNUAL,
        "rows": rows,
        "us_reference": us,
        "not_used": [
            {"name": "GRGintech banknote dispenser module", "fob": 4900, "why": "A module, not a kiosk."},
            {"name": "Hyosung CDU-1100 dispenser part", "fob_low": 500, "fob_high": 1400, "why": "A spare part. No Hyosung China whole-machine FOB was found."},
            {"name": "Parts-channel GRG DT-7000 listing", "fob_low": 1500, "fob_high": 2500, "why": "The page also offers refurbished and generic stock and a 90-day warranty. Not used as a deployable kiosk price."},
            {"name": "Hongzhou currency-exchange kiosk", "fob_low": 2999, "fob_high": 3599, "why": "Coin dispenser and foreign-exchange kiosk, not the note-break machine."},
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "china_results.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    r = main()
    print("ce/tx", round(r["ce_per_tx"], 2), "sites", r["listed_sites"])
    print("US be cash/full", round(r["us_reference"]["be_cash"], 1), round(r["us_reference"]["be_full"], 1))
    for row in r["rows"]:
        h = row["cases"]["high"]
        print(
            f"{row['fob']:6} all-in {h['landed']['all_in_ngn']/1e6:.2f}m  "
            f"BE {h['be_cash']:.0f}/{h['be_full']:.0f}  "
            f"end400 {h['roll_400']['end']} hq {h['roll_400_hq']['end']}  "
            f"end250 {h['roll_250']['end']}"
        )
        for tx in ("150", "250", "400"):
            a = h["at"][tx]
            irr = None if a["irr"] is None else round(a["irr"] * 100, 1)
            print(
                f"   {tx}: cash {a['cash_profit']/1e6:.2f}m op {a['operating']/1e6:.2f}m "
                f"npv {a['npv_28']/1e6:.2f}m irr {irr} pb {a['payback']}"
            )
