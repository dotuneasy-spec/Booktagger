#!/usr/bin/env python3
"""Build the CashEase v3 study HTML and PDF from the planning model."""

from __future__ import annotations

import subprocess
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(ROOT / "source"))

from charts import draw  # noqa: E402
from financial_model import main, naira  # noqa: E402

CHROME = "google-chrome"


def comma(n: float) -> str:
    return f"{n:,.0f}"


def tx(n: float) -> str:
    return f"{n:,.0f}"


def pct(n: float | None) -> str:
    if n is None:
        return "Not defined"
    return f"{n * 100:.1f}%"


def html_table(headers: list[str], rows: list[list[str]], caption: str | None = None, tight: bool = False) -> str:
    cap = f"<caption>{caption}</caption>" if caption else ""
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    cls = " class=\"tight\"" if tight else ""
    return f"<table{cls}>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def short_naira(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000_000:
        return f"{sign}₦{n / 1_000_000_000_000:.2f}tn"
    if n >= 1_000_000_000:
        return f"{sign}₦{n / 1_000_000_000:.2f}bn"
    if n >= 1_000_000:
        return f"{sign}₦{n / 1_000_000:.1f}m"
    return f"{sign}₦{n:,.0f}"


def build() -> None:
    r = main()
    charts = draw(r, ROOT / "charts")
    ref = r["hardware"]["deposit_low"]
    be = r["breakeven"]
    u = r["unit_test_80"]
    c = r["contribution"]
    f = r["reference_fixed"]
    hurdle = r["hurdle_tx_per_open_day"]
    test = r["attended_test"]
    a = r["assumptions"]

    def scen_row(key: str, label: str) -> list[str]:
        s = r["scenarios"][key]
        p = s["pnl"]
        return [
            label,
            comma(p["kiosks"]),
            short_naira(p["capex_ngn"]),
            short_naira(p["float_ngn"]),
            short_naira(-s["year0_with_hq"]),
            short_naira(p["cash_profit_ngn"]),
            short_naira(p["operating_profit_ngn"]),
            short_naira(s["npv_28"]),
        ]

    pilot_flows = r["scenarios"]["pilot"]["cashflows"]
    cf_rows = []
    for year, cf in enumerate(pilot_flows):
        note = "Machines, float, and set-up" if year == 0 else (
            "Includes return of float" if year == len(pilot_flows) - 1 else "Operating cash flow"
        )
        cf_rows.append([str(year), naira(cf), note])

    sens_rows = []
    for s in r["sensitivities"]:
        sens_rows.append(
            [
                f"₦{comma(s['cit_per_visit_ngn'])}",
                f"₦{comma(s['note_fee_ngn'])}",
                f"₦{comma(s['surcharge_ngn'])}",
                f"₦{s['net_per_tx_ngn']:.0f}",
                tx(s["street_be_tx"]),
                tx(s["cash_be_tx"]),
                tx(s["full_be_tx"]),
            ]
        )

    vol_rows = []
    for row in r["volume_grid"]:
        vol_rows.append(
            [
                tx(row["tx"]),
                naira(row["net_revenue_ngn"]),
                naira(row["cash_profit_ngn"]),
                naira(row["operating_profit_ngn"]),
                naira(row["npv_28"]),
                pct(row["irr"]),
            ]
        )

    hw_rows = []
    labels = [
        ("dispense_low", "Dispense-only ATM, low end of published range", 25_000),
        ("recycler_median", "Teller recycler, published median", 36_000),
        ("deposit_low", "Deposit-automated ATM, low end (reference case)", 40_000),
        ("deposit_high", "Deposit-automated ATM, high end", 55_000),
    ]
    for key, name, usd in labels:
        h = r["hardware"][key]
        hw_rows.append(
            [
                name,
                f"${comma(usd)}",
                naira(h["exworks_ngn"]),
                naira(h["freight_ngn"]),
                naira(h["all_in_ngn"]),
            ]
        )

    unit_rows = [
        ["Gross fee revenue", naira(u["gross_revenue_ngn"])],
        ["Bank share of the cash-out surcharge", naira(-u["bank_share_ngn"])],
        ["Shrinkage on cash paid out", naira(-u["shrink_ngn"])],
        ["Net revenue", naira(u["net_revenue_ngn"])],
        ["Rent", naira(-u["rent_ngn"])],
        ["Power (diesel share plus solar upkeep)", naira(-u["power_ngn"])],
        ["Connectivity", naira(-u["connectivity_ngn"])],
        ["Cash-in-transit", naira(-u["cit_ngn"])],
        ["Security share", naira(-u["security_ngn"])],
        ["Maintenance", naira(-u["maintenance_ngn"])],
        ["Insurance", naira(-u["insurance_ngn"])],
        ["Cash profit", naira(u["cash_profit_ngn"])],
        ["Depreciation", naira(-u["depreciation_ngn"])],
        ["Opportunity cost of float at the MPR", naira(-u["float_cost_ngn"])],
        ["Operating result", naira(u["operating_profit_ngn"])],
    ]

    cob_share = 4.92 / 5.523 * 100
    float_share = 40e9 / 4.87e12 * 100

    css = r"""
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
h1 { font-size: 28pt; font-weight: 700; margin: 0 0 8px; }
h2 { font-size: 15pt; margin: 22px 0 8px; page-break-after: avoid; border-bottom: 1px solid #d5d0c8; padding-bottom: 4px; }
h3 { font-size: 12pt; margin: 16px 0 6px; page-break-after: avoid; }
p { margin: 0 0 8px; }
ul, ol { margin: 4px 0 10px; padding-left: 18px; }
li { margin: 0 0 4px; }
a { color: #1c3144; }
.cover { page-break-after: always; min-height: 250mm; padding-top: 18mm; }
.kicker { font-family: "Liberation Sans", Arial, sans-serif; letter-spacing: 0.12em; text-transform: uppercase; font-size: 9pt; color: #8a6a2f; margin-bottom: 10px; }
.deck { font-size: 13pt; max-width: 38em; }
.verdict { border: 2px solid #8d2b2b; background: #f8f1f1; padding: 12px 14px; margin: 18px 0; page-break-inside: avoid; }
.verdict strong { display: block; font-family: "Liberation Sans", Arial, sans-serif; font-size: 14pt; color: #8d2b2b; margin: 2px 0 6px; }
.verdict span { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.5pt; letter-spacing: 0.14em; text-transform: uppercase; color: #8d2b2b; }
.meta { color: #5c6b73; font-size: 9.5pt; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.4pt; page-break-inside: avoid; }
caption { caption-side: bottom; text-align: left; font-family: "Liberation Serif", serif; font-size: 8.5pt; color: #5c6b73; padding-top: 4px; font-style: italic; }
th { text-align: left; background: #1c3144; color: white; padding: 5px 6px; font-weight: 600; vertical-align: bottom; }
td { padding: 4px 6px; border-bottom: 1px solid #e0dbd2; vertical-align: top; }
table.tight { font-size: 7.5pt; }
table.tight th, table.tight td { padding: 3px 4px; }
tr:nth-child(even) td { background: #f7f4ef; }
figure { margin: 10px 0 14px; page-break-inside: avoid; }
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
.sources li { margin-bottom: 5px; font-size: 8.6pt; word-break: break-word; }
"""

    body = f"""
<footer class="running">CashEase Nigeria · Feasibility study · 7 October 2026 · Confidential planning document</footer>
<section class="cover">
  <p class="kicker">Feasibility study</p>
  <h1>CashEase Nigeria</h1>
  <p class="deck">Self-service kiosks at markets, motor parks, bus stops and stall clusters. They would break large naira notes, pay out cash, and sell airtime and bills. Is there a real case for up to 20,000 machines?</p>
  <div class="verdict">
    <span>Verdict</span>
    <strong>No-go on 20,000 machines. Do not order hardware.</strong>
    <p>Nigeria has a thin ATM network and a real small-note problem. It also already has millions of POS agents who sell cash. A kiosk that can do the job of a recycling ATM costs, on published US prices, about {naira(ref['all_in_ngn'])} before import duty. At the fees used in this study it needs about {tx(be['full_tx_per_open_day'])} transactions on a scheduled open day to cover its full cost, and about {tx(hurdle['base_fee'])} to earn a 28% return. Nothing in the public record supports that traffic. The only justified spend is a 90-day attended test of the change fee, after a lawyer and a bank have answered two questions in writing.</p>
  </div>
  <p class="meta">Prepared for Dotun, Lagos. Working name only. Company registration was not checked. Currency is the naira, nominal. Horizon is seven years. Discount rate is 28%, made of the 23% policy rate plus a 5 percentage-point planning premium. This document is not investment, legal, or tax advice. Figures tagged as assumptions are choices, not measurements. CashEase has no operating history, so there is no observed transactions-per-kiosk figure to import.</p>
</section>

<h2>1. How to read the numbers</h2>
<p>Three kinds of figure appear below.</p>
<ul>
  <li><strong>Sourced.</strong> An external fact, with a number in brackets that points to the sources list. If two sources disagree, both are shown. No statistic in this study was filled in to make a table complete.</li>
  <li><strong><span class="tag">Assumption</span>.</strong> A planning choice. Rent, cash-in-transit, the fee mix, uptime, and the freight adder are assumptions. They are listed again in the appendix so they can be replaced with quotes.</li>
  <li><strong><span class="tag">Result</span>.</strong> Arithmetic from the sourced inputs and the assumptions. The break-even, the profit and loss, the cash flows, and the NPV are results. They are not forecasts of how many people will use a machine.</li>
</ul>
<p>The reference case uses a deposit-capable ATM at the bottom of a published US price range, converted at the 5 October 2026 official rate. A cheaper purpose-built box may exist. No Nigerian written quote was found, so none is used. Import duty is excluded until a customs classification exists. Duty would make the machine dearer, not cheaper.</p>

<h2>2. Verdict</h2>
<p>There is a gap in small notes and in ATM coverage. There is not a gap in ordinary cash-out. A 20,000-machine network would be larger than the country’s entire active ATM stock of June 2024, and it would still be a rounding error beside the POS network. The economics fail before that scale is reached. They fail at one machine.</p>
<div class="callout">
  <p><strong>What to do.</strong> Do not buy kiosks and do not raise capital for 2,000 or 20,000 units. Ask counsel whether a note-exchange box is lawful, and ask two banks whether they will deliver small notes to a non-branch site on a schedule. If either answer is no, stop. If both are open, spend about {naira(test['spend_ex_float_ngn'])} plus {naira(test['sites'] * test['float_per_site_ngn'])} of float on a 90-day attended test at 10 Lagos parks. Buy a machine only if that test shows the fee and the traffic in the gates in section 13, and only if a written OEM quote lands inside a price the measured traffic can carry.</p>
</div>
<p>The later idea, a stall layer for restock and goods on credit, is not given a value here. It would need a licensed lender and a record of real stalls. It cannot rescue a cash machine that does not pay for itself.</p>

<h2>3. The concept</h2>
<p>CashEase would own fixed kiosks where people already handle cash: a market aisle, a motor park, a bus stop, a cluster of stalls. The customer puts in a large note and takes smaller notes, or takes cash against a card or account, or buys airtime and pays a bill. The company would own the box. A bank would be needed for cash, for settlement, and, if card cash-out is offered, for the licence path in section 8.</p>
<p>Note-breaking is the part a normal POS terminal does not do. Cash-out and bills are what POS agents already sell. The bundle only makes sense if the change service brings traffic the other services can charge for, and if the box can be bought and kept alive at a cost those fees can cover.</p>
<p>Three paths are easy to mix up. They are not the same business.</p>
{html_table(
    ["Path", "What the customer does", "Regulatory home", "Hardware the public prices describe"],
    [
        ["A. ATM", "Card or account cash-out, and a deposit only if the machine and the bank allow it", "Independent ATM deployer, with prior CBN approval and a bank that provides the cash", "Deposit-automated or recycling ATM"],
        ["B. Human agent", "Cash-out, cash-in, bills, at a staffed spot", "Agent of one principal. A machine cannot itself be the agent", "Ordinary POS terminal"],
        ["C. Note exchange", "Swaps notes for notes of the same total face value, and pays a fee", "Not settled by a published licence. Sits under the CBN’s currency powers", "A validator and dispenser. No public Nigerian price found"],
    ],
    "The three paths. Only Path B has a cheap, legal, crowded market today.",
)}

<h2>4. Problem and demand</h2>
<h3>4.1 Cash is still a large stock</h3>
<p>Currency in circulation was ₦5.73 trillion at the end of 2025, up from ₦5.44 trillion in 2024, according to reporting of the CBN’s 2025 annual report.<sup>32</sup> In June 2026 circulation was ₦5.523 trillion and currency outside banks was ₦4.92 trillion.<sup>33</sup> <span class="tag">Result</span> That is {cob_share:.1f}% of the June stock sitting outside banks. In August 2026 currency outside banks was ₦4.87 trillion, up from ₦4.80 trillion in July.<sup>34</sup> The CBN’s payments vision, as described in the same reports, aims to cut cash outside banks to below 40% of currency in circulation by 2028.<sup>33,34</sup> Policy is pointed at less cash in pockets, not more.</p>
<p>People still withdraw large sums. Reporting of the CBN quarterly statistical bulletin puts ATM withdrawals at ₦4.81 trillion in January 2025, ₦5.40 trillion in February and ₦5.76 trillion in March.<sup>13</sup> <span class="tag">Result</span> Those three months sum to ₦15.97 trillion, against ₦5.46 trillion in the first quarter of 2024. The first half of 2025 was ₦36.34 trillion and 858.80 million withdrawals, against ₦12.21 trillion and 496.47 million a year earlier.<sup>13,14</sup> A headline figure of ₦15.98 trillion for the first quarter is in circulation.<sup>15</sup> It is ₦0.01 trillion above the sum of the monthly lines those outlets attribute to the bulletin. This study uses ₦15.97 trillion.</p>
<p>The rise came after the CBN, on 10 February 2025, rewrote ATM fees. From 1 March 2025 a withdrawal at another bank’s on-site ATM costs ₦100 per ₦20,000. At an off-site ATM the charge is ₦100 plus a surcharge of not more than ₦500 per ₦20,000. The surcharge is income of the deployer and must be shown on the screen. The old allowance of three free monthly withdrawals at other banks’ ATMs was removed. Withdrawals at the customer’s own bank stay free.<sup>16,55</sup> Higher fees did not, on these figures, empty the ATMs.</p>

<h3>4.2 The ATM network is thin. The POS network is not</h3>
<p>The CBN’s payment-modes note says 16,714 ATMs were active in the first half of 2024, down 3.82% from 17,377 in the second half of 2023. ATM value in that half was ₦12.21 trillion.<sup>1</sup> The industry table gives the precise ATM line: volume 496,436,959 and value ₦12,206,733,099,741.90.<sup>2</sup> This study did not find a later official count of active ATMs.</p>
<p>IMF Financial Access Survey data, published through the World Bank, put ATMs per 100,000 adults in 2024 at 12.83 in Nigeria, 10.97 in Ghana, 6.42 in Kenya, 24.47 in India, 37.06 in Egypt and 45.96 in South Africa.<sup>3</sup> The St Louis Fed’s copy of the same IMF series gives Nigeria as 12.82854 and South Africa as 45.96149.<sup>4,5</sup> Nigeria is not an outlier against Ghana or Kenya. It is far behind Egypt and South Africa. Using the UN 2025 population of 237,527,782 and the mid-2024 ATM count gives one ATM per 14,211 residents.<sup>6,7,1</sup> <span class="tag">Result</span> That ratio mixes a 2025 population with a 2024 machine count. It is a scale check, not an official density.</p>
<figure>
  <img src="../charts/{charts['density']}" alt="Bar chart of ATMs per 100,000 adults in 2024">
  <figcaption>Figure 1. ATMs per 100,000 adults, 2024. Source: World Bank, indicator FB.ATM.TOTL.P5, drawn from the IMF Financial Access Survey.<sup>3</sup></figcaption>
</figure>
<p>POS is a different picture, and the published series do not measure the same thing. They must not be added together.</p>
{html_table(
    ["Series", "What it says", "Use it for"],
    [
        ["CBN industry table, January–June 2024", "POS volume 6,395,670,571 and value ₦85.91 trillion. ATM value ₦12.21 trillion in the same table.", "The broad CBN channel split. Result: the average POS ticket in this half is ₦13,433."],
        ["CBN payment-modes note, first half 2024", "2,935,765 POS terminals deployed, up 20% from 2,448,805.", "The CBN’s own terminal count. It is older and lower than the later NIBSS figure."],
        ["NIBSS, as reported for March 2025", "5.90 million deployed POS terminals, up 119.46% from 2.69 million a year earlier. Registered terminals 8.36 million.", "The 5.9 million figure in the brief. Confirmed as 5.90 million deployed, not registered."],
        ["NIBSS article and ThisDay, Q1 2025", "POS value ₦10.45 trillion, against ₦3.62 trillion a year earlier. All-channel electronic payments ₦284.99 trillion.", "A narrower NIBSS POS series. This is not the ₦85.91 trillion CBN series."],
        ["New Telegraph monthly sum, Q1 2025", "₦4.10 trillion, ₦3.17 trillion and ₦3.22 trillion, summing to ₦10.49 trillion.", "A second reading of NIBSS months. ₦10.51 trillion was not found."],
        ["New Telegraph, Q1 2026", "POS value ₦18.78 trillion, up 79.03% from ₦10.49 trillion in Q1 2025. Months: ₦6.08, ₦6.58 and ₦6.12 trillion.", "Shows the NIBSS-style series still growing into 2026."],
        ["TheCable on the CBN bulletin, H1 2025", "POS value ₦147.20 trillion, from ₦85.91 trillion in H1 2024. Volume 7.72 billion, from 6.4 billion.", "The broad CBN series, extended. Same family as the ₦85.91 trillion line."],
    ],
    "POS figures that are easy to mix up. Sources 1, 2, 8, 9, 10, 11, 12 and 14.",
)}
<p><span class="tag">Result</span> One deployed POS terminal per 40 residents, using 5.90 million terminals and the 2025 population. The CBN count of active ATMs is about 353 times smaller than that deployed POS stock (5,900,000 / 16,714). Cash-out at a stall is not an empty market.</p>

<h3>4.3 Small notes are scarce, and the issuer says demand is falling</h3>
<p>On 21 July 2026, after the 306th Monetary Policy Committee meeting, Governor Olayemi Cardoso said ₦5, ₦10, ₦20, ₦50 and ₦100 notes were still legal tender because the CBN had not said otherwise. He put the scarcity down to demand and supply: digitisation was reducing the need for coins and smaller notes, and a weaker naira had cut what those notes can buy. At that meeting the policy rate was held at 26.50%, and inflation was described as 15.91% in June.<sup>36,35</sup> Traders told Daily Trust they struggle to find ₦50 and ₦100 notes for change, and that many goods no longer have a price at those levels.<sup>37</sup> A separate report quotes economists who say banks rarely pay out the lower denominations, so the shortage is a distribution failure as well as a demand story.<sup>38</sup></p>
<p>Both accounts can be true, and both matter. Customers feel the pain. The institution that prints the notes has said, in public, that it expects still less need for them. A business whose product is a cassette of small notes is depending on a supply the issuer is not promising to expand. No CBN table found for this study splits currency in circulation by denomination. The share that is ₦200 and below is unknown. It is not assumed.</p>

<h3>4.4 Inclusion is wider than it was, and agents did much of the work</h3>
<p>EFInA’s 2023 access survey, the latest full demand-side release used here, reports formal financial inclusion of 64% in 2023, from 56% in 2020, with about 40 million adults still formally excluded. Overall inclusion, counting informal services, is shown at 74%. About one adult in four remained excluded. Use of financial-service agents rose from 4.4% of adults in 2018 to 54% in 2023.<sup>40</sup> The full report says 52% of adults, 58.3 million people, use a banking product, and 45.4 million use an informal mechanism.<sup>39</sup> Agents are already the channel that reached people ATMs did not. A new kiosk is not walking into a country without cash points. It is walking in beside those agents.</p>

<h2>5. Market size and the site screen</h2>
<p>A top-down “share of ATM withdrawals” would overstate the opportunity. Most of the ₦15.97 trillion in first-quarter ATM withdrawals is ordinary cash-out, which POS already contests, and it is not a measure of note-breaking. The useful question is how many sites can hold one secure, geo-fenced box that a cash van can reach.</p>
<h3>5.1 Method</h3>
<ol>
  <li>A qualifying site has a fixed structure, a real address, a daily cash crowd, road access for a cash van, a host who will lease, and a bank willing to service it. One machine per site. A second machine on the same pad splits the same queue.</li>
  <li>Count only places that appear in a published list. Do not turn “stalls” into a national total without a census. No national census of markets, bus stops or stall clusters was found.</li>
  <li>Do not multiply Lagos by 37. Lagos is not a typical state.</li>
  <li>Use the constitutional map only as a screen: one site per local authority is an upper planning grid, not a finding that the site exists.</li>
</ol>
<h3>5.2 What is actually counted</h3>
<p>In November 2024 the Lagos State Commissioner for Transportation said the state had 30 interstate parks on its books and well over 100 that were not regulated, and that at least 100 unregulated parks were to be upgraded.<sup>44,45</sup> A PPIAF-hosted assessment identified 145 bus parks across 39 Lagos areas and said the list might be incomplete. The file’s dates place that fieldwork well before 2024; it is a list, not a 2026 census.<sup>46</sup> A LAMATA project report posted in 2025 says Lagos bus parks had risen to more than 60, and it traces that remark to growth since a 2009 travel-demand model.<sup>47</sup> The higher current statement is the Commissioner’s: 30 registered plus more than 100 unregulated, so at least 130 park locations if “well over 100” is read as 100. <span class="tag">Assumption</span> This study treats 130 to 150 major Lagos park locations as the planning band for that reading. It is not a new count.</p>
<p>A 2025 presentation of a Lagos transit study cites a 2022 danfo census of 759 routes and 30,000 km, and observation work at 48 terminals and 79 bus stops.<sup>48</sup> The 79 stops are a sample, not the number of stops in the city.</p>
<p>Section 3(6) of the 1999 Constitution provides for 768 local government areas and six Federal Capital Territory area councils.<sup>27,28</sup> <span class="tag">Result</span> One qualifying site in each of those 774 authorities would be 774 machines. Twenty thousand machines would be 25.8 machines in every local authority, including places a cash van will not serve well.</p>
{html_table(
    ["Screen", "Sites", "Status"],
    [
        ["Lagos interstate parks on the state books, Nov 2024", "30", "Published"],
        ["Further unregulated Lagos parks, same statement", "More than 100", "Published as a floor, not a list"],
        ["Older identified Lagos bus parks (PPIAF file)", "145 in 39 areas", "Published list, earlier fieldwork"],
        ["LAMATA report’s bus-park figure", "More than 60", "Published, and the text points back to growth since 2009"],
        ["One site per LGA or area council", "774", "Screen only. Not a count of markets"],
        ["20,000 machines", "25.8 per local authority", "Not supported by any list found"],
    ],
    "Bottom-up screens. Only the first rows are counts.",
)}
<p><span class="tag">Result</span> Twenty thousand machines would be 1.20 times the 16,714 active ATMs of the first half of 2024, and 0.34% of the 5.90 million deployed POS terminals of March 2025. Against residents, 20,000 machines are 8.4 per 100,000 people. The ATM comparison is the right one, because the hardware and the licence look like an ATM, not like a POS terminal. A float of ₦2 million per machine at that scale is ₦40 billion. Set against ₦4.87 trillion outside banks in August 2026, that is {float_share:.1f}% of the cash stock.<sup>34</sup> The naira system is large enough to fill the cassettes. Whether the small-note slice is large enough is not in any table found here.</p>
<p>The addressable market this evidence supports is a few hundred carefully chosen fixed sites in places with published footfall and a cash-van route, starting inside the Lagos park band. It is not 20,000.</p>

<h2>6. Competition</h2>
<h3>6.1 POS agents, and the three large networks</h3>
<p>Moniepoint’s own guide prices a terminal at ₦21,500, plus a ₦10,000 caution fee, ₦10,000 for logistics and ₦1,500 of insurance for a year. <span class="tag">Result</span> That is ₦43,000 before the float the agent must hold. Withdrawals are charged at 0.5% between ₦1 and ₦20,000, and ₦100 above ₦20,000. Transfers are ₦20. Airtime is charged at 2% across networks. The same page sets a floor of ₦80,000 of transactions a day and says an underused terminal can be taken back.<sup>41</sup> <span class="tag">Result</span> At the ₦12,000 average cash-out used as an assumption in section 10, that floor is about seven cash-outs. It is a value floor, not evidence of 80 transactions a day.</p>
<p>Secondary write-ups describe a busy market or park agent doing 80 to 100 transactions a day.<sup>65</sup> Those are anecdotes, not a NIBSS average. They are used below only as a test case, and they are labelled as such.</p>
<p>Press accounts name Moniepoint, OPay and PalmPay as the large agent networks and quote agent or terminal counts in the hundreds of thousands or, in later 2025 pieces, above one million for Moniepoint and OPay. The figures conflict, PalmPay’s 500,000 is sometimes dated to 2023, and none of them is an audited estate in this study. They are not used as market shares. What is used is the NIBSS deployed-terminal count, and the fact that a new cash-out brand would be competing with those networks plus the banks’ own agents.<sup>8</sup></p>
<h3>6.2 Bank ATMs, recyclers, NCR, and Nibox</h3>
<p>Banks are being pushed to deploy more of their own machines. Guidelines announced in a circular of 13 March 2026 require card issuers to reach one ATM per 7,500 payment cards by 2028, with 30% of that requirement in 2026 and 60% in 2027. An independent ATM deployer needs prior written CBN approval, evidence of operational capacity, and a bank that provides the cash. Stand-alone closed networks are not allowed. Machines must take Nigerian cards.<sup>16,53,54</sup> That programme is a competitor. It is also the rulebook Path A would have to join.</p>
<p>NCR Nigeria sells ATMs, cash recyclers, financial kiosks and related software, and it runs warehouses in Lagos, Abuja and Port Harcourt plus regional stocking points.<sup>51,52</sup> It is the obvious local service and supply firm. It is not a partner until it gives a quote. Nothing in its public product page is a unit price.</p>
<p>Nibox, in Abuja, deploys self-service kiosks for cash-in, cash-out, transfers, bills and onboarding, and it describes itself as the leading firm of that kind. Its public profile says the first kiosk went in during 2019 and that the service has reached more than 180,000 people.<sup>49,50</sup> Those are company statements, not an audited machine count. No public source found here shows Nibox, or anyone else, running a national estate of thousands of cash-recycling kiosks. The closest analogue has not published the scale this brief asks about.</p>
<p>The competitive substitute for cash-out is a ₦43,000 terminal and a person. The competitive substitute for note-breaking is a trader who gives change, or refuses the sale, or rounds the price. Neither substitute costs {naira(ref['all_in_ngn'])}.</p>

<h2>7. Regulation and the legal position of note-breaking</h2>
<p>This section is a reading of public instruments for a business decision. It is not a legal opinion. Nigerian counsel has to confirm it against the signed PDFs before any site opens.</p>
<h3>7.1 Agent banking, from 6 October 2025</h3>
<p>The CBN issued guidelines for agent banking on 6 October 2025, under the CBN Act 2007 and the Banks and Other Financial Institutions Act 2020. They took effect on release, except the rules on agent location and exclusivity, which took effect on 1 April 2026.<sup>16,19,20</sup> Both of those dates are past.</p>
<p>The limits, as quoted by counsel from the guidelines, are: cash-in of ₦100,000 a day and ₦500,000 a week per customer; cash-out of ₦100,000 a day and ₦500,000 a week per customer; bill payments of ₦100,000 a day and a week; and a daily cumulative cash-out per agent of ₦1,200,000. The CBN can change the limits. Devices must be geo-fenced to the registered premises. An agent location is at least a kiosk at an identifiable place. Roaming is out. An agent may serve only one principal. Terminals connect through a payment-terminal service aggregator. Transactions go through a dedicated account or wallet of the principal.<sup>18,20,21</sup></p>
<p>The same guidelines list, at paragraph 3.2, activities that are not allowed. Law firms quote the list as including the use of non-human or automated machines as agents.<sup>20,21,22</sup> Mondaq points to the CBN PDF.<sup>23,24</sup> That URL returned an access error when it was requested for this study on 7 October 2026, so the quote is from the law-firm texts, not from a file opened here. The practical consequence is still clear enough to plan around: a self-service kiosk should not be filed as an agent. Putting a person next to an expensive box and calling the person the agent drops the business into Path B, under the ₦1.2 million daily cash-out cap, in competition with a ₦43,000 terminal.</p>
<h3>7.2 Geo-fencing</h3>
<p>A separate geo-fence rule for POS terminals, tied to an August 2025 circular on ISO 20022 and geotagging, was adjusted after industry consultation. The CBN’s reforms page says the allowed radius moved from 10 metres to 70 metres and the enforcement date moved to 1 August 2026.<sup>16</sup> Nairametrics quotes the later circular: radius increased from 10 metres to 70 metres, enforcement extended to 1 August 2026.<sup>17</sup> That date has passed. This study found no official compliance scorecard after the deadline. A fixed kiosk fits a geo-fence better than a roaming agent does. That is an operational advantage only if the kiosk is otherwise lawful.</p>
<h3>7.3 ATMs and the Guide to Charges</h3>
<p>Path A is the independent ATM deployer route in the 13 March 2026 guidelines: written approval first, a bank for cash, monthly returns, interoperability.<sup>16,54</sup> The fee the deployer can keep on another bank’s customer at an off-site machine is the disclosed surcharge, capped at ₦500 per ₦20,000.<sup>16,55</sup> The ₦100 is not modelled as CashEase income. On-us withdrawals bring the deployer nothing under that circular. A network that attracts a bank’s own customers to a co-branded machine can be busy and still earn no surcharge on those visits.</p>
<h3>7.4 Note-breaking</h3>
<p>Section 17 of the CBN Act 2007 gives the Bank the sole right to issue currency notes and coins. Section 18 requires the Bank to arrange printing and minting, and to issue, re-issue and exchange notes and coins at its offices and at agencies it establishes or appoints. Section 20 makes the Bank’s notes legal tender at face value for any amount.<sup>25,26</sup></p>
<p>Swapping one legal-tender note for others of the same total face value is not the act of issuing currency. It is also not a licence the Act hands out in general terms. The exchange function in section 18 sits with the Bank and with agencies the Bank appoints. This research did not find a circular that says a private company may charge the public for that swap, and it did not find one that bans the swap by name. That absence is not a permission. Large, repeated cash exchange will also raise anti-money-laundering questions. Counsel should map the activity to the Money Laundering (Prevention and Prohibition) Act and to the CBN’s AML rules before a till opens. No filing duty is asserted here, because that mapping was not done.</p>
<p>Until a written opinion says Path C is open, the prudent plan is to treat note exchange as a bank cash service on the bank’s float, done only if the bank will put its name on it. If the bank will not, Path C does not scale, whatever the footfall.</p>

<h2>8. Operations</h2>
<h3>8.1 Hardware and foreign exchange</h3>
<p>The machine has to accept mixed notes, reject counterfeits, and pay out more than one denomination. A POS terminal does not do that. Public US deployer prices are the cost evidence used here.<sup>42,43</sup></p>
<ul>
  <li>Dispense-only ATM: about $25,000 to $34,000.</li>
  <li>Deposit-automated ATM: about $40,000 to $55,000.</li>
  <li>Teller cash recycler: roughly $20,000 to the low $40,000s, with a median around $36,000. Annual maintenance of about 10% of the machine price is described as a fair US all-in service figure. Freight and installation are extra in that account.</li>
</ul>
<p>The reference case takes $40,000, the bottom of the deposit-automated range, because note-breaking needs acceptance as well as dispensing. The official NFEM closing rate on 5 October 2026 was ₦1,331.69 per dollar.<sup>31</sup></p>
{html_table(
    ["Published anchor", "US price used", "Ex-works at ₦1,331.69", "Freight at 8% (assumption)", "All-in, with ₦8 million local adders"],
    hw_rows,
    "Landed cost before import duty, levies and port charges. The ₦8 million adder is ₦6 million install, enclosure and solar plus ₦2 million software and certification. Both adders are assumptions.",
)}
<p>Hyosung’s public retail-recycler pages describe fitness sorting and note serial-number capture.<sup>66</sup> Those features are relevant to counterfeit risk. They are not a vendor selection.</p>
<p>No published price was found for a simpler Nigerian or Asian note-breaker. A quote below the reference case would change section 10. It is a gate, not an input. Duty is omitted on purpose. A customs ruling would add cost.</p>
<h3>8.2 Power</h3>
<p>Dangote’s diesel gantry price was cut to ₦1,700 a litre with effect from 7 October 2026.<sup>56,57</sup> A retail quote compiled for 6 October 2026 puts diesel at ₦1,810 a litre.<sup>58</sup> The model uses the retail figure. <span class="tag">Assumption</span> The box uses 8 kWh on each of 300 scheduled open days. Forty percent of that energy comes from a generator at 0.35 litres per kWh. The rest is solar, whose capital cost sits in the ₦6 million install line, with ₦80,000 a year of upkeep. <span class="tag">Result</span> That is 336 litres and {naira(u['power_ngn'])} a year for power. Site-by-site grid hours were not collected. A dark site burns more diesel than this.</p>
<h3>8.3 Cash logistics, float, maintenance, security</h3>
<p><span class="tag">Assumption</span> Opening float is ₦2 million of mixed notes per machine. Four cash-van visits a month at ₦40,000 a visit. No Nigerian tariff for that visit was found; the sensitivity table replaces ₦40,000 with ₦15,000 and ₦80,000. Maintenance is 10% of ex-works value a year, carried over from the US recycler comment, not from a Nigerian service contract. Insurance is 1.5% a year of all-in hardware plus float. Rent is ₦150,000 a month for a secured pad. A shared security allocation is ₦120,000 a month, against a national minimum wage of ₦70,000.<sup>59</sup> A guard who never leaves the machine costs more than ₦120,000. An unattended box saves the wage and raises theft. The pilot recommendation in section 11 is attended, because there is no loss history.</p>
<p>Shrinkage is modelled at 0.3% of cash-out value. That percentage is an assumption. Industry fraud losses are a different statistic: NIBSS reported ₦52.26 billion lost to fraud in 2024, of which about ₦31.1 billion was a single incident, and ₦25.85 billion in 2025. Lagos accounted for 63.43% of 2025 fraud activity in that briefing. POS is among the channels affected, behind e-commerce and internet banking.<sup>63,64</sup> Those totals are not a per-kiosk loss rate and are not used as one.</p>
<p>Small-note supply is the operational constraint that does not have a price. If the partner bank will not schedule ₦100, ₦200 and ₦500 notes, the change product stops on the first busy morning, whatever the NPV says.</p>

<h2>9. Unit economics</h2>
<p>There is no measured fee for breaking a note, and no measured number of breaks per site. The base case is a set of choices, then a break-even. It is not a prediction that the choices will happen.</p>
{html_table(
    ["Choice", "Base value", "Why this value and not another"],
    [
        ["Note-break share / fee", "55% of transactions at ₦100", "Assumption. No regulated tariff for a note swap was found."],
        ["Cash-out share / deployer surcharge", "35% at ₦250", "Assumption. Inside the ₦500 per ₦20,000 off-site cap. The ₦100 network charge is not treated as CashEase income."],
        ["Airtime and bills", "10% at ₦30 net", "Assumption. Kept small because an unmanned box may not be allowed to sell them as an agent."],
        ["Bank share", "25% of the surcharge, none of the note fee", "Assumption. There is no term sheet."],
        ["Average cash-out", "₦12,000", "Assumption, used only for shrinkage."],
        ["Shrinkage", "0.3% of cash-out value", "Assumption."],
        ["Scheduled days and uptime", "300 days, 90% uptime", "Assumption. Effective days = 270."],
        ["Life and salvage", "7 years, zero salvage", "Assumption."],
        ["Discount rate", "28%", "23% MPR from the 307th MPC, plus 5 percentage points. The add-on is a planning premium, not a measured cost of equity."],
    ],
    "Base commercial assumptions. Replace any row with a quote or a measured result and rerun the model.",
)}
<p><span class="tag">Result</span> Gross fee per transaction is ₦145.50. Bank share is ₦21.88. Shrinkage is ₦12.60. Net contribution is ₦111.03. Street costs (rent, power, link, cash van, security) are {naira(f['street_ngn'])} a year. Cash costs, adding maintenance and insurance, are {naira(f['cash_fixed_ngn'])}. Full cost, adding depreciation of {naira(f['depreciation_ngn'])} and float at the 23% policy rate ({naira(f['float_cost_ngn'])}), is {naira(f['full_fixed_ngn'])}.</p>
{html_table(
    ["Test", "Transactions per scheduled open day"],
    [
        ["Cover street costs only", tx(be["street_tx_per_open_day"])],
        ["Cover all cash costs, including maintenance and insurance", tx(be["cash_tx_per_open_day"])],
        ["Cover full cost, including depreciation and the cost of float", tx(be["full_tx_per_open_day"])],
        ["Drive one-kiosk NPV to zero at 28%", tx(hurdle["base_fee"])],
        ["Same NPV test if the note fee is ₦200 and the surcharge is the ₦500 cap", tx(hurdle["max_disclosed_surcharge"])],
        ["Anecdotal busy POS agent, for comparison", "80 to 100"],
    ],
    "Break-even on the reference machine. The 80 to 100 line is a blog anecdote, not a NIBSS mean.",
)}
<figure>
  <img src="../charts/{charts['breakeven']}" alt="Bar chart comparing break-even volumes with an 80-transaction benchmark">
  <figcaption>Figure 2. Transactions per scheduled open day. The first bar is the anecdote. The others are results from the reference machine.</figcaption>
</figure>
<p>The 80-transaction day is the test case below. It is not the forecast. At 80 transactions on a scheduled open day, times 270 effective days, a kiosk does 21,600 transactions a year.</p>
{html_table(
    ["Line, one reference kiosk, 80 transactions per open day", "Naira per year"],
    unit_rows,
    "Unit profit and loss. Negative lines are costs. Cash profit is before depreciation and the cost of float.",
)}
<figure>
  <img src="../charts/{charts['unit']}" alt="Bar chart of annual revenue and major costs per kiosk">
  <figcaption>Figure 3. Net revenue against the main annual costs at the 80-transaction test case. Depreciation alone is larger than net revenue.</figcaption>
</figure>
<p>Two readings follow, and they do not depend on believing the ₦40,000 machine price.</p>
<ul>
  <li>Even if maintenance, insurance, depreciation and the cost of float were all zero, street costs of {naira(f['street_ngn'])} still need about {tx(be['street_tx_per_open_day'])} transactions a day at a ₦111 net contribution. The anecdote of 80 does not pay the rent and the cash van.</li>
  <li>At the regulatory maximum surcharge of ₦500 and a ₦200 note fee, full-cost break-even on this machine is still {tx(hurdle['max_disclosed_surcharge'])} transactions a day before the 28% test is even applied. Charging the cap does not create a normal kiosk business.</li>
</ul>
<p>Interest makes the funding point in one line. <span class="tag">Result</span> Interest at the 23% policy rate on 70% of the reference all-in cost is {naira(r['interest_only_70pct_at_mpr'])} a year per machine. Net revenue at 80 transactions a day is {naira(u['net_revenue_ngn'])}. The policy rate is not a bank’s lending rate. A commercial rate would be higher. The machine cannot service debt.</p>
{html_table(
    ["Transactions per open day", "Net revenue", "Cash profit", "Operating result", "NPV at 28%", "IRR"],
    vol_rows,
    "One reference kiosk, no head office. IRR is undefined when every cash flow, including the return of float, is negative.",
)}
<p>At 400 transactions a day the project still has a negative NPV at 28% (IRR {pct(r['volume_grid'][4]['irr'])}). At 750 transactions a day, which would be a transaction every minute or so across a long day, operating profit is only just positive and the IRR is {pct(r['volume_grid'][5]['irr'])}, against a 28% hurdle. The NPV of that case is still {naira(r['volume_grid'][5]['npv_28'])}.</p>
<p>The model also asks the reverse question: what all-in price would a machine need to have for the NPV at 28% to be zero? At 80, 120 and 200 transactions a day there is no such price inside the range tested. The install and solar block alone, plus street costs, already overwhelms the fees. At 400 transactions a day the ceiling is {naira(r['capex_ceiling_ngn']['400'])}. Every published anchor in the table above lands above that ceiling, and the ceiling itself requires traffic this study has no evidence for.</p>
<figure>
  <img src="../charts/{charts['hardware']}" alt="Bar chart of all-in machine cost against the NPV price ceiling">
  <figcaption>Figure 4. All-in cost per machine before duty. The dashed line is the price at which NPV at 28% would be zero if the site did 400 transactions a day. At 80, 120 or 200 transactions a day that line does not exist.</figcaption>
</figure>
{html_table(
    ["Cash-van price per visit", "Note fee", "Surcharge", "Net per transaction", "Street break-even", "Cash break-even", "Full-cost break-even"],
    sens_rows,
    "Sensitivity. Transactions per scheduled open day. The ₦500 surcharge is the off-site cap, not a recommended price.",
)}
<p>The most favourable cell in the full grid (₦15,000 a visit, ₦200 note fee, ₦500 surcharge) still needs 336 transactions a day to cover full cost. Cutting the cash-van assumption does not reverse the result.</p>

<h2>10. Three rollout cases</h2>
<p>The brief asks for a pilot, about 2,000 machines, and about 20,000. All three are shown on the reference hardware at the 80-transaction test case. They are not recommended builds. Head-office cost is an assumption: ₦120 million to start and ₦60 million a year for the pilot; ₦400 million a year at 2,000; ₦1.2 billion a year at 20,000. Tax is not applied. A loss-making project does not become viable by adding a tax rate, and the rate that would apply to a new company was not re-derived for this study.</p>
{html_table(
    ["Case", "Kiosks", "Hardware", "Float", "Year-0 cash", "Cash profit", "Operating result", "NPV at 28%"],
    [
        scen_row("pilot", "Pilot"),
        scen_row("two_k", "2,000"),
        scen_row("twenty_k", "20,000"),
    ],
    "Seven-year hold, flat volume, reference machine, 80 transactions per open day. Year-0 cash includes hardware, float and set-up. Profit is annual and pre-tax. IRR is not defined in any of the three cases: every cash flow is a loss, including the year the float is returned.",
    tight=True,
)}
<p>NPV at the 23% policy rate and at 35% was also computed. It stays negative in every case, because the annual cash flow is negative. A lower discount rate does not rescue a project that never returns cash. IRR is not defined: there is no discount rate at which the present value is zero when every cash flow is a loss. Returning the float in year 7 does not create a positive cash flow. The year’s operating loss is larger than the float.</p>
<h3>10.1 Pilot cash flow, 25 reference machines</h3>
<p>Twenty-five machines fit inside the Lagos park band of at least 130 locations. That is the only reason 25 is used. It is still the wrong first purchase, as the cash flow shows.</p>
{html_table(
    ["Year", "Cash flow", "What it is"],
    cf_rows,
    "Pilot estate at the 80-transaction test case. Year 0 is the investment. Years 1 to 7 are cash profit after head office. Year 7 also returns the float.",
)}
<h3>10.2 What 2,000 and 20,000 would tie up</h3>
<p><span class="tag">Result</span> Two thousand reference machines are {naira(r['scenarios']['two_k']['pnl']['capex_ngn'])} of hardware and {naira(r['scenarios']['two_k']['pnl']['float_ngn'])} of float. Twenty thousand are {naira(r['scenarios']['twenty_k']['pnl']['capex_ngn'])} of hardware and {naira(r['scenarios']['twenty_k']['pnl']['float_ngn'])} of float. At the test-case volume the 20,000-machine estate shows an operating loss of about {naira(abs(r['scenarios']['twenty_k']['pnl']['operating_profit_ngn']))} a year. That number is a reason not to build. It is not a forecast that anyone will build it.</p>
<p>Nothing in the site screen of section 5 produces a file of 2,000 qualified pads, still less 20,000. The financial result and the site result fail separately. Either one is enough to stop.</p>
<h3>10.3 The spend that is justified</h3>
<p>Measure the change fee with people and a cash box, not with a {naira(ref['all_in_ngn'])} machine. <span class="tag">Assumption</span> Ten Lagos park sites, 90 days, one attendant at ₦180,000 a month, pad rent of ₦80,000 a month, ₦8,000 a day for transport and banking the cash, ₦500,000 float per site, and ₦5 million of set-up for signage, count kits, insurance and counsel.</p>
<p><span class="tag">Result</span> Cash tied up is {naira(test['cash_outlay_ngn'])}, of which {naira(test['sites'] * test['float_per_site_ngn'])} is float that should come back. The amount spent is about {naira(test['spend_ex_float_ngn'])}. A site that pays a ₦100 fee needs roughly 170 paid swaps a day to cover that site’s own attendant, rent and transport. The gate in section 13 is set at 200, in line with the machine’s street-cost break-even, so a pass means the fee might carry a later box and not merely the test itself.</p>

<h2>11. Funding</h2>
<p>The pilot estate in section 10 cannot pay interest. Funding it with debt would add a default. The attended test is an equity cheque from the sponsor, capped at the figure above, and written off if the gates fail.</p>
<p>Bank of Industry lending to small firms is described by the Bank as below market, with tenors of three to five years and a moratorium of 3 to 12 months, through project loans, cluster schemes, on-lending and intervention funds.<sup>60</sup> Its public portal advertises specific products, including a women-led facility of up to ₦50 million at 7%.<sup>61</sup> Those products are the wrong size and, unless the borrower qualifies, the wrong door. They are not a plan for a billion-naira machine order. No BOI term sheet is assumed.</p>
<p>Development Bank of Nigeria lends through participating financial institutions, not as a direct cheque to an operating company in the ordinary course. It reports ₦1.4 trillion disbursed as of December 2025.<sup>62</sup> Any end rate would be the partner bank’s rate. A content-site range of 9% to 13% is not used, because it is not DBN’s own price.</p>
<p>A commercial bank matters for a different reason. The March 2026 ATM guidelines require a cash-provisioning bank before an independent deployer can operate.<sup>54</sup> The same bank is the only realistic source of scheduled small notes. That partnership is a condition of operating, not a substitute for equity, and it is not evidence that a bank wants the exposure. The bank should be shown the unit loss in section 9 before it is asked for a term sheet. If the bank will only provide float once the unit makes cash profit, the project cannot start on bank float, because the unit does not make cash profit at evidenced volumes.</p>

<h2>12. Risks and what to do about them</h2>
{html_table(
    ["Risk", "Why it is real", "Mitigation"],
    [
        ["Small-note supply", "The CBN governor has tied scarcity to falling demand. No denomination split of the cash stock was found.", "Written bank schedule of ₦100, ₦200 and ₦500 notes before any machine order. If the bank refuses, stop."],
        ["Unlawful structure", "Automated machines are quoted as forbidden agents. Note exchange has no published private licence.", "Counsel’s written opinion on Path A and Path C against the signed guidelines and the CBN Act. No sites until that opinion is in hand."],
        ["Fee resistance", "No measured willingness to pay ₦100 to break a note. Traders sometimes give change for nothing.", "The 90-day test records refusals. If most people who need change refuse the posted fee, the fee assumption is dead."],
        ["Traffic below break-even", "Street break-even is about 202 transactions a day. The public anecdote is 80 to 100.", "Pre-register the 200-transaction gate. Do not buy machines on a narrative that the next site will be busier."],
        ["Hardware cost", "Published anchors land between about ₦44 million and ₦87 million all-in before duty.", "No order without a written quote. The quote has to sit under a ceiling calculated from the measured fee and volume, not from the 400-transaction hypothetical."],
        ["FX", "The box is imported. The rate used is ₦1,331.69. A weaker naira raises the naira price one for one on the ex-works portion.", "Price the quote in naira, delivered, or hold dollars for the deposit. Do not model a return to an old rate."],
        ["Power", "The diesel case is 336 litres a year. A site with no sun and no grid burns more.", "Solar in the install, and a generator sized in the quote. Drop sites where diesel would dominate."],
        ["Robbery and insider theft", "A cassette is a target. Fraud losses in the industry were ₦25.85 billion in 2025.", "Attended operation until loss data exist. Low cassette ceilings. Dual control on float. Insurance that actually names cash in transit. No unattended box in the test."],
        ["Counterfeit notes", "The machine pays out good notes against bad ones if the validator fails.", "Validator with fitness and serial capture in any later specification. In the test, a counting machine and a rule that suspect notes are refused."],
        ["Bank or regulator changes the cap", "The agent cap is ₦1.2 million. The surcharge cap is ₦500 per ₦20,000. Either can be revised.", "Do not underwrite a 2,000-unit order on today’s cap. Re-run the model if the circular changes."],
        ["Policy wants less cash", "The payments vision cited in 2026 reporting targets cash outside banks below 40% of circulation by 2028.", "Treat cash volume as a shrinking policy target. Do not use a cash-growth story in a funding memo."],
        ["Geo-fence and exclusivity already in force", "Location and exclusivity from 1 April 2026. POS geo-fence enforcement from 1 August 2026. Radius 70 metres.", "Only fixed, addressed sites. One principal. No roaming park-to-park model."],
    ],
    "Risks that change the decision, and the action attached to each.",
)}

<h2>13. Go and no-go gates</h2>
<p>Each gate is binary. A miss stops the next spend. Later gates are not opened early.</p>
<ol>
  <li><strong>Counsel, before the test.</strong> A written opinion that the attended note-exchange test is lawful, and a statement of which of Path A or Path C could later hold a machine. If the opinion says the test itself is unlawful, stop. Budget spent: professional fees only.</li>
  <li><strong>Bank, before the test scales.</strong> At least one bank says, in writing, whether it will sell or deliver small notes to the test sites. If every bank refuses, the test can still run for a few days on notes bought over the counter, but it cannot be a path to a network. Record the refusal and stop.</li>
  <li><strong>Attended test, 10 sites, 90 days, spend capped near {naira(test['spend_ex_float_ngn'])} plus float.</strong> Pass only if, over the last 30 days, the better half of sites (the median of the top five) does at least 200 paid note-breaks per day at a fee of at least ₦100, and fewer than half of approached customers who needed change refuse that fee. Fail means no machines.</li>
  <li><strong>Quote.</strong> An OEM or NCR (or another named supplier) quote, in naira, delivered and installed, including validator, dispenser, enclosure, solar and first-year service. Pass only if that all-in price is at or below the NPV ceiling computed from the measured fee and the measured transactions, at a 28% discount rate, over seven years. The ₦13.6 million ceiling in section 9 does not transfer to a weaker test result.</li>
  <li><strong>Twenty-five machines, and only twenty-five.</strong> All of gates 1 to 4 passed. Sites are inside the published Lagos park band, one machine each, leases signed, insurance bound, cash-van contract signed, cassette limit set. Fresh 90-day read. Pass only if cash profit per machine, after rent, power, cash van, security, maintenance and shrinkage, is positive. Depreciation and the cost of float are reported beside it, not hidden.</li>
  <li><strong>Two thousand.</strong> Gate 5 passed on the original cohort, not on a replacement set of busier sites. A site file of 2,000 qualifying pads exists, with addresses. A bank has a small-note schedule that covers the fleet. The cohort’s unlevered IRR is at least 28%. If it is not, stop. Do not average in a hopeful new city.</li>
  <li><strong>Twenty thousand.</strong> Gate 6 has been true for a full year, the CBN has not cut the surcharge or the relevant cash limits in a way that pushes the cohort below the hurdle, and the sponsor can fund the hardware without betting the company on a single debt drawdown. This gate is not a target. It is a lock.</li>
</ol>
<p>As of 7 October 2026, gates 1 to 7 are unmet. The decision is no-go beyond the work in gates 1 and 2, and no-go on hardware.</p>

<h2>14. Appendix: formulas</h2>
<p>Effective days = 300 × 0.90 = 270.</p>
<p>Gross per transaction = 0.55 × 100 + 0.35 × 250 + 0.10 × 30 = 145.50.</p>
<p>Bank share = 0.35 × 250 × 0.25 = 21.875. Note-fee share to the bank = 0 in the base case.</p>
<p>Shrinkage per transaction = 0.35 × 12,000 × 0.003 = 12.60.</p>
<p>Net contribution = 145.50 − 21.875 − 12.60 = 111.025.</p>
<p>Ex-works naira = 40,000 × 1,331.69 = {comma(ref['exworks_ngn'])}.</p>
<p>All-in = ex-works × 1.08 + 6,000,000 + 2,000,000 = {comma(ref['all_in_ngn'])}.</p>
<p>Depreciation = all-in / 7. Maintenance = 0.10 × ex-works. Insurance = 0.015 × (all-in + 2,000,000). Float cost = 2,000,000 × 0.23.</p>
<p>Diesel litres = 8 × 300 × 0.40 × 0.35 = 336. Power naira = 336 × 1,810 + 80,000.</p>
<p>Cash-in-transit = 40,000 × 4 × 12. Rent = 150,000 × 12. Security = 120,000 × 12. Connectivity = 18,000 × 12.</p>
<p>Break-even transactions per open day = (annual cost to cover / 111.025) / 270.</p>
<p>NPV uses year-0 investment of all-in plus float, seven years of cash profit, and return of float at the end, with no salvage. The estate cases subtract head-office cash as well. The rate is 28% unless a sensitivity says otherwise. The project is nominal and flat: fees and volumes do not grow, and costs do not inflate. Inflation was 15.39% in August 2026, with food inflation 19.57% and core inflation 13.29%.<sup>30</sup> If costs rose with that headline rate and fees did not, the losses would be wider. That case is not needed to reach a no-go.</p>
<p>The policy rate used as the floor of the discount rate is 23.00%, set at the 307th Monetary Policy Committee meeting on 21–22 September 2026, down from 26.50%. The standing-facilities corridor was set at +50 and −300 basis points. Cash reserve ratios were left unchanged, including 45% for deposit money banks.<sup>29,30</sup></p>
<p>Recompute from <span class="small">model/financial_model.py</span>. The tables in this PDF were written by that script so the prose and the file cannot drift.</p>

<h2>15. Sources</h2>
<p>Every external fact in the text points here. Pages were read in the first week of October 2026. Where a CBN file could not be opened, the failure is stated in the section that uses it.</p>
<ol class="sources">
  <li>Central Bank of Nigeria, “Payment Modes”, active ATMs and channel commentary for the first half of 2024. https://www.cbn.gov.ng/PaymentsSystem/modes.html</li>
  <li>Central Bank of Nigeria, e-payment statistics by channel, including the precise ATM and POS lines for January–June 2024. https://www.cbn.gov.ng/PaymentsSystem/ePaymentStatistics.html</li>
  <li>World Bank, “Automated teller machines (ATMs) (per 100,000 adults)”, indicator FB.ATM.TOTL.P5, 2024 values for Nigeria, Ghana, Kenya, India, Egypt and South Africa. https://data.worldbank.org/indicator/FB.ATM.TOTL.P5</li>
  <li>Federal Reserve Bank of St Louis, FRED series NGAFCAANUM, IMF Financial Access Survey, Nigeria, 2024 observation 12.82854. https://fred.stlouisfed.org/series/NGAFCAANUM</li>
  <li>Federal Reserve Bank of St Louis, FRED series ZAFFCAANUM, South Africa, 2024 observation 45.96149. https://fred.stlouisfed.org/series/ZAFFCAANUM</li>
  <li>World Bank, “Population, total — Nigeria”, 2025 value 237,527,782, from UN World Population Prospects. https://data.worldbank.org/indicator/SP.POP.TOTL?locations=NG</li>
  <li>WorldPop, Nigeria population release notes, version 3.0, 29 August 2025, confirming the July 2025 UN median of 237,527,782. https://data.worldpop.org/repo/wopr/NGA/population/v3.0/NGA_population_v3_0_README.pdf</li>
  <li>New Telegraph, “NIBSS: More Nigerians Embrace PoS As Deployed Terminals Up 119.4% To 5.90m”, deployed and registered terminals through March 2025. https://newtelegraphng.com/nibss-more-nigerians-embrace-pos-as-deployed-terminals-up-119-4-to-5-90m/</li>
  <li>NIBSS, “How NIBSS Innovation Drives Services in GDP Expansion”, POS value of ₦10.45 trillion in the first quarter of 2025. https://nibss-plc.com.ng/how-nibss-innovation-drives-services-in-gdp-expansion/</li>
  <li>ThisDay, “E-Payment Transactions Rise 17.7% to N284.99 Trillion in Q1 2025”, 29 July 2025. https://www.thisdaylive.com/2025/07/29/e-payment-transactions-rise-17-7-to-n284-99-trillion-in-q1-2025/</li>
  <li>New Telegraph, “Cashless: PoS Sustains Growth As Transactions Up 300.8% To N10.49trn”, monthly POS values for the first quarter of 2025. https://newtelegraphng.com/cashless-pos-sustains-growth-as-transactions-up-300-8-to-n10-49trn/</li>
  <li>New Telegraph, “Value Of PoS Transactions Surged 79.03% To N18.78trn In Q1’26”. https://newtelegraphng.com/value-of-pos-transactions-surged-79-03-to-n18-78trn-in-q126/</li>
  <li>Nairametrics, “ATM transactions surge to N36.34 trillion in six months despite fresh fees”, 19 January 2026, including the monthly lines for the first quarter of 2025. https://nairametrics.com/2026/01/19/atm-transactions-surge-to-n36-34trn-in-six-months-despite-fresh-fees/</li>
  <li>TheCable, “ATM withdrawals hit N36trn in H1 2025 — up by 196%”, 19 January 2026, including the first-half POS comparison of ₦147.20 trillion with ₦85.91 trillion. https://www.thecable.ng/atm-withdrawals-hit-n36trn-in-h1-2025-up-by-196/</li>
  <li>Valuechain, headline treatment of first-quarter 2025 ATM withdrawals as ₦15.98 trillion. https://www.thevaluechainng.com/%e2%82%a615-98tn-withdrawn-as-cbn-nudges-nigeria-back-to-atms/</li>
  <li>Central Bank of Nigeria, “Reforms and Initiatives”, including the 10 February 2025 ATM fee review, the 6 October 2025 agent-banking guidelines, the POS geo-fence extension to 1 August 2026, and the 13 March 2026 ATM guidelines. https://www.cbn.gov.ng/AboutCBN/Reforms.html</li>
  <li>Nairametrics, “CBN extends PoS geo-fencing enforcement to August 1”, 29 May 2026, quoting the radius change from 10 metres to 70 metres. https://nairametrics.com/2026/05/29/cbn-extends-pos-geo-fencing-enforcement-to-august-1/</li>
  <li>Punch, “CBN caps POS agent daily transactions at N1.2m in new guidelines”, 6 October 2025. https://punchng.com/cbn-caps-pos-agent-daily-transactions-at-n1-2m-in-new-guidelines/</li>
  <li>TheCable, “CBN issues guidelines for agent banking, sets daily transaction limit at N1.2m”, 6 October 2025. https://www.thecable.ng/cbn-issues-guidelines-for-agent-banking-sets-daily-transaction-limit-at-n1-2m/</li>
  <li>G. Elias, “The Central Bank of Nigeria’s Guidelines on the Operations of Agent Banking, 2025”, including transaction limits, the kiosk location rule, exclusivity, and the citation of paragraph 3.2(iv) on non-human machines. https://www.gelias.com/images/Central_Bank_of_Nigeria_Guidelines_on_the_Operations_of_Agent_Banking.pdf</li>
  <li>Manifield Solicitors, note quoting paragraph 3.2, “use of non-human/automated machines as Agents”. https://manifieldsolicitors.com/central-bank-of-nigeria-cbn-issues-new-daily-cash-withdrawal-limits-and-updated-agent-banking-guidelines/</li>
  <li>TNP, “The CBN Agent Banking Guidelines 2025: Key Innovations and Regulatory Implications”, article 3.2 on non-human machines. https://tnp.com.ng/the-cbn-agent-banking-guidelines-2025-key-innovations-and-regulatory-implications/</li>
  <li>Mondaq, “Regulatory Framework For Agent Banking In Nigeria”, citing the CBN PDF. https://www.mondaq.com/nigeria/financial-services/1701110/regulatory-framework-for-agent-banking-in-nigeria-cbn-guidelines-and-compliance-requirements</li>
  <li>Central Bank of Nigeria, file URL cited for the 6 October 2025 circular and guidelines. Retrieval for this study on 7 October 2026 returned an access error. https://www.cbn.gov.ng/Out/2025/CCD/CIRCULAR%20AND%20GUIDELINES%20FOR%20THE%20OPERATIONS%20OF%20AGENT%20BANKING%20IN%20NIGERIA%20OCTOBER%206%202025.pdf</li>
  <li>Central Bank of Nigeria Act 2007, sections 17 to 20. https://www.cbn.gov.ng/OUT/PUBLICATIONS/BSD/2007/CBNACT.PDF</li>
  <li>Central Bank of Nigeria, currency-management FAQ on the sole right to issue notes. https://www.cbn.gov.ng/FAQS/FAQS.html?Category=CurrencyManagement</li>
  <li>Constitution of the Federal Republic of Nigeria 1999, section 3(6): 768 local government areas and six area councils. https://nigerian-constitution.com/chapter-1-part-1-section-3-states-federation-federal-capital-territory-abuja/</li>
  <li>Senate Committee on Constitution Review, Chapter 1, Part 1, same section 3(6) text. https://sccr.gov.ng/chapter-1-part-1/</li>
  <li>Central Bank of Nigeria, monetary-policy decisions, 307th meeting, policy rate reset to 23%. https://www.cbn.gov.ng/MonetaryPolicy/decisions.html</li>
  <li>The Nation, “CBN cuts interest rate to 23 per cent in major policy reset”, including August 2026 inflation of 15.39%. https://thenationonlineng.net/cbn-cuts-interest-rate-to-23-per-cent-in-major-policy-reset/</li>
  <li>Arbiterz, NFEM close of ₦1,331.69 per dollar on 5 October 2026, reported 6 October 2026 from CBN data. https://arbiterz.com/naira-dollar-rate-october-6-2026-naira-trades-at-n1331-69-in-cbn-nfem-window/</li>
  <li>Premium Times, “Currency in circulation rose to N5.73 trillion as FX inflows hit $109.86bn in 2025”, 29 July 2026, citing the CBN annual report. https://www.premiumtimesng.com/business/business-news/899182-currency-in-circulation-rose-to-n5-73-trillion-as-fx-inflows-hit-109-86bn-in-2025-cbn.html</li>
  <li>Nairametrics, “CBN: Currency in circulation falls to N5.52 trillion in June 2026”, 24 July 2026, including currency outside banks of ₦4.92 trillion and the payments-vision 40% target. https://nairametrics.com/2026/07/24/cbn-currency-in-circulation-falls-to-n5-52-trillion-in-june-2026/</li>
  <li>The Sun, “Cash outside banks rose by 1.48% to N4.87trn in August”, citing CBN data, and the same 40% target. https://thesun.ng/cash-outside-banks-rose-by-1-48-to-n4-87trn-in-august-cbn/</li>
  <li>Premium Times, “Why lower Naira denominations are scarce — Cardoso”. https://www.premiumtimesng.com/business/business-news/897115-why-lower-naira-denominations-are-scarce-cardoso.html</li>
  <li>Daily Post, “CBN hasn’t said otherwise — Cardoso on validity of N50, N100, other lower naira notes”, 21 July 2026. https://dailypost.ng/2026/07/21/cbn-hasnt-said-otherwise-cardoso-on-validity-of-n50-n100-other-lower-naira-notes/</li>
  <li>Daily Trust, “N20, N50, N100, nothing to buy”, on trader experience of small-note shortage. https://dailytrust.com/n20-n50-n100-nothing-to-buy/</li>
  <li>The Business Times, “CBN Governor Attributes Lower Naira Note Scarcity to Declining Demand”, including the distribution critique. https://thebusinesstimesng.com/cbn-lower-naira-notes-scarcity-declining-demand/</li>
  <li>EFInA, Access to Financial Services in Nigeria 2023, full survey report. https://a2f.ng/wp-content/uploads/2024/07/A2F-2023-SURVEY-REPORT-1.pdf</li>
  <li>EFInA, A2F 2023 key highlights presentation. https://efina.org.ng/wp-content/uploads/2024/03/A2F-2023-Event-Day-Presentation-Version4-1.pdf</li>
  <li>Moniepoint, “How To Get Moniepoint Pos”, terminal price, charges, and the ₦80,000 daily floor. https://moniepoint.com/blog/how-to-get-moniepoint-pos</li>
  <li>Quality Data Systems, “How Much does a Cash Recycler Cost?”. https://blog.qualitydatasystems.com/how-much-does-a-cash-recycler-cost-pricing-freight-and-maintenance</li>
  <li>Quality Data Systems, ATM price ranges for dispense-only and deposit-automated machines. https://www.qualitydatasystems.com/atm</li>
  <li>New Dawn, “Lagos commences Motor Park accreditation”, 8 November 2024, quoting 30 parks on the books and well over 100 unregulated. https://www.newdawnngr.com/2024/11/08/lagosmotor-parks/</li>
  <li>New National Star, “Lagos to digitalise, regulate interstate transport services, upgrade 100 motor parks”. https://newnationalstar.com/lagos-to-digitalise-regulate-interstate-transport-services-upgrade-100-motor-parks/</li>
  <li>PPIAF-hosted mega-terminals assessment, identifying 145 Lagos bus parks in 39 areas. https://www.ppiaf.org/sites/default/files/documents/2023-07/Mega_Terminals_Assessment_Report_112419.pdf</li>
  <li>LAMATA, bus-reform project report, inventory of bus parks, stating the count had risen to more than 60. https://www.lamata-ng.com/wp-content/uploads/2025/04/Final-LBR-Project-Report.pdf</li>
  <li>MapMe / geo4Impact 2025 presentation, “Urban mobility in Lagos”, citing the 2022 danfo census of 759 routes and observation at 48 terminals and 79 stops. https://www.mapme-initiative.org/fileadmin/Dateien/Presentations_geo4Impact_2025/Lagos_Geo4Impact.pdf</li>
  <li>Nibox, company site. https://nibox.ng/</li>
  <li>Nibox, public company profile, first deployment in 2019 and the claim of more than 180,000 people reached. https://www.linkedin.com/company/niboxpay</li>
  <li>NCR Nigeria, products and services, including ATMs, recyclers and the service network. https://ncr.com.ng/products-services/</li>
  <li>NCR Nigeria Plc, annual report for the year ended 31 December 2024. https://ncr.com.ng/wp-content/uploads/2025/04/NCR-NIGERIA-PLC-ANNUAL-REPORT-YEAR-END-31-DEC-2024.pdf</li>
  <li>BRT-News, “CBN Orders Banks, Others To Deploy 1 ATM Per 7,500 Payment Cards”, on the 13 March 2026 circular. https://brtnews.ng/cbn-orders-banks-others-to-deploy-1-atm-per-7500-payment-cards/</li>
  <li>MSME Africa, “CBN Orders Banks to Expand ATM Access Nationwide”, 13 March 2026 guidelines, including the independent-deployer conditions. https://msmeafricaonline.com/cbn-orders-banks-to-expand-atm-access-nationwide-sets-2028-compliance-deadline/</li>
  <li>Foundation for Investigative Journalism, “CBN Orders N100, N500 Charges per N20,000 in ATM Transactions”, 11 February 2025, on circular FPR/DIR/GEN/CIR/001/002. https://fij.ng/article/cbn-orders-n100-n500-charges-per-n20000-in-off-network-atm-transactions/</li>
  <li>The Guardian, “Dangote cuts diesel price to N1,700”, gantry price with effect from 7 October 2026. https://guardian.ng/business-services/dangote-cuts-diesel-price-to-n1700-as-crude-import-costs-fall/</li>
  <li>Daily Post, “Dangote Refinery reduces diesel price”, 7 October 2026, gantry at ₦1,700 and MEMAN landing-cost context. https://dailypost.ng/2026/10/07/dangote-refinery-reduces-diesel-price-to-n85-litre-cheaper-than-imported-ago/</li>
  <li>DailyFuels, Nigeria fuel-price page, diesel at ₦1,810 a litre, updated 6 October 2026. https://dailyfuels.com/nigeria/</li>
  <li>BusinessDay, “Nigeria’s $52 minimum wage buckles as fuel prices jump”, 15 September 2026, stating the minimum wage of ₦70,000. https://businessday.ng/business-economy/article/nigerias-52-minimum-wage-buckles-as-fuel-prices-jump/</li>
  <li>Bank of Industry, MSME lending description: tenors, moratorium and below-market pricing. https://www.boi.ng/who-we-serve/msmes/</li>
  <li>Bank of Industry portal, including the GLOW product of up to ₦50 million at 7% for women-led firms. https://onlineportal.boi.ng/</li>
  <li>Development Bank of Nigeria, wholesale model and ₦1.4 trillion disbursed as of December 2025. https://www.devbankng.com/</li>
  <li>NIBSS, “Digital payment fraud drops 51% to N25.85b, Lagos accounts for 63%”. https://nibss-plc.com.ng/digital-payment-fraud-drops-51-to-n25-85b-lagos-accounts-for-63/</li>
  <li>Nairametrics, “Nigeria’s financial sector suffers N52.26 billion loss to fraud in 2024”, 26 February 2025. https://nairametrics.com/2025/02/26/nigerias-financial-sector-suffers-n52-26-billion-loss-to-fraud-in-2024-nibss-report/</li>
  <li>Turnet Finance, “Moniepoint Review 2026”, the secondary description of 80 to 100 daily transactions at a busy site. Not an official average. https://turnetfinance.ng/moniepoint-review/</li>
  <li>Hyosung Americas, Cajera CR-H product page, fitness sorting and serial-number recognition. Not a price and not a chosen supplier. https://hyosungamericas.com/products/cajera-cr-h/</li>
</ol>
<p class="small">End of study. Model file model/financial_model.py. Rebuild with source/build_study.py.</p>
"""

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CashEase Nigeria — Feasibility study, 7 October 2026</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""
    html_path = ROOT / "source" / "study.html"
    html_path.write_text(doc, encoding="utf-8")
    pdf_path = ROOT / "CashEase_Nigeria_Feasibility_Study.pdf"
    proc = subprocess.Popen(
        [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--user-data-dir=/tmp/chrome-cashease-pdf",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ]
    )
    try:
        proc.wait(timeout=25)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    if not pdf_path.exists() or pdf_path.stat().st_size < 100_000:
        raise SystemExit("PDF was not written")
    print(pdf_path, pdf_path.stat().st_size)


if __name__ == "__main__":
    build()
