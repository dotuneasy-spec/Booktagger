#!/usr/bin/env python3
"""Path to ₦50 billion if the machine is the published Hongzhou price.

Uses the v5 landing sheet (freight, duty, VAT, SON, install, NIBSS).
The US$3,650 listing floor is not treated as a factory invoice.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

V5 = Path(__file__).resolve().parents[2] / "cashease-v5-multiservice" / "model"
sys.path.insert(0, str(V5))
from multiservice_model import (  # noqa: E402
    CLEAR_HIGH,
    CONN,
    DAYS,
    DISCOUNT,
    HQ,
    HQ0,
    HQ0_PER,
    HQ_PER,
    INSTALL_R,
    INS,
    LIFE,
    MAINT,
    NIBSS_ONCE,
    OCEAN_HIGH,
    OCEAN_LOW,
    POWER_R,
    RENT_R,
    SEC_R,
    SOFTWARE_R,
    SURCHARGE,
    THC_HIGH,
    THC_LOW,
    CLEAR_LOW,
    irr,
    landed,
    npv,
    payback,
)

TARGET = 50_000_000_000
ATM_TX_H1 = 858.80e6
HALF_DAYS = 181
WORKS = INSTALL_R + SOFTWARE_R
CUSTOM = 1_800


def street_of(box: dict) -> float:
    return (
        RENT_R
        + POWER_R
        + SEC_R
        + CONN
        + MAINT * box["exworks_ngn"]
        + INS * box["all_in_ngn"]
    )


def full_of(box: dict, street: float) -> float:
    return street + box["all_in_ngn"] / LIFE


def be(cost: float, share: float, blocks: int = 1) -> float:
    return cost / (DAYS * SURCHARGE * blocks * share)


def flows_for(box, street, n, wd, share, blocks=1):
    income = wd * DAYS * SURCHARGE * blocks * share
    capex = box["all_in_ngn"] + (n - 1) * box["machine_ngn"]
    year0 = capex + HQ0 + HQ0_PER * n
    annual = n * (income - street) - (HQ + HQ_PER * n)
    return year0, annual, [-year0] + [annual] * LIFE


def pack(box, street, n, wd, share, blocks=1):
    year0, annual, flows = flows_for(box, street, n, wd, share, blocks)
    national = ATM_TX_H1 / HALF_DAYS
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
        "share_of_national": (n * wd) / national,
    }


def smallest(box, street, wd, share, blocks=1):
    lo, hi, hit = 1, 40_000, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if pack(box, street, mid, wd, share, blocks)["npv"] >= TARGET:
            hit = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return hit


def unit_row(box, street, wd, share):
    income = wd * DAYS * SURCHARGE * share
    cash = income - street
    full = full_of(box, street)
    flows = [-box["all_in_ngn"]] + [cash] * LIFE
    return {
        "revenue": income,
        "cash": cash,
        "npv": npv(DISCOUNT, flows),
        "irr": irr(flows),
        "payback": payback(flows),
        "full_cost": full,
    }


def reinvest(box, street, n0, wd, share):
    n = n0
    unit = box["machine_ngn"] + HQ0_PER
    year0, _, _ = flows_for(box, street, n, wd, share)
    cfs = [-year0]
    rows = []
    for year in range(1, LIFE + 1):
        _, annual, _ = flows_for(box, street, n, wd, share)
        buy = int(annual // unit) if annual > 0 else 0
        spend = buy * unit
        cfs.append(annual - spend)
        rows.append({"year": year, "open": n, "cash": annual, "bought": buy, "close": n + buy})
        n += buy
    return {"rows": rows, "npv": npv(DISCOUNT, cfs), "end": n, "year0": year0}


def main() -> dict:
    boxes = {
        "hz4800_plain": landed(4_800, OCEAN_HIGH, THC_HIGH, CLEAR_HIGH, WORKS, 0),
        "hz4800_custom": landed(4_800, OCEAN_HIGH, THC_HIGH, CLEAR_HIGH, WORKS, CUSTOM),
        "hz4800_plain_lowfreight": landed(4_800, OCEAN_LOW, THC_LOW, CLEAR_LOW, WORKS, 0),
        "hz5500_custom": landed(5_500, OCEAN_HIGH, THC_HIGH, CLEAR_HIGH, WORKS, CUSTOM),
        "high_band": landed(7_850, OCEAN_HIGH, THC_HIGH, CLEAR_HIGH, WORKS, CUSTOM),
    }
    streets = {k: street_of(v) for k, v in boxes.items()}
    work = boxes["hz4800_custom"]
    work_street = streets["hz4800_custom"]
    plain = boxes["hz4800_plain"]
    plain_street = streets["hz4800_plain"]

    def band(box, street):
        out = {"be": {}, "units": {}}
        for label, share in (("100/0", 1.0), ("70/30", 0.70), ("50/50", 0.50)):
            out["be"][label] = {
                "cash": be(street, share),
                "full": be(full_of(box, street), share),
            }
            out["units"][label] = {str(wd): unit_row(box, street, wd, share) for wd in (60, 120, 200)}
        return out

    specs = [
        ("custom_100_200", work, work_street, 200, 1.0),
        ("custom_100_120", work, work_street, 120, 1.0),
        ("custom_70_200", work, work_street, 200, 0.70),
        ("custom_70_120", work, work_street, 120, 0.70),
        ("custom_50_200", work, work_street, 200, 0.50),
        ("plain_100_200", plain, plain_street, 200, 1.0),
        ("plain_100_120", plain, plain_street, 120, 1.0),
        ("plain_70_200", plain, plain_street, 200, 0.70),
        ("plain_70_120", plain, plain_street, 120, 0.70),
        ("high_100_200", boxes["high_band"], streets["high_band"], 200, 1.0),
        ("high_100_120", boxes["high_band"], streets["high_band"], 120, 1.0),
    ]
    cases = {}
    for name, box, street, wd, share in specs:
        n = smallest(box, street, wd, share)
        cases[name] = {"machines": n, "fleet": None if n is None else pack(box, street, n, wd, share)}

    # Recommended opening fleet is the China custom case at 200/day, keep all,
    # if that fleet exists. Tranches use that count.
    rec_n = cases["custom_100_200"]["machines"]
    tranches = [pack(work, work_street, n, 200, 1.0) for n in (12, 100, 500, rec_n)]
    proof_120 = pack(work, work_street, 12, 120, 1.0)
    proof_70 = pack(work, work_street, 12, 200, 0.70)
    sweep = reinvest(work, work_street, 12, 200, 1.0)

    out = {
        "nibss_once": NIBSS_ONCE,
        "boxes": boxes,
        "streets": streets,
        "fulls": {k: full_of(boxes[k], streets[k]) for k in boxes},
        "custom": band(work, work_street),
        "plain": band(plain, plain_street),
        "cases": cases,
        "tranches": tranches,
        "proof_120": proof_120,
        "proof_70_200": proof_70,
        "reinvest": sweep,
        "daily_national": ATM_TX_H1 / HALF_DAYS,
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
    for key in ("hz4800_plain", "hz4800_custom", "hz5500_custom", "high_band"):
        print(key, "all-in", round(r["boxes"][key]["all_in_ngn"]), "street", round(r["streets"][key]), "full", round(r["fulls"][key]))
    print("BE custom 70/30", round(r["custom"]["be"]["70/30"]["cash"], 1), round(r["custom"]["be"]["70/30"]["full"], 1))
    print("BE custom 100/0", round(r["custom"]["be"]["100/0"]["cash"], 1), round(r["custom"]["be"]["100/0"]["full"], 1))
    print("BE plain 70/30", round(r["plain"]["be"]["70/30"]["cash"], 1), round(r["plain"]["be"]["70/30"]["full"], 1))
    for name, row in r["cases"].items():
        fleet = row["fleet"]
        if fleet is None:
            print(name, "NO")
        else:
            print(name, "n", row["machines"], "y0", round(fleet["year0"] / 1e9, 2), "ann", round(fleet["annual"] / 1e9, 2), "share", round(100 * fleet["share_of_national"], 2), "irr", round(100 * fleet["irr"], 1))
    print("proof12-200", round(r["tranches"][0]["npv"]), round(100 * r["tranches"][0]["irr"], 1))
    print("reinvest", r["reinvest"]["end"], round(r["reinvest"]["npv"]))
