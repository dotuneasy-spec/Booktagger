"""CashEase Nigeria — independent planning model.

Every output is either a sourced input (see SOURCES in build_study) or a
figure calculated from the assumptions in this file. Nothing here is an
observed kiosk result. CashEase has no operating history.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "outputs"
CHARTS = ROOT / "charts"

# --- Sourced market inputs (not model choices) ---
FX_NGN_PER_USD = 1331.69  # NFEM close, 5 Oct 2026
MPR = 0.23  # MPC 307, 21–22 Sept 2026
INFLATION_YOY = 0.1539  # headline, August 2026
DIESEL_RETAIL_NGN = 1810  # pump quote, 6 Oct 2026
DIESEL_GANTRY_NGN = 1700  # Dangote gantry, 7 Oct 2026
MIN_WAGE_MONTH = 70_000  # national minimum, 2024, still cited in 2026
POPULATION_2025 = 237_527_782
ATM_ACTIVE_H1_2024 = 16_714
POS_DEPLOYED_MAR_2025 = 5_900_000
LGA = 768
AREA_COUNCILS = 6
LOCAL_AUTHORITIES = LGA + AREA_COUNCILS  # 774

# US deployer list ranges, Quality Data Systems. Not a Nigerian quote.
USD_DISPENSE_LOW = 25_000
USD_RECYCLER_MEDIAN = 36_000
USD_DEPOSIT_LOW = 40_000  # reference: bottom of deposit-automated range
USD_DEPOSIT_HIGH = 55_000

# --- Planning assumptions. Each one is a choice, not a measured fact. ---
A = {
    "freight_rate": 0.08,
    "install_and_solar_ngn": 6_000_000,
    "software_and_cert_ngn": 2_000_000,
    "life_years": 7,
    "salvage_ngn": 0,
    "float_per_kiosk_ngn": 2_000_000,
    "discount_rate": 0.28,  # MPR 23% + 5 pp project premium
    "open_days": 300,
    "uptime": 0.90,
    "mix_note": 0.55,
    "mix_cashout": 0.35,
    "mix_vas": 0.10,
    "note_fee_ngn": 100,
    "cashout_surcharge_ngn": 250,  # deployer income; cap is N500 per N20,000
    "vas_net_ngn": 30,
    "bank_share_of_surcharge": 0.25,
    "bank_share_of_note_fee": 0.0,
    "avg_cashout_ticket_ngn": 12_000,
    "shrink_rate_of_cashout_value": 0.003,
    "maintenance_rate_of_exworks": 0.10,  # US recycler rule of thumb
    "rent_per_month_ngn": 150_000,
    "kwh_per_open_day": 8,
    "diesel_share_of_energy": 0.40,
    "litres_per_kwh": 0.35,
    "solar_opex_ngn": 80_000,
    "connectivity_per_month_ngn": 18_000,
    "insurance_rate": 0.015,  # of all-in capex + float
    "cit_per_visit_ngn": 40_000,
    "cit_visits_per_month": 4,
    "security_per_month_ngn": 120_000,
    "hq_year0": {"pilot": 120_000_000, "two_k": 400_000_000, "twenty_k": 1_200_000_000},
    "hq_annual": {"pilot": 60_000_000, "two_k": 400_000_000, "twenty_k": 1_200_000_000},
    "sizes": {"pilot": 25, "two_k": 2_000, "twenty_k": 20_000},
    "test_tx_per_open_day": 80,  # secondary blog benchmark, not a forecast
    "horizon_years": 7,
}


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


def landed(usd: float) -> dict:
    exworks = usd * FX_NGN_PER_USD
    freight = exworks * A["freight_rate"]
    install = A["install_and_solar_ngn"]
    software = A["software_and_cert_ngn"]
    all_in = exworks + freight + install + software
    return {
        "usd": usd,
        "exworks_ngn": exworks,
        "freight_ngn": freight,
        "install_ngn": install,
        "software_ngn": software,
        "all_in_ngn": all_in,
    }


def effective_days() -> float:
    return A["open_days"] * A["uptime"]


def contribution_per_tx() -> dict:
    gross = (
        A["mix_note"] * A["note_fee_ngn"]
        + A["mix_cashout"] * A["cashout_surcharge_ngn"]
        + A["mix_vas"] * A["vas_net_ngn"]
    )
    bank = (
        A["mix_note"] * A["note_fee_ngn"] * A["bank_share_of_note_fee"]
        + A["mix_cashout"] * A["cashout_surcharge_ngn"] * A["bank_share_of_surcharge"]
    )
    shrink = A["mix_cashout"] * A["avg_cashout_ticket_ngn"] * A["shrink_rate_of_cashout_value"]
    return {
        "gross_ngn": gross,
        "bank_share_ngn": bank,
        "shrink_ngn": shrink,
        "net_ngn": gross - bank - shrink,
    }


def annual_fixed(hardware: dict) -> dict:
    days = A["open_days"]
    diesel_litres = (
        A["kwh_per_open_day"] * days * A["diesel_share_of_energy"] * A["litres_per_kwh"]
    )
    power = diesel_litres * DIESEL_RETAIL_NGN + A["solar_opex_ngn"]
    maint = A["maintenance_rate_of_exworks"] * hardware["exworks_ngn"]
    rent = A["rent_per_month_ngn"] * 12
    conn = A["connectivity_per_month_ngn"] * 12
    ins = A["insurance_rate"] * (hardware["all_in_ngn"] + A["float_per_kiosk_ngn"])
    cit = A["cit_per_visit_ngn"] * A["cit_visits_per_month"] * 12
    security = A["security_per_month_ngn"] * 12
    dep = (hardware["all_in_ngn"] - A["salvage_ngn"]) / A["life_years"]
    float_cost = A["float_per_kiosk_ngn"] * MPR
    street = rent + power + conn + cit + security
    machine_cash = maint + ins
    return {
        "power_ngn": power,
        "diesel_litres": diesel_litres,
        "maintenance_ngn": maint,
        "rent_ngn": rent,
        "connectivity_ngn": conn,
        "insurance_ngn": ins,
        "cit_ngn": cit,
        "security_ngn": security,
        "depreciation_ngn": dep,
        "float_cost_ngn": float_cost,
        "street_ngn": street,
        "cash_fixed_ngn": street + machine_cash,
        "full_fixed_ngn": street + machine_cash + dep + float_cost,
    }


def annual_at_tx(tx_per_open_day: float, hardware: dict) -> dict:
    """tx_per_open_day is throughput on a day the site is scheduled open,
    before the uptime haircut. Uptime scales the year, not the day label."""
    c = contribution_per_tx()
    f = annual_fixed(hardware)
    annual_tx = tx_per_open_day * effective_days()
    gross = annual_tx * c["gross_ngn"]
    bank = annual_tx * c["bank_share_ngn"]
    shrink = annual_tx * c["shrink_ngn"]
    net = gross - bank - shrink
    cash_profit = net - f["cash_fixed_ngn"]
    operating = cash_profit - f["depreciation_ngn"] - f["float_cost_ngn"]
    return {
        "tx_per_open_day": tx_per_open_day,
        "effective_days": effective_days(),
        "annual_tx": annual_tx,
        "gross_revenue_ngn": gross,
        "bank_share_ngn": bank,
        "shrink_ngn": shrink,
        "net_revenue_ngn": net,
        "cash_profit_ngn": cash_profit,
        "operating_profit_ngn": operating,
        **{k: f[k] for k in f},
    }


def tx_to_cover(annual_cost: float) -> float:
    net = contribution_per_tx()["net_ngn"]
    if net <= 0:
        return float("inf")
    return (annual_cost / net) / effective_days()


def npv(rate: float, cashflows: list[float]) -> float:
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))


def irr(cashflows: list[float]) -> float | None:
    # Bisection over (-0.99, 5). None if no sign change in NPV.
    low, high = -0.99, 5.0
    f_low, f_high = npv(low, cashflows), npv(high, cashflows)
    if f_low * f_high > 0:
        return None
    for _ in range(80):
        mid = (low + high) / 2
        f_mid = npv(mid, cashflows)
        if abs(f_mid) < 1.0:
            return mid
        if f_low * f_mid <= 0:
            high, f_high = mid, f_mid
        else:
            low, f_low = mid, f_mid
    return (low + high) / 2


def estate_cashflows(n: int, tx: float, hardware: dict, hq0: float, hq_annual: float) -> list[float]:
    unit = annual_at_tx(tx, hardware)
    invest = n * (hardware["all_in_ngn"] + A["float_per_kiosk_ngn"]) + hq0
    yearly = n * unit["cash_profit_ngn"] - hq_annual
    # Year 7 releases float. No salvage.
    flows = [-invest]
    for year in range(1, A["horizon_years"] + 1):
        cf = yearly
        if year == A["horizon_years"]:
            cf += n * A["float_per_kiosk_ngn"]
        flows.append(cf)
    return flows


def estate_pnl(n: int, tx: float, hardware: dict, hq_annual: float) -> dict:
    u = annual_at_tx(tx, hardware)
    return {
        "kiosks": n,
        "tx_per_open_day": tx,
        "gross_revenue_ngn": n * u["gross_revenue_ngn"],
        "bank_share_ngn": n * u["bank_share_ngn"],
        "shrink_ngn": n * u["shrink_ngn"],
        "net_revenue_ngn": n * u["net_revenue_ngn"],
        "street_costs_ngn": n * u["street_ngn"],
        "maintenance_ngn": n * u["maintenance_ngn"],
        "insurance_ngn": n * u["insurance_ngn"],
        "hq_ngn": hq_annual,
        "cash_profit_ngn": n * u["cash_profit_ngn"] - hq_annual,
        "depreciation_ngn": n * u["depreciation_ngn"],
        "float_cost_ngn": n * u["float_cost_ngn"],
        "operating_profit_ngn": n * u["operating_profit_ngn"] - hq_annual,
        "capex_ngn": n * hardware["all_in_ngn"],
        "float_ngn": n * A["float_per_kiosk_ngn"],
    }


def solve_capex_ceiling(tx: float, rate: float) -> float | None:
    """Largest all-in capex (NGN) with NPV = 0 for one kiosk, no HQ.

    Maintenance stays 10% of ex-works. Ex-works is backed out by treating
    freight as 8% of ex-works and holding install+software fixed, so a lower
    ceiling means a cheaper machine, not a thinner install budget.
    """
    install_block = A["install_and_solar_ngn"] + A["software_and_cert_ngn"]

    def npv_for_all_in(all_in: float) -> float:
        # all_in = exworks * 1.08 + install_block
        exworks = (all_in - install_block) / (1 + A["freight_rate"])
        if exworks <= 0:
            return -1e18
        hw = {
            "usd": exworks / FX_NGN_PER_USD,
            "exworks_ngn": exworks,
            "freight_ngn": exworks * A["freight_rate"],
            "install_ngn": A["install_and_solar_ngn"],
            "software_ngn": A["software_and_cert_ngn"],
            "all_in_ngn": all_in,
        }
        flows = estate_cashflows(1, tx, hw, 0, 0)
        return npv(rate, flows)

    # If even a token machine (install block only) has negative NPV, no ceiling.
    if npv_for_all_in(install_block + 1_000_000) < 0 and npv_for_all_in(install_block + 50_000_000) < 0:
        # Check the cheap end more carefully: maybe a very cheap machine works.
        pass
    lo, hi = install_block + 100_000, 200_000_000
    if npv_for_all_in(lo) < 0:
        return None  # even the cheapest build in range fails
    if npv_for_all_in(hi) > 0:
        return hi
    for _ in range(60):
        mid = (lo + hi) / 2
        if npv_for_all_in(mid) > 0:
            lo = mid
        else:
            hi = mid
    return lo


def main() -> dict:
    ref = landed(USD_DEPOSIT_LOW)
    bounds = {
        "dispense_low": landed(USD_DISPENSE_LOW),
        "recycler_median": landed(USD_RECYCLER_MEDIAN),
        "deposit_low": ref,
        "deposit_high": landed(USD_DEPOSIT_HIGH),
    }
    c = contribution_per_tx()
    f = annual_fixed(ref)
    be = {
        "street_tx_per_open_day": tx_to_cover(f["street_ngn"]),
        "cash_tx_per_open_day": tx_to_cover(f["cash_fixed_ngn"]),
        "full_tx_per_open_day": tx_to_cover(f["full_fixed_ngn"]),
        "contribution_per_tx_ngn": c["net_ngn"],
        "gross_per_tx_ngn": c["gross_ngn"],
    }
    test_tx = A["test_tx_per_open_day"]
    unit_test = annual_at_tx(test_tx, ref)

    scenarios = {}
    for key, n in A["sizes"].items():
        flows = estate_cashflows(n, test_tx, ref, A["hq_year0"][key], A["hq_annual"][key])
        pnl = estate_pnl(n, test_tx, ref, A["hq_annual"][key])
        scenarios[key] = {
            "pnl": pnl,
            "cashflows": flows,
            "npv_28": npv(A["discount_rate"], flows),
            "npv_mpr": npv(MPR, flows),
            "npv_35": npv(0.35, flows),
            "irr": irr(flows),
            "year0_with_hq": flows[0],
        }

    # Volume grid at reference hardware, one kiosk, no HQ.
    volume_grid = []
    for tx in (40, 80, 120, 200, 400, 750):
        row = annual_at_tx(tx, ref)
        flows = estate_cashflows(1, tx, ref, 0, 0)
        volume_grid.append(
            {
                "tx": tx,
                "net_revenue_ngn": row["net_revenue_ngn"],
                "cash_profit_ngn": row["cash_profit_ngn"],
                "operating_profit_ngn": row["operating_profit_ngn"],
                "npv_28": npv(A["discount_rate"], flows),
                "irr": irr(flows),
            }
        )

    ceilings = {}
    for tx in (80, 120, 200, 400):
        ceilings[str(tx)] = solve_capex_ceiling(tx, A["discount_rate"])

    def tx_for_zero_npv(net_per_tx: float) -> float:
        """Open-day tx that sets one-kiosk NPV to zero at the study discount rate."""
        invest = ref["all_in_ngn"] + A["float_per_kiosk_ngn"]
        rate = A["discount_rate"]
        years = A["horizon_years"]
        annuity = (1 - (1 + rate) ** (-years)) / rate
        pv_float = A["float_per_kiosk_ngn"] / (1 + rate) ** years
        required_cash_profit = (invest - pv_float) / annuity
        annual_tx = (required_cash_profit + f["cash_fixed_ngn"]) / net_per_tx
        return annual_tx / effective_days()

    hurdle_tx = {
        "base_fee": tx_for_zero_npv(c["net_ngn"]),
    }

    # CIT and fee sensitivities on full break-even tx/day.
    sensitivities = []
    base_cit = A["cit_per_visit_ngn"]
    base_fee = A["note_fee_ngn"]
    base_sur = A["cashout_surcharge_ngn"]
    for cit in (15_000, 40_000, 80_000):
        for fee, sur in ((50, 150), (100, 250), (200, 500)):
            A["cit_per_visit_ngn"] = cit
            A["note_fee_ngn"] = fee
            A["cashout_surcharge_ngn"] = sur
            ff = annual_fixed(ref)
            sensitivities.append(
                {
                    "cit_per_visit_ngn": cit,
                    "note_fee_ngn": fee,
                    "surcharge_ngn": sur,
                    "net_per_tx_ngn": contribution_per_tx()["net_ngn"],
                    "full_be_tx": tx_to_cover(ff["full_fixed_ngn"]),
                    "cash_be_tx": tx_to_cover(ff["cash_fixed_ngn"]),
                    "street_be_tx": tx_to_cover(ff["street_ngn"]),
                }
            )
    A["cit_per_visit_ngn"] = base_cit
    A["note_fee_ngn"] = base_fee
    A["cashout_surcharge_ngn"] = base_sur

    A["note_fee_ngn"] = 200
    A["cashout_surcharge_ngn"] = 500
    hurdle_tx["max_disclosed_surcharge"] = tx_for_zero_npv(contribution_per_tx()["net_ngn"])
    A["note_fee_ngn"] = base_fee
    A["cashout_surcharge_ngn"] = base_sur

    # Attended 90-day demand test. No machine. Assumptions stated in the study.
    test = {
        "sites": 10,
        "days": 90,
        "attendant_month_ngn": 180_000,
        "rent_month_ngn": 80_000,
        "transport_per_site_day_ngn": 8_000,
        "float_per_site_ngn": 500_000,
        "setup_ngn": 5_000_000,  # signs, count kits, counsel, insurance binder
    }
    months = 3
    test_cash = test["sites"] * (
        (test["attendant_month_ngn"] + test["rent_month_ngn"]) * months
        + test["transport_per_site_day_ngn"] * test["days"]
        + test["float_per_site_ngn"]
    ) + test["setup_ngn"]
    # Float comes back. Cash spent excluding float:
    test_spend_ex_float = test_cash - test["sites"] * test["float_per_site_ngn"]

    people_per_atm = POPULATION_2025 / ATM_ACTIVE_H1_2024
    people_per_pos = POPULATION_2025 / POS_DEPLOYED_MAR_2025

    result = {
        "fx": FX_NGN_PER_USD,
        "mpr": MPR,
        "inflation": INFLATION_YOY,
        "diesel_retail": DIESEL_RETAIL_NGN,
        "diesel_gantry": DIESEL_GANTRY_NGN,
        "population": POPULATION_2025,
        "atm_h1_2024": ATM_ACTIVE_H1_2024,
        "pos_mar_2025": POS_DEPLOYED_MAR_2025,
        "local_authorities": LOCAL_AUTHORITIES,
        "people_per_atm_mixed_vintage": people_per_atm,
        "people_per_deployed_pos": people_per_pos,
        "machines_20k_per_100k_residents": 20_000 / POPULATION_2025 * 100_000,
        "machines_20k_over_atms": 20_000 / ATM_ACTIVE_H1_2024,
        "machines_20k_share_of_pos": 20_000 / POS_DEPLOYED_MAR_2025,
        "machines_per_local_authority_at_20k": 20_000 / LOCAL_AUTHORITIES,
        "assumptions": A,
        "contribution": c,
        "hardware": {k: v for k, v in bounds.items()},
        "reference_fixed": f,
        "breakeven": be,
        "unit_test_80": unit_test,
        "scenarios": scenarios,
        "volume_grid": volume_grid,
        "capex_ceiling_ngn": ceilings,
        "hurdle_tx_per_open_day": hurdle_tx,
        "sensitivities": sensitivities,
        "attended_test": {**test, "cash_outlay_ngn": test_cash, "spend_ex_float_ngn": test_spend_ex_float},
        "interest_only_70pct_at_mpr": 0.70 * ref["all_in_ngn"] * MPR,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    # Assumptions contain only JSON-safe values.
    serial = json.loads(json.dumps(result))
    (OUT / "results.json").write_text(json.dumps(serial, indent=2))
    return result


if __name__ == "__main__":
    r = main()
    b = r["breakeven"]
    print("net per tx", round(b["contribution_per_tx_ngn"], 2))
    print("street BE", round(b["street_tx_per_open_day"], 1))
    print("cash BE", round(b["cash_tx_per_open_day"], 1))
    print("full BE", round(b["full_tx_per_open_day"], 1))
    print("all-in", round(r["hardware"]["deposit_low"]["all_in_ngn"]))
    print("unit cash profit @80", round(r["unit_test_80"]["cash_profit_ngn"]))
    for k, s in r["scenarios"].items():
        print(k, "NPV", round(s["npv_28"]), "IRR", s["irr"], "op", round(s["pnl"]["operating_profit_ngn"]))
    print("ceilings", {k: None if v is None else round(v) for k, v in r["capex_ceiling_ngn"].items()})
    print("attended", round(r["attended_test"]["spend_ex_float_ngn"]))
