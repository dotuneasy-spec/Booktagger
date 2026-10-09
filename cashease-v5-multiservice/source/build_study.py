#!/usr/bin/env python3
"""Build the v5 bank-sponsored multi-service feasibility study."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(ROOT / "source"))

from charts import draw  # noqa: E402
from multiservice_model import main  # noqa: E402

PDF_NAME = "CashEase_Bank_Sponsored_Multiservice_Feasibility.pdf"


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


def pb_s(v) -> str:
    if v is None:
        return "Not within 7 years"
    return f"{v:.1f} years"


def num(v, digits=0) -> str:
    if v is None:
        return "None"
    return f"{v:,.{digits}f}"


def table(headers, rows, caption, keep=False) -> str:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    cls = "tight keep" if keep else "tight"
    return f"<table class='{cls}'><caption>{caption}</caption><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def build() -> None:
    results = main()
    draw(results, ROOT / "charts")
    u = results["units"]
    hi = u["recycler_high"]
    lo = u["recycler_low"]
    kh = u["kiosk_high"]
    kl = u["kiosk_low"]
    val = results["valuation"]
    fund = results["funding"]

    def row_machine(unit, split, wd):
        r = unit["splits"][split][str(wd)]
        return [
            str(wd),
            short(r["revenue"]),
            short(r["cash"]),
            short(r["operating"]),
            irr_s(r["irr"]),
            pb_s(r["payback"]),
            short(r["npv"]),
        ]

    pnl_rows = []
    for split in ("100/0", "70/30", "50/50"):
        for wd in (60, 120, 200):
            cells = row_machine(hi, split, wd)
            pnl_rows.append([split] + cells)

    be_rows = []
    for split in ("100/0", "70/30", "50/50"):
        s = hi["splits"][split]
        be_rows.append([
            split,
            num(s["be_cash"], 0),
            num(s["be_full"], 0),
            num(s["be_cash_host"], 0),
            num(s["be_cash_40"], 0),
            num(s["be_cash_cit"], 0),
        ])

    fleet_rows = []
    for n in (20, 300, 2000, 10000):
        for split in ("100/0", "70/30", "50/50"):
            match = [f for f in results["fleets"] if f["machines"] == n and f["wd"] == 120 and f["split"] == split][0]
            fleet_rows.append([
                f"{n:,}",
                split,
                short(match["year0"]),
                short(match["annual_cash"]),
                irr_s(match["irr"]),
                pb_s(match["payback"]),
                short(match["npv"]),
            ])

    pilot_rows = []
    for wd in (60, 120, 200):
        match = [f for f in results["fleets"] if f["machines"] == 20 and f["wd"] == wd and f["split"] == "70/30"][0]
        pilot_rows.append([
            str(wd),
            short(match["annual_cash"]),
            irr_s(match["irr"]),
            pb_s(match["payback"]),
            short(match["npv"]),
        ])

    low_rows = []
    for wd in (60, 120, 200):
        low_rows.append(["70/30"] + row_machine(lo, "70/30", wd)[1:])

    scale_rows = []
    for s in results["scale"]:
        scale_rows.append([
            f"{s['machines']:,}",
            f"{s['daily_withdrawals']:,.0f}",
            f"{s['share_of_h1_2025_daily'] * 100:.2f}%",
            short(s["naira_if_each_is_20000"]),
        ])

    n50 = val["machines_for_50bn_npv"]

    def n50s(key):
        v = n50[key]
        return "Not within 20,000 machines" if v is None else f"{v:,}"

    body = f"""
<div class="cover">
  <p class="kicker">Feasibility study · October 2026</p>
  <h1>CashEase Nigeria: Bank-Sponsored Multi-Service Machine Network Feasibility Study</h1>
  <p class="sub">CashEase owns the machines. One sponsor bank holds the licence and the cash. Full recyclers at the busiest sites. Cash-in kiosks only if someone else can name a fee this paper could not find.</p>
  <div class="verdict">
    <p><strong>Verdict. Do not build the network on this evidence.</strong> A recycler can earn a return above 28% in two narrow cases on the high landed cost: CashEase keeps the whole ₦500 off-site surcharge and the site does about 120 other-bank withdrawals a day, or CashEase keeps 70% and the site does about 200. The base case in the brief, 120 withdrawals and a 70/30 split, earns 14.1% and a negative value at 28%. The cash-in kiosk does not cover its own running costs on the only Nigerian commission schedule this search could quote. A ₦50 billion value appears in the model only when CashEase keeps every naira of the cap, at scale. That is an upper bound, not a forecast.</p>
  </div>
  <p>The ₦100 per ₦20,000 is not CashEase income. Cardtronics’ 41% is a 2019 US example of branding plus interchange, and branding makes the sponsor’s own customers free. Coinstar’s published cash fee is up to 15.9% plus up to $0.99, not 11.9%. CMS does not publish ₹11,000 to ₹40,000 per ATM per month. Euronet’s $1,881 is average monthly revenue per ATM in 2024, not profit and not Nigeria.</p>
</div>

<h2>1. What this paper tests</h2>
<p>CashEase buys two kinds of machine. A full cash recycler, at a few busy sites, would take deposits, pay out cash, break notes, and also sell airtime and take bills. A smaller cash-in kiosk, spread more widely and later offered to franchisees, would take cash for bills, airtime, wallet top-up and transfers, and would not pay cash out. A sponsor bank would hold the off-site ATM licence. Hosts would take a share. Later years would add managed services for other banks and government collections.</p>
<p>The phases in the brief are a pilot of 10 to 20 recyclers, then a few hundred recyclers plus franchised kiosks, then thousands of points plus managed services. This paper prices the pilot against a landed machine, then asks whether 20, 300, 2,000 and 10,000 points change the answer. They do not, when each machine is below the hurdle.</p>
<p>Three figures in the brief are real and mean something else. They are corrected in section 2 and they are not used as Nigerian income. Volumes of 60, 120 and 200 withdrawals a day are scenarios. No published count of withdrawals at a Nigerian off-site ATM was found, so none of those three is a forecast.</p>

<h2>2. Benchmarks, as published</h2>
<p><strong>Euronet.</strong> The 2024 Form 10-K says average monthly revenues per ATM increased to $1,881 in 2024 from $1,797 in 2023.<sup>1</sup> The same paragraph set sits on EFT Processing revenue of $1,161.2 million and average active ATMs of 51,450. Dividing those two figures by twelve months lands on $1,881. Revenue per transaction in that segment was $0.10. Direct operating costs were $605.4 million and include site rent, cash delivery, cash supply, maintenance, insurance, telecoms and processing-centre costs. Operating income for the whole segment was $256.0 million. Active ATMs at 31 December 2024 were 49,945. An earlier sentence in the same filing also says the company operated 55,248 ATMs. This paper uses the $1,881 sentence as written: it is revenue, it is a global average, and it is not a Nigerian profit.</p>
<p>At the 5 October 2026 NFEM rate, $1,881 a month is {short(val['euronet_annual_revenue_ngn'])} a year.<sup>2</sup> Two hundred withdrawals a day at a ₦500 surcharge for 270 days is ₦27.00 million. The high scenario in this paper is in the neighbourhood of Euronet’s average revenue, not of a quiet site. It still leaves out the cash-supply costs Euronet counts inside direct operating costs.</p>
<p><strong>Cardtronics.</strong> The 27 March 2019 investor-day slide shows one US network ATM where “Surcharge-free Branding” is “41% of total revenue”.<sup>3</sup> The lines under that label are a monthly fixed branding fee per ATM plus a per-transaction interchange fee. The slide says “Example based on U.S. Fee structures vary by country.” Branding, in Cardtronics’ own words, gives the bank’s customers surcharge-free access. Allpoint is a separate product: a fee per cardholder or per transaction, plus interchange. No Nigerian branding fee, and no current dollar monthly fee, was found. This paper does not book 41% of anything as CashEase revenue. A branding contract and a ₦500 surcharge on the sponsor’s own cards cannot both be collected from the same withdrawal.</p>
<p><strong>India1 and the Indian interchange.</strong> From 1 May 2025 the National Financial Switch interchange is ₹19 on a domestic financial ATM transaction and ₹7 on a non-financial one, and the customer cap beyond free transactions is ₹23.<sup>4,5</sup> K. Srinivas of India1 Payments told Business Standard that costs are not static, and that the practical answers are an interchange indexed to inflation or a customer surcharge “as is the practice in the rest of the world”.<sup>6</sup> That is a warning about a regulated fee that lags cost. It is not a naira revenue line. Indian interchange is not added to the CashEase account.</p>
<p><strong>CMS.</strong> The FY24 annual report says CMS managed 18,500 or more ATMs and that 75% of managed services were on a fixed-price model under CMS’s own classification. Order wins in managed services and technology solutions were ₹18,500 million for the year.<sup>7</sup> The report does not publish a fee of ₹11,000 to ₹40,000 per ATM per month. An Elara Securities note of 7 October 2024, which is a broker’s page and not a CMS tariff, prints remote-monitoring prices “from INR 4,000 to INR 14,000 per site” and a blended-revenue fragment near ₹40,000.<sup>8</sup> Neither figure is used as income.</p>
<p><strong>Coinstar.</strong> The US help page says a cash option may include a service fee of up to 15.9% plus a transaction fee of up to $0.99, and that the kiosk shows the exact fee.<sup>9</sup> There is no single nationwide 11.9%. The Canadian page states a 12.90% processing fee and says fees may vary.<sup>10</sup> A coin-counting percent is not a naira change fee. The change line in this model, where it appears, is a flat ₦100 assumption, and it is kept out of the base case.</p>
<p><strong>QIWI.</strong> QIWI plc sold the Russian operations, which were 89.9% of 2023 revenue, on 29 January 2024.<sup>11</sup> The agent protocol describes a terminal commission charged to the customer. It does not publish a franchise fee or a take rate this paper can copy. A Moscow business-for-sale advert is not a QIWI tariff and is not used.</p>
<p><strong>TouchPay.</strong> The 2023 Philippine site says the network had over 3,000 automated payment machines and a target of 10,000 by 2026. It does not print an investment or a franchisor fee.<sup>12</sup> A July 2020 article says the total investment was ₱350,000 and that there was no franchise fee.<sup>13</sup> That is a five-year-old secondary report, not a 2026 price list. The Brazilian company behind a different TouchPay product says, on its own page, that TouchPay is not a franchise.<sup>14</sup> No franchisor margin was found, so franchisee capital is described in section 8 as a way to move the kiosk bill, not as a source of CashEase profit.</p>

<h2>3. Licence, the agent ban, and the surcharge</h2>
<p>The official CBN agent-guidelines PDF returned an access error when it was requested for the earlier studies, and it was not re-opened for this one.<sup>15</sup> G. Elias, writing on the guidelines issued on 6 October 2025, says the guidelines prohibit the use of non-human or automated machines by agents.<sup>16</sup> A machine therefore should not be filed as an agent. That is the same reading as in the earlier papers.</p>
<p>A cash-in kiosk does not escape that sentence by dropping cash-out. Bill payment and cash-in are ordinary agent activities. The ban is on using an automated machine as the agent. The CBN has not published a statement that a bill-and-airtime kiosk with no cash-out sits outside the ban. This paper does not invent that safe harbour. The open path for a machine that accepts or pays cash is the ATM path: the sponsor bank’s off-site machine, or an independent deployer with prior written CBN approval and a bank that provides the cash.<sup>17</sup></p>
<p>From 1 March 2025, a withdrawal at another bank’s on-site ATM costs the customer ₦100 per ₦20,000. At an off-site ATM the customer pays that ₦100 plus a surcharge of up to ₦500 per ₦20,000. The circular language reported at the time says the surcharge is income of the ATM deployer and must be disclosed.<sup>18,19</sup> The ₦100 is not deployer income. On-us withdrawals are free. EFInA’s explainer also uses the phrase “up to ₦500 per transaction” in one place and “per ₦20,000” in the worked table. This model follows the per-₦20,000 reading and then assumes each counted withdrawal is one block. A customer who takes ₦100,000, the ATM daily cap in the later cash circular, could be five blocks if the cap stacks. That upside is not in the tables. One block is the case that is counted.</p>
<p>The sponsor-bank model cuts against the surcharge. If the bank brands the machine so its own customers pay nothing, those withdrawals produce ₦0 for CashEase. The 100/0 column below is the case where every withdrawal is another bank’s card and the surcharge is at the ₦500 cap. It is an upper bound. A labelled sensitivity cuts the paying share to 40%.</p>
<p>Cash funding of a non-bank ATM sits with the partner bank under the earlier ATM guidelines used in the machine study. The base case therefore leaves float and cash-in-transit off CashEase. A sensitivity puts the ₦1.92 million cash-in-transit assumption back on CashEase. If the bank will not sign that allocation, the base case is the wrong one.</p>

<h2>4. Landed cost</h2>
<p>The recycler band the brief names is on an Alibaba listing: US$3,650 to US$7,850, Guangdong, cash acceptor and cash dispenser, lead time 35 days for one to ten units, shipping “to be negotiated”.<sup>20</sup> A direct open of that page was blocked as unusual traffic, so the price is taken from the public listing extract read on 9 October 2026. A second Guangdong banking-kiosk listing prints US$6,500, US$6,250 and US$5,800 by quantity.<sup>21</sup> The manufacturer price already checked for Hongzhou, US$4,800 for ten or more and US$5,500 for one to nine, sits inside this band.<sup>22</sup> The US$3,650 floor is below that manufacturer price. It is a listing floor, not a factory invoice. The top of the band is used as the working machine, with the only published per-unit “Customized” adder of US$1,800. That adder does not say it is a naira template.<sup>23</sup></p>
<p>The cash-in band is on TradeIndia. Capital Business Systems Pvt. Ltd. in Kolkata lists an automated cash deposit machine at ₹150,000 to ₹600,000 a unit, suitable currency Indian rupees, indoor, floor-standing, cash deposit only.<sup>24</sup> It is not a naira machine and it does not dispense. A second seller page repeats the same price band and much of the same text. The rupee is converted at the FBIL reference rate on the RBI site at 1:00pm on 9 October 2026, ₹96.6149 per dollar.<sup>25</sup> No Mumbai–Lagos container quote was found, so the Shenzhen–Lagos 20-foot band is used as a stand-in and labelled as one.<sup>26</sup></p>
<p>Naira conversion uses the CBN NFEM rate on 5 October 2026, ₦1,331.6875 per dollar.<sup>2</sup> Press reports for 9 October put the official window around ₦1,327 to ₦1,332. The difference does not change the verdict, and this paper does not replace a table rate with a rounded headline. Duty is 5% of CIF, a representative rate for heading 8471.60, not a Nigeria Customs ruling.<sup>27</sup> VAT is 7.5% of CIF plus duty.<sup>28</sup> SONCAP is US$850 a consignment, split by an assumption of ten machines in a 20-foot box.<sup>29</sup> Terminal handling and clearing use the forwarder’s published container ranges, also split by ten.<sup>30</sup> Site works are assumptions: ₦8.00 million on a recycler, carried from the machine study, and ₦3.00 million on a cash-in kiosk. NIBSS’s May 2024 note charges ₦250,000 for a device and ₦250,000 for an application. That ₦500,000 is added once, to the first machine. It is a POS-terminal fee, not a published ATM type-approval fee.<sup>31</sup></p>

{table(
    ["Machine", "Goods", "Border", "First machine"],
    [
        ["Recycler, US$3,650, no adder, low freight", short(lo["box"]["exworks_ngn"]), short(lo["box"]["border_ngn"]), short(lo["box"]["all_in_ngn"])],
        ["Recycler, US$7,850 plus US$1,800, high freight", short(hi["box"]["exworks_ngn"]), short(hi["box"]["border_ngn"]), short(hi["box"]["all_in_ngn"])],
        ["Cash-in, ₹150,000, no adder, low freight", short(kl["box"]["exworks_ngn"]), short(kl["box"]["border_ngn"]), short(kl["box"]["all_in_ngn"])],
        ["Cash-in, ₹600,000 plus US$1,800, high freight", short(kh["box"]["exworks_ngn"]), short(kh["box"]["border_ngn"]), short(kh["box"]["all_in_ngn"])],
    ],
    "First-machine cost includes site works and one ₦500,000 NIBSS pair. The next machine drops the ₦500,000.",
)}
<img src="../charts/fig_landed.png" alt="Landed cost of the four machine cases"/>
<p>The working recycler is the high band, {short(hi['box']['all_in_ngn'])}. The low band, {short(lo['box']['all_in_ngn'])}, is shown because the verdict flips inside the listing range. The US deposit-ATM reference in the earlier papers, ₦65.53 million before duty, is not redrawn. It remains too dear for this fee.</p>

<h2>5. One recycler</h2>
<p>Cash costs on the high band, all assumptions except the maintenance rule applied to the goods value, are rent {short(hi['costs']['rent'])}, power {short(hi['costs']['power'])}, security {short(hi['costs']['security'])}, connectivity {short(hi['costs']['connectivity'])}, maintenance {short(hi['costs']['maintenance'])} and insurance {short(hi['costs']['insurance'])}. Street cost is {short(hi['costs']['street'])}. Depreciation over seven years is {short(hi['costs']['depreciation'])}. Full cost is {short(hi['costs']['full'])}. The bank carries float and cash-in-transit in this table. Effective days are 270. Income is the surcharge only.</p>
{table(
    ["Split", "Withdrawals a day", "Revenue", "Cash profit", "Operating", "IRR", "Payback", "NPV at 28%"],
    pnl_rows,
    "High-band recycler. Split is CashEase/bank of the ₦500 surcharge. One block per withdrawal. Every withdrawal pays the cap.",
)}
<img src="../charts/fig_cash.png" alt="Cash profit by volume and surcharge split"/>
<img src="../charts/fig_irr.png" alt="IRR by volume and surcharge split, with a 28 percent line"/>
<p>At 70/30, cash profit turns at {num(hi['splits']['70/30']['be_cash'], 0)} withdrawals a day and full cost at {num(hi['splits']['70/30']['be_full'], 0)}. The base volume of 120 earns {irr_s(hi['splits']['70/30']['120']['irr'])}, pays back in {pb_s(hi['splits']['70/30']['120']['payback'])}, and the net present value is {short(hi['splits']['70/30']['120']['npv'])}. At 200 withdrawals the same split earns {irr_s(hi['splits']['70/30']['200']['irr'])} and the value turns positive. At 60 it loses cash, and there is no return to quote.</p>
<p>Keeping the whole surcharge is the only high-band case that clears 28% at 120 withdrawals: {irr_s(hi['splits']['100/0']['120']['irr'])}, payback {pb_s(hi['splits']['100/0']['120']['payback'])}. At 60, even 100/0 earns {irr_s(hi['splits']['100/0']['60']['irr'])}. A 50/50 split at 200 earns {irr_s(hi['splits']['50/50']['200']['irr'])}, just under the hurdle, and the value is still {short(hi['splits']['50/50']['200']['npv'])}.</p>
{table(
    ["Split", "Cash break-even", "Full-cost break-even", "Host takes 20%", "Only 40% pay", "CashEase pays CIT"],
    be_rows,
    "Withdrawals per scheduled open day on the high-band recycler. Host share and the 40% paying share are assumptions. Cash-in-transit put back on CashEase is the ₦1.92 million assumption.",
    keep=True,
)}
<p>A host share was not found in a Nigerian tariff. Taking a labelled 20% of CashEase’s surcharge moves the 70/30 cash break-even from {num(hi['splits']['70/30']['be_cash'], 0)} to {num(hi['splits']['70/30']['be_cash_host'], 0)}. If only 40% of withdrawals pay the surcharge, because the rest are the sponsor’s own cards, the same break-even becomes {num(hi['splits']['70/30']['be_cash_40'], 0)}. Putting cash-in-transit back on CashEase moves it to {num(hi['splits']['70/30']['be_cash_cit'], 0)}.</p>
<p>The low band, {short(lo['box']['all_in_ngn'])}, at 70/30, has a cash break-even of {num(lo['splits']['70/30']['be_cash'], 0)} and a full-cost break-even of {num(lo['splits']['70/30']['be_full'], 0)}. At 120 withdrawals the return is {irr_s(lo['splits']['70/30']['120']['irr'])} and the value is {short(lo['splits']['70/30']['120']['npv'])}. At 60 it is still a loss. The listing range is wide enough that one end fails the base case and the other clears it. That is a reason to wait for a proforma invoice, not a reason to average the two prices.</p>
{table(
    ["Withdrawals a day", "Revenue", "Cash profit", "Operating", "IRR", "Payback", "NPV at 28%"],
    [["60"] + low_rows[0][1:], ["120"] + low_rows[1][1:], ["200"] + low_rows[2][1:]],
    "Low-band recycler at a 70/30 split. Same surcharge rules. Lower machine, lower maintenance.",
)}

<h2>6. The other services</h2>
<p>VTpass publishes a terminal-agent schedule. MTN airtime is 3.00%. Airtel airtime is 2.00%. Glo airtime is 3.00%. DSTV is 1.20%. Ikeja Electric for the “others” column is 1.00%, capped at ₦1,500.<sup>32</sup> These are VTpass shares for a terminal agent, not a contract with CashEase. The labelled stack uses the MTN rate on an assumed 30 airtime sales a day of ₦1,000, the Ikeja rate on an assumed 10 bills a day of ₦5,000, and a flat ₦100 on an assumed 20 change transactions. Transfers are zero because that schedule has no transfer line. Screen advertising is zero because no Nigerian kiosk rate was found. The stack is {short(results['stack_unit']['total'])} a year, of which change is {short(results['stack_unit']['change'])}.</p>
<p>Added to the high-band recycler at 120 withdrawals and 70/30, the stack lifts cash profit from {short(hi['splits']['70/30']['120']['cash'])} to {short(hi['with_stack_70_120']['cash'])}. The return becomes {irr_s(hi['with_stack_70_120']['irr'])}. The value at 28% is still {short(hi['with_stack_70_120']['npv'])}. Airtime, bills and a flat change fee do not repair a surcharge split that misses the hurdle.</p>
<p>The cash-in kiosk has no surcharge. On the same stack without the change fee, revenue is {short(kh['kiosk_only']['revenue'])} a year. Street cost is {short(kl['costs']['street'])} on the cheap kiosk and {short(kh['costs']['street'])} on the dear one. Both lose cash. There is no payback. Covering the dear kiosk’s street cost from MTN’s 3% alone would take about {short(kh['kiosk_only']['airtime_sales_per_day'])} of airtime sales a day. That figure is a threshold, not a forecast. Government collections are not added. No volume was published.</p>
<p>A franchise does not fill the gap. TouchPay’s 2020 article says the operator paid for the machine and paid no franchise fee. QIWI’s current take rate was not in the 20-F. Until a Nigerian contract names CashEase’s kiosk fee, the franchisor’s income in this model is zero and the kiosk is a cost.</p>

<h2>7. Fleets</h2>
<p>Head office is an assumption: ₦25 million a year plus ₦50,000 a machine, and ₦40 million plus ₦150,000 a machine at the start. The first machine carries the NIBSS pair. The rest do not. The table uses the high-band recycler, 120 withdrawals a day, surcharge only, bank carrying the cash.</p>
{table(
    ["Points", "Split", "Year 0", "Annual cash", "IRR", "Payback", "NPV at 28%"],
    fleet_rows,
    "High-band recyclers at 120 withdrawals a day. Year 0 is the machines plus the opening office.",
)}
<p>A larger fleet copies the machine. At 70/30 and 120 withdrawals, 20 machines earn {irr_s([f for f in results['fleets'] if f['machines']==20 and f['wd']==120 and f['split']=='70/30'][0]['irr'])} and 10,000 earn {irr_s([f for f in results['fleets'] if f['machines']==10000 and f['wd']==120 and f['split']=='70/30'][0]['irr'])}. The value stays negative and gets larger. At 100/0 and 120, the value is positive, and 10,000 machines reach {short([f for f in results['fleets'] if f['machines']==10000 and f['wd']==120 and f['split']=='100/0'][0]['npv'])}. That is the only cell on this table above ₦50 billion.</p>
{table(
    ["Withdrawals a day", "Annual cash, 20 machines", "IRR", "Payback", "NPV at 28%"],
    pilot_rows,
    "Pilot scale, 20 high-band recyclers, 70/30. Twenty is the top of the 10-to-20 pilot, not a measured site list.",
)}
<p>Twenty machines at the base volume make cash after the office and still miss 28% by a wide gap. The payback is {pb_s([f for f in results['fleets'] if f['machines']==20 and f['wd']==120 and f['split']=='70/30'][0]['payback'])}. At 200 withdrawals the same 20 machines earn {irr_s([f for f in results['fleets'] if f['machines']==20 and f['wd']==200 and f['split']=='70/30'][0]['irr'])}. The pilot is worth running only to find out which of those volumes is real. It is not worth staffing as a business before that count exists.</p>
{table(
    ["Points at 120 a day", "Withdrawals a day", "Share of recent national ATM withdrawals", "Naira if each withdrawal is ₦20,000"],
    scale_rows,
    "National denominator: 858.80 million ATM withdrawals in the first half of 2025, divided by 181 days. The 181 is the calendar length of 1 January to 30 June.",
)}
<p>Ten thousand machines at 120 withdrawals a day would be about a quarter of the withdrawals Nigeria’s ATMs already did in that half-year.<sup>33</sup> Two thousand would be about 5%. Cash out the door, on the one-block assumption, would be {short(results['scale'][3]['naira_if_each_is_20000'])} a day at 10,000 points. The sponsor bank would have to own that logistics. The address lists in the machine study summed to 2,887 places before overlap. Ten thousand new off-site sites are not in those lists. Active ATMs in the first half of 2024 were 16,714.<sup>34</sup></p>

<h2>8. Capital, funding, and ₦50 billion</h2>
<p>CashEase owns the machines in the base case, so the equity cheque is the year-0 column. For 20 high-band recyclers that is {short(fund['equity']['year0'])}, before the cash the bank must put in the cassettes. No vendor-finance rate was found on the Alibaba or TradeIndia pages. If a lender charged the policy rate of 23% on 70% of one high-band machine for five years, the annual instalment would be {short(hi['debt_service_70pct_5y_23'])}.<sup>35</sup> Cash profit at 70/30 and 120 withdrawals is {short(hi['splits']['70/30']['120']['cash'])}, which does not cover that instalment. At 200 withdrawals it does. The 23% is the September 2026 policy rate. It is not a term sheet.</p>
<p>Bank co-investment is modelled as the bank paying half the machines and still taking 30% of the surcharge. On 20 machines at 120 withdrawals, CashEase’s return rises to {irr_s(fund['bank_half_capex']['irr'])} and the value is still {short(fund['bank_half_capex']['npv'])}. Halving the cheque does not manufacture the missing yield. Franchisee capital applies to kiosks. With no franchisor fee on the record, moving the kiosk cheque to a franchisee sets CashEase’s kiosk income to zero and leaves the office cost standing.</p>
<p>No ATM-operator multiple was applied. ₦50 billion is the figure in the brief, not a result of a sale. At 28%, seven years of a flat cash profit have a present-value factor of {val['annuity_factor_7_at_28']:.2f}, so the profit that has a present value of ₦50 billion, ignoring the cheque that built the fleet, is {short(val['annual_cash_for_pv_50bn'])} a year. A perpetuity at 28% would need {short(val['perpetual_cash_at_28'])} a year. Counting the cheque, the high-band fleet reaches a ₦50 billion net present value at these sizes:</p>
<ul>
  <li>100/0 at 120 withdrawals a day: {n50s("100/0 at 120")} machines.</li>
  <li>100/0 at 200: {n50s("100/0 at 200")} machines.</li>
  <li>70/30 at 120: {n50s("70/30 at 120")}.</li>
  <li>70/30 at 200: {n50s("70/30 at 200")} machines.</li>
  <li>50/50 at 200: {n50s("50/50 at 200")}.</li>
</ul>
<p>The 70/30 base volume never gets there. The path that does is the path where the bank gives away the surcharge and CashEase still gets the bank’s cash operation for nothing, repeated at a national scale.</p>

<h2>9. Risks</h2>
<p><strong>Transfers on a phone.</strong> Deployed POS terminals at the end of March 2025 were 5.90 million.<sup>36</sup> A kiosk that sells airtime and pays bills is competing with an agent who already stands in the shop. The VTpass rates used here are the same family of rates those agents already earn. The machine has to beat a person on cost. On the numbers above, it does not.</p>
<p><strong>The surcharge can be cut.</strong> The ₦500 is a cap, set by circular, and the deployer has to disclose it. A later circular can lower the cap, can move off-site machines onto the on-site rule, or can widen the set of free withdrawals. The model has no hedge against that. India1’s public position is what a network looks like when the regulated fee lags cost.</p>
<p><strong>Cash.</strong> The base case works only if the sponsor bank loads the cassettes and pays the carrier. Sixty withdrawals of ₦20,000 is ₦1.20 million a day in one machine. Two hundred is ₦4.00 million. A bank that will brand the machine and also refuse the cash is not the bank in this paper.</p>
<p><strong>Theft and uptime.</strong> Security of ₦1.44 million a year on a recycler, and ₦360,000 on a kiosk, are assumptions. They are not a quote from a CIT company and they are not a loss record. A recycler holding a day’s pay-outs is a target. The 90% uptime assumption is the other way to miss the break-even: a machine that is down does not earn the day that was counted.</p>
<p><strong>The exchange rate and the listing.</strong> Goods are priced in dollars and rupees. A 20% move in the naira against the invoice currency moves the landed cost before a single withdrawal. The Alibaba band is not a proforma. The US$3,650 end has not been shown to be a whole recycler with a naira template, a warranty, and certificates NIBSS will accept.</p>

<h2>10. Gates and the next twelve months</h2>
<p>Gate 1. A lawyer’s note, and a letter from the sponsor bank’s compliance office, that these machines will be filed as the bank’s off-site ATMs or as an independent deployment with prior written CBN approval. A cash-in kiosk is not ordered while the agent question is unanswered.</p>
<p>Gate 2. A term sheet that states the surcharge split, states that the bank’s own cards are free or are not, and states that the bank supplies cash and pays cash-in-transit. If the split is 50/50, stop. If the bank’s cards are free and they are most of the traffic, stop. If CashEase must carry the cash, reprice before any order. The high-band machine needs the 70% share and a site near 200 other-bank withdrawals, or the 100% share and a site near 120, before it clears 28%.</p>
<p>Gate 3. A supplier proforma that replaces the listing, with the naira template, the warranty, and the certificates named. Do not average US$3,650 and US$7,850. Price the invoice in the landed sheet and rerun the break-even.</p>
<p>Gate 4. Ten machines, not two hundred, on sites the bank already believes are off-site and busy. Run them long enough to count other-bank withdrawals per open day. Expand only if that count clears the full-cost break-even of the invoiced machine at the signed split. Twenty machines at 120 a day and 70/30 still earn about 4% after the office. That is not an expansion case.</p>
<p>Gate 5. No franchise agreement, no managed-service pitch, and no government-collections volume in the first year. Those incomes were not found. Kiosks stay off the order list until a pilot kiosk covers its own street cost on written commissions.</p>
<p>The twelve months, if Gate 1 and Gate 2 are open:</p>
<ol>
  <li>Month 1. Counsel reads the agent guidelines against a cash-in kiosk and against a bank-sponsored recycler. Ask the CBN contact the bank already uses. Do not file the machine as an agent.</li>
  <li>Month 2. One bank, one term sheet. Split, on-us treatment, cash, cash-in-transit, host rent, and who speaks to NIBSS.</li>
  <li>Months 3 and 4. If the sheet survives Gate 2, take a proforma and a SONCAP reading. Pay the NIBSS sandbox only when the EMV, PCI and scheme letters the May 2024 note requires are in hand. Those letters were not attached to the listings.</li>
  <li>Months 5 to 8. Install ten recyclers. Publish the weekly count of paying withdrawals, downtime, cash-outs, and losses. No second order during the count.</li>
  <li>Months 9 to 12. If the count clears the break-even, price the next ten from retained cash and the same term sheet. If it does not, stop. Do not open a franchise offer to fill the gap.</li>
</ol>
<p>Two thousand points and ten thousand points are not steps in this year. They are the scale at which the model can print ₦50 billion, and only in the case the bank gives up the surcharge.</p>

<h2>11. Workings</h2>
<p>NFEM rate = 1,331.6875. Rupee rate = 96.6149 per dollar. Recycler high goods = (7,850 + 1,800) × 1,331.6875. Cash-in high goods = (600,000 / 96.6149 + 1,800) × 1,331.6875. Freight per machine = container rate / 10. CIF = goods + freight. Duty = 5% of CIF. VAT = 7.5% of (CIF + duty). SONCAP per machine = 850 / 10 dollars. Border naira = (CIF + duty + VAT + SONCAP) × 1,331.6875 + (terminal handling + clearing) / 10. Recycler works = 8,000,000. Kiosk works = 3,000,000. First machine = border + works + 500,000.</p>
<p>Effective days = 300 × 0.90 = 270. Surcharge income = withdrawals × 270 × 500 × CashEase share. The ₦100 is not in the sum. Street cost is rent + power + security + 216,000 + 10% of goods naira + 1.5% of the first-machine cost. Recycler rent, power and security are 1,800,000, 688,160 and 1,440,000. Kiosk figures are 600,000, 180,000 and 360,000. Full cost adds the first-machine cost divided by 7.</p>
<p>Cash profit = surcharge income − street cost. Operating profit subtracts depreciation as well. The return uses year 0 equal to the first-machine cost and seven years of cash profit. No salvage, no tax, no debt inside the return. The hurdle is 28%. “Not defined” means the cash flows do not change sign inside a solver range from −99% to 500%.</p>
<p>Fleet year 0 = first machine + (machines − 1) × (first machine − 500,000) + 40,000,000 + 150,000 × machines. Annual cash = machines × machine cash profit − 25,000,000 − 50,000 × machines. The ₦50 billion search finds the smallest fleet of 20,000 or fewer whose net present value at 28% is at least ₦50 billion.</p>
<p>The labelled stack is 30 × 1,000 × 0.03 × 270, plus 10 × 5,000 × 0.01 × 270, plus, on a recycler only, 20 × 100 × 270. Recompute from <span class="small">model/multiservice_model.py</span>.</p>

<h2>12. Sources</h2>
<ol class="sources">
  <li>Euronet Worldwide, Inc., Form 10-K for the year ended 31 December 2024, EFT Processing discussion. Average monthly revenues per ATM $1,881. Average active ATMs 51,450. Revenue $1,161.2 million. Revenue per transaction $0.10. https://www.sec.gov/Archives/edgar/data/1029199/000121390025017068/eeft-20241231.htm</li>
  <li>Central Bank of Nigeria, NFEM rates, 5 October 2026, NFEM rate ₦1,331.6875. https://www.cbn.gov.ng/rates/ExchRateByCurrency.html and the same close as reported by Arbiterz. https://arbiterz.com/naira-dollar-rate-october-6-2026-naira-trades-at-n1331-69-in-cbn-nfem-window/</li>
  <li>Cardtronics plc, Investor Day, 27 March 2019, slide on multiple revenue sources at a single network ATM. “41% of total revenue” is the US example for surcharge-free branding, a monthly fee plus interchange. “Fee structures vary by country.” https://www.sec.gov/Archives/edgar/data/1671013/000167101319000008/catminvestordaypresen098.htm</li>
  <li>Business Standard, ATM interchange to ₹19 from 1 May 2025, non-financial ₹7. https://www.business-standard.com/finance/news/atm-interchange-fee-hiked-to-rs-19-new-rate-effective-from-may-1-125032501317_1.html</li>
  <li>Reserve Bank of India, ATM interchange and customer charges, customer cap ₹23 from 1 May 2025, interchange to be decided by the network. https://www.rbi.org.in/scripts/NotificationUser.aspx?Id=12111&amp;Mode=0</li>
  <li>Business Standard, K. Srinivas, India1 Payments, on indexing interchange or allowing a customer surcharge, 12 December 2025. https://www.business-standard.com/industry/banking/atm-interchange-fee-rbi-hike-cost-squeeze-125121201085_1.html</li>
  <li>CMS Info Systems, annual report FY24. Managed services, 18,500+ ATMs, 75% fixed-price model on CMS’s classification, order wins of ₹18,500 million. No per-ATM monthly tariff of ₹11,000–40,000. https://www.cms.com/annual-report-2024/cms-pdf/annual-report-2024.pdf</li>
  <li>Elara Securities, CMS Info Systems note, 7 October 2024. Broker ranges, including remote monitoring from ₹4,000 to ₹14,000 a site. Not a CMS price list. https://www.valoremadvisors.com/assets/admin/research_file/1744091795_CMS_Info_Systems_-_Elara_Securities_-_7_October_2024.pdf</li>
  <li>Coinstar, help centre. Cash option up to 15.9% plus up to $0.99. https://www.coinstar.com/helpcenter/</li>
  <li>Coinstar Canada, help centre. A 12.90% processing fee is stated, and fees may vary by location. https://coinstar.ca/helpcentre</li>
  <li>QIWI plc, Form 20-F for 2023. Sale of Russian operations consummated 29 January 2024. Those operations were 89.9% of 2023 revenue. https://www.sec.gov/Archives/edgar/data/1561566/000110465924050019/qiwi-20231231x20f.htm</li>
  <li>TouchPay Philippines, 2023 site. Over 3,000 automated payment machines, target 10,000 by 2026. No investment figure on the page. http://2023.touchpay.ph/</li>
  <li>BusinessNews, 27 July 2020. TouchPay total investment ₱350,000 and no franchise fee. Secondary, and five years old. https://www.businessnews.com.ph/franchising-touchpay-the-pioneer-express-payment-system-in-the-philippines-20200727/</li>
  <li>AMLabs, TouchPay page. The Brazilian product is not a franchise. https://www.amlabs.com.br/lp/touchpay/</li>
  <li>Central Bank of Nigeria, agent-guidelines PDF, 6 October 2025. Retrieval returned an access error. https://www.cbn.gov.ng/Out/2025/CCD/CIRCULAR%20AND%20GUIDELINES%20FOR%20THE%20OPERATIONS%20OF%20AGENT%20BANKING%20IN%20NIGERIA%20OCTOBER%206%202025.pdf</li>
  <li>G. Elias, note on the 2025 agent-banking guidelines, including the prohibition on non-human or automated machines. https://www.gelias.com/images/Central_Bank_of_Nigeria_Guidelines_on_the_Operations_of_Agent_Banking.pdf</li>
  <li>Nairametrics, 14 March 2026, CBN guidelines of 13 March 2026. Independent ATM deployers need prior written approval and a bank partnership for cash. https://nairametrics.com/2026/03/14/cbn-mandates-one-atm-per-7500-payment-cards-by-2028/</li>
  <li>EFInA, explainer of the 10 February 2025 ATM fee circular, effective 1 March 2025. https://efina.org.ng/wp-content/uploads/2025/04/EFInA-Explainer-Series-Issue-1-CBN-2025-Review-of-ATM-Transaction-Fees.pdf</li>
  <li>Foundation for Investigative Journalism, 11 February 2025, circular FPR/DIR/GEN/CIR/001/002. Surcharge of not more than ₦500 per ₦20,000 is income of the deployer. https://fij.ng/article/cbn-orders-n100-n500-charges-per-n20000-in-off-network-atm-transactions/</li>
  <li>Alibaba listing, self-service note recycler with cash dispenser, US$3,650–7,850, Guangdong. Page fetch blocked; price read from the public listing extract. https://www.alibaba.com/product-detail/Self-Service-Banking-Payment-Pay-Note_1601035609024.html</li>
  <li>Alibaba listing, banking ATM kiosk, US$6,500 / US$6,250 / US$5,800. https://www.alibaba.com/product-detail/Kiosk-Manufacturer-Banking-ATM-Kiosk-Cash_1601261054006.html</li>
  <li>Shenzhen Hongzhou, HZ-3326 cash in/out kiosk, US$5,500 and US$4,800. Manufacturer price already used in the China-kiosk addendum. https://hongzhou2.en.made-in-china.com/product/HnfURoZyAMhj/China-Bank-Government-Cash-in-out-Kiosk-Cash-Recycler-ATM-Machine-Bulk-Cash-Deposit-Payment-Kiosk.html</li>
  <li>Alibaba listing, “Customized + US$1,800/unit”. The line does not say the adder is a naira template. https://www.alibaba.com/product-detail/Customized-SDK-Enabled-Cash-POS-Self_1601385352394.html</li>
  <li>TradeIndia, Capital Business Systems Pvt. Ltd., automated cash deposit machine, ₹150,000–600,000, Indian rupees, cash deposit. https://www.tradeindia.com/products/automated-self-service-banking-cash-deposit-machine-7467245.html</li>
  <li>Reserve Bank of India home page, FBIL reference rate, INR 96.6149 per US dollar at 1:00pm on 9 October 2026. https://www.rbi.org.in/</li>
  <li>DTFU Logistics, Shenzhen to Nigeria 20-foot port-to-port, US$2,970–3,450. Used also as a stand-in for the Indian shipment. https://www.dtfulogistics.com/news/20ft-and-40ft-shipping-from-china-to-nigeria/</li>
  <li>HS Code DB, heading 8471.60, representative Nigeria rate 5%. Not a customs ruling. https://hscodedb.com/ng/hs-code/8471-60/</li>
  <li>LawGlobal Hub, Nigeria Tax Act 2025, section 148, VAT at 7.5%. https://www.lawglobalhub.com/section-148-nigeria-tax-act-2025/</li>
  <li>Standards Organisation of Nigeria, SONCAP FAQ. Product certificate US$500 and SONCAP certificate US$350. https://son.gov.ng/soncap-faq/</li>
  <li>Dantful, terminal handling ₦250,000–₦450,000 a container and clearing ₦150,000–₦350,000. https://www.dantful.com/how-much-is-shipping-from-china-to-nigeria/</li>
  <li>NIBSS, May 2024 sandbox note. Device ₦250,000 and application ₦250,000. https://nibss-plc.com.ng/wp-content/uploads/2024/05/Step-By-Step-Certification-process-on-Sandbox-for-use-updated.pdf</li>
  <li>VTpass, commission rates, terminal-agent column, read 9 October 2026. MTN airtime 3.00%. Ikeja Electric, others, 1.00% capped at ₦1,500. https://vtpass.com/commissions</li>
  <li>Nairametrics, 19 January 2026. ATM withdrawals ₦36.34 trillion and 858.80 million transactions in the first half of 2025. https://nairametrics.com/2026/01/19/atm-transactions-surge-to-n36-34trn-in-six-months-despite-fresh-fees/</li>
  <li>Central Bank of Nigeria, payment modes, active ATMs in the first half of 2024, 16,714. https://www.cbn.gov.ng/PaymentsSystem/modes.html</li>
  <li>Central Bank of Nigeria, monetary-policy decisions, 307th meeting, policy rate 23%. https://www.cbn.gov.ng/MonetaryPolicy/decisions.html</li>
  <li>New Telegraph, deployed POS terminals 5.90 million at end-March 2025. https://newtelegraphng.com/nibss-more-nigerians-embrace-pos-as-deployed-terminals-up-119-4-to-5-90m/</li>
</ol>
<p class="small">End of study. Earlier CashEase papers on this branch are unchanged.</p>
"""

    head = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CashEase Nigeria: Bank-Sponsored Multi-Service Machine Network Feasibility Study</title>
<style>
@page {
  size: A4;
  margin: 14mm 13mm 16mm 13mm;
  @bottom-center {
    content: "CashEase Nigeria · Bank-sponsored multi-service machines · October 2026";
    font-family: "Liberation Sans", Arial, sans-serif;
    font-size: 8pt;
    color: #5c6b73;
  }
}
* { box-sizing: border-box; }
html { font-size: 10.5pt; }
body { margin: 0; color: #1a242b; font-family: "Liberation Serif", "Times New Roman", serif; line-height: 1.45; }
h1, h2, h3 { font-family: "Liberation Sans", Arial, sans-serif; color: #1c3144; line-height: 1.2; }
h1 { font-size: 20pt; margin: 0 0 8px; }
h2 { font-size: 13.5pt; margin: 16px 0 6px; page-break-after: avoid; border-bottom: 1px solid #d5d0c8; padding-bottom: 3px; }
p { margin: 0 0 8px; }
ul, ol { margin: 4px 0 10px; padding-left: 18px; }
li { margin: 0 0 4px; }
.cover { page-break-after: always; padding-top: 8mm; }
.kicker { font-family: "Liberation Sans", Arial, sans-serif; letter-spacing: 0.12em; text-transform: uppercase; font-size: 9pt; color: #8a6a2f; margin-bottom: 10px; }
.sub { font-size: 11.5pt; color: #1c3144; }
.verdict { background: #f4f1ea; border-left: 4px solid #8a6a2f; padding: 8px 12px; margin: 12px 0; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.5pt; page-break-inside: auto; }
table.keep { page-break-inside: avoid; }
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
.footer { display: none; }
</style>
</head>
<body>
"""
    html_path = ROOT / "source" / "study.html"
    pdf_path = ROOT / PDF_NAME
    html_path.write_text(head + body + "\n</body>\n</html>\n", encoding="utf-8")
    # The low-band table header in section 5 dropped the withdrawal column alignment.
    # Rows were built as split + metrics and then sliced. Check by rendering.
    proc = subprocess.Popen(
        [
            "google-chrome",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--user-data-dir=/tmp/chrome-cashease-v5",
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
