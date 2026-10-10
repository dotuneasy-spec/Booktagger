#!/usr/bin/env python3
"""Path to ₦50 billion. Does not rewrite v3, v4, v5 or v6."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(ROOT / "source"))

from charts import draw  # noqa: E402
from path_model import main  # noqa: E402

PDF_NAME = "CashEase_Path_to_50_Billion.pdf"


def short(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000:
        return f"{sign}₦{n / 1_000_000_000:.2f}bn"
    if n >= 1_000_000:
        return f"{sign}₦{n / 1_000_000:.2f}m"
    return f"{sign}₦{n:,.0f}"


def irr_s(v) -> str:
    if v is None:
        return "Not defined"
    return f"{v * 100:.1f}%"


def pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def table(headers, rows, caption) -> str:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return (
        f"<table class='tight'><caption>{caption}</caption>"
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
    )


def case_row(label: str, row: dict) -> list[str]:
    fleet = row["fleet"]
    if fleet is None:
        return [label, "Does not reach", "—", "—", "—", "—"]
    return [
        label,
        f"{row['machines']:,}",
        short(fleet["year0"]),
        short(fleet["annual"]),
        pct(fleet["share_of_national"]),
        irr_s(fleet["irr"]),
    ]


def build() -> None:
    r = main()
    draw(r, ROOT / "charts")
    c = r["cases"]
    rec = c["high_100_200"]["fleet"]
    low = c["low_100_200"]["fleet"]
    two = c["high_100_120_two_blocks"]["fleet"]
    big = c["high_100_120"]["fleet"]
    split = c["high_70_200"]["fleet"]
    t12, t100, t500, t1292 = r["tranches"]
    sweep = r["reinvest_200"]
    p120 = r["proof_120"]
    pads = {row["n"]: row for row in r["leases"]}
    flip = {row["n"]: row for row in r["rent_flip"]}
    b = r["booths"]

    body = f"""
<div class="cover">
  <p class="kicker">Feasibility study · October 2026</p>
  <h1>CashEase Nigeria: A Path to ₦50 Billion</h1>
  <p class="sub">₦50 billion is a value, not a sales target and not revenue. One opening fleet reaches it without taking a sixth of the country’s ATM withdrawals. The cheque for that fleet is ₦30.23 billion, and it is written only after a 12-machine count.</p>
  <div class="verdict">
    <p><strong>The path.</strong> Keep every naira of the ₦500 off-site cap. Count 200 other-bank withdrawals a day. Open about 1,292 high-band machines together, at a landed cost of ₦23.72 million each. That fleet’s cash profit is ₦27.32 billion a year and its value at 28% is ₦50 billion. Those withdrawals are 5.4% of Nigeria’s recent daily ATM total. A 70/30 split at 120 a day never gets there. A human booth network and a cash-in kiosk do not get there on any site stock that has been counted. Retained cash from 12 machines does not get there inside seven years.</p>
  </div>
</div>

<h2>1. What the ₦50 billion is</h2>
<p>The figure in the brief is enterprise value. No Nigerian ATM-operator sale multiple was found, so none is used. Value here is the present value, at 28%, of seven years of cash profit, after the opening cheque and after the head office. The 28% is the policy rate of 23% plus five percentage points, the same hurdle as the earlier papers. Salvage at year 7 is zero. Tax is not in the sum. Volume is flat.</p>
<p>Seven years of ₦1 at 28% are worth {r['factor']:.2f}. The annual cash profit that has a present value of ₦50 billion, before counting the cheque, is {short(r['annual_cash_for_50bn'])}. A perpetuity at 28% would need {short(r['perpetual_cash'])} a year. Both are hurdles. The tables below include the cheque, so a row that “reaches” is a fleet whose value, net of the money that built it, clears ₦50 billion.</p>

<h2>2. The machine, carried over</h2>
<p>The high band is the v5 listing: ex-works US$7,850 plus the published US$1,800 customisation stand-in, landed at {short(r['high_all_in'])}. The low band is the other end of that listing, ex-works US$3,650, landed at {short(r['low_all_in'])}. It is not the Hongzhou price from the earlier addendum. Street cost on the high band is {short(r['high_street'])} a year. The bank carries the cash and the cash-in-transit, as in v5. Effective days are 270. One counted withdrawal is one ₦20,000 block at the ₦500 cap. The ₦100 is not CashEase income. On-us withdrawals pay nothing.</p>
<p>At a 70/30 split the high band still covers cash costs at about 61 withdrawals a day and full cost at about 97. That is a machine that can trade. It is not, by itself, a machine that is worth ₦50 billion.</p>

<h2>3. Which plans reach ₦50 billion</h2>
<img src="../charts/fig_machines.png" alt="Machines required for a 50 billion naira value"/>
{table(
    ["Plan", "Machines", "Opening cheque", "Cash profit a year", "Share of ATM withdrawals", "Return"],
    [
        case_row("200 a day, keep all, high band", c["high_100_200"]),
        case_row("200 a day, keep all, low invoice", c["low_100_200"]),
        case_row("120 a day, two blocks, keep all", c["high_100_120_two_blocks"]),
        case_row("200 a day, bank takes 30%", c["high_70_200"]),
        case_row("120 a day, keep all, high band", c["high_100_120"]),
        case_row("120 a day, bank takes 30%", c["high_70_120"]),
        case_row("200 a day, split 50/50", c["high_50_200"]),
    ],
    "Smallest opening fleet whose value at 28% clears ₦50 billion. Share is of the 858.80 million ATM withdrawals in the first half of 2025, spread over 181 days.",
)}
<p>Read the table as a filter. Keeping the whole surcharge and doing 200 other-bank withdrawals a day is the plan this paper will walk. Giving the bank 30% still reaches, and it needs 3,340 machines and {pct(split['share_of_national'])} of national withdrawals, on a cheque of {short(split['year0'])}. Giving the bank half, even at 200 a day, does not reach inside the search. A 70/30 split at 120 a day does not reach at any fleet up to 40,000 machines, because each machine’s value is negative and more of them make it worse.</p>

<h2>4. The plan this paper will walk</h2>
<p>Open {c['high_100_200']['machines']:,} high-band machines on day one, after a count, not before it. Each does 200 paying withdrawals. CashEase keeps ₦500 on each. The opening cheque is {short(rec['year0'])}. Cash profit after the office is {short(rec['annual'])} a year. The value at 28% is {short(rec['npv'])}. The return is {irr_s(rec['irr'])}. Payback is {rec['payback']:.1f} years. The 200 withdrawals, times {c['high_100_200']['machines']:,} machines, are {pct(rec['share_of_national'])} of the country’s recent daily ATM withdrawals. That is about one withdrawal in eighteen. They have to be other banks’ cards. The sponsor’s own cards pay zero if the machine is branded for them.</p>
<p>The same shape on the low invoice is {c['low_100_200']['machines']:,} machines, a cheque of {short(low['year0'])}, cash profit of {short(low['annual'])}, and {pct(low['share_of_national'])} of national withdrawals. Chase that proforma. Do not average it with the high band, and do not spend the high-band cheque if the invoice comes in at the low band.</p>
<img src="../charts/fig_tranches.png" alt="Value of opening fleets from 12 machines to 1292"/>
{table(
    ["Opening fleet", "Cheque", "Cash profit a year", "Value at 28%", "Return"],
    [
        [f"{t12['n']:,}", short(t12["year0"]), short(t12["annual"]), short(t12["npv"]), irr_s(t12["irr"])],
        [f"{t100['n']:,}", short(t100["year0"]), short(t100["annual"]), short(t100["npv"]), irr_s(t100["irr"])],
        [f"{t500['n']:,}", short(t500["year0"]), short(t500["annual"]), short(t500["npv"]), irr_s(t500["irr"])],
        [f"{t1292['n']:,}", short(t1292["year0"]), short(t1292["annual"]), short(t1292["npv"]), irr_s(t1292["irr"])],
    ],
    "Each row is a fleet bought at the start and run for seven years at 200 paying withdrawals. It is not a fleet added in year four.",
)}
<p>Twelve machines are already a business if they truly do 200 a day: cheque {short(t12['year0'])}, cash profit {short(t12['annual'])}, value {short(t12['npv'])}, return {irr_s(t12['irr'])}. One hundred machines are worth {short(t100['npv'])}. Five hundred are worth {short(t500['npv'])}. The ₦50 billion appears at {t1292['n']:,}. Stopping at 500 is a ₦19 billion company. That is a choice. It is not the brief.</p>

<h2>5. Where the 1,292 machines sit</h2>
<p>No station, mall, park or market has a published count of other-bank withdrawals. The 200 a day is the rate the plan needs, not a rate a forecourt has reported. The site stocks that can hold a fleet of this size are the filling stations. NMDPRA counts about 22,681 registered retail outlets. MEMAN’s members, a subset, are 3,293, of which 1,392 are in the South West and 529 in the North Central. 1,292 machines are about 6% of the regulator’s outlets and about two-thirds of the South West plus Abuja member stations. The machines go only where a visit shows there is no bank ATM already dispensing, and only where the 90-day count holds.</p>
<p>Malls stay a two-site test. Ikeja, The Palms and Jabi have owner crowd figures large enough that 200 withdrawals is a small share of the people, and those malls already name banks or supermarket anchors. Parks and markets are not machine sites in this plan. A recycler at Ojota is still a guess.</p>
<p>The average existing ATM, mixing the 16,714 active machines of the first half of 2024 with the first-half 2025 volumes, does about 284 withdrawals a day of every kind of card. Two hundred paying withdrawals is inside that average only if most of the traffic is another bank’s card. A site that already has the landlord bank’s ATM will not look like that.</p>

<h2>6. How it is paid for</h2>
<p>The twelve-machine proof is equity of {short(t12['year0'])}. The step from a passed proof to the ₦50 billion fleet is a further raise, not retained profit. Cash swept into new machines, with no dividend and no new equity, grows a 12-machine fleet to {sweep['end']:,} machines by year 7. The value of that sweep, on the same seven-year clock and with no resale at the end, is {short(sweep['npv'])}. The late machines are bought with cash that then has no years left to earn. Reinvestment is the wrong engine for this target.</p>
<p>So the raise, once the count is in, is the opening cheque of the fleet you actually intend to run. A founder who will live with 100 machines raises {short(t100['year0'])}. A founder who wants the ₦50 billion raises {short(rec['year0'])}. No vendor-finance rate was found. Borrowing at the 23% policy rate was priced in v5 and is not a new source of value here. The bank does not take a share of the surcharge in this plan. The bank supplies the licence, the cash and the transit. In return the machines sit on its name. Whether those machines count toward the issuer’s duty of one ATM per 7,500 cards is a question for counsel. The circular, as reported, tells each issuer to deploy. It does not say a third party’s machine counts.</p>
<p>If counsel says they do not count, the bank has a weaker reason to give away the whole surcharge. The fallback that still hits ₦50 billion is the 70/30 row: {c['high_70_200']['machines']:,} machines, cheque {short(split['year0'])}, {pct(split['share_of_national'])} of national withdrawals. This paper does not prefer it. A 50/50 term sheet does not have a fleet that reaches.</p>

<h2>7. A second strategy: sell the pad, not the box</h2>
<p>CashEase can sign the forecourt and let the card issuer own the ATM. Income is then an annual fee, not the ₦500. The cost of papering a site is an assumption of ₦50,000. Watching it is an assumption of ₦20,000 a year. The office assumptions are unchanged. There is no machine to depreciate. The fee that produces a ₦50 billion value is:</p>
{table(
    ["Paying sites", "Annual fee that hits ₦50 billion", "Cheque to open the book"],
    [
        ["100", "Does not reach, even at ₦50m a site", "—"],
        ["500", short(pads[500]["fee"]), short(pads[500]["year0"])],
        ["1,000", short(pads[1000]["fee"]), short(pads[1000]["year0"])],
        ["3,293 (all MEMAN members)", short(pads[3293]["fee"]), short(pads[3293]["year0"])],
        ["5,000", short(pads[5000]["fee"]), short(pads[5000]["year0"])],
        ["10,000", short(pads[10000]["fee"]), short(pads[10000]["year0"])],
    ],
    "The fee is what a bank would have to pay. It is not a quote from any bank.",
)}
<p>A fee near the v5 rent assumption of ₦1.80 million a year, paid the other way, is worth the following. These rows use ₦1.80 million exactly.</p>
{table(
    ["Sites paying ₦1.80m a year", "Cash profit", "Value at 28%"],
    [
        ["100", short(flip[100]["annual"]), short(flip[100]["npv"])],
        ["500", short(flip[500]["annual"]), short(flip[500]["npv"])],
        ["1,392 (MEMAN South West)", short(flip[1392]["annual"]), short(flip[1392]["npv"])],
        ["3,293 (all MEMAN members)", short(flip[3293]["annual"]), short(flip[3293]["npv"])],
        ["10,000", short(flip[10000]["annual"]), short(flip[10000]["npv"])],
    ],
    "₦1.80 million is the rent assumption from the machine papers, reversed. It is not a signed host contract.",
)}
<p>Ten thousand sites at that rent clear ₦50 billion, on a cheque of about {short(flip[10000]['year0'])}. Nobody has signed ten thousand sites. The whole MEMAN network at the same rent is worth {short(flip[3293]['npv'])}, not ₦50 billion. The useful version of this strategy is smaller: paper the forecourts the proof will need, and either put CashEase’s own machine there or offer the pad to one issuer. Do not add the pad value on top of the machine value. A site earns once.</p>
<p>The 2028 rule does not, on the figures found, force a national rush of new ATMs. Sixteen thousand seven hundred and fourteen active ATMs already cover {r['cards_already_covered']:,} cards at one ATM per 7,500. CBN has spoken of more than 12 million contactless cards. NIBSS has spoken of more than one million AfriGO cards. Both sit far below 125 million. The rule binds each issuer, and no issuer’s card stock was published in the sources read, so the number of ATMs the rule still requires is not computed. Pads are a sales list, not a quota.</p>

<h2>8. The attendant business is a side door</h2>
<p>The brief’s human change point takes a franchise fee of ₦150,000 to ₦300,000 and splits the change fee 70% attendant, 20% CashEase, 10% host. The change fee used here is the ₦100 assumption, and the fee used in the value sum is the top of the range, ₦300,000. At 120 changes a day, CashEase’s 20% is ₦648,000 a year per booth.</p>
{table(
    ["Changes a day", "Booths whose value hits ₦50 billion"],
    [
        ["60", f"{b['60']['n']:,}"],
        ["120", f"{b['120']['n']:,}"],
        ["200", f"{b['200']['n']:,}"],
    ],
    "Franchise fee treated as cash in. Office of ₦40 million at the start and ₦25 million a year. Rent and any union levy are not in the sum.",
)}
<p>Lagos has 30 registered interstate parks. At 120 changes a day and a ₦300,000 fee, that book’s value is {short(b['lagos_registered_30']['npv'])}. The cash profit does not cover the office. The 2017 count of 145 Lagos inter-state parks, at the same rate, is worth {short(b['lagos_2017_145']['npv'])}. That is a small company. It is not a path to ₦50 billion. Twenty-two thousand booths would be. No park census holds them, and putting a change booth on a fuel forecourt is a fire and a theft problem, not a shortcut. Run the Lagos booths as their own test. Leave them out of the ₦50 billion sum.</p>
<p>The cash-in kiosk is not a third door. On the v5 commission stack it takes in ₦378,000 a year and loses about ₦2.29 million of cash against street costs of about ₦2.67 million. Adding sites adds losses.</p>

<h2>9. The upside that is not in the cheque</h2>
<p>The base plan charges ₦500 once per withdrawal. The circular is written per ₦20,000. EFInA’s explainer says “per ₦20,000” in the worked lines and “per transaction” in one sentence. Nairametrics reported a CBN clarification that the ₦100 applies whether or not the withdrawal reaches ₦20,000. The average ATM ticket in the first half of 2025, ₦36.34 trillion divided by 858.80 million transactions, is about ₦42,315. That ticket covers two full ₦20,000 blocks.</p>
<p>If counsel confirms that the ₦500 cap stacks, and if these machines match that average ticket, then 120 withdrawals a day at two blocks behave like the row in the first table: {c['high_100_120_two_blocks']['machines']:,} machines, cheque {short(two['year0'])}, {pct(two['share_of_national'])} of national withdrawals, return {irr_s(two['irr'])}. That row is not the cheque this paper asks anyone to raise. It is the reason to ask the lawyer the question before the term sheet is signed.</p>

<h2>10. Twelve months, then the raise</h2>
<p>Month 1. Counsel writes two answers: the machines can sit under the sponsor’s licence as off-site ATMs, and whether they count toward that issuer’s one-per-7,500 duty. The term sheet asks for 100% of the surcharge, the bank carrying cash and transit. A 70/30 sheet is filed only as the fallback in section 6. A 50/50 sheet is refused.</p>
<p>Month 2. Visit Lagos and Abuja forecourts. Keep a station only if no bank ATM is already dispensing. Ask one mall landlord, in writing, whether an anchor bank already holds the ATM right. Paper those pads. Do not pay a host a share that has not been written down.</p>
<p>Months 3 and 4. Proforma against the high band and the low band. NIBSS device and application fees, once. No shipment before the certificates.</p>
<p>Months 5 to 8. Install 12 high-band machines, ten stations and two malls, cheque {short(t12['year0'])}. Publish the weekly count of paying withdrawals, separate from the sponsor’s own cards.</p>
<p>Months 9 to 12. Decide. A median of 200 paying withdrawals opens the raise for the next fleet, first 100 machines if the median is holding, and the 1,292 only when the raise is subscribed. A median of 120, with 100% of the surcharge, is a small fleet worth keeping and not a reason to order 7,084 machines. Anything below the full-cost line of the signed split is a stop. Kiosks stay off the order. Booths, if tried, stay inside the Lagos register and outside this value.</p>

<h2>11. What kills the path</h2>
<ul>
  <li>The bank will not give up the surcharge, and will not accept the 3,340-machine fallback.</li>
  <li>The counted median is 120 rather than 200. The only high-band fleet that then hits ₦50 billion is {c['high_100_120']['machines']:,} machines, a cheque of {short(big['year0'])}, and {pct(big['share_of_national'])} of national withdrawals. This paper refuses that fleet.</li>
  <li>A bank ATM is already on the forecourt, so the paying share collapses. v5’s labelled case of 40% paying moves the cash break-even sharply higher. The 200 in this plan are paying withdrawals, not gross visits.</li>
  <li>The cap is cut, or a court treats it as once per transaction rather than per ₦20,000. The base plan already assumes once per withdrawal, so that reading does not break the cheque. It removes the upside in section 9.</li>
  <li>The pads and the machines are both booked as value. They are the same site.</li>
</ul>

<h2>12. Workings</h2>
<p>Machine costs, the 270-day year, the ₦500, the office (₦40 million plus ₦150,000 a machine at the start; ₦25 million plus ₦50,000 a machine a year) and the 28% hurdle are read from the v5 results, not rebuilt. National daily withdrawals = 858,800,000 / 181. Cards the current ATM stock already covers = 16,714 × 7,500. A fleet reaches when its present value is at least ₦50 billion. The search stops at 40,000 machines. Two blocks mean the cap is applied twice to one withdrawal. The pad fee solves the same present-value test. Reinvestment buys the next machine at the subsequent-unit price plus ₦150,000, and the unsold fleet is worth nothing at year 7. Recompute from <span class="small">model/path_model.py</span>.</p>

<h2>13. Sources</h2>
<ol class="sources">
  <li>v5 results file in this repository. High-band landed cost, low-band landed cost, street costs, surcharge cap, office and hurdle. The listing and the circular are sourced in that paper.</li>
  <li>Nairametrics, 19 January 2026. ATM withdrawals ₦36.34 trillion and 858.80 million transactions in the first half of 2025. https://nairametrics.com/2026/01/19/atm-transactions-surge-to-n36-34trn-in-six-months-despite-fresh-fees/</li>
  <li>Central Bank of Nigeria, payment modes. 16,714 active ATMs in the first half of 2024. https://www.cbn.gov.ng/PaymentsSystem/modes.html</li>
  <li>EFInA explainer on the 10 February 2025 ATM fee circular. ₦100 per ₦20,000 on-site, and up to ₦500 on top off-site. The note uses both “per ₦20,000” and “per transaction”. https://efina.org.ng/wp-content/uploads/2025/04/EFInA-Explainer-Series-Issue-1-CBN-2025-Review-of-ATM-Transaction-Fees.pdf</li>
  <li>Nairametrics, 13 February 2025. The ₦100 applies whether or not the withdrawal reaches ₦20,000. Off-site surcharge is capped at ₦500 per ₦20,000. https://nairametrics.com/2025/02/13/cbn-clarifies-n100-charge-on-customers-using-other-banks-atm/</li>
  <li>Nairametrics, 14 March 2026. One ATM per 7,500 payment cards by 2028, phased 30%, 60%, 100%. https://nairametrics.com/2026/03/14/cbn-mandates-one-atm-per-7500-payment-cards-by-2028/</li>
  <li>AIT, 13 February 2026, quoting CBN. More than 12 million contactless cards. Not a total of all payment cards. https://ait.live/nigeria-records-over-12-million-cashless-cards-cbn/</li>
  <li>NIBSS, AfriGO note. More than one million cards issued, transactions above ₦70 billion by September 2025. https://nibss-plc.com.ng/insight-three-years-later-how-is-cbns-afrigo-doing/</li>
  <li>NMDPRA downstream fact sheet, Q1–Q3 2025. Retail outlets approximately 22,681. https://alps.blob.core.windows.net/nmdprawebsite/Statistics/Upload-80c82709-7f84-4cea-959e-668d6e6d030e.pdf</li>
  <li>MEMAN, 2024 downstream report. 3,293 member stations, 1,392 of them in the South West. https://moman.org/wp-content/uploads/2025/05/2024-Nigeria-Energy-Downstream-Industry-Report.pdf</li>
</ol>
<p class="small">End of study. Earlier CashEase files are unchanged. The 200 withdrawals a day are the rate this value needs. They are not a count from a Nigerian forecourt.</p>
"""

    head = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CashEase Nigeria: A Path to ₦50 Billion</title>
<style>
@page {
  size: A4;
  margin: 14mm 13mm 16mm 13mm;
  @bottom-center {
    content: "CashEase Nigeria · Path to ₦50 billion · October 2026";
    font-family: "Liberation Sans", Arial, sans-serif;
    font-size: 8pt;
    color: #5c6b73;
  }
}
* { box-sizing: border-box; }
html { font-size: 10.5pt; }
body { margin: 0; color: #1a242b; font-family: "Liberation Serif", "Times New Roman", serif; line-height: 1.45; }
h1, h2 { font-family: "Liberation Sans", Arial, sans-serif; color: #1c3144; line-height: 1.2; }
h1 { font-size: 18pt; margin: 0 0 8px; }
h2 { font-size: 13.5pt; margin: 16px 0 6px; page-break-after: avoid; border-bottom: 1px solid #d5d0c8; padding-bottom: 3px; }
p { margin: 0 0 8px; }
ul { margin: 4px 0 10px; padding-left: 18px; }
li { margin: 0 0 4px; }
.cover { page-break-after: always; padding-top: 6mm; }
.kicker { font-family: "Liberation Sans", Arial, sans-serif; letter-spacing: 0.12em; text-transform: uppercase; font-size: 9pt; color: #8a6a2f; margin-bottom: 10px; }
.sub { font-size: 11.5pt; color: #1c3144; }
.verdict { background: #f4f1ea; border-left: 4px solid #8a6a2f; padding: 8px 12px; margin: 12px 0; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.5pt; page-break-inside: auto; }
table.tight td, table.tight th { padding: 3px 4px; }
caption { caption-side: bottom; text-align: left; font-family: "Liberation Serif", serif; font-size: 8.5pt; color: #3d4a52; padding-top: 4px; }
th { background: #1c3144; color: white; text-align: left; }
td { border-bottom: 1px solid #e6e1d8; vertical-align: top; }
tr { page-break-inside: avoid; }
thead { display: table-header-group; }
img { width: 92%; max-height: 78mm; object-fit: contain; display: block; margin: 4px auto 8px; }
sup { font-size: 0.75em; }
.sources { font-size: 9pt; }
.sources li { margin-bottom: 5px; }
.small { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.5pt; color: #3d4a52; }
</style>
</head>
<body>
"""
    html_path = ROOT / "source" / "study.html"
    pdf_path = ROOT / PDF_NAME
    html_path.write_text(head + body + "\n</body>\n</html>\n", encoding="utf-8")
    proc = subprocess.Popen(
        [
            "google-chrome",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--user-data-dir=/tmp/chrome-cashease-v7",
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
