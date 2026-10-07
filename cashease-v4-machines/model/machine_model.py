"""CashEase v4 — bank-backed machine planning model.

Constants match cashease-v3/model/financial_model.py. This file does not
import v3, so the earlier study stays untouched. Every output is either one
of those sourced inputs or arithmetic on the assumptions below. CashEase
has no operating history. Test volumes are not forecasts.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"

FX = 1331.69
MPR = 0.23
DIESEL = 1810
POPULATION = 237_527_782
ATM_H1_2024 = 16_714
POS_DEPLOYED = 5_900_000
LOCAL_AUTHORITIES = 774
POSTAL_OUTLETS_2025 = 2_048
LAGOS_PARKS_REGISTERED = 30
LAGOS_IBADAN_STATIONS = 10
LAMATA_BLUE_PLANNED = 13
LAMATA_RED_PROPOSED = 12

USD_REF = 40_000
LIFE = 7
FREIGHT = 0.08
INSTALL = 6_000_000
SOFTWARE = 2_000_000
FLOAT = 2_000_000
OPEN_DAYS = 300
UPTIME = 0.90
DAYS = OPEN_DAYS * UPTIME  # 270
DISCOUNT = 0.28
HORIZON = 7

MIX_NOTE = 0.55
MIX_CASH = 0.35
MIX_VAS = 0.10
NOTE_FEE = 100
SURCHARGE = 250
VAS = 30
SHRINK_RATE = 0.003
AVG_CASHOUT = 12_000

RENT = 150_000 * 12
CIT = 40_000 * 4 * 12
SECURITY = 120_000 * 12
CONN = 18_000 * 12
MAINT_RATE = 0.10
INS_RATE = 0.015
MONITORING = 400_000  # assumption, managed-service only
ICRC = 0.01
DEBT_SHARE = 0.70
DEBT_YEARS = 5
# 7% equals the published BOI GLOW rate. It is the wrong product for this
# asset. It is used only as a sourced low-rate bound, not as a term sheet.
CONCESSIONAL = 0.07

HQ_FIXED = 25_000_000
HQ_PER_MACHINE = 50_000
HQ0_FIXED = 40_000_000
HQ0_PER_MACHINE = 150_000
UNSOLICITED_FEE = 100_000_000  # ICRC schedule, project cost above N100bn

TEST_TX = (150, 250, 400)
FLEET_N = (50, 500, 1_500, 20_000)


def naira(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000_000:
        return f"{sign}₦{n / 1_000_000_000_000:.2f} trillion"
    if n >= 1_000_000_000:
        return f"{sign}₦{n / 1_000_000_000:.2f} billion"
    if n >= 1_000_000:
        return f"{sign}₦{n / 1_000_000:.2f} million"
    return f"{sign}₦{n:,.0f}"


def landed(usd: float, fx_shock: float = 0.0) -> dict:
    exworks = usd * FX * (1 + fx_shock)
    freight = exworks * FREIGHT
    all_in = exworks + freight + INSTALL + SOFTWARE
    return {
        "usd": usd,
        "fx_shock": fx_shock,
        "exworks_ngn": exworks,
        "freight_ngn": freight,
        "install_ngn": INSTALL,
        "software_ngn": SOFTWARE,
        "all_in_ngn": all_in,
    }


def power_ngn() -> float:
    litres = 8 * OPEN_DAYS * 0.40 * 0.35
    return litres * DIESEL + 80_000


def line_costs(hw: dict) -> dict:
    dep = hw["all_in_ngn"] / LIFE
    maint = MAINT_RATE * hw["exworks_ngn"]
    machine_ins = INS_RATE * hw["all_in_ngn"]
    float_ins = INS_RATE * FLOAT
    return {
        "rent": RENT,
        "power": power_ngn(),
        "connectivity": CONN,
        "cit": CIT,
        "security": SECURITY,
        "maintenance": maint,
        "machine_insurance": machine_ins,
        "float_insurance": float_ins,
        "depreciation": dep,
        "float_opportunity": FLOAT * MPR,
        "monitoring": MONITORING,
    }


def pmt(principal: float, rate: float, years: int) -> float:
    if principal <= 0:
        return 0.0
    if rate == 0:
        return principal / years
    growth = (1 + rate) ** years
    return principal * rate * growth / (growth - 1)


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


def irr_label(flows: list[float], value: float | None) -> str | None:
    """Plain-language IRR when the solver has no root inside (−99%, 500%)."""
    if value is not None:
        return None
    if not flows:
        return None
    if abs(flows[0]) < 1 and all(cf >= -1 for cf in flows[1:]):
        return "no_capital"
    if flows[0] < 0 and npv(5.0, flows) > 0:
        return "above_500"
    return "not_defined"


def payback(flows: list[float]) -> float | None:
    cum = 0.0
    for t, cf in enumerate(flows):
        prev = cum
        cum += cf
        if t == 0:
            continue
        if prev < 0 <= cum:
            if cf == 0:
                return float(t)
            return (t - 1) + (-prev / cf)
    if flows and flows[0] >= 0 and cum >= 0:
        return 0.0
    return None


def fees(note: float, surcharge: float, onsite: bool) -> dict:
    sur = 0.0 if onsite else surcharge
    gross = MIX_NOTE * note + MIX_CASH * sur + MIX_VAS * VAS
    shrink = MIX_CASH * AVG_CASHOUT * SHRINK_RATE
    return {"gross": gross, "shrink": shrink, "surcharge_used": sur, "note_fee": note}


# Who bears each cost line. "ce" is CashEase (or the SPV it owns).
# Capex and the cash float are flags, not P&L lines.
STRUCTURES = {
    "v3": {
        "name": "v3 owner-pays",
        "onsite": False,
        "mode": "v3",
        "ce_share": None,
        "icrc": 0.0,
        "pays": {
            "rent", "power", "connectivity", "cit", "security", "maintenance",
            "machine_insurance", "float_insurance", "depreciation", "float_opportunity",
        },
        "capex": True,
        "float_cash": True,
        "who": {
            "rent": "CashEase",
            "cit": "CashEase",
            "float": "CashEase",
            "capex": "CashEase",
            "finance": "CashEase, if it borrows",
            "maintenance": "CashEase",
            "security": "CashEase",
            "power": "CashEase",
        },
    },
    "s60": {
        "name": "60/40, bank pays CIT and float",
        "onsite": False,
        "mode": "share",
        "ce_share": 0.60,
        "bank_share": 0.40,
        "gov_share": 0.0,
        "icrc": 0.0,
        "pays": {
            "rent", "power", "connectivity", "security", "maintenance",
            "machine_insurance", "depreciation",
        },
        "capex": True,
        "float_cash": False,
        "who": {
            "rent": "CashEase",
            "cit": "Bank",
            "float": "Bank",
            "capex": "CashEase",
            "finance": "CashEase, if it borrows",
            "maintenance": "CashEase",
            "security": "CashEase",
            "power": "CashEase",
        },
    },
    "s50": {
        "name": "50/50, bank pays CIT and float",
        "onsite": False,
        "mode": "share",
        "ce_share": 0.50,
        "bank_share": 0.50,
        "gov_share": 0.0,
        "icrc": 0.0,
        "pays": {
            "rent", "power", "connectivity", "security", "maintenance",
            "machine_insurance", "depreciation",
        },
        "capex": True,
        "float_cash": False,
        "who": {
            "rent": "CashEase",
            "cit": "Bank",
            "float": "Bank",
            "capex": "CashEase",
            "finance": "CashEase, if it borrows",
            "maintenance": "CashEase",
            "security": "CashEase",
            "power": "CashEase",
        },
    },
    "gallery": {
        "name": "60/40 at a bank gallery",
        "onsite": True,
        "mode": "share",
        "ce_share": 0.60,
        "bank_share": 0.40,
        "gov_share": 0.0,
        "icrc": 0.0,
        "pays": {
            "power", "connectivity", "security", "maintenance",
            "machine_insurance", "depreciation",
        },
        "capex": True,
        "float_cash": False,
        "who": {
            "rent": "Bank premises, no extra rent",
            "cit": "Bank",
            "float": "Bank",
            "capex": "CashEase",
            "finance": "CashEase, if it borrows",
            "maintenance": "CashEase",
            "security": "CashEase",
            "power": "CashEase",
        },
    },
    "managed": {
        "name": "Managed service, bank owns the machine",
        "onsite": False,
        "mode": "share",
        "ce_share": 0.15,
        "bank_share": 0.85,
        "gov_share": 0.0,
        "icrc": 0.0,
        "pays": {"monitoring"},
        "capex": False,
        "float_cash": False,
        "who": {
            "rent": "Bank",
            "cit": "Bank",
            "float": "Bank",
            "capex": "Bank",
            "finance": "Bank",
            "maintenance": "Bank",
            "security": "Bank",
            "power": "Bank",
        },
    },
    "concession": {
        "name": "Concession, free site, 50/30/20",
        "onsite": False,
        "mode": "share",
        "ce_share": 0.50,
        "bank_share": 0.30,
        "gov_share": 0.20,
        "icrc": ICRC,
        "pays": {
            "power", "connectivity", "security", "maintenance",
            "machine_insurance", "depreciation",
        },
        "capex": True,
        "float_cash": False,
        "who": {
            "rent": "Free public site",
            "cit": "Bank",
            "float": "Bank or CBN supply",
            "capex": "SPV, 70% debt",
            "finance": "SPV debt",
            "maintenance": "SPV / CashEase",
            "security": "SPV / CashEase",
            "power": "SPV / CashEase",
        },
    },
}


def pool_split(spec: dict, fee: dict) -> dict:
    gross = fee["gross"]
    shrink = fee["shrink"]
    icrc_amt = spec["icrc"] * gross
    distributable = gross - shrink - icrc_amt
    if spec["mode"] == "v3":
        bank = MIX_CASH * fee["surcharge_used"] * 0.25
        ce = gross - bank - shrink
        gov = 0.0
    else:
        ce = spec["ce_share"] * distributable
        bank = spec["bank_share"] * distributable
        gov = spec["gov_share"] * distributable
    return {
        "gross": gross,
        "shrink": shrink,
        "icrc": icrc_amt,
        "distributable": distributable,
        "ce": ce,
        "bank": bank,
        "gov": gov,
    }


def ce_cost_block(spec: dict, lines: dict) -> dict:
    cash_keys = [k for k in spec["pays"] if k not in ("depreciation", "float_opportunity")]
    cash = sum(lines[k] for k in cash_keys)
    full = cash
    if "depreciation" in spec["pays"]:
        full += lines["depreciation"]
    if "float_opportunity" in spec["pays"]:
        full += lines["float_opportunity"]
    return {"cash": cash, "full": full, "cash_keys": cash_keys}


def tx_for(annual_cost: float, per_tx: float) -> float | None:
    if per_tx <= 0:
        return None
    return (annual_cost / per_tx) / DAYS


def unit_flows(spec: dict, tx: float, hw: dict, fee: dict, lines: dict) -> list[float]:
    split = pool_split(spec, fee)
    block = ce_cost_block(spec, lines)
    annual_tx = tx * DAYS
    yearly = annual_tx * split["ce"] - block["cash"]
    invest = 0.0
    if spec["capex"]:
        invest += hw["all_in_ngn"]
    if spec["float_cash"]:
        invest += FLOAT
    flows = [-invest]
    for year in range(1, HORIZON + 1):
        cf = yearly
        if year == HORIZON and spec["float_cash"]:
            cf += FLOAT
        flows.append(cf)
    return flows


def levered_flows(
    spec: dict, tx: float, hw: dict, fee: dict, lines: dict, rate: float,
    n: int = 1, hq0: float = 0.0, hq_annual: float = 0.0, extra_year0: float = 0.0,
) -> dict:
    split = pool_split(spec, fee)
    block = ce_cost_block(spec, lines)
    annual_tx = tx * DAYS
    operating_cash = n * (annual_tx * split["ce"] - block["cash"]) - hq_annual
    capex = n * hw["all_in_ngn"] if spec["capex"] else 0.0
    float_cash = n * FLOAT if spec["float_cash"] else 0.0
    debt = DEBT_SHARE * capex
    equity = (capex - debt) + float_cash + hq0 + extra_year0
    service = pmt(debt, rate, DEBT_YEARS)
    flows = [-equity]
    for year in range(1, HORIZON + 1):
        cf = operating_cash
        if year <= DEBT_YEARS:
            cf -= service
        if year == HORIZON:
            cf += float_cash
        flows.append(cf)
    return {
        "debt": debt,
        "equity_year0": equity,
        "annual_service": service,
        "year1_interest": debt * rate,
        "operating_cash_after_hq": operating_cash,
        "flows": flows,
        "npv_28": npv(DISCOUNT, flows),
        "npv_mpr": npv(MPR, flows),
        "irr": irr(flows),
        "payback": payback(flows),
    }


def evaluate(key: str, hw: dict, note: float = NOTE_FEE, surcharge: float = SURCHARGE) -> dict:
    spec = STRUCTURES[key]
    fee = fees(note, surcharge, spec["onsite"])
    lines = line_costs(hw)
    split = pool_split(spec, fee)
    block = ce_cost_block(spec, lines)
    debt = DEBT_SHARE * hw["all_in_ngn"] if spec["capex"] else 0.0
    service_23 = pmt(debt, MPR, DEBT_YEARS)
    service_7 = pmt(debt, CONCESSIONAL, DEBT_YEARS)
    # Levered cash break-even covers cash operating costs plus full debt service.
    levered_cash_23 = block["cash"] + service_23
    levered_cash_7 = block["cash"] + service_7

    at = {}
    for tx in TEST_TX:
        flows = unit_flows(spec, tx, hw, fee, lines)
        annual_tx = tx * DAYS
        revenue = annual_tx * split["ce"]
        cash_profit = revenue - block["cash"]
        operating = revenue - block["full"]
        # Partner results. Bank cash costs are the lines it bears.
        bank_cash = 0.0
        bank_full = 0.0
        if key == "v3":
            bank_cash = 0.0
            bank_full = 0.0
        elif key == "managed":
            bank_pays = [k for k in lines if k not in spec["pays"]]
            bank_cash = sum(lines[k] for k in bank_pays if k not in ("depreciation", "float_opportunity"))
            bank_full = sum(lines[k] for k in bank_pays)
        elif key == "concession":
            bank_cash = lines["cit"] + lines["float_insurance"]
            bank_full = bank_cash + lines["float_opportunity"]
        else:
            # 60/40, 50/50, gallery: bank pays CIT, float insurance, float opportunity
            bank_cash = lines["cit"] + lines["float_insurance"]
            bank_full = bank_cash + lines["float_opportunity"]
        bank_revenue = annual_tx * split["bank"]
        gov_revenue = annual_tx * split["gov"]
        at[str(tx)] = {
            "annual_tx": annual_tx,
            "ce_revenue": revenue,
            "ce_cash_profit": cash_profit,
            "ce_operating": operating,
            "gap_full": block["full"] - revenue,
            "bank_revenue": bank_revenue,
            "bank_cash_profit": bank_revenue - bank_cash,
            "bank_full_profit": bank_revenue - bank_full,
            "gov_revenue": gov_revenue,
            "npv_28": npv(DISCOUNT, flows),
            "npv_mpr": npv(MPR, flows),
            "irr": irr(flows),
            "irr_label": irr_label(flows, irr(flows)),
            "payback": payback(flows),
            "flows": flows,
        }

    return {
        "key": key,
        "name": spec["name"],
        "who": spec["who"],
        "onsite": spec["onsite"],
        "ce_share": spec["ce_share"],
        "per_tx": split,
        "ce_cash_cost": block["cash"],
        "ce_full_cost": block["full"],
        "be_cash": tx_for(block["cash"], split["ce"]),
        "be_full": tx_for(block["full"], split["ce"]),
        "be_debt_23": tx_for(levered_cash_23, split["ce"]) if spec["capex"] else None,
        "be_debt_7": tx_for(levered_cash_7, split["ce"]) if spec["capex"] else None,
        "debt_service_23": service_23,
        "debt_service_7": service_7,
        "at": at,
    }


def capex_ceiling(key: str, tx: float, note: float = NOTE_FEE, surcharge: float = SURCHARGE) -> float | None:
    """Largest all-in capex with one-machine unlevered NPV = 0. None if even a cheap box fails."""
    spec = STRUCTURES[key]
    if not spec["capex"]:
        return None
    install_block = INSTALL + SOFTWARE

    def npv_at(all_in: float) -> float:
        exworks = (all_in - install_block) / (1 + FREIGHT)
        if exworks <= 0:
            return -1e18
        hw = {
            "usd": exworks / FX,
            "fx_shock": 0.0,
            "exworks_ngn": exworks,
            "freight_ngn": exworks * FREIGHT,
            "install_ngn": INSTALL,
            "software_ngn": SOFTWARE,
            "all_in_ngn": all_in,
        }
        fee = fees(note, surcharge, spec["onsite"])
        lines = line_costs(hw)
        flows = unit_flows(spec, tx, hw, fee, lines)
        return npv(DISCOUNT, flows)

    lo = install_block + 100_000
    hi = 80_000_000
    if npv_at(lo) < 0:
        return None
    if npv_at(hi) > 0:
        return hi
    for _ in range(50):
        mid = (lo + hi) / 2
        if npv_at(mid) > 0:
            lo = mid
        else:
            hi = mid
    return lo


def fleet(
    key: str, n: int, tx: float, hw: dict, rate: float | None,
    extra_year0: float = 0.0,
) -> dict:
    spec = STRUCTURES[key]
    fee = fees(NOTE_FEE, SURCHARGE, spec["onsite"])
    lines = line_costs(hw)
    one = evaluate(key, hw)
    row = one["at"][str(tx)]
    hq_a = HQ_FIXED + HQ_PER_MACHINE * n
    hq0 = HQ0_FIXED + HQ0_PER_MACHINE * n
    capex = n * hw["all_in_ngn"] if spec["capex"] else 0.0
    float_cash = n * FLOAT if spec["float_cash"] else 0.0
    yearly = n * row["ce_cash_profit"] - hq_a
    flows = [-(capex + float_cash + hq0 + extra_year0)]
    for year in range(1, HORIZON + 1):
        cf = yearly
        if year == HORIZON:
            cf += float_cash
        flows.append(cf)
    out = {
        "n": n,
        "tx": tx,
        "structure": key,
        "capex": capex,
        "float": float_cash,
        "hq0": hq0 + extra_year0,
        "hq_annual": hq_a,
        "ce_revenue": n * row["ce_revenue"],
        "ce_cash_profit": yearly,
        "ce_operating": n * row["ce_operating"] - hq_a,
        "bank_full_profit": n * row["bank_full_profit"],
        "gov_revenue": n * row["gov_revenue"],
        "year0": flows[0],
        "npv_28": npv(DISCOUNT, flows),
        "npv_mpr": npv(MPR, flows),
        "irr": irr(flows),
        "payback": payback(flows),
        "flows": flows,
    }
    out["irr_label"] = irr_label(flows, out["irr"])
    if rate is not None and spec["capex"]:
        lev = levered_flows(spec, tx, hw, fee, lines, rate, n=n, hq0=hq0, hq_annual=hq_a, extra_year0=extra_year0)
        out["levered"] = {k: lev[k] for k in (
            "debt", "equity_year0", "annual_service", "year1_interest",
            "npv_28", "npv_mpr", "irr", "payback",
        )}
    else:
        out["levered"] = None
    return out


def system_view(hw: dict, lines: dict) -> dict:
    fee = fees(NOTE_FEE, SURCHARGE, False)
    gross, shrink = fee["gross"], fee["shrink"]
    pool = gross - shrink
    icrc_amt = ICRC * gross
    commercial = sum(v for k, v in lines.items() if k != "monitoring")
    # Concession stack: no rent, no CIT. Float opportunity and float insurance stay
    # in the "economic" stack and drop out of the "notes treated as free" stack.
    concession_econ = commercial - lines["rent"] - lines["cit"]
    concession_free_notes = concession_econ - lines["float_opportunity"] - lines["float_insurance"]
    out = {}
    for label, cost, per in (
        ("commercial", commercial, pool),
        ("concession_econ", concession_econ, pool - icrc_amt),
        ("concession_free_notes", concession_free_notes, pool - icrc_amt),
    ):
        be = tx_for(cost, per)
        row = {"annual_cost": cost, "per_tx": per, "be_tx": be}
        for tx in TEST_TX:
            revenue = tx * DAYS * per
            row[str(tx)] = {"revenue": revenue, "gap": cost - revenue}
        out[label] = row
    return out


def clean(obj):
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items() if k != "flows"}
    if isinstance(obj, list):
        return [clean(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def main() -> dict:
    hw = landed(USD_REF)
    lines = line_costs(hw)
    # Reconciliation with v3 full fixed cost.
    v3_full = sum(v for k, v in lines.items() if k != "monitoring")
    structures = {k: evaluate(k, hw) for k in STRUCTURES}
    ceilings = {}
    for key in STRUCTURES:
        ceilings[key] = {str(tx): capex_ceiling(key, tx) for tx in TEST_TX}

    fleets = []
    for key, sizes in (
        ("s60", (50, 500, 1_500)),
        ("s50", (50, 500, 1_500)),
        ("gallery", (50,)),
        ("managed", (50, 500, 1_500, 20_000)),
        ("concession", (20_000,)),
        ("v3", (50,)),
    ):
        for n in sizes:
            extra = UNSOLICITED_FEE if key == "concession" else 0.0
            for tx in TEST_TX:
                fleets.append(fleet(key, n, tx, hw, MPR if STRUCTURES[key]["capex"] else None, extra))

    # Interest-rate bound on the 20,000 concession and on a 500-machine 60/40 case.
    interest_cases = []
    for key, n, tx in (("concession", 20_000, 250), ("concession", 20_000, 400), ("s60", 500, 400), ("s60", 50, 400)):
        extra = UNSOLICITED_FEE if key == "concession" else 0.0
        for rate in (MPR, CONCESSIONAL, 0.0):
            row = fleet(key, n, tx, hw, rate, extra)
            interest_cases.append({
                "structure": key, "n": n, "tx": tx, "rate": rate,
                "npv_28": row["levered"]["npv_28"],
                "irr": row["levered"]["irr"],
                "payback": row["levered"]["payback"],
                "annual_service": row["levered"]["annual_service"],
                "equity_year0": row["levered"]["equity_year0"],
                "cash_profit_before_debt": row["ce_cash_profit"],
            })

    sensitivities = []
    hw_fx = landed(USD_REF, 0.20)
    for key in ("s60", "s50", "gallery", "concession", "managed"):
        for note, sur in ((50, 150), (100, 250), (200, 500)):
            for shock, hardware in ((0.0, hw), (0.20, hw_fx)):
                if shock and (note, sur) != (100, 250):
                    continue
                ev = evaluate(key, hardware, note, sur)
                sensitivities.append({
                    "structure": key,
                    "note_fee": note,
                    "surcharge": 0 if STRUCTURES[key]["onsite"] else sur,
                    "fx_shock": shock,
                    "ce_per_tx": ev["per_tx"]["ce"],
                    "be_full": ev["be_full"],
                    "be_cash": ev["be_cash"],
                    "cash_profit_250": ev["at"]["250"]["ce_cash_profit"],
                    "operating_250": ev["at"]["250"]["ce_operating"],
                    "npv_250": ev["at"]["250"]["npv_28"],
                    "cash_profit_400": ev["at"]["400"]["ce_cash_profit"],
                    "npv_400": ev["at"]["400"]["npv_28"],
                })

    listed_sites = [
        {"name": "Local authorities", "count": LOCAL_AUTHORITIES},
        {"name": "Postal outlets, 2025", "count": POSTAL_OUTLETS_2025},
        {"name": "Lagos parks on the register", "count": LAGOS_PARKS_REGISTERED},
        {"name": "Lagos–Ibadan stations", "count": LAGOS_IBADAN_STATIONS},
        {"name": "Blue Line planned stations", "count": LAMATA_BLUE_PLANNED},
        {"name": "Red Line proposed stations", "count": LAMATA_RED_PROPOSED},
    ]
    listed_sum = sum(s["count"] for s in listed_sites)

    result = {
        "fx": FX,
        "mpr": MPR,
        "discount": DISCOUNT,
        "days": DAYS,
        "hardware": hw,
        "lines": lines,
        "v3_full_fixed_check": v3_full,
        "diesel_litres": 8 * OPEN_DAYS * 0.40 * 0.35,
        "structures": structures,
        "ceilings": ceilings,
        "fleets": fleets,
        "interest_cases": interest_cases,
        "sensitivities": sensitivities,
        "system": system_view(hw, lines),
        "sites": {
            "listed": listed_sites,
            "listed_sum": listed_sum,
            "atms": ATM_H1_2024,
            "target": 20_000,
            "postal": POSTAL_OUTLETS_2025,
            "population": POPULATION,
            "pos": POS_DEPLOYED,
        },
        "people_per_atm": POPULATION / ATM_H1_2024,
        "assumptions_hq": {
            "annual_fixed": HQ_FIXED,
            "annual_per_machine": HQ_PER_MACHINE,
            "year0_fixed": HQ0_FIXED,
            "year0_per_machine": HQ0_PER_MACHINE,
            "unsolicited_fee_if_concession": UNSOLICITED_FEE,
            "monitoring": MONITORING,
            "managed_share": 0.15,
            "debt_share": DEBT_SHARE,
            "debt_years": DEBT_YEARS,
            "concessional_rate": CONCESSIONAL,
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(clean(result), indent=2))
    return result


if __name__ == "__main__":
    r = main()
    print("all-in", round(r["hardware"]["all_in_ngn"]))
    print("v3 full check", round(r["v3_full_fixed_check"]))
    print("power", round(r["lines"]["power"]), "litres", r["diesel_litres"])
    for key, s in r["structures"].items():
        print(
            f"{key:12} ce/tx {s['per_tx']['ce']:.2f}  "
            f"cashBE {s['be_cash']}  fullBE {s['be_full']}  "
            f"debt23 {s['be_debt_23']}"
        )
        for tx in ("150", "250", "400"):
            a = s["at"][tx]
            print(
                f"   {tx}: cash {a['ce_cash_profit']/1e6:.2f}m  "
                f"op {a['ce_operating']/1e6:.2f}m  "
                f"npv {a['npv_28']/1e6:.2f}m  irr {a['irr']}  "
                f"bank {a['bank_full_profit']/1e6:.2f}m"
            )
    print("--- ceilings ---")
    for k, v in r["ceilings"].items():
        print(k, {t: None if x is None else round(x) for t, x in v.items()})
    print("--- system ---")
    for k, v in r["system"].items():
        print(k, "BE", None if v["be_tx"] is None else round(v["be_tx"], 1),
              "gap150", round(v["150"]["gap"]))
    print("sites", r["sites"]["listed_sum"])
