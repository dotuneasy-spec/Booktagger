#!/usr/bin/env python3
"""Site-partnership screen. Machine costs are the v5 high and low bands."""

from __future__ import annotations

import json
import sys
from pathlib import Path

V5 = Path(__file__).resolve().parents[2] / "cashease-v5-multiservice" / "model"
sys.path.insert(0, str(V5))
from multiservice_model import DAYS, DISCOUNT, LIFE, SURCHARGE, npv, irr, payback  # noqa: E402

# Brief's human change point. The fee and the split are the brief, not a surveyed tariff.
FEE_LOW = 150_000
FEE_HIGH = 300_000
CHANGE_FEE = 100  # assumption carried from the machine studies; not a statute
ATTENDANT = 0.70
CASHEASE = 0.20
HOST = 0.10
VOLUMES = (60, 120, 200)

# Published counts used only as site stocks, not as sites that clear.
MEMAN = {
    "South West": {"stations": 1392, "lead": "Lagos 722"},
    "South East": {"stations": 173, "lead": "Enugu 53"},
    "South South": {"stations": 458, "lead": "Rivers 141"},
    "North Central": {"stations": 529, "lead": "Abuja 200"},
    "North West": {"stations": 467, "lead": "Kano 140"},
    "North East": {"stations": 274, "lead": "Adamawa 78"},
}
ATM_TX_H1 = 858.80e6
ATM_VALUE_H1 = 36.34e12
ATM_STOCK = 16_714
HALF_DAYS = 181
MALL_MONTH = 800_000  # Actis, "up to", Ikeja, stated while Actis still described the asset
MALL_DAYS = 30  # assumption: the month is 30 days


def human(wd: int) -> dict:
    gross = wd * DAYS * CHANGE_FEE
    ce = CASHEASE * gross
    attendant = ATTENDANT * gross
    host = HOST * gross
    # CashEase puts up no machine. The franchise fee is inflow at t0.
    flows_low = [FEE_LOW] + [ce] * LIFE
    flows_high = [FEE_HIGH] + [ce] * LIFE
    return {
        "wd": wd,
        "gross": gross,
        "cashease": ce,
        "attendant": attendant,
        "host": host,
        "npv_if_fee_150": npv(DISCOUNT, flows_low),
        "npv_if_fee_300": npv(DISCOUNT, flows_high),
    }


def machine_row(unit: dict, split: str, wd: int) -> dict:
    r = unit["splits"][split][str(wd)]
    return {
        "revenue": r["revenue"],
        "cash": r["cash"],
        "operating": r["operating"],
        "npv": r["npv"],
        "irr": r["irr"],
        "payback": r["payback"],
    }


def fleet(unit: dict, n: int, wd: int, share: float) -> dict:
    box = unit["box"]
    street = unit["costs"]["street"]
    all_in = box["all_in_ngn"]
    nxt = box["machine_ngn"]
    capex = all_in + (n - 1) * nxt
    year0 = capex + 40_000_000 + 150_000 * n
    annual = n * (wd * DAYS * SURCHARGE * share - street) - (25_000_000 + 50_000 * n)
    flows = [-year0] + [annual] * LIFE
    return {
        "n": n,
        "wd": wd,
        "year0": year0,
        "capex": capex,
        "annual": annual,
        "npv": npv(DISCOUNT, flows),
        "irr": irr(flows),
        "payback": payback(flows),
    }


def main() -> dict:
    v5 = json.loads((V5 / "outputs" / "results.json").read_text())
    hi = v5["units"]["recycler_high"]
    lo = v5["units"]["recycler_low"]
    kh = v5["units"]["kiosk_high"]
    daily_atm = ATM_TX_H1 / HALF_DAYS
    per_atm = daily_atm / ATM_STOCK
    ticket = ATM_VALUE_H1 / ATM_TX_H1
    mall_day = MALL_MONTH / MALL_DAYS
    be = {}
    for label in ("100/0", "70/30", "50/50"):
        be[label] = {
            "cash": hi["splits"][label]["be_cash"],
            "full": hi["splits"][label]["be_full"],
            "low_full": lo["splits"][label]["be_full"],
            "share_of_avg_atm_full": hi["splits"][label]["be_full"] / per_atm,
            "mall_visitors_per_withdrawal_full": mall_day / hi["splits"][label]["be_full"],
            "mall_conversion_full": hi["splits"][label]["be_full"] / mall_day,
        }
    machines = {}
    for split in ("100/0", "70/30", "50/50"):
        machines[split] = {str(wd): machine_row(hi, split, wd) for wd in VOLUMES}
    low70 = {str(wd): machine_row(lo, "70/30", wd) for wd in VOLUMES}
    humans = {str(wd): human(wd) for wd in VOLUMES}
    test = {str(wd): fleet(hi, 12, wd, 0.70) for wd in VOLUMES}
    out = {
        "days": DAYS,
        "surcharge": SURCHARGE,
        "high_all_in": hi["box"]["all_in_ngn"],
        "low_all_in": lo["box"]["all_in_ngn"],
        "high_street": hi["costs"]["street"],
        "high_full": hi["costs"]["full"],
        "low_street": lo["costs"]["street"],
        "kiosk_high_all_in": kh["box"]["all_in_ngn"],
        "kiosk_street": kh["costs"]["street"],
        "kiosk_revenue": kh["kiosk_only"]["revenue"],
        "kiosk_cash": kh["kiosk_only"]["cash"],
        "per_atm_withdrawals": per_atm,
        "daily_national": daily_atm,
        "avg_ticket": ticket,
        "mall_visitors_day": mall_day,
        "be": be,
        "machines": machines,
        "low70": low70,
        "humans": humans,
        "test_fleet_12": test,
        "meman_total": sum(z["stations"] for z in MEMAN.values()),
        "meman": MEMAN,
        "chains_top10": 124 + 44 + 36 + 31 + 26 + 22 + 14 + 13 + 9 + 8,
    }
    dest = Path(__file__).resolve().parent / "outputs" / "results.json"
    dest.parent.mkdir(parents=True, exist_ok=True)

    def conv(o):
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, float):
            return round(o, 6) if abs(o) < 10 else round(o, 2)
        return o

    dest.write_text(json.dumps(conv(out), indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    r = main()
    print("per atm", round(r["per_atm_withdrawals"], 1), "ticket", round(r["avg_ticket"]))
    print("mall/day", round(r["mall_visitors_day"]), "conv", r["be"]["70/30"]["mall_conversion_full"])
    print("share of avg", r["be"]["70/30"]["share_of_avg_atm_full"])
    print("human 120", round(r["humans"]["120"]["cashease"]), round(r["humans"]["120"]["attendant"]))
    print("fleet 120", round(r["test_fleet_12"]["120"]["npv"]), r["test_fleet_12"]["120"]["irr"])
