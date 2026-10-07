#!/usr/bin/env python3
"""Build the v4.2 bank-owned operator addendum. Does not rewrite v4 or v4.1."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(ROOT / "source"))

from operator_charts import draw  # noqa: E402
from operator_scenario import main  # noqa: E402

PDF_NAME = "CashEase_Bank_Owned_Operator_Addendum.pdf"


def short(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000:
        return f"{sign}₦{n / 1_000_000_000:.2f}bn"
    if n >= 1_000_000:
        return f"{sign}₦{n / 1_000_000:.2f}m"
    return f"{sign}₦{n:,.0f}"


def tx(n: float | None) -> str:
    if n is None:
        return "None"
    return f"{n:,.0f}"


def irr_s(v) -> str:
    if v is None:
        return "Not defined"
    return f"{v * 100:.1f}%"


def pb_s(v) -> str:
    if v is None:
        return "Not within 7 years"
    return f"{v:.1f} years"


def signed(n: float) -> str:
    if n < 0:
        return f"loss of {short(abs(n))}"
    return short(n)


def table(headers, rows, caption, tight=False) -> str:
    cap = f"<caption>{caption}</caption>"
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    cls = ' class="tight"' if tight else ""
    return f"<table{cls}>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CashEase Nigeria: Bank-Owned Operator Scenario</title>
<style>
@page { size: A4; margin: 14mm 13mm 18mm 13mm; }
* { box-sizing: border-box; }
html { font-size: 10.5pt; }
body { margin: 0; color: #1a242b; font-family: "Liberation Serif", "Times New Roman", serif; line-height: 1.45; padding-bottom: 8mm; }
h1, h2, h3 { font-family: "Liberation Sans", Arial, sans-serif; color: #1c3144; line-height: 1.2; }
h1 { font-size: 22pt; margin: 0 0 8px; }
h2 { font-size: 14.5pt; margin: 18px 0 8px; page-break-after: avoid; border-bottom: 1px solid #d5d0c8; padding-bottom: 4px; }
h3 { font-size: 12pt; margin: 14px 0 6px; page-break-after: avoid; }
p { margin: 0 0 8px; }
ul, ol { margin: 4px 0 10px; padding-left: 18px; }
li { margin: 0 0 4px; }
.cover { page-break-after: always; padding-top: 14mm; }
.kicker { font-family: "Liberation Sans", Arial, sans-serif; letter-spacing: 0.12em; text-transform: uppercase; font-size: 9pt; color: #8a6a2f; margin-bottom: 10px; }
.deck { font-size: 12.5pt; }
.verdict { border: 2px solid #8d2b2b; background: #f8f1f1; padding: 12px 14px; margin: 16px 0; page-break-inside: avoid; }
.verdict strong { display: block; font-family: "Liberation Sans", Arial, sans-serif; font-size: 13pt; color: #8d2b2b; margin: 2px 0 6px; }
.verdict span { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.5pt; letter-spacing: 0.14em; text-transform: uppercase; color: #8d2b2b; }
.meta { color: #5c6b73; font-size: 9.5pt; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-family: "Liberation Sans", Arial, sans-serif; font-size: 8pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
thead { display: table-header-group; }
caption { caption-side: bottom; text-align: left; font-size: 8.5pt; color: #5c6b73; padding-top: 4px; font-style: italic; font-family: "Liberation Serif", serif; }
th { text-align: left; background: #1c3144; color: white; padding: 4px 5px; font-weight: 600; vertical-align: bottom; }
td { padding: 3px 5px; border-bottom: 1px solid #e0dbd2; vertical-align: top; }
table.tight { font-size: 7.4pt; }
table.tight th, table.tight td { padding: 3px 4px; }
tr:nth-child(even) td { background: #f7f4ef; }
figure { margin: 8px 0 12px; page-break-inside: avoid; }
img { width: 100%; height: auto; }
figcaption { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.5pt; color: #5c6b73; margin-top: 4px; }
.callout { background: #f4efe4; border-left: 4px solid #8a6a2f; padding: 8px 12px; margin: 10px 0 12px; page-break-inside: avoid; }
.tag { font-family: "Liberation Sans", Arial, sans-serif; font-size: 7.5pt; letter-spacing: 0.04em; text-transform: uppercase; color: #8a6a2f; font-weight: 700; }
footer.running { position: fixed; bottom: 4mm; left: 0; right: 0; font-family: "Liberation Sans", Arial, sans-serif; font-size: 8pt; color: #5c6b73; border-top: 1px solid #d5d0c8; padding-top: 2px; background: white; }
sup { font-size: 7.5pt; }
.sources li { margin-bottom: 4px; font-size: 8.3pt; word-break: break-word; }
</style>
</head>
<body>
<footer class="running">CashEase Nigeria · Bank-owned operator addendum · 7 October 2026 · Planning document</footer>
"""


def build() -> None:
    r = main()
    charts = draw(r, ROOT / "charts")
    plain, custom, us = r["rows"]
    ce_take = 0.20 * r["gross"]
    bank_take = 0.80 * r["gross"] - r["shrink"]
    us_share_400 = us["ce"]["400"]["cash_cost"] / (us["ce"]["400"]["revenue"] / 0.20)

    fleet_rows = []
    for n in (5, 20, 50, 200):
        for volume in ("150", "250", "400"):
            fleet_rows.append([
                str(n),
                volume,
                short(plain["fleets"][str(n)][volume]["ce"]["profit"]),
                short(custom["fleets"][str(n)][volume]["ce"]["profit"]),
                short(us["fleets"][str(n)][volume]["ce"]["profit"]),
            ])

    fee_rows = []
    for n in (5, 20, 50, 200):
        fee = plain["fee"][str(n)]
        fee_rows.append([
            str(n),
            short(fee["machine_monthly"]),
            short(fee["firm_monthly"]),
            short(fee["firm_plus_one_engineer_monthly"]),
        ])

    share_rows = []
    for share in ("0.15", "0.2", "0.25", "0.3"):
        block = plain["shares"][share]
        share_rows.append([
            f"{float(share) * 100:.0f}%",
            short(block["150"]["ce"]["profit"]),
            short(block["400"]["ce"]["profit"]),
            irr_s(block["400"]["bank"]["irr"]),
            pb_s(block["400"]["bank"]["payback"]),
        ])

    bank_rows = []
    for row in r["rows"]:
        bank_rows.append([
            row["name"],
            short(row["all_in"]),
            tx(row["be_cash"]),
            tx(row["be_irr_mpr"]),
            tx(row["be_irr_28"]),
            irr_s(row["bank"]["400"]["irr"]),
            pb_s(row["bank"]["400"]["payback"]),
            short(row["bank"]["400"]["npv_28"]),
        ])

    body = f"""
<section class="cover">
  <p class="kicker">Addendum to the bank-backed machine study</p>
  <h1>CashEase Nigeria: Bank-Owned Operator Scenario</h1>
  <p class="deck">A v4.2 test in which the bank owns the machines and CashEase operates them for 20% of gross fee revenue.</p>
  <div class="verdict">
    <span>Verdict</span>
    <strong>No. Twenty percent does not work for both sides.</strong>
    <p>On the cheaper Chinese box, CashEase’s 20% covers servicing and monitoring at 250 and 400 transactions a day, and misses at 150. The ₦25 million office then needs about {tx(plain['office_machines']['250'])} of those machines at 250 transactions and about {tx(plain['office_machines']['400'])} at 400. Five machines lose money at every tested volume. The published US machine loses money for CashEase at all three volumes. The bank, keeping 80% and paying for the box, needs about {tx(plain['be_irr_28'])} transactions a day on the cheaper box to earn 28%. At 400 it earns {irr_s(plain['bank']['400']['irr'])}.</p>
  </div>
  <p class="meta">Prepared for Dotun, Lagos. Working name only. This paper does not replace v4 or the China-kiosk addendum. Currency is the naira. The model is nominal, pre-tax and flat for seven years. Discount rate 28%. Not investment, legal or tax advice. Figures tagged as assumptions are choices. CashEase has no operating history.</p>
</section>

<h2>1. The deal being costed</h2>
<p>The bank buys the machines, holds the cash and keeps 80% of the gross fee. CashEase runs the machines and keeps 20%. Gross fee is the v4 mix: 55% note-breaking at ₦100, 35% cash-out surcharge at ₦250, and 10% other fees at ₦30. That mix is ₦{r['gross']:.2f} a transaction. <span class="tag">Assumption</span> Shrink of ₦{r['shrink']:.2f} a transaction stays with the bank, because the bank owns the notes. It is not deducted before the 20% is calculated. CashEase therefore takes ₦{ce_take:.2f} a transaction. The bank’s fee after shrink is ₦{bank_take:.2f}.</p>
<p>Three machine prices are used, and no others. The two Chinese figures are the v4.1 high freight band for the Hongzhou US$4,800 kiosk: ₦16.43 million with no programming adder, and ₦19.13 million with the US$1,800 customization line inside the customs value. Both already include the ₦8 million site-works assumption and one ₦500,000 NIBSS pair. The third figure is the v4 published US reference, ₦65.53 million before duty. A 2014 BusinessDay report put average ATM support at US$2,500 a year.<sup>1</sup> That figure is twelve years old, so it is not in the arithmetic.</p>

<h2>2. Who pays</h2>
<p>The bank pays the machine, the float, rent, cash-in-transit, certification and the opportunity cost of the money. The float is the v4 assumption of ₦2.00 million a machine. Rent is ₦150,000 a month. Cash-in-transit is four visits a month at ₦40,000 a visit. Both are v4 assumptions. Certification for the Chinese cases is already inside the landed figures. The US case adds the same ₦500,000 NIBSS pair once, from the May 2024 sandbox note: ₦250,000 for a device and ₦250,000 for an application.<sup>2</sup> No CBN approval fee was found. The opportunity rate is the 23% policy rate reset at the 307th Monetary Policy Committee meeting.<sup>3,4</sup> The CBN’s own cost-of-funds framework also includes interbank borrowing, deposit-insurance premium and the cost of reserve requirements, and it excludes overhead.<sup>5</sup> A weekly deposit-rate table for 18 September 2026 is listed on the CBN site. The PDF returned 403, so no deposit rate from that file is used. Twenty-three percent is the policy rate. It is not a completed cost-of-funds formula.</p>
<p>CashEase pays servicing, software and monitoring, the data link, and its own overhead. Servicing is 10% of the ex-works price a year, the same rule of thumb as v4. On these three boxes that is {short(plain['ce']['150']['servicing'])}, {short(custom['ce']['150']['servicing'])} and {short(us['ce']['150']['servicing'])}. Monitoring is the v4 assumption of ₦400,000 a year. The data link is the v4 assumption of ₦18,000 a month. Overhead is the v4 assumption of ₦25 million a year plus ₦50,000 a machine. The ₦2 million software line inside the machine price stays with the bank, because it is part of the landed cost. It is not charged again as CashEase’s monitoring.</p>
<p><span class="tag">Assignment.</span> Power and on-site security were not named in this brief. They are the v4 assumptions, ₦688,160 and ₦1.44 million a year, and this paper puts them on the bank as site costs. Power uses the retail diesel price of ₦1,810 a litre on 6 October 2026 and the v4 energy assumptions.<sup>6</sup> Insurance at 1.5% of the machine plus the float also sits with the bank. A second bank view, further down, drops power and security so the assignment can be seen.</p>
<p>Field staff are not spread across machines. PayScale’s average base salary for a field service engineer in Nigeria is ₦1,085,000, from eight profiles, last updated 8 January 2026. The reported base range is ₦814,000 to ₦3 million.<sup>7</sup> The title is not “ATM technician”, and no published count of machines per engineer was found. The model therefore reports how much surplus pays one such salary. It does not invent a crew.</p>

<h2>3. CashEase, one machine</h2>
{table(
    ["Machine", "150", "250", "400", "Servicing"],
    [
        [row["name"], short(row["ce"]["150"]["profit"]), short(row["ce"]["250"]["profit"]), short(row["ce"]["400"]["profit"]), short(row["ce"]["150"]["servicing"])]
        for row in r["rows"]
    ],
    "Cash profit per machine at a 20% share, before the office and before any engineer. Revenue minus servicing, monitoring and the data link.",
    tight=True,
)}
<figure>
  <img src="../charts/{charts['ce']}" alt="CashEase profit per machine at three volumes">
  <figcaption>Figure 1. CashEase cash profit per machine at 20% of gross fees, before head office. The US bar is a loss at every tested volume.</figcaption>
</figure>
<p><span class="tag">Result</span> On the ₦16.43 million box, one machine at 150 transactions is a {signed(plain['ce']['150']['profit'])} a year. At 250 it is {short(plain['ce']['250']['profit'])}. At 400 it is {short(plain['ce']['400']['profit'])}. The ₦19.13 million box is a {signed(custom['ce']['150']['profit'])} at 150, then {short(custom['ce']['250']['profit'])} and {short(custom['ce']['400']['profit'])}. The US reference is a loss at all three volumes, from {short(abs(us['ce']['150']['profit']))} at 150 to {short(abs(us['ce']['400']['profit']))} at 400. Its servicing line alone is {short(us['ce']['150']['servicing'])}, against ₦{ce_take:.2f} a transaction.</p>
<p>At 400 transactions on the cheaper box, the surplus of {plain['engineer_machines']['400']:.1f} machines pays one engineer at ₦1,085,000. At 250 it takes the surplus of {plain['engineer_machines']['250']:.1f} machines. At 150 there is no surplus to pay anyone. That is a salary test. It is not evidence that one engineer can cover the sites.</p>

<h2>4. Fleets, and the office</h2>
{table(
    ["Fleet", "Transactions a day", "China, no adder", "China, US$1,800", "US reference"],
    fleet_rows,
    "CashEase fleet cash profit after the ₦25 million office and ₦50,000 a machine. Field-engineer salaries are not in this table.",
    tight=True,
)}
<p><span class="tag">Result</span> On the cheaper box, the office is covered at about {tx(plain['office_machines']['250'])} machines if each does 250 transactions a day, and at about {tx(plain['office_machines']['400'])} machines if each does 400. A fleet of 5 loses money at 150, 250 and 400. A fleet of 20 loses money at 150 and at 250, and makes {short(plain['fleets']['20']['400']['ce']['profit'])} at 400. A fleet of 50 makes {short(plain['fleets']['50']['250']['ce']['profit'])} at 250 and {short(plain['fleets']['50']['400']['ce']['profit'])} at 400. At 150 every fleet in the table loses money, and a larger fleet loses more, because each extra machine adds a loss.</p>
<p>The ₦19.13 million box needs about {tx(custom['office_machines']['250'])} machines at 250 transactions and about {tx(custom['office_machines']['400'])} at 400. Twenty of those machines at 400 make {short(custom['fleets']['20']['400']['ce']['profit'])}. The US reference has no positive per-machine profit at these volumes, so no fleet size covers the office. The v4 year-0 setup assumption of ₦40 million is not in these annual figures. An annual profit still has to recover that cash if it is spent.</p>

<h2>5. The bank’s 80%</h2>
<p>The bank’s cash profit is its fee after shrink, minus rent, cash-in-transit, power, security and insurance. The internal rate of return uses that cash profit for seven years. The float goes out at purchase and comes back at year 7. There is no salvage. The 23% opportunity charge is shown beside the return. It is not deducted a second time inside the return. The hurdle used in v4 is 28%, the policy rate plus a 5 percentage-point planning premium.</p>
{table(
    ["Machine", "Capital", "Cash break-even", "Transactions to earn 23%", "Transactions to earn 28%", "IRR at 400", "Payback at 400", "NPV at 400"],
    bank_rows,
    "One machine. Transactions are per scheduled open day. NPV is at 28%. Payback is undiscounted and includes the float coming back.",
    tight=True,
)}
<figure>
  <img src="../charts/{charts['bank']}" alt="Bank cash profit per machine at three volumes">
  <figcaption>Figure 2. Bank cash profit per machine on an 80% share, after rent, cash-in-transit, power, security and insurance. Cash profit is not the 28% test.</figcaption>
</figure>
<p><span class="tag">Result</span> On the cheaper box the bank’s cash turns positive at {tx(plain['be_cash'])} transactions a day. Earning the 23% policy rate takes {tx(plain['be_irr_mpr'])}. Earning 28% takes {tx(plain['be_irr_28'])}. At 400 transactions the cash profit is {short(plain['bank']['400']['cash_profit'])}, payback is {pb_s(plain['bank']['400']['payback'])}, the return is {irr_s(plain['bank']['400']['irr'])}, and NPV at 28% is {short(plain['bank']['400']['npv_28'])}. A flat 23% charge on the opening machine and float is {short(plain['bank']['400']['cost_of_funds'])} a year, which this cash profit covers, with {short(plain['bank']['400']['after_cof'])} left. The internal rate of return is still {irr_s(plain['bank']['400']['irr'])}, because the flat charge treats the whole outlay as outstanding for all seven years. The return is the figure the bank earns. At 150 the cash result is a loss of {short(abs(plain['bank']['150']['cash_profit']))}. At 250 it is {short(plain['bank']['250']['cash_profit'])}, and payback is not inside seven years.</p>
<p>The ₦19.13 million box needs {tx(custom['be_irr_28'])} transactions a day to earn 28%, and at 400 its return is {irr_s(custom['bank']['400']['irr'])}. The US reference needs {tx(us['be_irr_28'])} transactions a day. At 400 its cash profit is {short(us['bank']['400']['cash_profit'])} and its return is {irr_s(us['bank']['400']['irr'])}. Payback is not inside seven years. A 200-machine fleet of the cheaper box earns about {irr_s(plain['fleets']['200']['400']['bank']['irr'])} at 400 transactions, close to the one-machine rate, because the ₦500,000 certification pair is paid once.</p>
<div class="callout">
  <p><strong>Power and security.</strong> Drop those two v4 assumptions and the cheaper box breaks even on cash at {tx(plain['be_cash_named'])} transactions a day. At 400 its return becomes {irr_s(plain['bank_named_only']['400']['irr'])} and NPV at 28% becomes {short(plain['bank_named_only']['400']['npv_28'])}. The bank verdict in this paper keeps power and security in the cost. Taking them out is what produces a return above 28%.</p>
</div>

<h2>6. The share, and a monthly fee</h2>
{table(
    ["CashEase share", "CashEase at 150", "CashEase at 400", "Bank IRR at 400", "Bank payback at 400"],
    share_rows,
    "The cheaper Chinese box only. CashEase figures are one machine, before the office. The bank keeps the rest of the gross fee and still bears shrink.",
    tight=True,
)}
<p><span class="tag">Result</span> Raising CashEase from 15% to 30% raises CashEase’s profit and cuts the bank’s return. On the cheaper box, 15% and 20% both miss at 150 transactions. Twenty-five percent produces {short(plain['shares']['0.25']['150']['ce']['profit'])} before the office, and 30% produces {short(plain['shares']['0.3']['150']['ce']['profit'])}. At 400 transactions the bank’s return runs from {irr_s(plain['shares']['0.15']['400']['bank']['irr'])} at a 15% operator share to {irr_s(plain['shares']['0.3']['400']['bank']['irr'])} at 30%. None of those four shares earns the bank 28% at 400 transactions. On the US machine, CashEase would need about {us_share_400 * 100:.0f}% of gross fee revenue just to cover servicing, monitoring and the link at 400 transactions, before the office.</p>
<p>The monthly fee below is the extra naira, on top of the 20% share, that brings CashEase’s cash to zero at 150 transactions a day. The first column covers one cheaper machine’s own ops. The second also covers that machine’s share of the ₦25 million office. The third adds one field engineer at the PayScale average, spread across the fleet.</p>
{table(
    ["Fleet", "Machine only", "Machine and office", "Machine, office and one engineer"],
    fee_rows,
    "Monthly fee per machine, cheaper Chinese box, 150 transactions a day, on top of the 20% share. A zero would mean the 20% already covers that line.",
    tight=True,
)}
<p><span class="tag">Result</span> The machine-only fee is {short(plain['fee']['5']['machine_monthly'])} a month. It does not keep the firm whole. On five machines the fee that also carries the office is {short(plain['fee']['5']['firm_monthly'])} a machine a month. On 20 machines it is {short(plain['fee']['20']['firm_monthly'])}. On 50 it is {short(plain['fee']['50']['firm_monthly'])}. On 200 it is {short(plain['fee']['200']['firm_monthly'])}. One engineer changes those figures by a few thousand naira a machine. The ₦19.13 million box needs {short(custom['fee']['5']['machine_monthly'])} a month before the office. The US box needs {short(us['fee']['5']['machine_monthly'])} a month before the office.</p>

<h2>7. Verdict</h2>
<p>Twenty percent does not work for both parties on these numbers.</p>
<p>It can work for CashEase on the cheaper Chinese machines once volume is 250 or 400 transactions a day and the fleet is large enough to carry a ₦25 million office: about {tx(plain['office_machines']['250'])} machines at 250, and about {tx(plain['office_machines']['400'])} at 400. It does not work at 150 transactions without a fee. It does not work at five machines at any tested volume. It does not work on the published US machine at 150, 250 or 400, because the servicing rule is 10% of a ₦53.27 million ex-works price.</p>
<p>It does not work for the bank at the volumes a 20% operator can live on. The cheaper box pays its cash costs at {tx(plain['be_cash'])} transactions a day and pays the money back in {pb_s(plain['bank']['400']['payback'])} at 400, but the return is {irr_s(plain['bank']['400']['irr'])}. The bank needs about {tx(plain['be_irr_28'])} transactions a day to earn 28%. The US box needs about {tx(us['be_irr_28'])}. A higher share for CashEase makes that bank return worse. Dropping power and security is the change that pushes the cheaper box over 28% at 400 transactions, and those costs are still in the v4 assumptions.</p>

<h2>8. Workings</h2>
<p>Gross fee = 0.55 × 100 + 0.35 × 250 + 0.10 × 30 = 145.50. Shrink = 0.35 × 12,000 × 0.003 = 12.60.</p>
<p>CashEase naira per transaction at 20% = 0.20 × 145.50 = 29.10. Bank naira after shrink = 0.80 × 145.50 − 12.60 = 103.80.</p>
<p>Effective days = 300 × 0.90 = 270. Annual transactions = daily transactions × 270.</p>
<p>CashEase machine cost = 10% of ex-works + 400,000 + 216,000. Ex-works is US$4,800 × 1,331.69, or US$6,600 × 1,331.69, or US$40,000 × 1,331.69.</p>
<p>Office = 25,000,000 + 50,000 × machines. Break-even fleet = 25,000,000 / (machine profit − 50,000), when machine profit exceeds 50,000.</p>
<p>Bank cash cost = rent 1,800,000 + cash-in-transit 1,920,000 + power 688,160 + security 1,440,000 + 1.5% of (machine + 2,000,000).</p>
<p>Opening cash = machine + float, with the ₦500,000 NIBSS pair counted once on a fleet. Years 1 to 6 are the bank’s cash profit. Year 7 adds the float back. No debt and no salvage. The 23% line is opening cash × 0.23. It is not inside the return.</p>
<p>The monthly fee is the annual gap divided by 12. Recompute from <span class="small">model/operator_scenario.py</span>.</p>

<h2>9. Sources</h2>
<ol class="sources">
  <li>BusinessDay, 8 July 2014, average annual ATM support spend of US$2,500. Not used in the 2026 arithmetic. https://businessday.ng/technology/article/rising-maintenance-cost-force-banks-to-outsource-atm-management/</li>
  <li>NIBSS, May 2024 sandbox note. Device certification ₦250,000. Application certification ₦250,000. https://nibss-plc.com.ng/wp-content/uploads/2024/05/Step-By-Step-Certification-process-on-Sandbox-for-use-updated.pdf</li>
  <li>Central Bank of Nigeria, monetary-policy decisions, 307th meeting, policy rate reset to 23%. https://www.cbn.gov.ng/MonetaryPolicy/decisions.html</li>
  <li>The Nation, CBN cuts the policy rate to 23%. https://thenationonlineng.net/cbn-cuts-interest-rate-to-23-per-cent-in-major-policy-reset/</li>
  <li>CBN monetary-policy circular, framework for banks’ cost of funds: deposit interest, interbank borrowing, deposit insurance and reserve requirements; overhead excluded. https://policyvault.africa/wp-content/uploads/2024/09/NGA2304.pdf</li>
  <li>DailyFuels, diesel at ₦1,810 a litre, updated 6 October 2026. The litres and the solar-upkeep line are v4 assumptions. https://dailyfuels.com/nigeria/</li>
  <li>PayScale, field service engineer in Nigeria, average base ₦1,085,000, eight profiles, updated 8 January 2026. https://www.payscale.com/research/NG/Job=Field_Service_Engineer/Salary</li>
  <li>Arbiterz, NFEM close of ₦1,331.69 per dollar on 5 October 2026, the rate inside the v4.1 landed costs. https://arbiterz.com/naira-dollar-rate-october-6-2026-naira-trades-at-n1331-69-in-cbn-nfem-window/</li>
  <li>CBN publications list, deposit and lending rates for the week ended 18 September 2026. The PDF request returned 403, so no rate from it is used. https://www.cbn.gov.ng/Out/2026/BSD/WEEKLY%20INTEREST%20RATES%20as%20at%20September%2018th%202026xx.pdf</li>
</ol>
<p class="small">End of addendum. The v4 study and the China-kiosk addendum are unchanged.</p>
"""
    html_path = ROOT / "source" / "operator.html"
    pdf_path = ROOT / PDF_NAME
    html_path.write_text(HEAD + body + "\n</body>\n</html>\n", encoding="utf-8")
    proc = subprocess.Popen(
        [
            "google-chrome",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--user-data-dir=/tmp/chrome-cashease-v42",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        proc.wait(timeout=25)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    print("pdf", pdf_path, "bytes", pdf_path.stat().st_size if pdf_path.exists() else 0)


if __name__ == "__main__":
    build()
