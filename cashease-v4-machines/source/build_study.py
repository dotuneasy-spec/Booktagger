#!/usr/bin/env python3
"""Build the CashEase v4 machine-study HTML and PDF from the planning model."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(ROOT / "source"))

from charts import draw  # noqa: E402
from machine_model import landed, main, naira  # noqa: E402

CHROME = "google-chrome"
PDF_NAME = "CashEase_Bank_Backed_Machine_Feasibility.pdf"


def comma(n: float) -> str:
    return f"{n:,.0f}"


def tx(n: float | None) -> str:
    if n is None:
        return "Not reached"
    return f"{n:,.0f}"


def short(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000_000:
        return f"{sign}₦{n / 1_000_000_000_000:.2f}tn"
    if n >= 1_000_000_000:
        return f"{sign}₦{n / 1_000_000_000:.2f}bn"
    if n >= 1_000_000:
        return f"{sign}₦{n / 1_000_000:.1f}m"
    return f"{sign}₦{n:,.0f}"


def loss(n: float) -> str:
    return naira(abs(n))


def show_irr(value, label) -> str:
    if value is not None:
        return f"{value * 100:.1f}%"
    if label == "above_500":
        return "Above 500%"
    if label == "no_capital":
        return "No capital outlay"
    return "Not defined"


def show_pb(v) -> str:
    if v is None:
        return "Never"
    if v < 0.05:
        return "Immediate"
    return f"{v:.1f} years"


def html_table(headers, rows, caption=None, tight=False) -> str:
    cap = f"<caption>{caption}</caption>" if caption else ""
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    cls = ' class="tight"' if tight else ""
    return f"<table{cls}>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def find_fleet(fleets, key, n, volume):
    for row in fleets:
        if row["structure"] == key and row["n"] == n and row["tx"] == volume:
            return row
    raise KeyError((key, n, volume))


def find_sens(rows, key, note, fx):
    for row in rows:
        if row["structure"] == key and row["note_fee"] == note and row["fx_shock"] == fx and (
            fx > 0 or note in (50, 100, 200)
        ):
            if fx > 0 and note != 100:
                continue
            return row
    raise KeyError((key, note, fx))


def find_rate(rows, key, n, volume, rate):
    for row in rows:
        if row["structure"] == key and row["n"] == n and row["tx"] == volume and abs(row["rate"] - rate) < 1e-9:
            return row
    raise KeyError((key, n, volume, rate))


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CashEase Nigeria: Bank-Backed Machine Network Feasibility Study</title>
<style>
@page { size: A4; margin: 14mm 13mm 18mm 13mm; }
* { box-sizing: border-box; }
html { font-size: 10.5pt; }
body {
  margin: 0; color: #1a242b;
  font-family: "Liberation Serif", "Times New Roman", serif;
  line-height: 1.45;
  padding-bottom: 8mm;
}
h1, h2, h3, h4 { font-family: "Liberation Sans", Arial, sans-serif; color: #1c3144; line-height: 1.2; }
h1 { font-size: 22pt; font-weight: 700; margin: 0 0 8px; }
h2 { font-size: 14.5pt; margin: 20px 0 8px; page-break-after: avoid; border-bottom: 1px solid #d5d0c8; padding-bottom: 4px; }
h3 { font-size: 12pt; margin: 14px 0 6px; page-break-after: avoid; }
p { margin: 0 0 8px; }
ul, ol { margin: 4px 0 10px; padding-left: 18px; }
li { margin: 0 0 4px; }
.cover { page-break-after: always; padding-top: 12mm; }
.kicker { font-family: "Liberation Sans", Arial, sans-serif; letter-spacing: 0.12em; text-transform: uppercase; font-size: 9pt; color: #8a6a2f; margin-bottom: 10px; }
.deck { font-size: 12.5pt; }
.verdict { border: 2px solid #8d2b2b; background: #f8f1f1; padding: 12px 14px; margin: 16px 0; page-break-inside: avoid; }
.verdict strong { display: block; font-family: "Liberation Sans", Arial, sans-serif; font-size: 13pt; color: #8d2b2b; margin: 2px 0 6px; }
.verdict span { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.5pt; letter-spacing: 0.14em; text-transform: uppercase; color: #8d2b2b; }
.meta { color: #5c6b73; font-size: 9.5pt; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.2pt; page-break-inside: auto; }
tr, thead, tbody { page-break-inside: avoid; }
thead { display: table-header-group; }
caption { caption-side: bottom; text-align: left; font-family: "Liberation Serif", serif; font-size: 8.5pt; color: #5c6b73; padding-top: 4px; font-style: italic; }
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
.small { font-size: 9pt; color: #3d4a51; }
footer.running {
  position: fixed; bottom: 4mm; left: 0; right: 0;
  font-family: "Liberation Sans", Arial, sans-serif; font-size: 8pt; color: #5c6b73;
  border-top: 1px solid #d5d0c8; padding-top: 2px;
  background: white;
}
sup { font-size: 7.5pt; }
.sources li { margin-bottom: 4px; font-size: 8.4pt; word-break: break-word; }
</style>
</head>
<body>
<footer class="running">CashEase Nigeria · Bank-backed machine feasibility · 7 October 2026 · Planning document</footer>
"""


def build() -> None:
    r = main()
    charts = draw(r, ROOT / "charts")
    S = r["structures"]
    L = r["lines"]
    hw = r["hardware"]
    hw20 = landed(40_000, 0.20)
    sysv = r["system"]
    sites = r["sites"]
    days = r["days"]

    def F(key, n, volume):
        return find_fleet(r["fleets"], key, n, volume)

    def sens(key, note, fx=0.0):
        return find_sens(r["sensitivities"], key, note, fx)

    delta = S["v3"]["per_tx"]["ce"] - S["s60"]["per_tx"]["ce"]
    cash_save = L["cit"] + L["float_insurance"]
    cross = (cash_save / delta) / days
    gal_full = S["gallery"]["ce_full_cost"]
    gal_nose = (gal_full - L["security"]) / S["gallery"]["per_tx"]["ce"] / days
    gap_free = sysv["concession_free_notes"]["150"]["gap"]
    gap_econ = sysv["concession_econ"]["150"]["gap"]
    gap_com = sysv["commercial"]["150"]["gap"]

    who_rows = []
    for key in ("v3", "s60", "s50", "gallery", "managed", "concession"):
        w = S[key]["who"]
        who_rows.append([
            S[key]["name"], w["rent"], w["cit"], w["float"], w["capex"], w["maintenance"], w["finance"],
        ])

    be_rows = []
    for key in ("v3", "s60", "s50", "gallery", "concession", "managed"):
        s = S[key]
        be_rows.append([
            s["name"],
            f"₦{s['per_tx']['ce']:.2f}",
            tx(s["be_cash"]),
            tx(s["be_full"]),
            tx(s["be_debt_23"]),
        ])

    profit_rows = []
    for key in ("v3", "s60", "s50", "gallery", "concession", "managed"):
        s = S[key]
        profit_rows.append([
            s["name"],
            short(s["at"]["150"]["ce_cash_profit"]),
            short(s["at"]["150"]["ce_operating"]),
            short(s["at"]["250"]["ce_cash_profit"]),
            short(s["at"]["400"]["ce_cash_profit"]),
            short(s["at"]["400"]["ce_operating"]),
            short(s["at"]["400"]["npv_28"]),
            show_irr(s["at"]["400"]["irr"], s["at"]["400"]["irr_label"]),
            show_pb(s["at"]["400"]["payback"]),
        ])

    partner_rows = []
    for key in ("s60", "s50", "gallery", "concession", "managed"):
        s = S[key]
        partner_rows.append([
            s["name"],
            short(s["at"]["150"]["bank_full_profit"]),
            short(s["at"]["250"]["bank_full_profit"]),
            short(s["at"]["400"]["bank_full_profit"]),
            short(s["at"]["250"]["gov_revenue"]),
        ])

    def fleet_row(label, row):
        return [
            label,
            short(row["year0"]),
            short(row["ce_cash_profit"]),
            short(row["ce_operating"]),
            short(row["npv_28"]),
            show_irr(row["irr"], row["irr_label"]),
            show_pb(row["payback"]),
        ]

    fleet_rows = [
        fleet_row("50 · 60/40 · 250 tx", F("s60", 50, 250)),
        fleet_row("50 · 60/40 · 400 tx", F("s60", 50, 400)),
        fleet_row("50 · gallery · 400 tx", F("gallery", 50, 400)),
        fleet_row("500 · 60/40 · 400 tx", F("s60", 500, 400)),
        fleet_row("500 · 50/50 · 400 tx", F("s50", 500, 400)),
        fleet_row("1,500 · 60/40 · 400 tx", F("s60", 1500, 400)),
        fleet_row("1,500 · 50/50 · 400 tx", F("s50", 1500, 400)),
        fleet_row("20,000 · concession · 150 tx", F("concession", 20000, 150)),
        fleet_row("20,000 · concession · 250 tx", F("concession", 20000, 250)),
        fleet_row("20,000 · concession · 400 tx", F("concession", 20000, 400)),
    ]

    def rate_row(label, row):
        return [
            label,
            f"{row['rate'] * 100:.0f}%",
            short(row["annual_service"]),
            short(row["cash_profit_before_debt"]),
            short(row["npv_28"]),
            show_irr(row["irr"], None),
        ]

    rate_rows = []
    for label, key, n, volume in (
        ("50 machines, 60/40, 400 tx", "s60", 50, 400),
        ("500 machines, 60/40, 400 tx", "s60", 500, 400),
        ("20,000 concession, 250 tx", "concession", 20000, 250),
        ("20,000 concession, 400 tx", "concession", 20000, 400),
    ):
        for rate in (0.23, 0.07, 0.0):
            rate_rows.append(rate_row(label, find_rate(r["interest_cases"], key, n, volume, rate)))

    sens_rows = []
    for key, name in (("s60", "60/40"), ("concession", "Concession"), ("gallery", "Gallery")):
        for note, sur_label in ((50, "₦50 / ₦150"), (100, "₦100 / ₦250"), (200, "₦200 / ₦500")):
            row = sens(key, note, 0.0)
            shown = "Note fee only" if key == "gallery" else sur_label
            sens_rows.append([
                name,
                shown if note != 100 or key == "gallery" else sur_label,
                f"₦{row['ce_per_tx']:.2f}",
                tx(row["be_full"]),
                short(row["npv_400"]),
                "Base FX",
            ])
        fxrow = sens(key, 100, 0.20)
        sens_rows.append([
            name,
            "₦100 / ₦250" if key != "gallery" else "Note fee ₦100",
            f"₦{fxrow['ce_per_tx']:.2f}",
            tx(fxrow["be_full"]),
            short(fxrow["npv_400"]),
            "FX +20% on the machine",
        ])

    ceiling_rows = []
    for key in ("v3", "s60", "s50", "gallery", "concession"):
        c = r["ceilings"][key]
        ceiling_rows.append([
            S[key]["name"],
            "No price works" if c["150"] is None else short(c["150"]),
            "No price works" if c["250"] is None else short(c["250"]),
            "No price works" if c["400"] is None else short(c["400"]),
        ])

    m50 = F("managed", 50, 250)
    m20 = F("managed", 20000, 250)
    c20_150 = F("concession", 20000, 150)
    c20_400 = F("concession", 20000, 400)
    s500 = F("s60", 500, 400)
    s1500 = F("s60", 1500, 400)
    s50_400 = F("s60", 50, 400)

    body = f"""
<section class="cover">
  <p class="kicker">Feasibility study</p>
  <h1>CashEase Nigeria: Bank-Backed Machine Network Feasibility Study</h1>
  <p class="deck">CashEase would own change-and-cash kiosks. A partner bank would hold the licence, supply small notes, run cash-in-transit and settle. This study tests whether that structure makes the machines feasible.</p>
  <div class="verdict">
    <span>Verdict</span>
    <strong>No-go on buying machines. Phase 1, Phase 2 and Phase 3 all fail.</strong>
    <p>A 60/40 fee share does not pay for a {naira(hw['all_in_ngn'])} machine. Off-site, CashEase still needs {tx(S['s60']['be_full'])} transactions on a scheduled open day to cover its own full cost. A bank gallery is on-site, so the ₦500 off-site surcharge does not apply, and the full-cost line there is {tx(S['gallery']['be_full'])} transactions. The concession, with free rent and bank-paid cash handling, still needs {tx(S['concession']['be_full'])}. Published address lists sum to {comma(sites['listed_sum'])} places before overlap and before any traffic test. That is the site screen behind a 20,000-machine target. The only open door is a bank-owned handful of machines, paid for by the bank, used to measure the change fee.</p>
  </div>
  <p class="meta">Prepared for Dotun, Lagos. Working name only. Company registration was not checked. Currency is the naira. The model is nominal, pre-tax and flat for seven years. The discount rate is 28%: the 23% policy rate plus a 5 percentage-point planning premium. This document is not investment, legal or tax advice. Figures tagged as assumptions are choices. CashEase has no operating history. The v3 study is unchanged and is the source of the machine price, the fee mix and the regulatory file reused here.</p>
</section>

<h2>1. How to read the numbers</h2>
<p>Three kinds of figure appear below.</p>
<ul>
  <li><strong>Sourced.</strong> An external fact, with a bracketed number that points to the source list. Where two sources disagree, both are shown.</li>
  <li><strong><span class="tag">Assumption</span>.</strong> A planning choice: the fee mix, the rent, the uptime, the 60/40 split, the 15% management fee, the head-office budget. Each one can be replaced with a contract or a quote.</li>
  <li><strong><span class="tag">Result</span>.</strong> Arithmetic. Break-even, profit, cash flow, payback, NPV and IRR are results. They are not forecasts of how many people will use a machine.</li>
</ul>
<p>The reference machine is the same one as in v3: a deposit-capable ATM at the bottom of a published US range, {comma(hw['usd'])} dollars, converted at the official ₦{r['fx']:,.2f} per dollar on 5 October 2026.<sup>31,43</sup> <span class="tag">Result</span> Ex-works {naira(hw['exworks_ngn'])}. Freight is an 8% assumption. Install, solar and software are a ₦8.00 million assumption. All-in before import duty is {naira(hw['all_in_ngn'])}. Duty is excluded until a customs code exists. Duty would make the machine dearer.</p>
<p>The v3 checks reprint. Full fixed cost of one owner-operated machine is {naira(r['v3_full_fixed_check'])}. Cash-cost break-even is {tx(S['v3']['be_cash'])} transactions a scheduled open day. Full-cost break-even is {tx(S['v3']['be_full'])}. At 400 transactions the one-machine NPV is {short(S['v3']['at']['400']['npv_28'])} and the capex that would earn 28% is {naira(r['ceilings']['v3']['400'])}. Those are the v3 results, recovered here so this paper is tied to the same file.</p>
<p>Test volumes of 150, 250 and 400 transactions a scheduled open day are assumptions. They are not observed kiosk counts. Uptime of 90% on 300 scheduled days gives {days:.0f} effective days, so 400 transactions a day is {comma(400 * days)} transactions a year. The only public busy-site anecdote in the file is 80 to 100 POS transactions a day, and it is a blog, not a NIBSS average.<sup>60</sup></p>

<h2>2. Verdict by phase</h2>
<h3>Phase 1 — 20 to 50 machines. No-go if CashEase buys them.</h3>
<p>The proposed sites are bank ATM galleries and forecourts, plus the busiest parks, markets and BRT hubs. A gallery or forecourt of the cash-providing bank is an on-site ATM. From 1 March 2025 the deployer surcharge of up to ₦500 per ₦20,000 is an off-site charge. On-site, another bank’s customer pays ₦100 per ₦20,000, and the customer’s own bank is free.<sup>16,51</sup> v3 did not treat the ₦100 as deployer income. This study does not either. <span class="tag">Result</span> CashEase’s take at a gallery, on a 60% share of what remains after shrink, is ₦{S['gallery']['per_tx']['ce']:.2f} a transaction. Full-cost break-even is {tx(S['gallery']['be_full'])} transactions a scheduled open day. At 400 transactions the machine still loses {loss(S['gallery']['at']['400']['ce_cash_profit'])} of cash a year and {loss(S['gallery']['at']['400']['ce_operating'])} after depreciation. Fifty galleries have an unlevered NPV of {short(F('gallery', 50, 400)['npv_28'])}.</p>
<p>A park or market can be off-site, so the ₦250 surcharge assumption can apply there. That is the 60/40 case. <span class="tag">Result</span> Full-cost break-even is {tx(S['s60']['be_full'])} transactions. At 400 the cash loss is {loss(S['s60']['at']['400']['ce_cash_profit'])} a machine. Fifty off-site machines at that volume have an unlevered NPV of {short(s50_400['npv_28'])}. Phase 1 fails at the gallery and at the park.</p>
<div class="callout">
  <p><strong>The only Phase 1 step that survives.</strong> A bank owns a handful of machines, pays the box, the maintenance, the cash and the site, and CashEase is paid to watch the meter. At a 15% fee assumption, CashEase’s own monitoring cost is covered once a machine does about {tx(S['managed']['be_full'])} transactions a day. The bank, on the same machine, loses {loss(S['managed']['at']['150']['bank_full_profit'])} a year at 150 transactions and {loss(S['managed']['at']['400']['bank_full_profit'])} at 400. That is a measurement the bank would be choosing to fund. It is not a rollout of 20 to 50 CashEase-owned boxes.</p>
</div>

<h3>Phase 2 — 100 to 1,500 commercial machines. No-go.</h3>
<p>Phase 2 is the 60/40 or 50/50 commercial case, off-site, with CashEase still buying the machines. <span class="tag">Result</span> Five hundred machines at 400 transactions a day, under 60/40, lose {loss(s500['ce_cash_profit'])} of cash a year after head office and {loss(s500['ce_operating'])} after depreciation. Unlevered NPV is {short(s500['npv_28'])}. The IRR is not defined: every cash flow in the seven years is negative, including the year the project ends. One thousand five hundred machines at the same volume have an unlevered NPV of {short(s1500['npv_28'])}. The 50/50 split is worse at every test volume, because CashEase gives away more of the fee and still depreciates the same box.</p>
<p>Giving the bank 40% of all fees, in exchange for the bank paying cash-in-transit and the float, helps CashEase only while volume is low and the result is still a large loss. <span class="tag">Result</span> The cash-profit crossover is about {cross:,.0f} scheduled transactions a day. Below that, 60/40 loses less cash than v3. Above it, 60/40 loses more, because ₦{delta:.2f} a transaction given away overtakes the {naira(cash_save)} a year of cash-handling cost the bank has taken. The volumes at which a machine could approach break-even sit above that crossover. The share makes the owner worse off exactly where the owner would need the help.</p>

<h3>Phase 3 — about 20,000 machines under a concession. No-go.</h3>
<p>The sketch is a 10-to-15-year build-operate-transfer concession, free public sites, CBN notes, a sandbox, concessional debt, and a 50/30/20 split of fees. The evidence contradicts the economics of that sketch.</p>
<ul>
  <li><span class="tag">Result</span> CashEase’s full-cost break-even under the concession split is {tx(S['concession']['be_full'])} transactions a scheduled open day, not 100 to 150. Cash costs alone, before depreciation, need {tx(S['concession']['be_cash'])}.</li>
  <li><span class="tag">Result</span> If rent, cash-in-transit and the float are all free, the fees of the whole project still need {tx(sysv['concession_free_notes']['be_tx'])} transactions a day to cover power, security, maintenance, insurance and depreciation. At 150 transactions the gap is {naira(gap_free)} a machine, or {naira(gap_free * 20000)} a year across 20,000 machines.</li>
  <li><span class="tag">Result</span> The address lists found for this paper sum to {comma(sites['listed_sum'])}. Active ATMs in the first half of 2024 were {comma(sites['atms'])}.<sup>1</sup> Neither figure is a stock of empty sites that clear the break-even above.</li>
  <li>A zero interest rate, which no lender has offered, still leaves the 20,000-machine NPV at {short(find_rate(r['interest_cases'], 'concession', 20000, 400, 0.0)['npv_28'])} when each machine does 400 transactions a day. Debt service is not the thing that breaks the case. The operating cash is already negative.</li>
</ul>
<p>Section 6 counts the sites. Section 8 counts the money. Section 9 shows that the interest rate, the foreign-exchange rate and the fee do not reverse it.</p>

<h2>3. The structure under test, and where the sketch breaks</h2>
<p>Five structures are calculated. The first is v3, kept so the new contracts can be compared with the owner-pays case. The others are readings of the brief. The split, the management fee and the head-office budget are assumptions. No term sheet was provided.</p>
{html_table(
    ["Structure", "Rent", "CIT", "Float", "Capex", "Maintenance", "Finance"],
    who_rows,
    "Who pays. CIT is cash-in-transit. The float is the stock of notes in the machine.",
    tight=True,
)}
<p>The fee pool starts from the v3 mix. <span class="tag">Assumption</span> 55% of transactions are note-breaks at ₦100, 35% are cash-outs at a ₦250 deployer surcharge, and 10% are airtime or bills at ₦30 net. Gross is ₦145.50. Shrink on the cash-out slice is ₦12.60. The pool after shrink is ₦132.90. A 60/40 share gives CashEase ₦{S['s60']['per_tx']['ce']:.2f}. A 50/50 share gives ₦{S['s50']['per_tx']['ce']:.2f}. v3 gave the bank only a quarter of the surcharge, so CashEase kept ₦{S['v3']['per_tx']['ce']:.2f}. The new share is a larger giveaway.</p>
<p>On a gallery the surcharge is set to zero. Shrink stays, because the cash still leaves the machine. The pool falls to ₦{S['gallery']['per_tx']['distributable']:.2f} and CashEase’s 60% is ₦{S['gallery']['per_tx']['ce']:.2f}.</p>
<p>The concession takes the ICRC annual fee of 1% of gross off the top, then splits what remains 50/30/20.<sup>63,65</sup> <span class="tag">Result</span> CashEase keeps ₦{S['concession']['per_tx']['ce']:.2f} a transaction. The 1% was missing from the sketch. It is small beside depreciation. It is still a real claim on gross, and the Commission’s own guide calls it mandatory.</p>
<p>Managed service gives CashEase 15% of the pool after shrink, which is ₦{S['managed']['per_tx']['ce']:.2f} a transaction, and a monitoring budget of {naira(L['monitoring'])} a machine. <span class="tag">Assumption</span> The bank pays every other line, including the machine. That 15% is not a negotiated fee.</p>
<p>Other corrections, each one tied to a source or to the arithmetic:</p>
<ul>
  <li>From 1 January 2026, banks may load every denomination in an ATM.<sup>74,75</sup> The 2020 guidelines already said every ATM shall be able to dispense every denomination.<sup>72</sup> Permission to load a cassette is not evidence that the cassette holds ₦200 and ₦500 notes. In July 2026 the CBN governor still described the lower notes as scarce, and he tied that scarcity to falling demand.<sup>35,36</sup></li>
  <li>No CBN sandbox instrument covering a note-breaking kiosk was found. Sandbox access is not a planning input.</li>
  <li>No Nigerian ex-works quote for local assembly was found. This study applies no percentage discount. Section 9 states the delivered price that would be required, and shows that at 150 and 250 transactions a day no price works.</li>
  <li>No AFC or Afreximbank naira rate for an ATM network was found. The 7% line in the sensitivity is the published Bank of Industry GLOW rate. GLOW is for women-led firms and is capped at ₦50 million.<sup>56</sup> It is the wrong product. It is used only as a sourced low-rate bound.</li>
  <li>A 10-to-15-year concession outlasts the seven-year machine life used here. Salvage is zero. A second machine at year 7 would be another {naira(hw['all_in_ngn'])} at today’s price. The model does not treat that replacement as free. Because the seven-year cash flows are already negative, a second purchase cannot create a return.</li>
  <li>State parks, LAMATA stations and LASPARK sites are state assets. The ICRC Act, as restated in the August 2025 notice, covers public-private partnerships of federal ministries, departments and agencies.<sup>66</sup> A federal certificate does not hand over a state market.</li>
</ul>

<h2>4. Customer demand and fee tolerance</h2>
<p>People in Nigeria still hold and withdraw cash. Currency in circulation was ₦5.73 trillion at the end of 2025.<sup>32</sup> In June 2026 it was ₦5.523 trillion, of which ₦4.92 trillion sat outside banks.<sup>33</sup> In August 2026 currency outside banks was ₦4.87 trillion.<sup>34</sup> The payments vision described with those figures aims to cut cash outside banks to below 40% of currency in circulation by 2028. Policy is pointed at less cash in pockets.</p>
<p>ATM withdrawals in the first quarter of 2025 were ₦4.81 trillion, ₦5.40 trillion and ₦5.76 trillion by month.<sup>13</sup> <span class="tag">Result</span> The quarter sums to ₦15.97 trillion. A headline of ₦15.98 trillion is ₦0.01 trillion above that sum.<sup>15</sup> This study uses ₦15.97 trillion. The first half of 2025 was ₦36.34 trillion and 858.80 million withdrawals.<sup>13,14</sup> The rise followed the fee change. It is evidence that people still take cash. It is not a count of note-breaking.</p>
<p>The ATM network is thin beside peers and tiny beside POS. Active ATMs in the first half of 2024 were 16,714.<sup>1</sup> ATMs per 100,000 adults in 2024 were 12.83 in Nigeria, 10.97 in Ghana, 6.42 in Kenya, 24.47 in India, 37.06 in Egypt and 45.96 in South Africa.<sup>3,4,5</sup> Deployed POS terminals at the end of March 2025 were 5.90 million, with 8.36 million registered.<sup>8</sup> The CBN’s own POS series and the NIBSS series do not measure the same thing. First-half 2024 CBN POS value was ₦85.91 trillion. NIBSS first-quarter 2025 POS value was ₦10.45 trillion on the NIBSS site and ₦10.49 trillion on a monthly sum. ₦10.51 trillion was not found.<sup>2,9,11</sup> They must not be added together. <span class="tag">Result</span> Using the 2025 population of 237,527,782, there is one mid-2024 ATM per {comma(round(r['people_per_atm']))} residents, and one deployed POS per {r['sites']['population'] / r['sites']['pos']:,.0f} residents.<sup>6,7</sup> The ratios mix vintages. They are scale checks.</p>
<p>Agents did the work ATMs did not. EFInA’s 2023 survey shows formal inclusion at 64%, up from 56% in 2020, with about 40 million adults still formally excluded, and overall inclusion at 74%. Agent use rose from 4.4% of adults in 2018 to 54% in 2023. The full report says 58.3 million adults use a banking product and 45.4 million use an informal mechanism.<sup>39,40</sup> A new cash-out machine stands next to that agent network. Note-breaking is the piece a normal POS terminal does not do.</p>
<p>Small notes are the product, and the issuer is not promising more of them. On 21 July 2026 Governor Cardoso said ₦5, ₦10, ₦20, ₦50 and ₦100 notes remained legal tender, and he put the scarcity down to digitisation and to the weak purchasing power of those notes.<sup>35,36</sup> Traders told Daily Trust they struggle to find change.<sup>37</sup> Economists quoted elsewhere say banks rarely pay the lower denominations out.<sup>38</sup> Both accounts can be true. No CBN table found for this study splits the cash stock by denomination. The share that is ₦200 and below is unknown.</p>
<p>What a customer will pay is also unknown. No willingness-to-pay survey was found, so none is invented. The legal ceiling on the deployer is the off-site surcharge of ₦500 per ₦20,000, and it must be shown on the screen.<sup>51</sup> The separate ₦100 per ₦20,000 is not modelled as CashEase income. A ₦100 fee to break a note is an assumption. Moniepoint’s published card charge is 0.5% on ₦1 to ₦20,000 and ₦100 above ₦20,000, with an ₦80,000 floor on a day’s takings.<sup>41</sup> Customers already have a cash-out price in the market.</p>
<p><span class="tag">Result</span> At the top of the range this study will test, a ₦200 note fee and a ₦500 surcharge, the 60/40 full-cost break-even is still {tx(sens('s60', 200)['be_full'])} transactions a day, and the one-machine NPV at 400 transactions is {short(sens('s60', 200)['npv_400'])}. The concession at those fees still needs {tx(sens('concession', 200)['be_full'])} transactions and has a one-machine NPV of {short(sens('concession', 200)['npv_400'])}. Fee tolerance, even if every customer paid the top of that range, does not carry the published machine. From 1 January 2026 an ATM withdrawal is also capped at ₦100,000 a day per customer, inside a weekly cap of ₦500,000 for an individual.<sup>74,75</sup> Whether a pure note-for-note swap sits inside that cap is a question for counsel. It is not assumed away.</p>

<h2>5. Regulation and the legal structure</h2>
<p>Three paths stay distinct. They were distinct in v3, and the new contract does not merge them.</p>
{html_table(
    ["Path", "What it is", "What the public record says"],
    [
        ["Human agent", "A person takes cash in and pays cash out for one principal", "Guidelines of 6 October 2025. A non-human machine is quoted as barred from being the agent."],
        ["Independent ATM", "A deployer runs a machine with prior CBN approval and a bank that provides the cash", "Circular reported on 13 March 2026. This is the licence path in the brief."],
        ["Note exchange", "Notes in, notes of the same total out, plus a fee", "No published private licence, and no published ban. The CBN Act gives the Bank the currency."],
    ],
    "The machine cannot take the agent path. The bank-licence path is the one this study costs.",
)}
<p>Law firms quoting the 6 October 2025 agent guidelines cite a bar on non-human and automated machines as agents, together with customer cash-in and cash-out limits of ₦100,000 a day and ₦500,000 a week, a bill limit of ₦100,000, an agent cash-out limit of ₦1.2 million a day, exclusivity, a dedicated account, and a geo-fence.<sup>18,19,20,21,22,23</sup> The official CBN PDF returned an access error when this project was checked on 7 October 2026.<sup>24</sup> The signed file was not opened. Geo-fence enforcement moved to 1 August 2026, and the radius in the later report is 70 metres rather than 10.<sup>16,17</sup> That date has passed. None of the agent caps are used as the capacity of an ATM. They are the reason the machine cannot be dressed up as an agent.</p>
<p>The independent-ATM route, as reported from the 13 March 2026 circular, requires prior written CBN approval, a bank that provides the cash, and interoperability. Card issuers are to reach one ATM per 7,500 cards by 2028, with 30% of that ratio in 2026 and 60% in 2027.<sup>16,49,50</sup> The 2020 electronic-payment guidelines, which those later rules are reported to have replaced in part, say that all ATMs shall be able to dispense all denominations of naira, and that funding of an ATM deployed by a non-bank is the sole responsibility of the bank that agreed to provide the cash.<sup>50,72,73</sup> This study did not re-read a March 2026 PDF line by line on denominations. The open 2020 file and the January 2026 cash circular are the texts quoted here. The January circular says denominations may be loaded. It also removes deposit limits and sets the withdrawal caps above.<sup>74,75</sup> Excess withdrawals are charged at 3% for individuals and 5% for corporates. BusinessDay describes the split of those charges as 40% to the CBN and 60% to the institution.<sup>75</sup></p>
<p>Sections 17 to 20 of the CBN Act 2007 give the Bank the sole right to issue notes and the exchange function at its offices and at appointed agencies.<sup>25,26</sup> A private note-for-note fee has no published licence and no published prohibition. Counsel has to say which side of that line a change kiosk sits on before anyone bolts one to a floor. The ATM-approval path does not, by itself, answer the note-exchange question.</p>
<p>A federal concession is a separate legal object. The August 2025 ICRC notice says the Commission covers every federal public-private partnership, and that an approval without an ICRC certificate of compliance is null and void.<sup>66</sup> The approval thresholds sit in circular SGF.59804/II/243 of 7 July 2025, as cited in the Project Approval Board guide.<sup>67</sup> An unsolicited proposal needs an outline business case, a financial model, a draft agreement, a non-refundable fee, and later a project bond of 1% to 5% of project cost.<sup>64</sup> The fee schedule tops out at ₦100 million once project cost is above ₦100 billion. <span class="tag">Result</span> The 20,000-machine capex in this model is {naira(c20_400['capex'])}, so a proposal at that size would sit in the top band. The ₦100 million is included in that case’s year-0 cash. It does not drive the result. The bond is a requirement, not a cost charged in the profit and loss.</p>
<p>The financial-model guide says government may take an agreed revenue share on a user-fee partnership, and that ICRC fees may include a one-off charge of up to 5% of entry fees plus a mandatory 1% of gross revenue.<sup>63</sup> “Entry fees” is not defined as a share of capex in the pages read here, so 5% of capex is not charged. The 1% of gross is charged, because both the guide and the 2026 model agreement treat it as payable by the concessionaire.<sup>65</sup> The government’s 20% in the sketch is an extra assumption on top of that 1%. It is not a substitute for it.</p>
<p>Lagos parks, LAMATA and LASPARK are not federal MDA assets. A federal build-operate-transfer agreement cannot be assumed to include them. Each state concession would be its own statute, its own approval and its own site list. None of those documents exists for this project.</p>

<h2>6. How many sites clear break-even</h2>
<p>No public file gives daily transactions at Nigerian markets, parks, post offices or local-government counters. The number of sites that clear break-even is therefore unknown. What can be counted is the list of addresses, and the volume a site would have to produce.</p>
{html_table(
    ["Published list", "Count", "What it is"],
    [
        ["Local government areas and FCT area councils", "774", "Constitution, section 3(6): 768 local governments and six area councils."],
        ["Post offices and postal agencies, 2025", "2,048", "NBS postal data, unchanged from 2024. The breakdown sums to 2,048."],
        ["Lagos parks on the books, November 2024", "30", "The register. The same report says well over 100 parks are unregulated. That is not a census."],
        ["Lagos–Ibadan standard-gauge stations", "10", "Reported at commissioning. This is one line, not a national station census."],
        ["LAMATA Blue Line, planned", "13", "Okokomaiko to Marina, on LAMATA’s own page."],
        ["LAMATA Red Line, proposed", "12", "Agbado to Marina. The same page names eight first-phase stops."],
        ["Sum of the rows above", comma(sites["listed_sum"]), "Before removing places that appear twice, and before asking whether anyone would use a machine there."],
    ],
    "Address lists. Sources 27, 28, 44, 61, 62, 68, 69, 70 and 71. Adding the rows double-counts junctions such as Agbado and Agege.",
    tight=True,
)}
<figure>
  <img src="../charts/{charts['sites']}" alt="Bar chart comparing listed addresses, active ATMs and the 20,000 target">
  <figcaption>Figure 1. The lists that were found, the mid-2024 ATM stock, and the 20,000-machine target. The ATM bar is an existing network, not a set of empty pads.</figcaption>
</figure>
<p>The postal breakdown reported with the 2025 release is 730 post offices or departments, 110 head post offices, 667 post shops, 201 postal agencies, 136 counter extensions, 115 branch offices and 89 sub-post offices.<sup>61</sup> <span class="tag">Result</span> Those seven numbers sum to 2,048. An older NIPOST page that speaks of a 120 million population was not used. Putting 20,000 machines on 2,048 outlets would be about {20000 / 2048:.1f} machines per outlet. Putting them on 774 local authorities would be {20000 / 774:.1f} machines per authority. The v3 scale check still holds: 20,000 machines would be {20000 / 16714:.2f} times the mid-2024 ATM stock.</p>
<p>Other lists were found and not added, because they overlap Lagos and they are not national. PPIAF’s older assessment names 145 Lagos bus parks. A LAMATA bus report says the park count had risen to more than 60. A 2022 danfo census counted 759 routes; 79 stops in one presentation are a sample.<sup>45,46,47,48</sup> No national census of markets, bus stops or stall clusters was found. Federal secretariats and LASPARK sites were named in the brief and were not found as a counted list, so they are not given a number.</p>
<p>The 16,714 ATMs are machines that already exist. A second machine beside each of them would still be 16,714, not 20,000, and a machine in a bank’s own gallery would fall under the on-site fee rules in section 2. Most of those sites fail the gallery economics even before a queue is counted.</p>
<p><span class="tag">Result</span> Sites that clear break-even, on the evidence in hand: none identified. The off-site 60/40 full-cost line is {tx(S['s60']['be_full'])} transactions a scheduled open day. The concession line is {tx(S['concession']['be_full'])}. The gallery line is {tx(S['gallery']['be_full'])}. The busy-POS anecdote of 80 to 100 sits under all three.<sup>60</sup> A claim of 1,500 to 3,000 hot sites at 300 transactions a day would be an illustration. It is not a count, and 300 would still sit under those break-evens. Twenty thousand is not a plausible network on these lists. It is a target with no site file behind it.</p>
<p>Added government collections and payouts would be extra transactions. No volume for that use was found, so none is added. A concession that needs {tx(S['concession']['be_cash'])} transactions a day just to cover CashEase’s cash costs would have to show those government transactions in a count, site by site, before they could be treated as the missing traffic.</p>

<h2>7. Stakeholders</h2>
{html_table(
    ["Party", "Role in the sketch", "What this study can say"],
    [
        ["CashEase", "Owns the boxes in the commercial sketch, or operates them if a bank owns them", "Buying the boxes fails every phase. A fee for watching a bank-owned pilot is the only positive CashEase profit and loss."],
        ["Partner bank", "Holds the ATM approval, supplies notes, runs cash-in-transit, settles, takes a fee share", "At 60/40 the bank can make a small surplus while CashEase loses the machine. At managed service the bank inherits a loss of about " + loss(S['managed']['at']['250']['bank_full_profit']) + " a machine at 250 transactions."],
        ["CBN", "Issuer, ATM-approval authority, possible note supplier", "Approval is required and is not in hand. A note-supply contract and a sandbox instrument were not found. Public comments point to less small-note demand."],
        ["ICRC and the host MDA", "Federal concession path", "Certificate of compliance, 1% of gross, an unsolicited-proposal fee, a project bond. Federal assets only."],
        ["NIPOST, NRC, secretariats, local governments", "Named federal or local sites", "2,048 postal outlets and 774 local authorities are real counts. They are not a traffic study. Secretariats were not found as a count."],
        ["State governments, LAMATA, LASPARK", "Parks, markets, rail and bus sites", "Outside the federal ICRC process. Lagos has 30 parks on the November 2024 register. LAMATA’s pages give 13 Blue Line stations planned and 12 Red Line stations proposed."],
        ["BOI, DBN, AFC, Afreximbank", "Named as debt sources", "BOI describes below-market MSME tenors of 3 to 5 years. DBN is wholesale and reports ₦1.4 trillion disbursed by December 2025. No AFC or Afreximbank rate for this asset was found."],
        ["Customers and today’s agents", "The queue, and the competing cash-out", "No measured willingness to pay a change fee. Millions of POS terminals already sell cash-out."],
    ],
    "Stakeholders. Sources for the counts and the institutions are in sections 4, 5 and 6.",
    tight=True,
)}

<h2>8. Per-machine economics</h2>
<p>Annual costs of the reference machine, carried from v3 and split so a partner can take a line. Power uses 336 litres of diesel at the ₦1,810 pump quote of 6 October 2026, plus an ₦80,000 solar-upkeep assumption.<sup>54</sup> The Dangote gantry price of ₦1,700 on 7 October 2026 is lower and is not used; using it would make power slightly cheaper and would not change the verdict.<sup>52,53</sup></p>
{html_table(
    ["Line", "A year", "Carried by"],
    [
        ["Rent", naira(L["rent"]), "CashEase, except a gallery or a free public site"],
        ["Power", naira(L["power"]), "CashEase, unless the contract says otherwise"],
        ["Connectivity", naira(L["connectivity"]), "CashEase in the commercial cases"],
        ["Cash-in-transit", naira(L["cit"]), "Bank in every new structure"],
        ["Security", naira(L["security"]), "CashEase, including at a gallery"],
        ["Maintenance, 10% of ex-works", naira(L["maintenance"]), "Whoever owns the machine"],
        ["Insurance on the machine", naira(L["machine_insurance"]), "Whoever owns the machine"],
        ["Insurance on the float", naira(L["float_insurance"]), "Whoever holds the notes"],
        ["Depreciation, seven years, no salvage", naira(L["depreciation"]), "Whoever owns the machine"],
        ["Float, opportunity at the 23% policy rate", naira(L["float_opportunity"]), "Whoever funds the notes"],
        ["Monitoring, managed service only", naira(L["monitoring"]), "CashEase"],
    ],
    "Assumption, except diesel price, the policy rate and the maintenance rule of thumb taken from the US recycler note. Maintenance moves if the dollar price moves.",
    tight=True,
)}
<p><span class="tag">Result</span> CashEase’s full annual cost is {naira(S['s60']['ce_full_cost'])} under 60/40, {naira(S['gallery']['ce_full_cost'])} at a gallery, and {naira(S['concession']['ce_full_cost'])} under the concession. The gallery and the concession match, because both leave CashEase with power, the link, security, maintenance, machine insurance and depreciation. They differ only in the fee. Taking security off the gallery as well, on the theory that the bank’s guards already stand there, moves full-cost break-even from {tx(S['gallery']['be_full'])} to about {gal_nose:,.0f}. It remains a different business from 150, 250 or 400 transactions.</p>
{html_table(
    ["Structure", "CashEase per tx", "Cash break-even", "Full-cost break-even", "Cash break-even after 23% debt service"],
    be_rows,
    "Transactions per scheduled open day. Debt service is the annual payment on 70% of the machine over five years at the 23% policy rate. Managed service has no CashEase debt.",
    tight=True,
)}
<figure>
  <img src="../charts/{charts['breakeven']}" alt="Horizontal bar chart of full-cost break-even by structure">
  <figcaption>Figure 2. Full-cost break-even for CashEase. The vertical lines are the three test volumes of 150, 250 and 400 transactions a scheduled open day.</figcaption>
</figure>
{html_table(
    ["Structure", "150 cash", "150 operating", "250 cash", "400 cash", "400 operating", "NPV at 400", "IRR at 400", "Payback"],
    profit_rows,
    "One machine, no head office. Cash profit is fees minus cash costs. Operating profit also subtracts depreciation and, where CashEase funds it, the float. NPV is unlevered at 28%.",
    tight=True,
)}
<figure>
  <img src="../charts/{charts['profit']}" alt="Grouped bars of cash profit per machine">
  <figcaption>Figure 3. CashEase cash profit per machine. The managed-service bars are positive because CashEase does not pay for the machine. Figure the bank’s result in the next table before reading those bars as a business.</figcaption>
</figure>
{html_table(
    ["Structure", "Bank result at 150", "Bank at 250", "Bank at 400", "Government cash at 250"],
    partner_rows,
    "Bank result is the bank’s fee share minus the costs this structure assigns to the bank, including the opportunity cost of the float and, in managed service, depreciation of the machine. Government cash is the 20% share. It is zero outside the concession.",
    tight=True,
)}
<p>Read the partner table with the CashEase table. Under 60/40 at 400 transactions the bank’s full result is a surplus of {naira(S['s60']['at']['400']['bank_full_profit'])} while CashEase’s operating result is a loss of {loss(S['s60']['at']['400']['ce_operating'])}. The contract moves the loss onto the owner of the box. Under managed service the signs flip: CashEase’s cash profit at 250 transactions is {naira(S['managed']['at']['250']['ce_cash_profit'])}, and the bank’s full result is a loss of {loss(S['managed']['at']['250']['bank_full_profit'])}. Fifty bank-owned machines at that volume would cost the bank about {loss(m50['bank_full_profit'])} a year. Twenty thousand would cost about {loss(m20['bank_full_profit'])} a year. No reason was found for a bank to sign the larger number.</p>
<p>The whole project, ignoring who holds the shares, has the same problem. <span class="tag">Result</span> Commercial full cost against the full fee pool breaks even at {tx(sysv['commercial']['be_tx'])} transactions a day. At 150 transactions the gap is {naira(gap_com)} a machine. A concession that drops rent and cash-in-transit, and still counts the float as having a cost, breaks even at {tx(sysv['concession_econ']['be_tx'])}. Treating the notes as free as well moves that to {tx(sysv['concession_free_notes']['be_tx'])}. The 100-to-150-transaction break-even in the sketch does not survive the cost stack. It would survive only if someone else also gave away the machine and the maintenance. That is a grant.</p>
<p>Debt makes the cash line worse. Seventy percent of one machine, repaid over five years, costs {naira(S['s60']['debt_service_23'])} a year at 23% and {naira(S['s60']['debt_service_7'])} a year at 7%. Both payments exceed CashEase’s fee income at 400 transactions under 60/40, which is {naira(S['s60']['at']['400']['ce_revenue'])}. The machine cannot service the debt at the test volumes. The 70/30 sketch and the five-year tenor are assumptions. Bank of Industry’s MSME page describes tenors of 3 to 5 years and a moratorium of 3 to 12 months, at below-market rates, for MSMEs.<sup>55</sup> That page is not an offer to finance a {naira(hw['all_in_ngn'])} imported ATM.</p>

<h2>9. Fleets: 50, 500, 1,500 and 20,000</h2>
<p>Head office is an assumption, not a quote: {naira(r['assumptions_hq']['year0_fixed'])} at the start plus {naira(r['assumptions_hq']['year0_per_machine'])} a machine, and {naira(r['assumptions_hq']['annual_fixed'])} a year plus {naira(r['assumptions_hq']['annual_per_machine'])} a machine. The 20,000-machine concession also pays the ₦100 million unsolicited-proposal fee from the ICRC schedule. Float sits with the bank in every new structure, so it is not in CashEase’s year-0 cheque. There is no salvage and, unless the row is the v3 comparison, no float comes back at year 7.</p>
{html_table(
    ["Case", "Year-0 cash", "Cash profit", "Operating", "NPV at 28%", "IRR", "Payback"],
    fleet_rows,
    "Unlevered CashEase or SPV, after head office. Year-0 cash is the machine capex plus head office. IRR is not defined when every cash flow is negative. Payback is undiscounted.",
    tight=True,
)}
<p>The shape of the cash flow is the same in every CashEase-owned case. Year 0 is the outflow in the table. Each of the next seven years is the cash-profit column, repeated. Nothing large comes back at the end. Cumulative cash never crosses zero. Payback does not occur. A levered case is tighter still: year 0 falls to the 30% equity cheque, and years 1 to 5 then subtract debt service.</p>
{html_table(
    ["Case", "Rate", "Annual debt service", "Cash profit before debt", "Equity NPV at 28%", "IRR"],
    rate_rows,
    "Seventy percent of capex, five-year annuity. The 7% column uses the BOI GLOW rate and is not a term sheet. The 0% column is a bound. Cash profit before debt is already negative, so a cheaper rate cannot turn the project.",
    tight=True,
)}
<p><span class="tag">Result</span> At 400 transactions, 20,000 concession machines have a year-0 cheque of {loss(c20_400['year0'])} unlevered and an annual operating loss of {loss(c20_400['ce_operating'])}. Equity NPV stays negative at a zero interest rate. The same pattern holds at 250 transactions, where the operating loss is larger. At 150 transactions the unlevered NPV is {short(c20_150['npv_28'])}.</p>
<p>Foreign exchange and the fee were moved one at a time. A 20% rise in the naira cost of the imported machine, freight included, takes all-in cost from {naira(hw['all_in_ngn'])} to {naira(hw20['all_in_ngn'])}. Install and software stay at the naira assumption.</p>
{html_table(
    ["Structure", "Fee case", "CashEase per tx", "Full-cost break-even", "NPV at 400 tx", "FX"],
    sens_rows,
    "Gallery rows ignore the surcharge, because the site is on-site. NPV is one machine, unlevered, no head office.",
    tight=True,
)}
<p>The generous fee pair, ₦200 to break a note and the ₦500 legal cap on the surcharge, still leaves a negative NPV at 400 transactions for 60/40, for the concession and for the gallery. A weaker naira widens the loss. The split is already the difference between the rows: 50/50 is in section 8, and it is worse than 60/40. The interest-rate table is the rate sensitivity. None of the five switches — fee, volume, split, rate, exchange rate — produces a CashEase-owned machine with a positive NPV at the published price.</p>
{html_table(
    ["Structure", "Ceiling at 150 tx", "Ceiling at 250 tx", "Ceiling at 400 tx"],
    ceiling_rows,
    "Largest all-in delivered cost with a one-machine NPV of zero at 28%. Maintenance stays at 10% of ex-works, so a cheaper box also has cheaper maintenance. The published all-in cost is " + naira(hw["all_in_ngn"]) + ".",
    tight=True,
)}
<p>Local assembly would have to land at or below the ceiling, after freight, install and software. At 150 and at 250 transactions a day there is no such price for any structure in which CashEase buys the machine. The cash costs that do not shrink with the box — rent where it applies, security, power, the link — already consume the fee share. At 400 transactions the 60/40 ceiling is {naira(r['ceilings']['s60']['400'])} and the concession ceiling is {naira(r['ceilings']['concession']['400'])}. Both sit far under {naira(hw['all_in_ngn'])}. No Nigerian factory quote was found, so this study does not apply a discount and then hope. A quote above the ceiling fails. A quote below it would still need the 400-transaction volume, which nobody has measured.</p>

<h2>10. Funding plan</h2>
<p>Do not raise equity to buy machines. Do not draw a 70/30 debt package against this asset. The funding that matches the arithmetic is narrower.</p>
<ul>
  <li><strong>Stop.</strong> If counsel says the machine is unlawful, or if no bank will own a pilot, CashEase’s spend is the opinion and the travel. <span class="tag">Assumption</span> ₦3 million. Then stop.</li>
  <li><strong>Measure.</strong> If a bank will buy a handful of machines and write the operating loss, CashEase can staff the measurement. <span class="tag">Assumption</span> ₦8 million over twelve months for counsel, a project lead and travel. Zero machine capex on CashEase’s balance sheet. The bank’s loss, at the managed-service numbers, is about {loss(S['managed']['at']['250']['bank_full_profit'])} a machine a year at 250 transactions. The bank has to name the number of machines whose loss it will accept. This study does not pick that number for the bank. It does say that 50 machines at that loss rate are about {loss(m50['bank_full_profit'])} a year, which is already a programme rather than a test.</li>
  <li><strong>Build.</strong> There is no build case on these figures. A later raise would need a measured volume above the full-cost break-even of the signed contract, and a written machine price at or below the ceiling for that volume. Neither exists today.</li>
</ul>
<p>Development Bank of Nigeria lends wholesale through financial institutions and reports ₦1.4 trillion disbursed as of December 2025.<sup>57</sup> That is the scale of the institution. It is not a commitment. Bank of Industry’s public MSME terms are the closest concessional description, and GLOW’s 7% is the only specific rate used here, with the product limit stated.<sup>55,56</sup> AFC and Afreximbank are named in the brief. No rate from either was found for this asset, so none is shown.</p>

<h2>11. Risk register</h2>
{html_table(
    ["Risk", "Why it is in the file", "What to do"],
    [
        ["Small-note supply", "The governor has tied scarcity to falling demand. The 2026 rule allows every denomination. It does not show that cassettes are filled.", "A written delivery schedule of ₦100, ₦200 and ₦500 notes before any order. If the bank will not sign it, stop."],
        ["Wrong licence", "Agent rules are quoted as barring non-human machines. Note exchange has no published private licence.", "Counsel’s opinion on the ATM path and the note-exchange path, against the signed guidelines and the CBN Act."],
        ["On-site fee", "Galleries do not earn the ₦500 surcharge. The model’s gallery break-even is " + tx(S['gallery']['be_full']) + " transactions.", "Do not underwrite a gallery on off-site fee maths."],
        ["Volume", "No site file shows 150, 250 or 400 paid transactions a day. The public anecdote is 80 to 100.", "Count paid transactions, refusals and stock-outs on bank-owned machines. Do not extrapolate."],
        ["Fee refusal", "No willingness-to-pay study. Traders sometimes need change and sometimes will not pay for it.", "The pilot records the refusal rate at the posted fee. A refusal majority kills the fee assumption."],
        ["FX and duty", "A 20% dearer machine raises 60/40 full-cost break-even to " + tx(sens('s60', 100, 0.20)['be_full']) + ". Duty is not in the price yet.", "A naira quote, duty included, before any order. If it sits above the ceiling, stop."],
        ["Debt service", "Five-year service on 70% of one machine is " + naira(S['s60']['debt_service_23']) + " a year at 23%, against fee income of " + naira(S['s60']['at']['400']['ce_revenue']) + " at 400 transactions.", "Do not borrow to buy the box. A zero rate was tested. The NPV stays negative."],
        ["Fraud and theft", "NIBSS reports ₦52.26 billion lost in 2024 and ₦25.85 billion in 2025, with Lagos at 63.43% of 2025 fraud activity.", "The bank’s existing ATM controls, or no machine. Shrink in this model is only the 0.3% assumption."],
        ["Concession process", "ICRC certificate, 1% of gross, a bond, and a second capex cycle inside a 10-to-15-year term. State sites sit outside the federal process.", "Do not file a 20,000-machine unsolicited proposal on this record."],
        ["Partner economics", "Managed service makes CashEase’s books look healthy by handing the bank a loss of " + loss(S['managed']['at']['400']['bank_full_profit']) + " a machine at 400 transactions.", "Ask the bank to initial that loss in a term sheet. A verbal interest is not a term sheet."],
    ],
    "Risks that change the decision. Fraud figures: sources 58 and 59.",
    tight=True,
)}

<h2>12. Go and no-go gates</h2>
<ol>
  <li><strong>Law, in writing.</strong> Counsel confirms a path that is not the agent path: a bank-held independent-ATM approval, and a stated position on note-for-note exchange under the CBN Act. A “maybe” is a no-go.</li>
  <li><strong>The bank owns the pilot.</strong> The term sheet names the bank as buyer of the machines and as payer of maintenance, cash-in-transit, the float and the site. If the sheet puts capex on CashEase, stop. The full-cost break-even CashEase would then be signing is {tx(S['s60']['be_full'])} transactions off-site or {tx(S['gallery']['be_full'])} at a gallery.</li>
  <li><strong>Notes, in a schedule.</strong> The bank commits to ₦100, ₦200 and ₦500 notes on a stated cycle. A general promise to “support cash” is a no-go.</li>
  <li><strong>Measured volume.</strong> Paid transactions on the bank-owned machines, net of refusals and downtime, clear the full-cost break-even of the contract the bank has actually signed. For a managed service, the relevant test is whether the bank will keep funding its own loss. For any later CashEase purchase, the relevant lines are the break-evens in section 8, at the signed split.</li>
  <li><strong>A quote under the ceiling.</strong> Delivered cost, duty included, at or below the ceiling for the measured volume. At 150 and 250 transactions that ceiling does not exist. At 400 transactions it is {naira(r['ceilings']['s60']['400'])} on a 60/40 off-site contract and {naira(r['ceilings']['concession']['400'])} on the concession split. The published reference price is {naira(hw['all_in_ngn'])} before duty.</li>
  <li><strong>Concession only after the gates above, and only on a counted site list.</strong> Federal assets and state assets are separate approvals. The list has to contain real addresses whose measured twins clear the volume gate. A target of 20,000 does not pass this gate. The lists in section 6 sum to {comma(sites['listed_sum'])} before overlap.</li>
</ol>

<h2>13. Twelve-month action plan</h2>
{html_table(
    ["Months", "Work", "Spend", "Stop if"],
    [
        ["1–2", "Two opinions: counsel on the licence and the note swap; two banks on who would own a machine.", "Inside the ₦3 million stop-case assumption.", "Either opinion comes back closed."],
        ["3–4", "If a bank will own the boxes, write the measurement: fee, refusals, paid transactions, stock-outs, cash-in-transit misses. Cap the fleet at the loss the bank initials.", "CashEase still buys no machines. Staffing sits in the ₦8 million assumption.", "The bank will not put the loss in a term sheet."],
        ["5–8", "Run the bank-owned machines. Publish the weekly counts to the bank and to CashEase. No press release that treats a pilot as a network.", "Bank opex. CashEase time only.", "Uptime, notes or the fee collapse in the first month. Stop early."],
        ["9–10", "Set the measured daily transactions next to the break-even of the signed structure.", "No new money.", "The count sits under the break-even. Stop."],
        ["11–12", "Only if the count clears the gate: ask for one Nigerian delivered quote, duty included, and set it next to the ceiling.", "The quote is free to request. Do not place an order in this year.", "The quote sits above the ceiling, or no quote comes."],
    ],
    "Assumption on the two cash sums. They are not quotes. Machine capex in this year is zero for CashEase.",
    tight=True,
)}
<p>Do not file an ICRC unsolicited proposal in these twelve months. Do not commission a factory. Do not hire a national site-acquisition team. The v3 attended test, a person with a cash box and no machine, remains available if the banks refuse the pilot and counsel leaves the note-exchange question open. That test is specified in the v3 study. It is not re-costed here.</p>

<h2>14. Workings</h2>
<p>Ex-works naira = 40,000 × {r['fx']:,.2f} = {comma(hw['exworks_ngn'])}.</p>
<p>All-in = ex-works × 1.08 + 6,000,000 + 2,000,000 = {comma(hw['all_in_ngn'])}.</p>
<p>Gross fee = 0.55 × note fee + 0.35 × surcharge + 0.10 × 30. Shrink = 0.35 × 12,000 × 0.003 = 12.60. On a gallery the surcharge is zero and shrink stays.</p>
<p>v3 CashEase take = gross − 0.25 × (0.35 × surcharge) − shrink = ₦{S['v3']['per_tx']['ce']:.3f}.</p>
<p>Share take = CashEase share × (gross − shrink − ICRC rate × gross). ICRC rate is 1% on the concession and zero otherwise.</p>
<p>Depreciation = all-in / 7. Maintenance = 0.10 × ex-works. Machine insurance = 0.015 × all-in. Float insurance = 0.015 × 2,000,000. Float opportunity = 2,000,000 × 0.23.</p>
<p>Diesel litres = 8 × 300 × 0.40 × 0.35 = 336. Power = 336 × 1,810 + 80,000.</p>
<p>Break-even transactions per open day = (annual cost CashEase bears / CashEase naira per transaction) / {days:.0f}.</p>
<p>NPV discounts year-0 capex, seven years of cash profit after head office where a fleet is shown, and no salvage. The rate is 28% unless a row says 23%. IRR uses a solver between −99% and 500%. “Not defined” means there is no root in that range and the project does not earn a positive return. “Above 500%” would mean a thin CashEase outlay against a fee; it does not appear in the CashEase-owned fleet, because those cash flows never turn positive. Payback is undiscounted and is “Never” when cumulative cash stays negative.</p>
<p>Debt service is an annuity on 70% of capex for five years. The 23% rate is the policy rate from the 307th Monetary Policy Committee meeting on 21–22 September 2026, down from 26.50%.<sup>29,30</sup> Inflation was 15.39% in August 2026.<sup>30</sup> The model does not inflate costs. If costs rose with that rate and fees did not, the losses would be wider. Tax is not modelled. Losses do not need a tax rate to be losses.</p>
<p>The 20% exchange-rate case multiplies ex-works and the 8% freight by 1.2 and leaves the naira install and software unchanged. All-in becomes {comma(round(hw20['all_in_ngn']))}.</p>
<p>Recompute from <span class="small">model/machine_model.py</span>. The tables in this PDF were written by that script.</p>

<h2>15. Sources</h2>
<p>Every external fact points here. Pages were read in the first week of October 2026. Where a CBN file could not be opened, the failure is stated in the section that uses it. The v3 study remains the fuller narrative of the market statistics reused below.</p>
<ol class="sources">
  <li>Central Bank of Nigeria, “Payment Modes”, active ATMs in the first half of 2024. https://www.cbn.gov.ng/PaymentsSystem/modes.html</li>
  <li>Central Bank of Nigeria, e-payment statistics by channel, January–June 2024. https://www.cbn.gov.ng/PaymentsSystem/ePaymentStatistics.html</li>
  <li>World Bank, “Automated teller machines (ATMs) (per 100,000 adults)”, indicator FB.ATM.TOTL.P5. https://data.worldbank.org/indicator/FB.ATM.TOTL.P5</li>
  <li>Federal Reserve Bank of St Louis, FRED series NGAFCAANUM, Nigeria, 2024 observation 12.82854. https://fred.stlouisfed.org/series/NGAFCAANUM</li>
  <li>Federal Reserve Bank of St Louis, FRED series ZAFFCAANUM, South Africa, 2024 observation 45.96149. https://fred.stlouisfed.org/series/ZAFFCAANUM</li>
  <li>World Bank, “Population, total — Nigeria”, 2025 value 237,527,782. https://data.worldbank.org/indicator/SP.POP.TOTL?locations=NG</li>
  <li>WorldPop, Nigeria population release notes, version 3.0, 29 August 2025. https://data.worldpop.org/repo/wopr/NGA/population/v3.0/NGA_population_v3_0_README.pdf</li>
  <li>New Telegraph, “NIBSS: More Nigerians Embrace PoS As Deployed Terminals Up 119.4% To 5.90m”. https://newtelegraphng.com/nibss-more-nigerians-embrace-pos-as-deployed-terminals-up-119-4-to-5-90m/</li>
  <li>NIBSS, “How NIBSS Innovation Drives Services in GDP Expansion”, POS value of ₦10.45 trillion in the first quarter of 2025. https://nibss-plc.com.ng/how-nibss-innovation-drives-services-in-gdp-expansion/</li>
  <li>ThisDay, “E-Payment Transactions Rise 17.7% to N284.99 Trillion in Q1 2025”, 29 July 2025. https://www.thisdaylive.com/2025/07/29/e-payment-transactions-rise-17-7-to-n284-99-trillion-in-q1-2025/</li>
  <li>New Telegraph, “Cashless: PoS Sustains Growth As Transactions Up 300.8% To N10.49trn”. https://newtelegraphng.com/cashless-pos-sustains-growth-as-transactions-up-300-8-to-n10-49trn/</li>
  <li>New Telegraph, “Value Of PoS Transactions Surged 79.03% To N18.78trn In Q1’26”. https://newtelegraphng.com/value-of-pos-transactions-surged-79-03-to-n18-78trn-in-q126/</li>
  <li>Nairametrics, “ATM transactions surge to N36.34 trillion in six months despite fresh fees”, 19 January 2026. https://nairametrics.com/2026/01/19/atm-transactions-surge-to-n36-34trn-in-six-months-despite-fresh-fees/</li>
  <li>TheCable, “ATM withdrawals hit N36trn in H1 2025 — up by 196%”, 19 January 2026. https://www.thecable.ng/atm-withdrawals-hit-n36trn-in-h1-2025-up-by-196/</li>
  <li>Valuechain, headline treatment of first-quarter 2025 ATM withdrawals as ₦15.98 trillion. https://www.thevaluechainng.com/%e2%82%a615-98tn-withdrawn-as-cbn-nudges-nigeria-back-to-atms/</li>
  <li>Central Bank of Nigeria, “Reforms and Initiatives”. https://www.cbn.gov.ng/AboutCBN/Reforms.html</li>
  <li>Nairametrics, “CBN extends PoS geo-fencing enforcement to August 1”, 29 May 2026. https://nairametrics.com/2026/05/29/cbn-extends-pos-geo-fencing-enforcement-to-august-1/</li>
  <li>Punch, “CBN caps POS agent daily transactions at N1.2m in new guidelines”, 6 October 2025. https://punchng.com/cbn-caps-pos-agent-daily-transactions-at-n1-2m-in-new-guidelines/</li>
  <li>TheCable, “CBN issues guidelines for agent banking, sets daily transaction limit at N1.2m”, 6 October 2025. https://www.thecable.ng/cbn-issues-guidelines-for-agent-banking-sets-daily-transaction-limit-at-n1-2m/</li>
  <li>G. Elias, note on the 2025 agent-banking guidelines, including paragraph 3.2 on non-human machines. https://www.gelias.com/images/Central_Bank_of_Nigeria_Guidelines_on_the_Operations_of_Agent_Banking.pdf</li>
  <li>Manifield Solicitors, note quoting paragraph 3.2. https://manifieldsolicitors.com/central-bank-of-nigeria-cbn-issues-new-daily-cash-withdrawal-limits-and-updated-agent-banking-guidelines/</li>
  <li>TNP, “The CBN Agent Banking Guidelines 2025”. https://tnp.com.ng/the-cbn-agent-banking-guidelines-2025-key-innovations-and-regulatory-implications/</li>
  <li>Mondaq, “Regulatory Framework For Agent Banking In Nigeria”. https://www.mondaq.com/nigeria/financial-services/1701110/regulatory-framework-for-agent-banking-in-nigeria-cbn-guidelines-and-compliance-requirements</li>
  <li>Central Bank of Nigeria, file URL for the 6 October 2025 agent guidelines. Retrieval on 7 October 2026 returned an access error. https://www.cbn.gov.ng/Out/2025/CCD/CIRCULAR%20AND%20GUIDELINES%20FOR%20THE%20OPERATIONS%20OF%20AGENT%20BANKING%20IN%20NIGERIA%20OCTOBER%206%202025.pdf</li>
  <li>Central Bank of Nigeria Act 2007, sections 17 to 20. https://www.cbn.gov.ng/OUT/PUBLICATIONS/BSD/2007/CBNACT.PDF</li>
  <li>Central Bank of Nigeria, currency-management FAQ. https://www.cbn.gov.ng/FAQS/FAQS.html?Category=CurrencyManagement</li>
  <li>Constitution of the Federal Republic of Nigeria 1999, section 3(6). https://nigerian-constitution.com/chapter-1-part-1-section-3-states-federation-federal-capital-territory-abuja/</li>
  <li>Senate Committee on Constitution Review, Chapter 1, Part 1. https://sccr.gov.ng/chapter-1-part-1/</li>
  <li>Central Bank of Nigeria, monetary-policy decisions, 307th meeting. https://www.cbn.gov.ng/MonetaryPolicy/decisions.html</li>
  <li>The Nation, “CBN cuts interest rate to 23 per cent in major policy reset”, including August 2026 inflation of 15.39%. https://thenationonlineng.net/cbn-cuts-interest-rate-to-23-per-cent-in-major-policy-reset/</li>
  <li>Arbiterz, NFEM close of ₦1,331.69 per dollar on 5 October 2026. https://arbiterz.com/naira-dollar-rate-october-6-2026-naira-trades-at-n1331-69-in-cbn-nfem-window/</li>
  <li>Premium Times, “Currency in circulation rose to N5.73 trillion as FX inflows hit $109.86bn in 2025”, 29 July 2026. https://www.premiumtimesng.com/business/business-news/899182-currency-in-circulation-rose-to-n5-73-trillion-as-fx-inflows-hit-109-86bn-in-2025-cbn.html</li>
  <li>Nairametrics, “CBN: Currency in circulation falls to N5.52 trillion in June 2026”, 24 July 2026. https://nairametrics.com/2026/07/24/cbn-currency-in-circulation-falls-to-n5-52-trillion-in-june-2026/</li>
  <li>The Sun, “Cash outside banks rose by 1.48% to N4.87trn in August”. https://thesun.ng/cash-outside-banks-rose-by-1-48-to-n4-87trn-in-august-cbn/</li>
  <li>Premium Times, “Why lower Naira denominations are scarce — Cardoso”. https://www.premiumtimesng.com/business/business-news/897115-why-lower-naira-denominations-are-scarce-cardoso.html</li>
  <li>Daily Post, “CBN hasn’t said otherwise — Cardoso on validity of N50, N100, other lower naira notes”, 21 July 2026. https://dailypost.ng/2026/07/21/cbn-hasnt-said-otherwise-cardoso-on-validity-of-n50-n100-other-lower-naira-notes/</li>
  <li>Daily Trust, “N20, N50, N100, nothing to buy”. https://dailytrust.com/n20-n50-n100-nothing-to-buy/</li>
  <li>The Business Times, “CBN Governor Attributes Lower Naira Note Scarcity to Declining Demand”. https://thebusinesstimesng.com/cbn-lower-naira-notes-scarcity-declining-demand/</li>
  <li>EFInA, Access to Financial Services in Nigeria 2023, full survey report. https://a2f.ng/wp-content/uploads/2024/07/A2F-2023-SURVEY-REPORT-1.pdf</li>
  <li>EFInA, A2F 2023 key highlights. https://efina.org.ng/wp-content/uploads/2024/03/A2F-2023-Event-Day-Presentation-Version4-1.pdf</li>
  <li>Moniepoint, “How To Get Moniepoint Pos”. https://moniepoint.com/blog/how-to-get-moniepoint-pos</li>
  <li>Quality Data Systems, “How Much does a Cash Recycler Cost?”. https://blog.qualitydatasystems.com/how-much-does-a-cash-recycler-cost-pricing-freight-and-maintenance</li>
  <li>Quality Data Systems, ATM price ranges. https://www.qualitydatasystems.com/atm</li>
  <li>New Dawn, “Lagos commences Motor Park accreditation”, 8 November 2024. https://www.newdawnngr.com/2024/11/08/lagosmotor-parks/</li>
  <li>New National Star, “Lagos to digitalise, regulate interstate transport services, upgrade 100 motor parks”. https://newnationalstar.com/lagos-to-digitalise-regulate-interstate-transport-services-upgrade-100-motor-parks/</li>
  <li>PPIAF-hosted mega-terminals assessment, 145 Lagos bus parks. https://www.ppiaf.org/sites/default/files/documents/2023-07/Mega_Terminals_Assessment_Report_112419.pdf</li>
  <li>LAMATA, bus-reform project report. https://www.lamata-ng.com/wp-content/uploads/2025/04/Final-LBR-Project-Report.pdf</li>
  <li>MapMe / geo4Impact 2025, “Urban mobility in Lagos”. https://www.mapme-initiative.org/fileadmin/Dateien/Presentations_geo4Impact_2025/Lagos_Geo4Impact.pdf</li>
  <li>BRT-News, “CBN Orders Banks, Others To Deploy 1 ATM Per 7,500 Payment Cards”. https://brtnews.ng/cbn-orders-banks-others-to-deploy-1-atm-per-7500-payment-cards/</li>
  <li>MSME Africa, “CBN Orders Banks to Expand ATM Access Nationwide”, 13 March 2026. https://msmeafricaonline.com/cbn-orders-banks-to-expand-atm-access-nationwide-sets-2028-compliance-deadline/</li>
  <li>Foundation for Investigative Journalism, “CBN Orders N100, N500 Charges per N20,000 in ATM Transactions”, 11 February 2025. https://fij.ng/article/cbn-orders-n100-n500-charges-per-n20000-in-off-network-atm-transactions/</li>
  <li>The Guardian, “Dangote cuts diesel price to N1,700”. https://guardian.ng/business-services/dangote-cuts-diesel-price-to-n1700-as-crude-import-costs-fall/</li>
  <li>Daily Post, “Dangote Refinery reduces diesel price”, 7 October 2026. https://dailypost.ng/2026/10/07/dangote-refinery-reduces-diesel-price-to-n85-litre-cheaper-than-imported-ago/</li>
  <li>DailyFuels, diesel at ₦1,810 a litre, 6 October 2026. https://dailyfuels.com/nigeria/</li>
  <li>Bank of Industry, MSME lending: tenors, moratorium and below-market pricing. https://www.boi.ng/who-we-serve/msmes/</li>
  <li>Bank of Industry portal, GLOW product, up to ₦50 million at 7% for women-led firms. https://onlineportal.boi.ng/</li>
  <li>Development Bank of Nigeria, wholesale model and ₦1.4 trillion disbursed as of December 2025. https://www.devbankng.com/</li>
  <li>NIBSS, “Digital payment fraud drops 51% to N25.85b, Lagos accounts for 63%”. https://nibss-plc.com.ng/digital-payment-fraud-drops-51-to-n25-85b-lagos-accounts-for-63/</li>
  <li>Nairametrics, “Nigeria’s financial sector suffers N52.26 billion loss to fraud in 2024”, 26 February 2025. https://nairametrics.com/2025/02/26/nigerias-financial-sector-suffers-n52-26-billion-loss-to-fraud-in-2024-nibss-report/</li>
  <li>Turnet Finance, “Moniepoint Review 2026”, the 80-to-100 daily transaction anecdote. https://turnetfinance.ng/moniepoint-review/</li>
  <li>Premium Times, “Nigeria’s postal revenue rose by 167% in 2025 — NBS”, 12 June 2026, including 2,048 outlets and the breakdown. https://www.premiumtimesng.com/business/business-news/887198-nigerias-postal-revenue-rose-by-167-in-2025-nbs.html</li>
  <li>National Bureau of Statistics, Postal Services Data catalogue. https://microdata.nigerianstat.gov.ng/index.php/catalog/183</li>
  <li>Infrastructure Concession Regulatory Commission, PPP Project Financial Model Guide, 2025. https://www.icrc.gov.ng/wp-content/uploads/2025/08/PUBLIC-PRIVATE-PARTNERSHIP-PPP-PROJECT-FINANCIAL-MODEL-GUIDE.pdf</li>
  <li>Infrastructure Concession Regulatory Commission, Unsolicited PPP Procurement Guide, 11 August 2025. https://www.icrc.gov.ng/wp-content/uploads/2025/08/UNSOLICITED-PPP-PROCUREMENT-GUIDE.pdf</li>
  <li>Infrastructure Concession Regulatory Commission, model PPP agreement, clause 6.3, 1% of gross revenue. https://www.icrc.gov.ng/wp-content/uploads/2026/06/PUBLIC-PRIVATE-PARTNERSHIP-AGREEMENT.pdf</li>
  <li>Infrastructure Concession Regulatory Commission, PPP Regulatory Notice, August 2025. https://www.icrc.gov.ng/wp-content/uploads/2025/08/PPP-REGULATORY-NOTICE-%E2%80%93-AUGUST-2025.pdf</li>
  <li>Infrastructure Concession Regulatory Commission, Project Approval Board guide, citing SGF circular Ref. No. 59804/II243 of 7 July 2025. https://www.icrc.gov.ng/wp-content/uploads/2025/08/PROJECT-APPROVAL-BOARD-PAB-GOVERNANCE-STRUCTURE-AND-FUNCTIONS.pdf</li>
  <li>LAMATA, train services: Blue Line 27 km and 13 stations; Red Line 37 km and 12 proposed stations, with eight named first-phase stops. https://www.lamata-ng.com/train-services/</li>
  <li>Lagos Public Procurement Agency, LAMATA Blue Line advertisement, 19 January 2022, 27 km and 13 stations. https://www.lagosppa.gov.ng/wp-content/uploads/2022/01/LAMATA-Advert-for-Blue-Line.pdf</li>
  <li>ThisDay, “Buhari Inaugurates $1.5bn Lagos-Ibadan Rail Project”, 10 June 2021, “10 stations in the project”. https://www.thisdaylive.com/2021/06/10/update-buhari-inaugurates-1-5bn-lagos-ibadan-rail-project-for-full-commercial-operations/</li>
  <li>Daily Trust, “As the Lagos-Ibadan standard gauge comes alive today”, ten stations once the Apapa extension is counted. https://dailytrust.com/as-the-lagos-ibadan-standard-gauge-comes-alive-today/</li>
  <li>Central Bank of Nigeria, Guidelines on Operations of Electronic Payment Channels in Nigeria, 2020. “All ATMs shall be able to dispense all denominations of Naira.” Cash funding of a non-bank ATM is the partner bank’s responsibility. https://www.cbn.gov.ng/Out/2020/CCD/Reviewed%20and%20Approved%20Guidelines%20on%20Operations%20of%20Electronic%20Payment%20Channels%20in%20Nigeria%202020.pdf</li>
  <li>NIBSS copy of the same 2020 guidelines. https://nibss-plc.com.ng/wp-content/uploads/2023/03/Approved-Guidelines-on-Operations-of-Electronic-Payment-Channels-in-Nige1.pdf</li>
  <li>Keystone Bank, reproduction of the revised cash-management policies effective 1 January 2026, including “All currency denominations may be loaded in ATMs” and the ₦100,000 daily ATM cap. https://www.keystonebankng.com/cbn-revised-cash-management-policies/</li>
  <li>BusinessDay, “CBN’s new cash policy sets higher withdrawal limits, eliminates deposit charges”, circular of 2 December 2025 signed by Dr Rita Sike, effective 1 January 2026. https://businessday.ng/news/article/cbns-new-cash-policy-sets-higher-withdrawal-limits-eliminates-deposit-charges/</li>
</ol>
<p class="small">End of study. Model file model/machine_model.py. Rebuild with source/build_study.py.</p>
"""
    html_path = ROOT / "source" / "study.html"
    pdf_path = ROOT / PDF_NAME
    html_path.write_text(HEAD + body + "\n</body>\n</html>\n", encoding="utf-8")

    proc = subprocess.Popen(
        [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--user-data-dir=/tmp/chrome-cashease-v4",
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
