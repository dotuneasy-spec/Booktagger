#!/usr/bin/env python3
"""Build the v4.1 China-kiosk addendum. Does not rewrite the v4 study."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(ROOT / "source"))

from china_charts import draw  # noqa: E402
from china_scenario import main, naira  # noqa: E402

PDF_NAME = "CashEase_China_Kiosk_Addendum.pdf"


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
        return "—"
    return f"{n:,.0f}"


def irr_s(v) -> str:
    if v is None:
        return "Not defined"
    return f"{v * 100:.1f}%"


def pb_s(v) -> str:
    if v is None:
        return "Not within 7 years"
    return f"{v:.1f} years"


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
<title>CashEase Nigeria: China-Built Kiosk Scenario</title>
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
<footer class="running">CashEase Nigeria · China-kiosk addendum · 7 October 2026 · Planning document</footer>
"""


def build() -> None:
    r = main()
    charts = draw(r, ROOT / "charts")
    rows = r["rows"]
    cheap = rows[0]["cases"]["high"]
    cheap_low = rows[0]["cases"]["low"]
    plain = rows[0]["cases"]["plain"]
    dear = rows[-1]["cases"]["high"]
    bare = rows[0]["cases"]["bare"]
    us = r["us_reference"]

    price_rows = []
    for row in rows:
        h = row["cases"]["high"]["landed"]
        lo = row["cases"]["low"]["landed"]
        price_rows.append([
            row["name"],
            f"US${row['fob']:,.0f}",
            short(lo["all_in_ngn"]),
            short(h["all_in_ngn"]),
            tx(row["cases"]["high"]["be_cash"]),
            tx(row["cases"]["high"]["be_full"]),
        ])

    profit_rows = []
    for row in rows:
        h = row["cases"]["high"]
        cells = [f"${row['fob']:,.0f}"]
        for volume in ("150", "250", "400"):
            a = h["at"][volume]
            cells.append(short(a["cash_profit"]))
            cells.append(short(a["operating"]))
        profit_rows.append(cells)

    return_rows = []
    for row in rows:
        h = row["cases"]["high"]
        a = h["at"]["400"]
        b = h["at"]["250"]
        return_rows.append([
            f"${row['fob']:,.0f}",
            short(h["landed"]["all_in_ngn"]),
            pb_s(b["payback"]),
            irr_s(b["irr"]),
            short(b["npv_28"]),
            pb_s(a["payback"]),
            irr_s(a["irr"]),
            short(a["npv_28"]),
        ])

    body = f"""
<section class="cover">
  <p class="kicker">Addendum to the bank-backed machine study</p>
  <h1>CashEase Nigeria: China-Built Kiosk Scenario</h1>
  <p class="deck">A v4.1 test of published Chinese FOB prices, landed in Nigeria, with no debt, a 60/40 bank share, and government support treated as a scenario rather than a contract.</p>
  <div class="verdict">
    <span>Verdict</span>
    <strong>No-go. Do not order from these listings.</strong>
    <p>The cheapest whole kiosk with a manufacturer price on the page is US$4,800. Factory programming for every naira denomination is treated as done. No naira-template invoice was found, so the landed cost uses a range: US$0, because the Hongzhou and GRG prices do not print an adder, up to US$1,800 a machine, the only published per-unit “Customized” line on a cash-recycler kiosk. With that US$1,800 inside the customs value, the high freight band is about {naira(cheap['landed']['all_in_ngn'])} and full-cost break-even is {tx(cheap['be_full'])} transactions on a scheduled open day. At 150 and at 250 the machine does not pay back inside seven years. At 400 the cash comes back in about {pb_s(cheap['at']['400']['payback'])} and the return is {irr_s(cheap['at']['400']['irr'])}, short of 28%. Cash reinvested from one such machine ends at {cheap['roll_400']['end']} machines in seven years, and only if every machine does 400 transactions a day and there is no head office. CBN, NIBSS and SON approval is a cost and a wait. It is not a reason to treat the note template as unsolved.</p>
  </div>
  <p class="meta">Prepared for Dotun, Lagos. Working name only. This paper does not replace the v4 study and does not edit it. Currency is the naira. The model is nominal, pre-tax and flat for seven years. Discount rate 28%. Not investment, legal or tax advice. Government free sites, free notes and free cash-in-transit are a scenario asked for in this addendum. They are not in hand. Figures tagged as assumptions are choices.</p>
</section>

<h2>1. What this addendum tests</h2>
<p>v4 priced a US deposit ATM at about {naira(us['all_in'])} before duty and found that a 60/40 share does not pay for it. This paper asks a narrower question. If the box is a Chinese kiosk at a price that is actually printed on a supplier page, and if the state really does give the site, the small notes and the cash-in-transit, and if CashEase borrows nothing and keeps 60% of the fee, does one machine pay, and can its cash buy the next one?</p>
<p>Four answers are already fixed by the evidence, before the arithmetic.</p>
<ul>
  <li>No Hyosung whole-machine FOB was found. The Hyosung figure in the search is a dispenser part at US$500 to US$1,400.<sup>7</sup> GRG’s own H22V page describes a cash dispenser and prints no price.<sup>8</sup></li>
  <li>NAFDAC does not regulate a cash kiosk. The registration Act covers processed food, drugs, cosmetics, medical devices and water.<sup>16</sup> NAFDAC’s own description of its mandate is the same list, plus bottled water, chemicals and detergents.<sup>17</sup> No NAFDAC fee is added. Applying one would invent a charge.</li>
  <li>No published count of “government collections” transactions at a kiosk was found. The 150, 250 and 400 tests are unchanged. They are still test volumes, not a forecast.</li>
  <li>Naira recognition is treated as solved. The factory is assumed to build and program the kiosk for every naira denomination. That is the instruction for this revision. It is not a certificate in the file.</li>
</ul>

<h2>2. Prices that are on a page</h2>
{table(
    ["Listing", "What it is", "Printed price", "Used in the model"],
    [
        ["Hongzhou HZ-3326, Shenzhen manufacturer", "Cash in/out kiosk. Page lists RoHS, CE and ISO. Cabinet 400 × 420 × 1,900 mm. HS code printed as 8471604000.", "US$5,500 for 1–9. US$4,800 for 10 or more.", "Yes. Both prices."],
        ["GRGintech showroom, GRGBanking brand, Guangzhou", "CCS-30 banknote and coin recycler. FOB terms are stated.", "US$9,000–10,000 a piece.", "Yes. Both ends."],
        ["GRGintech, same showroom", "Banknote dispenser module for retail and gaming.", "US$4,900.", "No. A module is not a kiosk."],
        ["Shenzhen Rong Mei Guang, Alibaba reseller", "Described as a GRG H68N whole cash-recycling machine. Not the GRG factory.", "US$6,000–11,000, minimum one piece.", "Yes, as a reseller band, not a factory quote."],
        ["Parts-channel page for a GRG DT-7000 / H68N", "Also offers new generic and refurbished stock, 90-day warranty, lead time of a few days.", "US$1,500–2,500.", "No. That channel is not a deployable-kiosk quote."],
        ["Hongzhou currency-exchange kiosk", "Cash acceptor and coin dispenser.", "US$2,999 to US$3,599.", "No. It is a different product."],
        ["Hyosung CDU-1100", "Front-load dispenser part.", "US$500–1,400.", "No. No Hyosung China machine price was found."],
    ],
    "Sources 1 to 8. A listing price is not a Nigerian delivered quote. Naira programming is costed in section 3.",
    tight=True,
)}

<h2>3. Landed cost</h2>
<p>The exchange rate is the same one used in v4: ₦1,331.69 per dollar, the NFEM close on 5 October 2026.<sup>23</sup></p>
<p>Ocean freight from Shenzhen to Lagos, port to port, is published at US$2,970 to US$3,450 for a 20-foot container.<sup>9,10</sup> A forwarder puts terminal handling at ₦250,000 to ₦450,000 a container and clearing at ₦150,000 to ₦350,000.<sup>11</sup> Those are forwarder ranges, not a terminal tariff. <span class="tag">Assumption</span> Ten kiosks in one 20-foot container. The Hongzhou cabinet is 0.319 cubic metres before a crate, so ten machines leave most of the box unused. The assumption raises freight per machine rather than pretending a full cube. It is not a packing quote. Freight per machine on that split is US${cheap_low['landed']['freight_usd']:.0f} at the low ocean rate and US${cheap['landed']['freight_usd']:.0f} at the high rate.</p>
<p>Hongzhou prints HS 8471.60.40.00.<sup>1</sup> A third-party tariff page gives a representative Nigeria rate of 5% for heading 8471.60 and says the national 8-digit and 10-digit line is not in its file. It tells the importer to confirm the line with Nigeria Customs.<sup>12</sup> The Customs CET portal was opened. It did not return an ATM ruling for this paper.<sup>13</sup> <span class="tag">Result</span> Duty in the table is 5% of CIF, labeled as that representative rate, not as a classification. A forwarder also describes an ETLS and inspection charge of about 1.5%.<sup>11</sup> That approximation is not in the sum. If it is real, landed cost is higher.</p>
<p>VAT is 7.5% under section 148 of the Nigeria Tax Act 2025, as set out by a statute note, and the rate is unchanged by the 2026 reform.<sup>14,15</sup> It is applied to CIF plus the 5% duty. SON’s published product-certificate fee for unregistered status is US$500, and a SONCAP certificate is US$350 a consignment.<sup>18</sup> Split across the ten-kiosk assumption, that is US$85 a machine. The 5% of FOB import-permit charge, minimum ₦550,000, is a different route, for manufacturers bringing in machinery. It is not applied to a commercial kiosk.</p>
<p>Installation and solar at ₦6.00 million, and software integration at ₦2.00 million, are the v4 assumptions. They were not re-quoted for a Chinese box. Spares have no Nigerian invoice in the file. Annual maintenance stays at 10% of the goods value converted to naira, so the programming adder is inside that base. Insurance stays at 1.5% of all-in. Both are assumptions.</p>
<p><span class="tag">Assumption, anchored to one listing.</span> No Hongzhou, GRG or Hyosung page printed a fee for a naira note template. Hongzhou’s own site says it customizes currency denominations for Nigeria, Kenya, South Africa, Tanzania and Uganda, and it prints no price for that work. The same page says a custom build takes 30 to 35 working days.<sup>25</sup> A CashCode part number lists naira denominations from ₦5 to ₦1,000 and the dealer page says “call for pricing”, so that page is not a cost.<sup>26</sup> The only published per-unit customization dollar amount found on a cash-recycler kiosk is “Customized + US$1,800/unit”, minimum one unit.<sup>27</sup> That line does not say it is a naira template. It is used here as the top of the range, added to the FOB before duty and VAT, because a silent sticker is not evidence that programming is free. The bottom of the range is US$0, which is what the Hongzhou and GRG prices actually print.</p>
<p>On the US$4,800 machine the US$1,800 adder produces a high-band all-in of {naira(cheap['landed']['all_in_ngn'])}. Dropping the adder, and keeping the same freight, duty, SONCAP, site works and the NIBSS payments below, produces {naira(plain['landed']['all_in_ngn'])}. Full-cost break-even moves from {tx(cheap['be_full'])} transactions a day to {tx(plain['be_full'])}.</p>
<p>NIBSS’s May 2024 sandbox note charges ₦250,000 for a device certification and ₦250,000 for an application certification.<sup>28</sup> The September 2026 recertification note says “the applicable fee” and does not restate the naira amount.<sup>22</sup> The ₦500,000 pair is added once, to the first machine, because the form is one named device and one named application. Later machines in the cash-flow count do not pay it again. It is a POS-terminal payment. It is not a published ATM type-approval fee, and no CBN fee for an independent-ATM approval was found. SONCAP is already in the border cost. NAFDAC stays at zero.</p>
{table(
    ["Listing", "FOB", "Landed, low band", "Landed, high band", "Cash break-even", "Full-cost break-even"],
    price_rows,
    "High and low bands both include the US$1,800 programming adder and a one-time ₦500,000 NIBSS pair on the first machine. Break-even uses the high band. Transactions are per scheduled open day.",
    tight=True,
)}
<figure>
  <img src="../charts/{charts['landed']}" alt="Bar chart of landed cost against the US reference machine">
  <figcaption>Figure 1. High-band landed cost of each listing, with the US$1,800 programming adder, next to the v4 US reference of {naira(us['all_in'])} before duty.</figcaption>
</figure>
<p><span class="tag">Result</span> On the US$4,800 listing the high band, with the programming adder, is {naira(cheap['landed']['all_in_ngn'])}. The border piece of that, before the ₦8.00 million of site works and before the ₦500,000 NIBSS pair, is {naira(cheap['landed']['border_ngn'])}. The US$11,000 end of the reseller band lands at {naira(dear['landed']['all_in_ngn'])}. The v4 US machine, still before duty, remains {naira(us['all_in'])}.</p>

<h2>4. The scenario being costed</h2>
<p>CashEase pays cash for the machine. There is no debt, so there is no interest to cut. The bank takes 40% of the fee pool and keeps 60% for CashEase. The pool is the v4 mix: ₦145.50 gross, ₦12.60 of shrink, ₦132.90 left. CashEase’s 60% is ₦{r['ce_per_tx']:.2f} a transaction. Public sites are treated as off-site, so the ₦250 surcharge assumption is still in the mix. A bank gallery would not earn it. That case was costed in v4 and is worse.</p>
<p><span class="tag">Scenario, not a contract.</span> Rent is zero. The float’s opportunity cost is zero, on the story that the CBN supplies the notes. Cash-in-transit is zero in the base, and half of the v4 visit assumption in a sensitivity. That half is ₦960,000 a year. Power, the data link and security stay with CashEase. Free ground is not a free guard. The ICRC 1% of gross is not charged, because this scenario is not filed as an ICRC concession. If it were, v4 already shows that fee.</p>
<p>The CBN governor, in July 2026, still tied lower-note scarcity to falling demand. A scenario in which the CBN fills  the cassettes is a planning switch. It is not a supply letter.</p>
<figure>
  <img src="../charts/{charts['breakeven']}" alt="Full-cost break-even for each Chinese price">
  <figcaption>Figure 2. Full-cost break-even on the high landed band, with free rent, free notes and free cash-in-transit. The lines are the three test volumes.</figcaption>
</figure>

<h2>5. One machine at 150, 250 and 400</h2>
{table(
    ["FOB", "150 cash", "150 operating", "250 cash", "250 operating", "400 cash", "400 operating"],
    profit_rows,
    "High freight band. One machine, no head office, no debt. Cash profit is the 60% fee minus power, link, security, maintenance and insurance. Operating profit also subtracts depreciation.",
    tight=True,
)}
{table(
    ["FOB", "All-in", "Payback at 250", "IRR at 250", "NPV at 250", "Payback at 400", "IRR at 400", "NPV at 400"],
    return_rows,
    "Unlevered equity. NPV is at 28%. Payback is undiscounted. “Not within 7 years” means the cash flows in the model horizon do not recover the machine.",
    tight=True,
)}
<p>Read the US$4,800 row first. It is the most generous whole-kiosk price on a manufacturer page.</p>
<ul>
  <li><span class="tag">Result</span> At 150 transactions, cash profit is a loss of {naira(abs(cheap['at']['150']['cash_profit']))}. Operating profit is a loss of {naira(abs(cheap['at']['150']['operating']))}. NPV is {short(cheap['at']['150']['npv_28'])}. The machine does not pay back inside seven years.</li>
  <li><span class="tag">Result</span> At 250, cash profit is {naira(cheap['at']['250']['cash_profit'])} and operating profit is a loss of {naira(abs(cheap['at']['250']['operating']))}. IRR is {irr_s(cheap['at']['250']['irr'])}. Payback is not inside seven years. NPV is {short(cheap['at']['250']['npv_28'])}.</li>
  <li><span class="tag">Result</span> At 400, cash profit is {naira(cheap['at']['400']['cash_profit'])} and operating profit is {naira(cheap['at']['400']['operating'])}. Undiscounted payback is {pb_s(cheap['at']['400']['payback'])}. On the high freight band, IRR is {irr_s(cheap['at']['400']['irr'])} and NPV is {short(cheap['at']['400']['npv_28'])}. On the low freight band, IRR is {irr_s(cheap_low['at']['400']['irr'])} and NPV is {short(cheap_low['at']['400']['npv_28'])}. The hurdle is 28%. Both freight bands miss it. Getting the cash back is not the same as earning 28%.</li>
</ul>
<p>Every dearer listing is worse. The GRGintech CCS-30 at US$9,000 to US$10,000, and the top of the reseller band at US$11,000, have full-cost break-evens of {tx(rows[3]['cases']['high']['be_full'])} to {tx(dear['be_full'])} transactions a day. At 400 their IRRs are {irr_s(rows[3]['cases']['high']['at']['400']['irr'])} and {irr_s(dear['at']['400']['irr'])}. Both miss 28%.</p>
<p>Putting back half of the v4 cash-in-transit assumption moves the US$4,800 full-cost break-even from {tx(cheap['be_full'])} to {tx(cheap['be_full_half_cit'])}. A subsidy that is only a discount, rather than a waiver, leaves 250 transactions under the line.</p>
<p>The zero-adder case, high freight, still misses the hurdle. Its all-in cost is {naira(plain['landed']['all_in_ngn'])}, its full-cost break-even is {tx(plain['be_full'])} transactions, and its IRR at 400 transactions is {irr_s(plain['at']['400']['irr'])}, with NPV {short(plain['at']['400']['npv_28'])}.</p>
<p>The same supports do not rescue the US reference machine. Its cash break-even is still {tx(us['be_cash'])} transactions a day and its full-cost break-even is {tx(us['be_full'])}. The Chinese sticker moves the break-even down. With the programming adder in the price, the move stops at {tx(cheap['be_full'])} transactions, not at 150.</p>
<div class="callout">
  <p><strong>The ₦8.00 million site-works assumption.</strong> Strip it out and the US$4,800 machine, high freight band, has an all-in cost of {naira(bare['landed']['all_in_ngn'])}, a full-cost break-even of {tx(rows[0]['cases']['bare']['be_full'])} transactions, and an IRR at 400 transactions of {irr_s(bare['at']['400']['irr'])}. That case is shown so the sticker price is not confused with the Nigerian works. The works were not re-quoted. They stay in the verdict.</p>
</div>

<h2>6. Paying for the next machine out of cash</h2>
<p>The rule is equity only. One machine is bought at the start. Each year’s cash profit, and only that, buys the next machine. Nothing is borrowed. The fleet stops at the {r['listed_sites']:,} addresses listed in v4, which is a ceiling the cash never reaches.</p>
<p><span class="tag">Result</span> On the US$4,800 machine, high band, with the programming adder, at 400 transactions and with no head office, the fleet path over seven years is {", ".join(str(n) for n in cheap['roll_400']['path'])}. It ends at {cheap['roll_400']['end']} machines. At 250 transactions the path stays at one machine, because a year of cash profit does not buy the next box inside the horizon. At 150 it stays at one. The same 400-transaction case, after the v4 head-office assumption of {naira(r['hq_annual'])} a year, also stays at one machine. It takes about {r['hq_annual'] / cheap['at']['400']['cash_profit']:.1f} machines at 400 transactions a day just to cover that office. Starting from one machine, the office consumes the cash before a second machine is bought.</p>
<p>That is the maximum fleet this cash-flow rule produces: {cheap['roll_400']['end']} machines in seven years, on the cheapest listing, at a test volume of 400, with the US$1,800 adder, with the government supports assumed and with no head office. It is not a demand forecast. A 500-machine phase, a 1,500-machine phase and a 20,000-machine phase are not funded by this cash flow.</p>

<h2>7. How many sites clear the line</h2>
<p>No public file gives daily transactions for a change kiosk. The number of sites above the break-even is unknown. What is known is the hurdle and the address count.</p>
<ul>
  <li>Full-cost break-even on the listings used here runs from {tx(cheap['be_full'])} to {tx(dear['be_full'])} transactions a scheduled open day, after the free-site and free-cash assumptions.</li>
  <li>Cash break-even, which ignores depreciation, runs from {tx(cheap['be_cash'])} to {tx(dear['be_cash'])}.</li>
  <li>The only public busy-site anecdote in the v4 file is 80 to 100 POS transactions a day, and it is a blog.<sup>24</sup> It sits under every cash line and every full-cost line in this paper. The lowest cash line, on the US$4,800 machine, is {tx(cheap['be_cash'])} transactions a day.</li>
  <li>The address lists in v4 sum to {r['listed_sites']:,} before overlap: 774 local authorities, 2,048 postal outlets, 30 Lagos parks on the register, 10 Lagos–Ibadan stations, 13 planned Blue Line stations and 12 proposed Red Line stations. None of those lists is a traffic count. Twenty thousand remains a target without a site file.</li>
</ul>
<p><span class="tag">Result</span> Sites evidenced to clear break-even: none. Maximum fleet the cash-flow rule will buy: {cheap['roll_400']['end']}, and only in the case stated in section 6. A realistic planning fleet, once a head office and a volume below 400 are admitted, is the first machine, kept as a test if a bank and a standards body will touch it, and not a network.</p>

<h2>8. Compliance</h2>
<p>Naira validation is not the stop in this revision. The factory is assumed to program every naira denomination before shipment. What remains is permission to connect the machine, and that permission has a price and a clock.</p>
<ul>
  <li>The 2020 CBN guidelines require ATM deployers to meet PCI DSS, require every ATM to be able to dispense every naira denomination, and require EMV Level 1 and Level 2.<sup>19</sup> The 2010 ATM standards say the same things in an earlier form, and they require Nigerian processing and naira collateral for domestic settlement.<sup>20</sup> March 2026 was reported to replace parts of the ATM chapter. This paper does not pretend a line-by-line reading of that PDF. The open requirements are the ones quoted. No fee and no calendar for a CBN independent-ATM approval were found.</li>
  <li>NIBSS certifies payment terminals and applications. The May 2024 note charges ₦250,000 to certify a device and ₦250,000 to certify an application, and it asks for EMV Level 1 and Level 2, PCI, TQM, Visa and Mastercard approvals, other scheme letters, and an OEM support letter. Sign-up asks for a CBN licence. The note names banks, PSSPs and MMOs as the firms that can enter that process.<sup>28</sup> The September 2026 recertification note keeps the same document list, says “the applicable fee”, and limits re-certification sign-up to PTSPs.<sup>21,22</sup> After the papers are in, the stated service time is 48 hours for a device and 72 hours for an application. The renewal fee in the 2024 note is ₦50,000. The note does not say how often that renewal falls. No fee was found for the EMV, PCI or scheme certificates themselves. Those certificates are the long pole. The sandbox clock does not start until they exist.</li>
  <li>Hongzhou’s cash in/out listing shows RoHS, CE and ISO.<sup>1</sup> A different Hongzhou page says the card reader is EMV-compliant, the keypad is PCI-compliant, and currency denominations can be customized for Nigeria.<sup>25</sup> Those are manufacturer sentences. They are not a NIBSS certificate and they are not a CBN approval. SONCAP, already in the landed cost, checks a product certificate. It does not approve a naira template.</li>
  <li>The parts-channel listing that offers a GRG recycler at US$1,500 to US$2,500 also offers refurbished and generic stock and a 90-day warranty.<sup>6</sup> A 90-day warranty against a seven-year model life is a spares risk. That price was kept out of the economics for that reason. None of the cleaner listings came with a Nigerian spares contract.</li>
  <li>Agent-banking rules still bar a non-human machine from being the agent, on the law-firm quotations used in v4. A Chinese box does not open that route. The licence path is still a bank-held independent-ATM approval. That approval was not in hand for v4, and it is not in hand here.</li>
</ul>
<p>Custom production, on Hongzhou’s page, is 30 to 35 working days after the order.<sup>25</sup> NIBSS then waits on certificates this search did not find priced or dated. The ₦500,000 sandbox pair is in the first machine’s cost. It does not buy those certificates.</p>

<h2>9. Verdict</h2>
<p>No-go.</p>
<p>The Chinese listings are real, and they are much cheaper than the US reference. Naira recognition is assumed to be done at the factory. Under free sites, free notes, free cash-in-transit, a 60/40 share and no debt, the cheapest manufacturer price plus the US$1,800 programming stand-in still needs about {tx(cheap['be_full'])} transactions a day to cover full cost. The volumes of 150 and 250 do not pay the machine back inside its seven-year life. The volume of 400 pays the cash back in {pb_s(cheap['at']['400']['payback'])} and earns {irr_s(cheap['at']['400']['irr'])}, which is short of 28% on both freight bands. Leaving the programming adder at zero still earns {irr_s(plain['at']['400']['irr'])}. Cash flow from the 400-transaction case buys a fleet of {cheap['roll_400']['end']} only if head office is ignored. Head office, on the v4 assumption, stops the fleet at one.</p>
<p>Government backing is not secured. No collections volume was found to add. NAFDAC is the wrong agency. SONCAP is a few hundred dollars. The NIBSS sandbox payments that are published come to ₦500,000 and still require EMV and PCI certificates that were not attached to these listings. The order gate is a delivered price that earns 28% at a measured volume, a site above {tx(cheap['be_full'])} transactions a day, and the government supports in a signed paper. None of those three exists. The v4 conclusion stands: do not buy the machines.</p>

<h2>10. Workings</h2>
<p>Goods dollars = printed FOB + 1,800 in the base case, or printed FOB alone in the zero-adder case. The 1,800 is the Alibaba customization line used as a stand-in. It is not a naira-template invoice.</p>
<p>FOB naira in the maintenance base = goods dollars × 1,331.69.</p>
<p>Freight dollars per machine = container rate / 10. The 10 is an assumption. Container rates used are US$2,970 and US$3,450.</p>
<p>CIF = goods dollars + freight. Duty = 0.05 × CIF. VAT = 0.075 × (CIF + duty). SONCAP dollars per machine = (500 + 350) / 10.</p>
<p>Border naira = (CIF + duty + VAT + SONCAP dollars) × 1,331.69 + (terminal handling + clearing) / 10.</p>
<p>All-in for the first machine = border naira + 6,000,000 + 2,000,000 + 500,000. The 6,000,000 and 2,000,000 are the v4 install and software assumptions. The 500,000 is one device payment plus one application payment from the May 2024 NIBSS note. The next machine drops the 500,000.</p>
<p>CashEase naira per transaction = 0.60 × (145.50 − 12.60) = 79.74.</p>
<p>Cash cost = power + link + security + 10% of goods naira + 1.5% of all-in. Rent, cash-in-transit and float cost are zero in the base scenario. Full cost adds all-in / 7.</p>
<p>Break-even transactions per open day = annual cost / 79.74 / 270.</p>
<p>NPV discounts the all-in outflow and seven years of cash profit. No salvage. No debt service. IRR is solved between −99% and 500%.</p>
<p>Recompute from <span class="small">model/china_scenario.py</span>. The v4 file <span class="small">model/machine_model.py</span> is not changed.</p>

<h2>11. Sources</h2>
<ol class="sources">
  <li>Shenzhen Hongzhou Smart Technology, cash in/out kiosk HZ-3326, US$5,500 and US$4,800, RoHS, CE, ISO, cabinet size and HS 8471604000. https://hongzhou2.en.made-in-china.com/product/HnfURoZyAMhj/China-Bank-Government-Cash-in-out-Kiosk-Cash-Recycler-ATM-Machine-Bulk-Cash-Deposit-Payment-Kiosk.html</li>
  <li>Shenzhen Hongzhou, currency-exchange kiosk with coin dispenser, US$2,999 to US$3,599. Not used as the note-break machine. https://hongzhou2.en.made-in-china.com/product/fQSYjIHlCyVk/China-ATM-Kiosk-Foreign-Currency-Exchange-Machine-with-Cash-Acceptor-Coin-Dispenser.html</li>
  <li>GRGintech showroom, CCS-30 FOB US$9,000–10,000 and a dispenser module at US$4,900. https://www.made-in-china.com/showroom/grgintech/</li>
  <li>GRGintech banknote dispenser module page, US$4,900. https://www.made-in-china.com/showroom/grgintech/product-detailuJiRWEaxoeYP/China-Grgintech-Grg-Banknote-Dispenser-for-Retail-Gaming.html</li>
  <li>Alibaba listing by Shenzhen Rong Mei Guang, GRG H68N described as a whole recycling machine, US$6,000–11,000. https://www.alibaba.com/product-detail/GRG-H68N-ATM-Machine-Bank-Whole_1600881455348.html</li>
  <li>Parts-channel listing, GRG DT-7000 / H68N, US$1,500–2,500, refurbished and generic options, 90-day warranty. Not used as a kiosk price. https://atmmall.wholesale.autoplansearch.com/pz6c99590-cash-recycle-system-grg-dt-7000-h68n-bank-atm-machines.html</li>
  <li>Hyosung CDU-1100 dispenser part, US$500–1,400. Not a whole machine. https://www.rc363.com/products-search/pz756a7c4-cz57ed439-hyosung-front-load-6k-cdu-1100-cash-dispenser-hyosung-note-dispenser-force-7010000193.html</li>
  <li>GRGBanking H22V product page. No price is printed. https://global.grgbanking.com/en/ProductDetail_79_128.html</li>
  <li>DTFU Logistics, Shenzhen to Nigeria 20-foot port-to-port, US$2,970–3,450. https://www.dtfulogistics.com/news/20ft-and-40ft-shipping-from-china-to-nigeria/</li>
  <li>Presou, Shenzhen 20GP, US$2,970–3,450, April 2026 capacity note. https://presou.com/fcl-shipping-china-to-nigeria-2026-20gp-40gp-rates/</li>
  <li>Dantful, terminal handling ₦250,000–₦450,000 a container, clearing ₦150,000–₦350,000, and a description of ETLS/CISS as about 1.5%. https://www.dantful.com/how-much-is-shipping-from-china-to-nigeria/</li>
  <li>HS Code DB, heading 8471.60, representative Nigeria rate 5%, national line not covered, confirm with Nigeria Customs. https://hscodedb.com/ng/hs-code/8471-60/</li>
  <li>Nigeria Customs Service tariff portal. No ATM classification ruling was retrieved for this paper. https://cet.customs.gov.ng/</li>
  <li>LawGlobal Hub, Nigeria Tax Act 2025, section 148, VAT at 7.5%. https://www.lawglobalhub.com/section-148-nigeria-tax-act-2025/</li>
  <li>BDO, Nigeria Tax Act 2025, standard VAT rate remains 7.5% from 1 January 2026. https://www.bdo.global/en-gb/insights/tax/indirect-tax/nigeria-new-legislation-includes-important-changes-to-vat-rules</li>
  <li>Food, Drugs and Related Products (Registration, etc.) Act, section 1. https://www.nafdac.gov.ng/wp-content/uploads/Files/Resources/Regulations/NAFDAC_Acts/FOOD-DRUGS-AND-RELATED-PRODUCTS-REGISTRATION-ACT-Cap.F.33.pdf</li>
  <li>NAFDAC annual report 2024, mandate over food, drugs, cosmetics, medical devices, bottled water, chemicals and detergents. https://nafdac.gov.ng/wp-content/uploads/Files/Resources/Reports/NAFDAC_Annual_Report/NAFDAC-ANNUAL-REPORT-2024.pdf</li>
  <li>Standards Organisation of Nigeria, SONCAP FAQ, product-certificate and SONCAP-certificate fees, and the import-permit route. https://son.gov.ng/soncap-faq/</li>
  <li>Central Bank of Nigeria, Guidelines on Operations of Electronic Payment Channels in Nigeria, 2020. PCI DSS, all naira denominations, EMV Levels 1 and 2. https://www.cbn.gov.ng/Out/2020/CCD/Reviewed%20and%20Approved%20Guidelines%20on%20Operations%20of%20Electronic%20Payment%20Channels%20in%20Nigeria%202020.pdf</li>
  <li>Central Bank of Nigeria, Standards and Guidelines on ATM Operations, 2010. https://www.cbn.gov.ng/OUT/2010/CIRCULARS/BSPD/ATM%20STANDARDS%201.PDF</li>
  <li>NIBSS, payment terminal and application certification. https://nibss-plc.com.ng/payment-terminal-and-application-certification/</li>
  <li>NIBSS, step-by-step certification on the sandbox, September 2026 file. The fee is described, not quantified. https://nibss-plc.com.ng/wp-content/uploads/2026/09/Step-By-Step-Recertification-Process-on-NIBSS-Sandbox-_v5-1.pdf</li>
  <li>Arbiterz, NFEM close of ₦1,331.69 per dollar on 5 October 2026. https://arbiterz.com/naira-dollar-rate-october-6-2026-naira-trades-at-n1331-69-in-cbn-nfem-window/</li>
  <li>Turnet Finance, the 80-to-100 daily transaction anecdote used in v4. Not a NIBSS average. https://turnetfinance.ng/moniepoint-review/</li>
  <li>Hongzhou Smart, through-the-wall cash machine page. Nigeria is named under currency-denomination customization. No fee is printed. Custom production is stated as 30 to 35 working days. The page also describes an EMV card reader and a PCI keypad. Those sentences are not certificates. https://www.hongzhousmart.com/through-the-wall-cdm.html</li>
  <li>CashCode FLX-NG10-622736, a bill acceptor whose page lists naira denominations. The displayed price is a call for pricing, so no dollar figure is used. https://billacceptors.us/cashcode-flx-ng10-622736-bill-acceptor-nigeria</li>
  <li>Alibaba listing of a cash POS self-service kiosk with a bill recycler. Customization option printed as “Customized + US$1,800/unit”, minimum one unit. The line does not say the adder is a naira template. https://www.alibaba.com/product-detail/Customized-SDK-Enabled-Cash-POS-Self_1601385352394.html</li>
  <li>NIBSS, step-by-step certification of payment terminals and applications, May 2024 file. Device certification ₦250,000. Application certification ₦250,000. Renewal fee ₦50,000, with no interval stated. Sign-up requires a CBN licence. https://nibss-plc.com.ng/wp-content/uploads/2024/05/Step-By-Step-Certification-process-on-Sandbox-for-use-updated.pdf</li>
</ol>
<p class="small">End of addendum. The v4 PDF and its model are unchanged.</p>
"""
    html_path = ROOT / "source" / "addendum.html"
    pdf_path = ROOT / PDF_NAME
    html_path.write_text(HEAD + body + "\n</body>\n</html>\n", encoding="utf-8")
    proc = subprocess.Popen(
        [
            "google-chrome",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--user-data-dir=/tmp/chrome-cashease-v41",
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
