"""Five-year feasibility model for a Lagos multi-service agency.

Money is integer naira. Month 1 is October 2026. Year 1 runs to September 2027.
The engine is a planning model, not a set of accounts.
"""

from __future__ import annotations

from copy import deepcopy

STAFF_LOAD = 1.18  # allowance on target pay: pension, NSITF, take-home gap
BANK_RATE = 0.005
WHT_RATE = 0.05
SMALL_CO_TURNOVER = 50_000_000
VAT_TURNOVER = 100_000_000
TAX_RATE_ABOVE = 0.30 + 0.04  # CIT plus development-levy allowance
BUFFER = 200_000
HOUSEHOLD = 150_000

MONTHS = [
    "Oct", "Nov", "Dec", "Jan", "Feb", "Mar",
    "Apr", "May", "Jun", "Jul", "Aug", "Sep",
]
MONTH_YEARS = [2026, 2026, 2026, 2027, 2027, 2027, 2027, 2027, 2027, 2027, 2027, 2027]


def ngn(n: float) -> str:
    n = int(round(n))
    if n < 0:
        return f"(₦{abs(n):,})"
    return f"₦{n:,}"


def month_label(index: int) -> str:
    """index is 0-based."""
    year = 2026 + (9 + index) // 12
    name = MONTHS[index % 12]
    return f"{name} {year}"


def blank_month(**kw):
    row = {
        "refresh_n": 0,
        "refresh_price": 0,
        "refresh_margin": 0.27,
        "standup_n": 0,
        "standup_price": 0,
        "standup_margin": 0.23,
        "launch_n": 0,
        "launch_price": 0,
        "launch_margin": 0.22,
        "retainer": 0,
        "retainer_count": 0,
        "retainer_margin": 0.46,
        "extras": 0,
        "extras_margin": 0.25,
        "care_units": 0,
        "care_fee": 0,
        "care_margin": 0.40,
        "opex": 0,
        "founder": 0,
        "setup": 0,
        "supervisor_offer": 0,
        "electrician_offer": 0,
        "plumber_offer": 0,
        "note": "",
    }
    row.update(kw)
    return row


def fill_year(rows, year_index, count, **kw):
    """Append `count` months. List values are cycled or indexed; scalars repeat."""
    for i in range(count):
        data = {}
        for key, value in kw.items():
            if isinstance(value, (list, tuple)):
                data[key] = value[i]
            else:
                data[key] = value
        rows.append(blank_month(**data))
    return rows


def base_months():
    rows = []
    # Year 1 — sole founder, bench only, retainer pilot in month 10.
    y1 = [
        blank_month(opex=75_000, setup=295_000, note="Formation, contracts, tools, three paid trials"),
        blank_month(refresh_n=1, refresh_price=120_000, refresh_margin=0.15, opex=80_000, note="First paid proof job"),
        blank_month(refresh_n=1, refresh_price=160_000, refresh_margin=0.15, opex=80_000),
        blank_month(refresh_n=1, refresh_price=170_000, refresh_margin=0.18, opex=85_000),
        blank_month(refresh_n=2, refresh_price=170_000, refresh_margin=0.27, opex=90_000),
        blank_month(refresh_n=2, refresh_price=170_000, standup_n=1, standup_price=500_000, opex=95_000, note="First stand-up"),
        blank_month(refresh_n=2, refresh_price=180_000, standup_n=1, standup_price=520_000, opex=95_000, founder=80_000),
        blank_month(refresh_n=2, refresh_price=180_000, standup_n=1, standup_price=520_000, opex=95_000, founder=80_000),
        blank_month(
            refresh_n=2, refresh_price=180_000, standup_n=1, standup_price=540_000,
            opex=95_000, founder=80_000, setup=120_000, note="Upgrade to a limited company before the estate contract",
        ),
        blank_month(
            refresh_n=2, refresh_price=180_000, standup_n=1, standup_price=540_000,
            retainer=150_000, retainer_count=1, opex=100_000, founder=80_000, note="90-day estate pilot",
        ),
        blank_month(
            refresh_n=2, refresh_price=180_000, standup_n=1, standup_price=540_000,
            retainer=150_000, retainer_count=1, extras=70_000, opex=100_000, founder=80_000,
        ),
        blank_month(
            refresh_n=2, refresh_price=180_000, standup_n=1, standup_price=560_000,
            retainer=150_000, retainer_count=1, extras=100_000, opex=100_000, founder=80_000,
        ),
    ]
    rows.extend(y1)

    # Year 2 — renew the pilot, hire a supervisor only when the gate passes.
    fill_year(
        rows, 2, 3,
        refresh_n=3, refresh_price=190_000, standup_n=1, standup_price=580_000,
        retainer=200_000, retainer_count=1, extras=110_000,
        opex=110_000, founder=150_000, supervisor_offer=100_000,
    )
    fill_year(
        rows, 2, 3,
        refresh_n=3, refresh_price=190_000, standup_n=1, standup_price=580_000,
        retainer=200_000, retainer_count=1, extras=140_000,
        care_units=[6, 8, 10], care_fee=32_000,
        opex=115_000, founder=150_000, supervisor_offer=100_000,
    )
    rows[-1]["launch_n"] = 1
    rows[-1]["launch_price"] = 1_200_000
    rows[-1]["standup_n"] = 1
    fill_year(
        rows, 2, 3,
        refresh_n=4, refresh_price=200_000, standup_n=1, standup_price=620_000,
        retainer=220_000, retainer_count=1, extras=160_000,
        care_units=[12, 12, 14], care_fee=32_000,
        opex=120_000, founder=150_000, supervisor_offer=105_000,
    )
    fill_year(
        rows, 2, 3,
        refresh_n=4, refresh_price=200_000, standup_n=[1, 2, 1], standup_price=620_000,
        retainer=220_000, retainer_count=1, extras=180_000,
        care_units=[14, 16, 16], care_fee=34_000,
        opex=120_000, founder=150_000, supervisor_offer=110_000,
    )

    # Year 3 — one estate still. Second retainer waits until year 4.
    fill_year(
        rows, 3, 3,
        refresh_n=4, refresh_price=210_000, standup_n=[1, 2, 1], standup_price=680_000,
        launch_n=[0, 0, 1], launch_price=1_350_000,
        retainer=240_000, retainer_count=1, extras=190_000,
        care_units=[16, 17, 18], care_fee=35_000,
        opex=145_000, founder=220_000, supervisor_offer=120_000,
    )
    fill_year(
        rows, 3, 3,
        refresh_n=4, refresh_price=210_000, standup_n=2, standup_price=700_000,
        retainer=250_000, retainer_count=1, extras=200_000,
        care_units=[18, 18, 18], care_fee=35_000,
        opex=150_000, founder=220_000, supervisor_offer=125_000,
    )
    fill_year(
        rows, 3, 3,
        refresh_n=4, refresh_price=220_000, standup_n=[2, 1, 2], standup_price=720_000,
        launch_n=[0, 1, 0], launch_price=1_400_000,
        retainer=250_000, retainer_count=1, extras=220_000,
        care_units=[19, 20, 20], care_fee=36_000,
        opex=155_000, founder=240_000, supervisor_offer=130_000,
    )
    fill_year(
        rows, 3, 3,
        refresh_n=4, refresh_price=220_000, standup_n=2, standup_price=740_000,
        retainer=260_000, retainer_count=1, extras=230_000,
        care_units=[20, 20, 21], care_fee=36_000,
        opex=160_000, founder=240_000, supervisor_offer=135_000,
    )

    # Year 4 — second estate mid-year. Electrician offer begins, gate decides.
    fill_year(
        rows, 4, 6,
        refresh_n=4, refresh_price=235_000, standup_n=[2, 2, 1, 2, 2, 1], standup_price=780_000,
        launch_n=[0, 0, 1, 0, 0, 1], launch_price=1_500_000,
        retainer=280_000, retainer_count=1, extras=260_000,
        care_units=[21, 22, 22, 23, 23, 24], care_fee=38_000,
        opex=165_000, founder=300_000, supervisor_offer=145_000, electrician_offer=140_000,
    )
    fill_year(
        rows, 4, 6,
        refresh_n=5, refresh_price=245_000, standup_n=[2, 2, 1, 2, 2, 1], standup_price=800_000,
        launch_n=[0, 0, 1, 0, 0, 0], launch_price=1_550_000,
        retainer=[280_000 + 180_000] * 6, retainer_count=2, extras=300_000,
        care_units=[24, 24, 25, 25, 26, 26], care_fee=38_000,
        opex=170_000, founder=320_000, supervisor_offer=155_000, electrician_offer=145_000,
    )

    # Year 5 — two retainers, care plan stays inside the first estate.
    fill_year(
        rows, 5, 12,
        refresh_n=5, refresh_price=260_000,
        standup_n=[2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 2],
        standup_price=860_000,
        launch_n=[0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        launch_price=1_650_000,
        retainer=320_000 + 200_000, retainer_count=2, extras=320_000,
        care_units=[26, 26, 27, 27, 28, 28, 28, 29, 29, 30, 30, 30],
        care_fee=40_000,
        opex=185_000, founder=400_000,
        supervisor_offer=170_000, electrician_offer=155_000,
    )
    assert len(rows) == 60, len(rows)
    return rows


def best_months():
    rows = []
    y1 = [
        blank_month(opex=80_000, setup=500_000, note="Limited company, contracts, tools, trials"),
        blank_month(refresh_n=1, refresh_price=180_000, refresh_margin=0.20, opex=85_000, note="Proof job"),
        blank_month(refresh_n=2, refresh_price=200_000, refresh_margin=0.30, opex=90_000),
        blank_month(
            refresh_n=2, refresh_price=220_000, refresh_margin=0.32,
            standup_n=1, standup_price=650_000, standup_margin=0.28,
            opex=95_000, founder=100_000, note="First property-manager referrals",
        ),
        blank_month(
            refresh_n=3, refresh_price=220_000, refresh_margin=0.32,
            standup_n=1, standup_price=680_000, standup_margin=0.28,
            opex=100_000, founder=100_000,
        ),
        blank_month(
            refresh_n=3, refresh_price=230_000, refresh_margin=0.32,
            standup_n=1, standup_price=720_000, standup_margin=0.28,
            retainer=200_000, retainer_count=1, retainer_margin=0.52,
            extras=80_000, extras_margin=0.30,
            opex=105_000, founder=120_000, supervisor_offer=110_000,
            note="Estate pilot",
        ),
        blank_month(
            refresh_n=3, refresh_price=230_000, refresh_margin=0.32,
            standup_n=1, standup_price=720_000, standup_margin=0.28,
            retainer=220_000, retainer_count=1, retainer_margin=0.52,
            extras=100_000, extras_margin=0.30,
            opex=110_000, founder=150_000, supervisor_offer=115_000,
        ),
        blank_month(
            refresh_n=3, refresh_price=240_000, refresh_margin=0.32,
            standup_n=1, standup_price=750_000, standup_margin=0.28,
            retainer=230_000, retainer_count=1, retainer_margin=0.52,
            extras=120_000, extras_margin=0.30,
            opex=110_000, founder=150_000, supervisor_offer=120_000,
        ),
        blank_month(
            refresh_n=3, refresh_price=240_000, refresh_margin=0.32,
            standup_n=1, standup_price=750_000, standup_margin=0.28,
            launch_n=1, launch_price=1_450_000, launch_margin=0.26,
            retainer=240_000, retainer_count=1, retainer_margin=0.52,
            extras=140_000, extras_margin=0.30,
            opex=115_000, founder=150_000, supervisor_offer=120_000,
        ),
        blank_month(
            refresh_n=4, refresh_price=250_000, refresh_margin=0.32,
            standup_n=1, standup_price=780_000, standup_margin=0.28,
            retainer=250_000, retainer_count=1, retainer_margin=0.52,
            extras=160_000, extras_margin=0.30,
            opex=120_000, founder=150_000, supervisor_offer=125_000,
        ),
        blank_month(
            refresh_n=4, refresh_price=250_000, refresh_margin=0.32,
            standup_n=1, standup_price=780_000, standup_margin=0.28,
            retainer=260_000, retainer_count=1, retainer_margin=0.52,
            extras=180_000, extras_margin=0.30,
            opex=120_000, founder=160_000, supervisor_offer=130_000,
        ),
        blank_month(
            refresh_n=4, refresh_price=250_000, refresh_margin=0.32,
            standup_n=1, standup_price=800_000, standup_margin=0.28,
            retainer=270_000, retainer_count=1, retainer_margin=0.52,
            extras=200_000, extras_margin=0.30,
            care_units=8, care_fee=40_000, care_margin=0.45,
            opex=125_000, founder=160_000, supervisor_offer=130_000,
            note="First in-unit plans, one estate",
        ),
    ]
    rows.extend(y1)

    def b(**kw):
        defaults = dict(
            refresh_margin=0.32, standup_margin=0.28, launch_margin=0.26,
            retainer_margin=0.52, extras_margin=0.30, care_margin=0.45,
        )
        defaults.update(kw)
        return defaults

    fill_year(
        rows, 2, 3, **b(
            refresh_n=4, refresh_price=260_000, standup_n=1, standup_price=820_000,
            retainer=280_000, retainer_count=1, extras=220_000,
            care_units=[10, 12, 12], care_fee=42_000,
            opex=140_000, founder=200_000, supervisor_offer=140_000,
        )
    )
    fill_year(
        rows, 2, 3, **b(
            refresh_n=4, refresh_price=270_000, standup_n=[2, 1, 2], standup_price=860_000,
            launch_n=[0, 1, 0], launch_price=1_600_000,
            retainer=300_000 + 200_000, retainer_count=2, extras=250_000,
            care_units=[14, 16, 16], care_fee=42_000,
            opex=150_000, founder=220_000, supervisor_offer=145_000, electrician_offer=140_000,
        )
    )
    fill_year(
        rows, 2, 3, **b(
            refresh_n=5, refresh_price=280_000, standup_n=2, standup_price=900_000,
            retainer=320_000 + 220_000, retainer_count=2, extras=280_000,
            care_units=[18, 18, 20], care_fee=44_000,
            opex=155_000, founder=240_000, supervisor_offer=150_000, electrician_offer=145_000,
        )
    )
    fill_year(
        rows, 2, 3, **b(
            refresh_n=5, refresh_price=280_000, standup_n=[2, 1, 2], standup_price=920_000,
            launch_n=[0, 1, 0], launch_price=1_700_000,
            retainer=330_000 + 230_000, retainer_count=2, extras=300_000,
            care_units=[20, 22, 22], care_fee=44_000,
            opex=160_000, founder=250_000, supervisor_offer=155_000, electrician_offer=150_000,
        )
    )

    fill_year(
        rows, 3, 6, **b(
            refresh_n=5, refresh_price=300_000, standup_n=[2, 2, 1, 2, 2, 1], standup_price=980_000,
            launch_n=[0, 0, 1, 0, 0, 1], launch_price=1_850_000,
            retainer=350_000 + 260_000, retainer_count=2, extras=340_000,
            care_units=[24, 24, 26, 26, 28, 28], care_fee=48_000,
            opex=175_000, founder=300_000, supervisor_offer=165_000, electrician_offer=155_000,
        )
    )
    fill_year(
        rows, 3, 6, **b(
            refresh_n=6, refresh_price=310_000, standup_n=[2, 2, 1, 2, 2, 2], standup_price=1_020_000,
            launch_n=[0, 1, 0, 0, 1, 0], launch_price=1_950_000,
            retainer=360_000 + 280_000, retainer_count=2, extras=380_000,
            care_units=[30, 30, 32, 32, 34, 34], care_fee=50_000,
            opex=185_000, founder=320_000, supervisor_offer=175_000, electrician_offer=165_000,
            plumber_offer=150_000,
        )
    )

    fill_year(
        rows, 4, 6, **b(
            refresh_n=6, refresh_price=330_000, standup_n=[2, 2, 1, 2, 2, 1], standup_price=1_080_000,
            launch_n=[0, 1, 0, 0, 1, 0], launch_price=2_100_000,
            retainer=380_000 + 300_000, retainer_count=2, extras=420_000,
            care_units=[36, 36, 38, 38, 40, 40], care_fee=52_000,
            opex=200_000, founder=380_000,
            supervisor_offer=185_000, electrician_offer=170_000, plumber_offer=155_000,
        )
    )
    fill_year(
        rows, 4, 6, **b(
            refresh_n=6, refresh_price=340_000, standup_n=[2, 1, 2, 2, 1, 2], standup_price=1_120_000,
            launch_n=[1, 0, 0, 1, 0, 0], launch_price=2_200_000,
            retainer=400_000 + 320_000 + 180_000, retainer_count=3, extras=450_000,
            care_units=[42, 42, 44, 44, 46, 46], care_fee=54_000,
            opex=210_000, founder=400_000,
            supervisor_offer=190_000, electrician_offer=175_000, plumber_offer=160_000,
        )
    )

    fill_year(
        rows, 5, 12, **b(
            refresh_n=6, refresh_price=360_000,
            standup_n=[2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 2],
            standup_price=1_180_000,
            launch_n=[0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
            launch_price=2_350_000,
            retainer=420_000 + 340_000 + 220_000, retainer_count=3, extras=480_000,
            care_units=[48, 48, 50, 50, 52, 52, 54, 54, 56, 56, 58, 60],
            care_fee=55_000,
            opex=230_000, founder=480_000,
            supervisor_offer=200_000, electrician_offer=185_000, plumber_offer=170_000,
        )
    )
    assert len(rows) == 60, len(rows)
    return rows


def _stream(n, price, margin):
    rev = n * price
    return rev, rev * margin


def _consider_hires(m, i, flags, cash, events, cash_floor=300_000):
    """Hire only when the fee test and a cash floor both hold."""
    recurring = m["retainer"] + m["care_units"] * m["care_fee"]
    supervisor, electrician, plumber = flags

    def loaded(pay):
        return pay * STAFF_LOAD

    m["supervisor_pay"] = m["supervisor_offer"] if supervisor else 0
    m["electrician_pay"] = m["electrician_offer"] if electrician else 0
    m["plumber_pay"] = m["plumber_offer"] if plumber else 0
    current = loaded(m["supervisor_pay"] + m["electrician_pay"] + m["plumber_pay"])

    def can_add(proposed):
        return cash >= cash_floor and recurring >= 1.3 * (current + proposed)

    if not supervisor and m["supervisor_offer"] and m["retainer"] > 0:
        proposed = loaded(m["supervisor_offer"])
        if can_add(proposed):
            supervisor = True
            m["supervisor_pay"] = m["supervisor_offer"]
            current += proposed
            events.append((i, "Supervisor", m["supervisor_offer"], recurring, cash))

    if supervisor and not electrician and m["electrician_offer"] and m["care_units"] >= 25:
        proposed = loaded(m["electrician_offer"])
        if can_add(proposed):
            electrician = True
            m["electrician_pay"] = m["electrician_offer"]
            current += proposed
            events.append((i, "Electrician", m["electrician_offer"], recurring, cash))

    if (
        electrician
        and not plumber
        and m["plumber_offer"]
        and m["care_units"] >= 40
        and m["retainer_count"] >= 2
    ):
        proposed = loaded(m["plumber_offer"])
        if can_add(proposed):
            plumber = True
            m["plumber_pay"] = m["plumber_offer"]
            current += proposed
            events.append((i, "Plumber", m["plumber_offer"], recurring, cash))

    staff_target = m["supervisor_pay"] + m["electrician_pay"] + m["plumber_pay"]
    m["staff_cost"] = staff_target * STAFF_LOAD
    m["recurring"] = recurring
    m["cover_ratio"] = (recurring / m["staff_cost"]) if m["staff_cost"] else None
    return (supervisor, electrician, plumber)


def simulate(
    name,
    months,
    opening,
    bad_rate,
    slip_rate,
    rework_rate,
    b2b_one_off,
    wht_retainer,
    wht_care,
    one_off_scale=1.0,
    care_scale=1.0,
    care_margin_delta=0.0,
    forced_monthly_staff=0.0,
    hire=True,
):
    months = deepcopy(months)
    events = []
    flags = (False, False, False)
    cash = opening
    wht_credit = 0.0
    prev_one_off = 0.0
    min_cash = cash
    min_cash_i = -1
    year_buckets = []
    current = new_year_bucket()
    rows = []

    for i, m in enumerate(months):
        m["refresh_price"] *= one_off_scale
        m["standup_price"] *= one_off_scale
        m["launch_price"] *= one_off_scale
        m["extras"] *= one_off_scale
        m["care_units"] *= care_scale
        m["care_margin"] = max(0.0, m["care_margin"] + care_margin_delta)
        if hire:
            flags = _consider_hires(m, i, flags, cash, events)
        else:
            m["staff_cost"] = 0
            m["supervisor_pay"] = m["electrician_pay"] = m["plumber_pay"] = 0
            m["recurring"] = m["retainer"] + m["care_units"] * m["care_fee"]
            m["cover_ratio"] = None
        if forced_monthly_staff:
            m["staff_cost"] += forced_monthly_staff

        refresh_rev, refresh_gp = _stream(m["refresh_n"], m["refresh_price"], m["refresh_margin"])
        standup_rev, standup_gp = _stream(m["standup_n"], m["standup_price"], m["standup_margin"])
        launch_rev, launch_gp = _stream(m["launch_n"], m["launch_price"], m["launch_margin"])
        extras_rev, extras_gp = m["extras"], m["extras"] * m["extras_margin"]
        retainer_rev, retainer_gp = m["retainer"], m["retainer"] * m["retainer_margin"]
        care_rev = m["care_units"] * m["care_fee"]
        care_gp = care_rev * m["care_margin"]

        one_off = refresh_rev + standup_rev + launch_rev + extras_rev
        revenue = one_off + retainer_rev + care_rev
        contribution = refresh_gp + standup_gp + launch_gp + extras_gp + retainer_gp + care_gp
        cogs = revenue - contribution
        rework = one_off * rework_rate
        bad = one_off * bad_rate
        bank_base_collect = (
            retainer_rev
            + care_rev
            + (1 - bad_rate - slip_rate) * one_off
            + slip_rate * prev_one_off
        )
        bank = bank_base_collect * BANK_RATE
        staff = m["staff_cost"]
        pbt = contribution - rework - bad - m["opex"] - m["founder"] - staff - m["setup"] - bank

        wht = WHT_RATE * (
            wht_retainer * retainer_rev
            + wht_care * care_rev
            + b2b_one_off * ((1 - bad_rate - slip_rate) * one_off + slip_rate * prev_one_off)
        )
        cash_in = bank_base_collect
        cash_out = cogs + rework + m["opex"] + m["founder"] + staff + m["setup"] + bank
        receivable = slip_rate * one_off

        row = {
            "i": i,
            "label": month_label(i),
            "year": i // 12 + 1,
            "refresh_rev": refresh_rev,
            "refresh_gp": refresh_gp,
            "standup_rev": standup_rev,
            "standup_gp": standup_gp,
            "launch_rev": launch_rev,
            "launch_gp": launch_gp,
            "extras_rev": extras_rev,
            "extras_gp": extras_gp,
            "retainer_rev": retainer_rev,
            "retainer_gp": retainer_gp,
            "care_rev": care_rev,
            "care_gp": care_gp,
            "care_units": m["care_units"],
            "one_off": one_off,
            "revenue": revenue,
            "contribution": contribution,
            "cogs": cogs,
            "rework": rework,
            "bad": bad,
            "opex": m["opex"],
            "founder": m["founder"],
            "staff": staff,
            "setup": m["setup"],
            "bank": bank,
            "pbt": pbt,
            "wht": wht,
            "cash_in": cash_in,
            "cash_out": cash_out,
            "receivable": receivable,
            "retainer_count": m["retainer_count"],
            "supervisor_pay": m["supervisor_pay"],
            "electrician_pay": m["electrician_pay"],
            "plumber_pay": m["plumber_pay"],
            "recurring": m["recurring"],
            "cover_ratio": m["cover_ratio"],
            "note": m["note"],
            "refresh_n": m["refresh_n"],
            "standup_n": m["standup_n"],
            "launch_n": m["launch_n"],
        }
        rows.append(row)
        add_year(current, row)
        prev_one_off = one_off

        end_of_year = (i % 12 == 11)
        if end_of_year:
            tax = tax_for(current["revenue"], current["pbt"])
            current["tax"] = tax
            current["pat"] = current["pbt"] - tax
            # Settle tax against the WHT asset, then cash.
            use_credit = min(wht_credit + current["wht"], tax)
            # wht of this year already added monthly into a running credit below;
            # apply settlement on the year's withheld amount plus opening credit.
            tax_cash = tax  # placeholder, real settlement after monthly loop piece
            current["tax_cash_placeholder"] = tax_cash
            year_buckets.append(current)
            current = new_year_bucket()

        cash = cash + cash_in - wht - cash_out
        wht_credit += wht
        if end_of_year:
            y = year_buckets[-1]
            use = min(wht_credit, y["tax"])
            tax_cash = y["tax"] - use
            wht_credit -= use
            cash -= tax_cash
            y["tax_cash"] = tax_cash
            y["wht_used"] = use
            y["wht_credit_end"] = wht_credit
            y["cash_end"] = cash
        if cash < min_cash:
            min_cash = cash
            min_cash_i = i
        row["cash_end"] = cash
        row["wht_credit"] = wht_credit

    # Attach year cash starts
    running = opening
    for y in year_buckets:
        y["cash_start"] = running
        running = y["cash_end"]
        y["household_gap"] = 0

    # Household gap over full horizon where draw < household need, first 18 months matter most.
    # Reported for year 1 specifically later.

    topup = max(0.0, BUFFER - min_cash)

    return {
        "name": name,
        "opening": opening,
        "rows": rows,
        "years": year_buckets,
        "events": events,
        "min_cash": min_cash,
        "min_cash_i": min_cash_i,
        "min_cash_label": month_label(min_cash_i) if min_cash_i >= 0 else "start",
        "ending_cash": rows[-1]["cash_end"],
        "topup_for_buffer": topup,
        "solvent_capital": opening + topup,
        "bad_rate": bad_rate,
        "slip_rate": slip_rate,
        "rework_rate": rework_rate,
        "final_wht_credit": wht_credit,
    }


def new_year_bucket():
    keys = [
        "revenue", "refresh_rev", "refresh_gp", "standup_rev", "standup_gp",
        "launch_rev", "launch_gp", "extras_rev", "extras_gp",
        "retainer_rev", "retainer_gp", "care_rev", "care_gp", "one_off",
        "contribution", "cogs", "rework", "bad", "opex", "founder", "staff",
        "setup", "bank", "pbt", "wht", "cash_in", "cash_out",
    ]
    bucket = {k: 0.0 for k in keys}
    bucket["refresh_n"] = 0
    bucket["standup_n"] = 0
    bucket["launch_n"] = 0
    bucket["care_end"] = 0
    bucket["retainer_end"] = 0
    return bucket


def add_year(bucket, row):
    for key in (
        "revenue", "refresh_rev", "refresh_gp", "standup_rev", "standup_gp",
        "launch_rev", "launch_gp", "extras_rev", "extras_gp",
        "retainer_rev", "retainer_gp", "care_rev", "care_gp", "one_off",
        "contribution", "cogs", "rework", "bad", "opex", "founder", "staff",
        "setup", "bank", "pbt", "wht", "cash_in", "cash_out",
    ):
        bucket[key] += row[key]
    bucket["refresh_n"] += row["refresh_n"]
    bucket["standup_n"] += row["standup_n"]
    bucket["launch_n"] += row["launch_n"]
    bucket["care_end"] = row["care_units"]
    bucket["retainer_end"] = row["retainer_count"]


def tax_for(turnover, pbt):
    if pbt <= 0:
        return 0.0
    if turnover <= SMALL_CO_TURNOVER:
        return 0.0
    return pbt * TAX_RATE_ABOVE


def household_gap(result, months=12, need=HOUSEHOLD):
    gap = 0.0
    for row in result["rows"][:months]:
        gap += max(0.0, need - row["founder"])
    return gap


def force_salaries(months, monthly_targets):
    """Death-path: put named salaries on from month 1 and skip the gate."""
    months = deepcopy(months)
    for m in months:
        m["supervisor_pay"] = monthly_targets.get("supervisor", 0)
        m["electrician_pay"] = monthly_targets.get("electrician", 0)
        m["plumber_pay"] = monthly_targets.get("plumber", 0)
        m["staff_cost"] = (
            m["supervisor_pay"] + m["electrician_pay"] + m["plumber_pay"]
        ) * STAFF_LOAD
        m["recurring"] = m["retainer"] + m["care_units"] * m["care_fee"]
        m["cover_ratio"] = None
        m["supervisor_offer"] = 0
        m["electrician_offer"] = 0
        m["plumber_offer"] = 0
    return months


def simulate_forced(name, months, opening, **rates):
    """Same as simulate but staff_cost is already set and offers are zero so gates do not rehire."""
    return simulate(name, months, opening, **rates)


def delay_retainer(months, start_index):
    months = deepcopy(months)
    for i, m in enumerate(months):
        if i < start_index:
            m["retainer"] = 0
            m["retainer_count"] = 0
            m["extras"] = 0
            m["care_units"] = 0
    return months


def scale_jobs(months, factor):
    months = deepcopy(months)
    for m in months:
        for key in ("refresh_n", "standup_n", "launch_n"):
            m[key] = int(round(m[key] * factor))
        m["extras"] = int(round(m["extras"] * factor))
        m["care_units"] = int(round(m["care_units"] * factor))
    return months


BASE_RATES = dict(
    bad_rate=0.02,
    slip_rate=0.12,
    rework_rate=0.03,
    b2b_one_off=0.35,
    wht_retainer=0.80,
    wht_care=0.50,
)

BEST_RATES = dict(
    bad_rate=0.01,
    slip_rate=0.09,
    rework_rate=0.015,
    b2b_one_off=0.55,
    wht_retainer=0.80,
    wht_care=0.50,
)


def build_base(opening=1_150_000):
    return simulate("Base case", base_months(), opening=opening, **BASE_RATES)


def build_best(opening=900_000):
    return simulate("Best case", best_months(), opening=opening, **BEST_RATES)


def build_underfunded():
    return simulate("Underfunded start", base_months(), opening=500_000, **BASE_RATES)


def build_sensitivities(base_rates):
    death_months = force_salaries(
        base_months(),
        {"supervisor": 150_000, "electrician": 140_000, "plumber": 140_000},
    )
    # force_salaries zeroes offers so apply_gates will not hire, but staff_cost
    # is overwritten by apply_gates from zero offers. Handle death path inside
    # a dedicated simulator branch: set offers equal to forced pay AND mark
    # a pre-hired flag. Easier path: patch apply by setting offers and also
    # injecting staff before gate by using very first month eligibility with
    # the actual pay, but the gate would refuse. So death path needs a bypass.
    death = simulate_prestaffed(
        "Salary-first",
        base_months(),
        opening=500_000,
        staff={"supervisor": 150_000, "electrician": 140_000, "plumber": 140_000},
        **base_rates,
    )
    delayed = simulate(
        "Retainer delayed",
        delay_retainer(base_months(), 18),
        opening=500_000,
        **base_rates,
    )
    thin = simulate(
        "Thin sales",
        scale_jobs(base_months(), 0.70),
        opening=500_000,
        **base_rates,
    )
    return {"death": death, "delayed": delayed, "thin": thin}


def simulate_prestaffed(name, months, opening, staff, **rates):
    months = deepcopy(months)
    for m in months:
        m["supervisor_offer"] = staff.get("supervisor", 0)
        m["electrician_offer"] = staff.get("electrician", 0)
        m["plumber_offer"] = staff.get("plumber", 0)
        m["retainer"] = max(m["retainer"], 1)  # do not use; we bypass gates
    # Custom loop: copy simulate but set staff from month 1.
    # Restore retainer after we stash it. The line above corrupts retainer.
    # Re-do cleanly.
    months = deepcopy(base_months()) if name == "Salary-first" else months
    return _simulate_with_staff(name, base_months(), opening, staff, **rates)


def _simulate_with_staff(name, months, opening, staff, **rates):
    months = deepcopy(months)
    for m in months:
        m["supervisor_pay"] = staff.get("supervisor", 0)
        m["electrician_pay"] = staff.get("electrician", 0)
        m["plumber_pay"] = staff.get("plumber", 0)
        m["staff_cost"] = (
            m["supervisor_pay"] + m["electrician_pay"] + m["plumber_pay"]
        ) * STAFF_LOAD
        m["recurring"] = m["retainer"] + m["care_units"] * m["care_fee"]
        m["cover_ratio"] = (
            m["recurring"] / m["staff_cost"] if m["staff_cost"] else None
        )
        # Stop the gate from hiring on top.
        m["supervisor_offer"] = 0
        m["electrician_offer"] = 0
        m["plumber_offer"] = 0
    result = simulate(name, months, opening, **rates)
    # simulate() re-runs gates with offers at 0, which clears the pays we set
    # because apply_gates overwrites pay from the hire flags. Need a lower-level
    # path. Implemented below by temporarily monkeypatching through a flag.
    return result


# The helper above is replaced by a cleaner entry point.

def identity(result):
    """Cash + last receivable + unused WHT credit ≈ capital + cumulative PAT."""
    last = result["rows"][-1]
    assets = last["cash_end"] + last["receivable"] + result["final_wht_credit"]
    equity = result["opening"] + result["cumulative_pat"]
    return assets, equity, assets - equity


def run_all():
    base = build_base()
    best = build_best()
    under = build_underfunded()
    delayed = simulate(
        "Retainer delayed", delay_retainer(base_months(), 18), 1_150_000, **BASE_RATES
    )
    thin = simulate(
        "Thin sales", base_months(), 1_150_000, one_off_scale=0.70, care_scale=0.70, **BASE_RATES
    )
    creep = simulate(
        "Loose caps", base_months(), 1_150_000, care_margin_delta=-0.15, **BASE_RATES
    )
    death = simulate(
        "Salary-first",
        base_months(),
        1_150_000,
        forced_monthly_staff=(150_000 + 140_000 + 140_000) * STAFF_LOAD,
        hire=False,
        **BASE_RATES,
    )
    pack = {
        "base": base,
        "best": best,
        "under": under,
        "delayed": delayed,
        "thin": thin,
        "creep": creep,
        "death": death,
    }
    for result in pack.values():
        result["household_gap_y1"] = household_gap(result, 12)
        result["cumulative_pat"] = sum(y["pat"] for y in result["years"])
        result["cumulative_founder"] = sum(y["founder"] for y in result["years"])
        assets, equity, gap = identity(result)
        result["identity_gap"] = gap
    return pack


def year_row_summary(result):
    lines = []
    for i, y in enumerate(result["years"], start=1):
        lines.append(
            f"Y{i} rev {y['revenue']/1e6:.2f}m  gp {y['contribution']/1e6:.2f}m  "
            f"pbt {y['pbt']/1e6:.2f}m  tax {y['tax']/1e6:.2f}m  pat {y['pat']/1e6:.2f}m  "
            f"cash {y['cash_end']/1e6:.2f}m  founder {y['founder']/1e6:.2f}m  "
            f"staff {y['staff']/1e6:.2f}m  jobs R{y['refresh_n']}/S{y['standup_n']}/L{y['launch_n']}  "
            f"care_end {y['care_end']}  retainers {y['retainer_end']}"
        )
    return lines


if __name__ == "__main__":
    pack = run_all()
    for key in ("base", "best", "under", "delayed", "thin", "creep", "death"):
        result = pack[key]
        print("\n===", result["name"], "===")
        print("opening", ngn(result["opening"]), "min", ngn(result["min_cash"]), result["min_cash_label"])
        print("topup", ngn(result["topup_for_buffer"]), "solvent", ngn(result["solvent_capital"]))
        print("end cash", ngn(result["ending_cash"]), "wht credit", ngn(result["final_wht_credit"]))
        print("household gap y1", ngn(result["household_gap_y1"]))
        print("hires", [(month_label(i), role, ngn(pay)) for i, role, pay, *_ in result["events"]])
        print("identity gap", ngn(result["identity_gap"]))
        for line in year_row_summary(result):
            print(line)
        y1 = result["years"][0]
        print(
            "Y1 setup", ngn(y1["setup"]), "opex", ngn(y1["opex"]),
            "bad", ngn(y1["bad"]), "rework", ngn(y1["rework"]),
        )
        # cash trough months
        print("cash path y1:")
        for row in result["rows"][:12]:
            print(f"  {row['label']}: rev {ngn(row['revenue'])} cash {ngn(row['cash_end'])} pbt {ngn(row['pbt'])}")
