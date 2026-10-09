#!/usr/bin/env python3
"""CashEase v5 bank-sponsored multi-service machine model.

External prices and fees are the figures named in SOURCES inside the study.
Every other naira amount is an assumption and is tagged as such in the JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

FX = 1331.6875  # CBN NFEM rate, 5 Oct 2026
INR_PER_USD = 96.6149  # FBIL reference on the RBI site, 9 Oct 2026, 1:00pm
DAYS = 270  # assumption: 300 open days × 90% uptime
LIFE = 7
DISCOUNT = 0.28  # assumption: policy rate 23% + 5 percentage points
MPR = 0.23
SURCHARGE = 500  # cap, one ₦20,000 block per counted withdrawal
NIBSS_ONCE = 500_000
PER_CONTAINER = 10  # assumption

OCEAN_LOW = 2_970
OCEAN_HIGH = 3_450
THC_LOW = 250_000
THC_HIGH = 450_000
CLEAR_LOW = 150_000
CLEAR_HIGH = 350_000
DUTY = 0.05  # representative 8471.60 rate, not an NCS ruling
VAT = 0.075
SON_USD = 850  # PC1 US$500 + SC US$350, per consignment
CUSTOM_HIGH = 1_800  # published adder; the listing does not say it is naira

INSTALL_R = 6_000_000  # assumption, carried from the machine study
SOFTWARE_R = 2_000_000
INSTALL_K = 2_000_000  # assumption: smaller indoor cash-in cabinet
SOFTWARE_K = 1_000_000

RENT_R = 1_800_000
POWER_R = 336 * 1_810 + 80_000  # 688,160; litres are an assumption
SEC_R = 1_440_000
RENT_K = 600_000  # assumption
POWER_K = 180_000  # assumption
SEC_K = 360_000  # assumption
CONN = 216_000
MAINT = 0.10
INS = 0.015
CIT = 40_000 * 4 * 12  # 1,920,000 assumption, only in the sensitivity

HQ = 25_000_000
HQ_PER = 50_000
HQ0 = 40_000_000
HQ0_PER = 150_000

# Labelled other-services stack. Counts and tickets are assumptions.
# Rates: VTpass terminal-agent MTN airtime 3%; Ikeja Electric "others" 1%.
AIRTIME_TX = 30
AIRTIME_TICKET = 1_000
AIRTIME_RATE = 0.03
BILL_TX = 10
BILL_TICKET = 5_000
BILL_RATE = 0.01
CHANGE_TX = 20  # recycler only
CHANGE_FEE = 100  # assumption; not the Coinstar percent

VOLUMES = (60, 120, 200)
SPLITS = (("100/0", 1.0), ("70/30", 0.70), ("50/50", 0.50))
FLEETS = (20, 300, 2_000, 10_000)


def npv(rate: float, flows: list[float]) -> float:
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(flows))


def irr(flows: list[float]) -> float | None:
    if all(cf <= 0 for cf in flows) or all(cf >= 0 for cf in flows):
        return None
    lo, hi = -0.99, 5.0
    if npv(lo, flows) < 0:
        return None
    if npv(hi, flows) > 0:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if npv(mid, flows) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def payback(flows: list[float]) -> float | None:
    cum = 0.0
    for t, cf in enumerate(flows):
        prev = cum
        cum += cf
        if t and prev < 0 <= cum and cf:
            return (t - 1) + (-prev / cf)
    return None


def landed(fob_usd: float, ocean: float, thc: float, clearing: float, works: float, custom: float) -> dict:
    freight = ocean / PER_CONTAINER
    goods = fob_usd + custom
    cif = goods + freight
    duty = DUTY * cif
    vat = VAT * (cif + duty)
    son = SON_USD / PER_CONTAINER
    border_usd = cif + duty + vat + son
    border_ngn = border_usd * FX + (thc + clearing) / PER_CONTAINER
    machine = border_ngn + works
    return {
        "fob_usd": fob_usd,
        "custom_usd": custom,
        "freight_usd": freight,
        "goods_usd": goods,
        "cif_usd": cif,
        "duty_usd": duty,
        "vat_usd": vat,
        "son_usd": son,
        "border_ngn": border_ngn,
        "works_ngn": works,
        "machine_ngn": machine,
        "all_in_ngn": machine + NIBSS_ONCE,
        "exworks_ngn": goods * FX,
    }


def annuity(principal: float, rate: float, years: int) -> float:
    if principal <= 0:
        return 0.0
    return principal * rate * (1 + rate) ** years / ((1 + rate) ** years - 1)


def stack(change: bool, scale: float = 1.0) -> dict:
    air = AIRTIME_TX * AIRTIME_TICKET * AIRTIME_RATE * DAYS * scale
    bills = BILL_TX * BILL_TICKET * BILL_RATE * DAYS * scale
    change_n = (CHANGE_TX * CHANGE_FEE * DAYS * scale) if change else 0.0
    return {
        "airtime": air,
        "bills": bills,
        "change": change_n,
        "transfers": 0.0,
        "ads": 0.0,
        "total": air + bills + change_n,
    }


def be_wd(annual_cost: float, share: float, kept: float = 1.0) -> float | None:
    per = DAYS * SURCHARGE * share * kept
    if per <= 0:
        return None
    return annual_cost / per


def one(name: str, box: dict, tier: str) -> dict:
    ex = box["exworks_ngn"]
    all_in = box["all_in_ngn"]
    if tier == "recycler":
        rent, power, sec = RENT_R, POWER_R, SEC_R
    else:
        rent, power, sec = RENT_K, POWER_K, SEC_K
    maint = MAINT * ex
    ins = INS * all_in
    street = rent + power + sec + CONN + maint + ins
    dep = all_in / LIFE
    full = street + dep
    parts = {
        "rent": rent,
        "power": power,
        "security": sec,
        "connectivity": CONN,
        "maintenance": maint,
        "insurance": ins,
        "street": street,
        "depreciation": dep,
        "full": full,
    }
    rows = {}
    for label, share in SPLITS:
        rows[label] = {}
        for wd in VOLUMES:
            rev = wd * DAYS * SURCHARGE * share
            cash = rev - street
            op = rev - full
            flows = [-all_in] + [cash] * LIFE
            rows[label][str(wd)] = {
                "revenue": rev,
                "cash": cash,
                "operating": op,
                "npv": npv(DISCOUNT, flows),
                "irr": irr(flows),
                "payback": payback(flows),
            }
        rows[label]["be_cash"] = be_wd(street, share)
        rows[label]["be_full"] = be_wd(full, share)
        rows[label]["be_cash_host"] = be_wd(street, share * 0.80)
        rows[label]["be_cash_40"] = be_wd(street, share, 0.40)
        rows[label]["be_cash_cit"] = be_wd(street + CIT, share)
    extra = stack(tier == "recycler")
    # Surcharge case plus the labelled stack, at 70/30, base volume.
    share = 0.70
    wd = 120
    rev = wd * DAYS * SURCHARGE * share + extra["total"]
    flows = [-all_in] + [rev - street] * LIFE
    with_stack = {
        "stack": extra,
        "revenue": rev,
        "cash": rev - street,
        "operating": rev - full,
        "npv": npv(DISCOUNT, flows),
        "irr": irr(flows),
        "payback": payback(flows),
    }
    # Kiosk has no withdrawal surcharge. Commission-only result.
    kiosk_only = None
    if tier == "kiosk":
        k = extra["total"]
        flows_k = [-all_in] + [k - street] * LIFE
        sales_for_street = street / AIRTIME_RATE if AIRTIME_RATE else None
        kiosk_only = {
            "revenue": k,
            "cash": k - street,
            "operating": k - full,
            "npv": npv(DISCOUNT, flows_k),
            "irr": irr(flows_k),
            "payback": payback(flows_k),
            "airtime_sales_to_cover_street": sales_for_street,
            "airtime_sales_per_day": (sales_for_street / DAYS) if sales_for_street else None,
        }
    debt = annuity(0.70 * all_in, MPR, 5)
    return {
        "name": name,
        "tier": tier,
        "box": box,
        "costs": parts,
        "splits": rows,
        "with_stack_70_120": with_stack,
        "kiosk_only": kiosk_only,
        "debt_service_70pct_5y_23": debt,
    }


def fleet_case(box: dict, n: int, wd: int, share: float, street: float, capex_share: float = 1.0) -> dict:
    all_in = box["all_in_ngn"]
    nxt = box["machine_ngn"]
    capex = (all_in + (n - 1) * nxt) * capex_share
    year0 = capex + HQ0 + HQ0_PER * n
    machine_cash = wd * DAYS * SURCHARGE * share - street
    annual = n * machine_cash - (HQ + HQ_PER * n)
    flows = [-year0] + [annual] * LIFE
    return {
        "machines": n,
        "wd": wd,
        "share": share,
        "capex_share": capex_share,
        "capex": capex,
        "year0": year0,
        "machine_cash": machine_cash,
        "annual_cash": annual,
        "npv": npv(DISCOUNT, flows),
        "irr": irr(flows),
        "payback": payback(flows),
    }


def main() -> dict:
    inr_to_usd = 1 / INR_PER_USD
    recycler_works = INSTALL_R + SOFTWARE_R
    kiosk_works = INSTALL_K + SOFTWARE_K
    boxes = {
        "recycler_low": landed(3_650, OCEAN_LOW, THC_LOW, CLEAR_LOW, recycler_works, 0),
        "recycler_high": landed(7_850, OCEAN_HIGH, THC_HIGH, CLEAR_HIGH, recycler_works, CUSTOM_HIGH),
        "kiosk_low": landed(150_000 * inr_to_usd, OCEAN_LOW, THC_LOW, CLEAR_LOW, kiosk_works, 0),
        "kiosk_high": landed(600_000 * inr_to_usd, OCEAN_HIGH, THC_HIGH, CLEAR_HIGH, kiosk_works, CUSTOM_HIGH),
    }
    units = {
        "recycler_low": one("Recycler, low band", boxes["recycler_low"], "recycler"),
        "recycler_high": one("Recycler, high band", boxes["recycler_high"], "recycler"),
        "kiosk_low": one("Cash-in kiosk, low band", boxes["kiosk_low"], "kiosk"),
        "kiosk_high": one("Cash-in kiosk, high band", boxes["kiosk_high"], "kiosk"),
    }
    high = units["recycler_high"]
    street = high["costs"]["street"]
    fleets = []
    for n in FLEETS:
        for wd in VOLUMES:
            for label, share in SPLITS:
                row = fleet_case(boxes["recycler_high"], n, wd, share, street)
                row["split"] = label
                fleets.append(row)
    # Funding alternatives on the high recycler, 20 machines, 120 wd, 70/30.
    funding = {
        "equity": fleet_case(boxes["recycler_high"], 20, 120, 0.70, street, 1.0),
        "bank_half_capex": fleet_case(boxes["recycler_high"], 20, 120, 0.70, street, 0.50),
        "vendor_note": {
            "rate": MPR,
            "share_financed": 0.70,
            "years": 5,
            "annual": annuity(0.70 * boxes["recycler_high"]["all_in_ngn"], MPR, 5),
            "note": "Policy rate used because no vendor-finance rate was found.",
        },
    }
    factor = (1 - (1 + DISCOUNT) ** (-LIFE)) / DISCOUNT
    target = 50_000_000_000
    need = target / factor

    def machines_for_target(wd: int, share: float) -> int | None:
        lo, hi = 1, 20000
        hit = None
        while lo <= hi:
            mid = (lo + hi) // 2
            row = fleet_case(boxes["recycler_high"], mid, wd, share, street)
            if row["npv"] >= target:
                hit = mid
                hi = mid - 1
            else:
                lo = mid + 1
        return hit
    # National scale check. H1 2025 withdrawals 858.80 million over a 181-day half.
    daily_national = 858.80e6 / 181
    scale = []
    for n in FLEETS:
        tx = n * 120
        scale.append({
            "machines": n,
            "wd": 120,
            "daily_withdrawals": tx,
            "share_of_h1_2025_daily": tx / daily_national,
            "naira_if_each_is_20000": tx * 20_000,
        })
    euronet_revenue_ngn = 1_881 * 12 * FX
    out = {
        "fx": FX,
        "inr_per_usd": INR_PER_USD,
        "days": DAYS,
        "surcharge": SURCHARGE,
        "discount": DISCOUNT,
        "boxes": boxes,
        "units": units,
        "fleets": fleets,
        "funding": funding,
        "valuation": {
            "target": target,
            "annuity_factor_7_at_28": factor,
            "annual_cash_for_pv_50bn": need,
            "perpetual_cash_at_28": target * DISCOUNT,
            "euronet_annual_revenue_ngn": euronet_revenue_ngn,
            "machines_for_50bn_npv": {
                "100/0 at 120": machines_for_target(120, 1.0),
                "100/0 at 200": machines_for_target(200, 1.0),
                "70/30 at 120": machines_for_target(120, 0.70),
                "70/30 at 200": machines_for_target(200, 0.70),
                "50/50 at 200": machines_for_target(200, 0.50),
            },
        },
        "scale": scale,
        "daily_national_atm_withdrawals": daily_national,
        "stack_unit": stack(True),
        "power_recycler": POWER_R,
    }
    dest = Path(__file__).resolve().parent / "outputs" / "results.json"
    dest.parent.mkdir(parents=True, exist_ok=True)

    def conv(o):
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, list):
            return [conv(v) for v in o]
        if isinstance(o, float):
            return round(o, 4) if abs(o) < 100 else round(o, 2)
        return o

    dest.write_text(json.dumps(conv(out), indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    r = main()
    h = r["units"]["recycler_high"]
    print("recycler high all-in", round(h["box"]["all_in_ngn"]))
    print("street", round(h["costs"]["street"]), "full", round(h["costs"]["full"]))
    for label, _ in SPLITS:
        s = h["splits"][label]
        print(label, "be", round(s["be_cash"], 1), round(s["be_full"], 1))
        for wd in VOLUMES:
            row = s[str(wd)]
            irr_s = None if row["irr"] is None else round(row["irr"] * 100, 1)
            print(" ", wd, "cash", round(row["cash"]), "irr", irr_s, "npv", round(row["npv"]))
    k = r["units"]["kiosk_high"]
    print("kiosk high", round(k["box"]["all_in_ngn"]), "street", round(k["costs"]["street"]))
    print("kiosk cash", round(k["kiosk_only"]["cash"]), "sales/day", round(k["kiosk_only"]["airtime_sales_per_day"]))
    print("need", round(r["valuation"]["annual_cash_for_pv_50bn"]))
    print("euronet ngn", round(r["valuation"]["euronet_annual_revenue_ngn"]))
