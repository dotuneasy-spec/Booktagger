#!/usr/bin/env python3
"""Path to a ₦50 billion present value. Machine costs are the v5 bands.

₦50 billion is the brief's value target. It is not a sale price and not revenue.
Every fee that is not in v5 is tagged as an assumption in the study.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

V5 = Path(__file__).resolve().parents[2] / "cashease-v5-multiservice" / "model"
sys.path.insert(0, str(V5))
from multiservice_model import (  # noqa: E402
    DAYS,
    DISCOUNT,
    HQ,
    HQ0,
    HQ0_PER,
    HQ_PER,
    LIFE,
    SURCHARGE,
    irr,
    npv,
    payback,
)

TARGET = 50_000_000_000
ATM_STOCK = 16_714
CARDS_PER_ATM = 7_500
ATM_TX_H1 = 858.80e6
HALF_DAYS = 181
# Attendant terms are the brief, not a surveyed tariff.
CHANGE_FEE = 100
ATTENDANT = 0.70
CE_SHARE = 0.20
FEE_HIGH = 300_000
# Pad strategy. Both amounts are assumptions: the cost of papering a site,
# and the annual cost of watching it, when CashEase does not own a machine.
PAPER = 50_000
WATCH = 20_000


def flows_for(box: dict, street: float, n: int, wd: int, share: float, blocks: int) -> tuple[float, float, list[float]]:
    income = wd * DAYS * SURCHARGE * blocks * share
    capex = box["all_in_ngn"] + (n - 1) * box["machine_ngn"]
    year0 = capex + HQ0 + HQ0_PER * n
    annual = n * (income - street) - (HQ + HQ_PER * n)
    return year0, annual, [-year0] + [annual] * LIFE


def pack(box: dict, street: float, n: int, wd: int, share: float, blocks: int) -> dict:
    year0, annual, flows = flows_for(box, street, n, wd, share, blocks)
    national = ATM_TX_H1 / HALF_DAYS
    # Blocks raise the fee on one withdrawal. They are not extra visits.
    visits = n * wd
    return {
        "n": n,
        "wd": wd,
        "share": share,
        "blocks": blocks,
        "year0": year0,
        "annual": annual,
        "npv": npv(DISCOUNT, flows),
        "irr": irr(flows),
        "payback": payback(flows),
        "daily_paying": visits,
        "share_of_national": visits / national,
    }


def smallest(box: dict, street: float, wd: int, share: float, blocks: int = 1) -> int | None:
    lo, hi = 1, 40_000
    hit = None
    while lo <= hi:
        mid = (lo + hi) // 2
        row = pack(box, street, mid, wd, share, blocks)
        if row["npv"] >= TARGET:
            hit = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return hit


def reinvest(box: dict, street: float, n0: int, wd: int, share: float, blocks: int = 1) -> dict:
    """Cash profit buys the next machine. No new equity and no dividend.

    The clock is the same seven years as the rest of the model. A machine
    bought in year 6 does not get a fresh seven-year life.
    """
    n = n0
    unit = box["machine_ngn"] + HQ0_PER
    year0, _, _ = flows_for(box, street, n, wd, share, blocks)
    cfs = [-year0]
    rows = []
    for year in range(1, LIFE + 1):
        _, annual, _ = flows_for(box, street, n, wd, share, blocks)
        buy = int(annual // unit) if annual > 0 else 0
        spend = buy * unit
        cfs.append(annual - spend)
        rows.append({
            "year": year,
            "open": n,
            "cash": annual,
            "bought": buy,
            "spend": spend,
            "close": n + buy,
        })
        n += buy
    return {"rows": rows, "npv": npv(DISCOUNT, cfs), "end": n, "year0": year0}


def lease_flows(n: int, fee: float) -> list[float]:
    year0 = HQ0 + PAPER * n
    annual = n * fee - (HQ + WATCH * n)
    return [-year0] + [annual] * LIFE


def fee_for(n: int) -> float | None:
    lo, hi = 0.0, 50_000_000.0
    if npv(DISCOUNT, lease_flows(n, hi)) < TARGET:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        if npv(DISCOUNT, lease_flows(n, mid)) >= TARGET:
            hi = mid
        else:
            lo = mid
    return hi


def booth_flows(n: int, wd: int, fee: float) -> list[float]:
    ce = CE_SHARE * wd * DAYS * CHANGE_FEE
    # The franchise fee is cash in. The office is cash out.
    t0 = fee * n - HQ0
    annual = n * ce - HQ
    return [t0] + [annual] * LIFE


def booths_for(wd: int, fee: float) -> int | None:
    lo, hi = 1, 200_000
    hit = None
    while lo <= hi:
        mid = (lo + hi) // 2
        if npv(DISCOUNT, booth_flows(mid, wd, fee)) >= TARGET:
            hit = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return hit


def main() -> dict:
    v5 = json.loads((V5 / "outputs" / "results.json").read_text())
    high = v5["boxes"]["recycler_high"]
    low = v5["boxes"]["recycler_low"]
    street_h = v5["units"]["recycler_high"]["costs"]["street"]
    street_l = v5["units"]["recycler_low"]["costs"]["street"]
    specs = [
        ("high_100_200", high, street_h, 200, 1.0, 1),
        ("high_100_120", high, street_h, 120, 1.0, 1),
        ("high_70_200", high, street_h, 200, 0.70, 1),
        ("high_70_120", high, street_h, 120, 0.70, 1),
        ("high_50_200", high, street_h, 200, 0.50, 1),
        ("low_100_200", low, street_l, 200, 1.0, 1),
        ("low_100_120", low, street_l, 120, 1.0, 1),
        ("low_70_120", low, street_l, 120, 0.70, 1),
        ("high_100_120_two_blocks", high, street_h, 120, 1.0, 2),
    ]
    cases = {}
    for name, box, street, wd, share, blocks in specs:
        n = smallest(box, street, wd, share, blocks)
        cases[name] = {
            "machines": n,
            "fleet": None if n is None else pack(box, street, n, wd, share, blocks),
        }
    # Tranches on the recommended case: 100% of one block, 200 a day, high band.
    rec_n = cases["high_100_200"]["machines"]
    tranches = []
    for n in (12, 100, 500, rec_n):
        tranches.append(pack(high, street_h, n, 200, 1.0, 1))
    sweep = reinvest(high, street_h, 12, 200, 1.0, 1)
    sweep_120 = reinvest(high, street_h, 12, 120, 1.0, 1)
    lease_ns = [100, 500, 1_000, 3_293, 5_000, 10_000]
    leases = []
    for n in lease_ns:
        fee = fee_for(n)
        row = {"n": n, "fee": fee}
        if fee is not None:
            f = lease_flows(n, fee)
            row["year0"] = -f[0]
            row["annual"] = f[1]
            row["npv"] = npv(DISCOUNT, f)
        leases.append(row)
    # What ₦1.8m a year, the v5 rent assumption paid the other way, is worth.
    rent_flip = []
    for n in (100, 500, 1_392, 3_293, 10_000):
        f = lease_flows(n, 1_800_000)
        rent_flip.append({"n": n, "fee": 1_800_000, "year0": -f[0], "annual": f[1], "npv": npv(DISCOUNT, f)})
    booth = {}
    for wd in (60, 120, 200):
        n = booths_for(wd, FEE_HIGH)
        booth[str(wd)] = {
            "n": n,
            "fee": FEE_HIGH,
            "fleet": None if n is None else {
                "npv": npv(DISCOUNT, booth_flows(n, wd, FEE_HIGH)),
                "annual": booth_flows(n, wd, FEE_HIGH)[1],
                "t0": booth_flows(n, wd, FEE_HIGH)[0],
            },
        }
    # Counted pitches, not a national park census.
    for label, n in (("lagos_registered_30", 30), ("lagos_2017_145", 145)):
        f = booth_flows(n, 120, FEE_HIGH)
        booth[label] = {"n": n, "npv": npv(DISCOUNT, f), "annual": f[1], "t0": f[0]}
    factor = (1 - (1 + DISCOUNT) ** (-LIFE)) / DISCOUNT
    out = {
        "target": TARGET,
        "factor": factor,
        "annual_cash_for_50bn": TARGET / factor,
        "perpetual_cash": TARGET * DISCOUNT,
        "cards_already_covered": ATM_STOCK * CARDS_PER_ATM,
        "daily_national": ATM_TX_H1 / HALF_DAYS,
        "high_all_in": high["all_in_ngn"],
        "low_all_in": low["all_in_ngn"],
        "high_street": street_h,
        "low_street": street_l,
        "cases": cases,
        "tranches": tranches,
        "proof_120": pack(high, street_h, 12, 120, 1.0, 1),
        "proof_70_200": pack(high, street_h, 12, 200, 0.70, 1),
        "reinvest_200": sweep,
        "reinvest_120": sweep_120,
        "leases": leases,
        "rent_flip": rent_flip,
        "booths": booth,
    }
    dest = Path(__file__).resolve().parent / "outputs" / "results.json"
    dest.parent.mkdir(parents=True, exist_ok=True)

    def conv(o):
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, list):
            return [conv(v) for v in o]
        if isinstance(o, float):
            return round(o, 6) if abs(o) < 10 else round(o, 2)
        return o

    dest.write_text(json.dumps(conv(out), indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    r = main()
    for name, row in r["cases"].items():
        fleet = row["fleet"]
        if fleet is None:
            print(name, "does not reach")
        else:
            print(name, "n", row["machines"], "year0", round(fleet["year0"] / 1e9, 2), "annual", round(fleet["annual"] / 1e9, 2), "share", round(fleet["share_of_national"] * 100, 2), "irr", fleet["irr"])
    print("reinvest 200", r["reinvest_200"]["end"], "npv", round(r["reinvest_200"]["npv"]))
    print("reinvest 120", r["reinvest_120"]["end"], "npv", round(r["reinvest_120"]["npv"]))
    for row in r["leases"]:
        print("lease", row["n"], "fee", None if row["fee"] is None else round(row["fee"]))
    print("booths", {k: r["booths"][k]["n"] for k in ("60", "120", "200")})
