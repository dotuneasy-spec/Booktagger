"""CashEase v4.2 — bank-owned machines, CashEase as operator.

Does not modify the v4 or v4.1 models. Landed costs are the two v4.1
China figures and the v4 published US reference. Operator and site costs
that are not new invoices are the labelled v4 assumptions.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"

FX = 1331.69
MPR = 0.23
DISCOUNT = 0.28
DAYS = 300 * 0.90
LIFE = 7
HORIZON = 7
GROSS = 0.55 * 100 + 0.35 * 250 + 0.10 * 30  # 145.50
SHRINK = 0.35 * 12_000 * 0.003  # 12.60, bank's cash, not taken off the fee

RENT = 150_000 * 12
CIT = 40_000 * 4 * 12
SECURITY = 120_000 * 12
POWER = 336 * 1810 + 80_000
CONN = 18_000 * 12
MONITORING = 400_000
FLOAT = 2_000_000
MAINT_RATE = 0.10
INS_RATE = 0.015
NIBSS_ONCE = 250_000 + 250_000
HQ_FIXED = 25_000_000
HQ_PER = 50_000
ENGINEER = 1_085_000  # PayScale average, 8 profiles, 8 Jan 2026. Not ATM-specific.

# v4.1 high-band landed cost, US$4,800 FOB. Plain excludes the US$1,800 adder.
# Exact v4.1 high-band totals, including the one-time NIBSS pair and the ₦8 million site works.
CHINA_PLAIN = 16_426_875.125187501
CHINA_PLAIN_EX = 4_800 * FX
CHINA_CUSTOM = 19_132_536.2826875
CHINA_CUSTOM_EX = (4_800 + 1_800) * FX
US_ALL_IN = 40_000 * FX * 1.08 + 6_000_000 + 2_000_000  # 65,529,008 before duty
US_EX = 40_000 * FX

MACHINES = [
    {"id": "plain", "name": "China, no programming adder", "all_in": CHINA_PLAIN, "exworks": CHINA_PLAIN_EX, "nibss_inside": True},
    {"id": "custom", "name": "China, US$1,800 adder", "all_in": CHINA_CUSTOM, "exworks": CHINA_CUSTOM_EX, "nibss_inside": True},
    {"id": "us", "name": "Published US reference", "all_in": US_ALL_IN, "exworks": US_EX, "nibss_inside": False},
]
VOLUMES = (150, 250, 400)
FLEETS = (5, 20, 50, 200)
SHARES = (0.15, 0.20, 0.25, 0.30)


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


def bank_cash_costs(all_in: float, with_site: bool) -> dict:
    insurance = INS_RATE * (all_in + FLOAT)
    named = RENT + CIT
    site = (POWER + SECURITY + insurance) if with_site else insurance
    # Insurance stays with the asset owner in both views. Power and security
    # are the v4 site assumptions the brief did not name.
    return {
        "rent": RENT,
        "cit": CIT,
        "power": POWER if with_site else 0.0,
        "security": SECURITY if with_site else 0.0,
        "insurance": insurance,
        "cash_cost": named + site,
    }


def ce_machine_cost(exworks: float) -> dict:
    servicing = MAINT_RATE * exworks
    return {
        "servicing": servicing,
        "monitoring": MONITORING,
        "connectivity": CONN,
        "cash_cost": servicing + MONITORING + CONN,
    }


def annual_tx(tx: float) -> float:
    return tx * DAYS


def ce_profit(exworks: float, tx: float, share: float) -> dict:
    cost = ce_machine_cost(exworks)
    revenue = annual_tx(tx) * share * GROSS
    profit = revenue - cost["cash_cost"]
    return {**cost, "revenue": revenue, "profit": profit}


def bank_annual(all_in: float, tx: float, share: float, with_site: bool) -> dict:
    costs = bank_cash_costs(all_in, with_site)
    revenue = annual_tx(tx) * ((1 - share) * GROSS - SHRINK)
    cash_profit = revenue - costs["cash_cost"]
    dep = all_in / LIFE
    cof = (all_in + FLOAT) * MPR
    return {
        **costs,
        "revenue": revenue,
        "cash_profit": cash_profit,
        "depreciation": dep,
        "operating": cash_profit - dep,
        "cost_of_funds": cof,
        "after_cof": cash_profit - cof,
    }


def bank_flows(all_in: float, cash_profit: float, n: int, nibss_inside: bool) -> list[float]:
    """Float goes out at purchase and comes back at year 7. No salvage."""
    extra = 0.0 if nibss_inside else NIBSS_ONCE
    # The China unit costs already contain one NIBSS pair. Count it once.
    if nibss_inside and n > 1:
        capex = all_in + (n - 1) * (all_in - NIBSS_ONCE)
    else:
        capex = all_in * n + extra
    locked = FLOAT * n
    flows = [-(capex + locked)]
    for _ in range(HORIZON - 1):
        flows.append(cash_profit * n)
    flows.append(cash_profit * n + locked)
    return flows


def bank_result(all_in: float, tx: float, share: float, with_site: bool, n: int, nibss_inside: bool) -> dict:
    annual = bank_annual(all_in, tx, share, with_site)
    flows = bank_flows(all_in, annual["cash_profit"], n, nibss_inside)
    return {
        **annual,
        "flows_one": flows if n == 1 else None,
        "npv_28": npv(DISCOUNT, flows),
        "irr": irr(flows),
        "payback": payback(flows),
        "year0": flows[0],
    }


def tx_for_cash(all_in: float, share: float, with_site: bool) -> float | None:
    net = (1 - share) * GROSS - SHRINK
    if net <= 0:
        return None
    cost = bank_cash_costs(all_in, with_site)["cash_cost"]
    return (cost / net) / DAYS


def tx_for_irr(all_in: float, share: float, with_site: bool, nibss_inside: bool, target: float) -> float | None:
    net = (1 - share) * GROSS - SHRINK
    if net <= 0:
        return None
    cost = bank_cash_costs(all_in, with_site)["cash_cost"]

    def value(tx: float) -> float:
        profit = annual_tx(tx) * net - cost
        flows = bank_flows(all_in, profit, 1, nibss_inside)
        return npv(target, flows)

    if value(5000) < 0:
        return None
    low, high = 0.0, 5000.0
    for _ in range(60):
        mid = (low + high) / 2
        if value(mid) > 0:
            high = mid
        else:
            low = mid
    return high


def fleet_ce(exworks: float, tx: float, n: int, share: float) -> dict:
    one = ce_profit(exworks, tx, share)
    hq = HQ_FIXED + HQ_PER * n
    profit = one["profit"] * n - hq
    return {"per_machine": one["profit"], "hq": hq, "profit": profit, "engineer": ENGINEER}


def fee_to_zero(exworks: float, n: int, share: float = 0.20) -> dict:
    """Monthly naira per machine so fleet cash profit is zero at 150 tx/day."""
    one = ce_profit(exworks, 150, share)
    hq = HQ_FIXED + HQ_PER * n
    gap_machine = -one["profit"]
    gap_firm = -(one["profit"] * n - hq)
    gap_firm_staff = gap_firm + ENGINEER
    return {
        "machine_monthly": max(0.0, gap_machine) / 12,
        "firm_monthly": max(0.0, gap_firm) / n / 12,
        "firm_plus_one_engineer_monthly": max(0.0, gap_firm_staff) / n / 12,
    }


def machines_for_office(exworks: float, tx: float, share: float) -> float | None:
    one = ce_profit(exworks, tx, share)["profit"] - HQ_PER
    if one <= 0:
        return None
    return HQ_FIXED / one


def machines_for_engineer(exworks: float, tx: float, share: float) -> float | None:
    one = ce_profit(exworks, tx, share)["profit"]
    if one <= 0:
        return None
    return ENGINEER / one


def main() -> dict:
    rows = []
    for m in MACHINES:
        ce = {str(tx): ce_profit(m["exworks"], tx, 0.20) for tx in VOLUMES}
        bank = {
            str(tx): bank_result(m["all_in"], tx, 0.20, True, 1, m["nibss_inside"])
            for tx in VOLUMES
        }
        bank_named = {
            str(tx): bank_result(m["all_in"], tx, 0.20, False, 1, m["nibss_inside"])
            for tx in VOLUMES
        }
        fleets = {}
        for n in FLEETS:
            fleets[str(n)] = {
                str(tx): {
                    "ce": fleet_ce(m["exworks"], tx, n, 0.20),
                    "bank": bank_result(m["all_in"], tx, 0.20, True, n, m["nibss_inside"]),
                }
                for tx in VOLUMES
            }
        shares = {}
        for share in SHARES:
            shares[str(share)] = {
                str(tx): {
                    "ce": ce_profit(m["exworks"], tx, share),
                    "bank": bank_result(m["all_in"], tx, share, True, 1, m["nibss_inside"]),
                }
                for tx in VOLUMES
            }
        rows.append(
            {
                **m,
                "ce": ce,
                "bank": bank,
                "bank_named_only": bank_named,
                "fleets": fleets,
                "shares": shares,
                "be_cash": tx_for_cash(m["all_in"], 0.20, True),
                "be_irr_28": tx_for_irr(m["all_in"], 0.20, True, m["nibss_inside"], DISCOUNT),
                "be_irr_mpr": tx_for_irr(m["all_in"], 0.20, True, m["nibss_inside"], MPR),
                "be_cash_named": tx_for_cash(m["all_in"], 0.20, False),
                "office_machines": {str(tx): machines_for_office(m["exworks"], tx, 0.20) for tx in VOLUMES},
                "engineer_machines": {str(tx): machines_for_engineer(m["exworks"], tx, 0.20) for tx in VOLUMES},
                "fee": {str(n): fee_to_zero(m["exworks"], n) for n in FLEETS},
            }
        )

    result = {
        "fx": FX,
        "gross": GROSS,
        "shrink": SHRINK,
        "days": DAYS,
        "mpr": MPR,
        "discount": DISCOUNT,
        "engineer": ENGINEER,
        "hq_fixed": HQ_FIXED,
        "hq_per": HQ_PER,
        "rows": rows,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "operator_results.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    r = main()
    for row in r["rows"]:
        print("\n==", row["name"], "all-in", round(row["all_in"]), "ex", round(row["exworks"]))
        print(
            " bank tx cash/irr23/irr28",
            None if row["be_cash"] is None else round(row["be_cash"], 1),
            None if row["be_irr_mpr"] is None else round(row["be_irr_mpr"], 1),
            None if row["be_irr_28"] is None else round(row["be_irr_28"], 1),
        )
        for tx in ("150", "250", "400"):
            c = row["ce"][tx]
            b = row["bank"][tx]
            irr = None if b["irr"] is None else round(b["irr"] * 100, 1)
            print(
                f"  {tx}: CE {c['profit']/1e6:.3f}m rev {c['revenue']/1e6:.3f}m "
                f"svc {c['servicing']/1e6:.3f}m | bank cash {b['cash_profit']/1e6:.2f}m "
                f"afterCOF {b['after_cof']/1e6:.2f}m irr {irr} pb {b['payback']} npv {b['npv_28']/1e6:.2f}m"
            )
        print(" office", {k: None if v is None else round(v, 1) for k, v in row["office_machines"].items()})
        print(" engineer", {k: None if v is None else round(v, 1) for k, v in row["engineer_machines"].items()})
        for n, fee in row["fee"].items():
            print(
                f"  fee n={n}: machine {fee['machine_monthly']:.0f} "
                f"firm {fee['firm_monthly']:.0f} +eng {fee['firm_plus_one_engineer_monthly']:.0f}"
            )
