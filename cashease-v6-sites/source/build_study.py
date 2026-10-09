#!/usr/bin/env python3
"""Nationwide site-partnership study. Does not rewrite v3, v4 or v5."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(ROOT / "source"))

from charts import draw  # noqa: E402
from site_model import main  # noqa: E402

PDF_NAME = "CashEase_Nationwide_Site_Partnership_Feasibility.pdf"


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


def table(headers, rows, caption) -> str:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return (
        f"<table class='tight'><caption>{caption}</caption>"
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
    )


def build() -> None:
    r = main()
    draw(r, ROOT / "charts")
    be = r["be"]["70/30"]
    m = r["machines"]["70/30"]
    zones = []
    for name, z in r["meman"].items():
        zones.append([name, f"{z['stations']:,}", z["lead"]])

    body = f"""
<div class="cover">
  <p class="kicker">Feasibility study · October 2026</p>
  <h1>CashEase Nigeria: Nationwide Site-Partnership Feasibility Study (Motor Parks, Markets, Malls, Filling Stations, Supermarkets)</h1>
  <p class="sub">Filling stations and malls are tested as busy sites. The published traffic can clear a machine only if the withdrawals are other banks’ cards and the machine actually gets them. No site file shows that yet.</p>
  <div class="verdict">
    <p><strong>Verdict.</strong> Do not roll out by site type. Filling stations and malls are the right places to measure, and they are the wrong places to assume. A high-band recycler at a 70/30 split still needs about 61 withdrawals a day to cover cash costs and about 97 to cover full cost. The average existing Nigerian ATM does about 284 withdrawals a day, so a site that already behaves like that average has the traffic. A new machine gets the ₦500 only on other banks’ cards, and malls and many stations already have a bank ATM. Parks and markets have no national count. The human change point is the only small cheque, and its rent and union levy were not found. Cash-in kiosks still do not pay.</p>
  </div>
</div>

<h2>1. What is being tested</h2>
<p>The founder’s view is that filling stations and malls are high-traffic, and that they should be tested rather than waved away. This paper does that. It keeps the v5 machine. The high band lands at {short(r['high_all_in'])}. The cheaper China band lands at {short(r['low_all_in'])}. Deployer income is the off-site surcharge, at most ₦500 per ₦20,000 block. The ₦100 is not CashEase income. At a 70/30 split the high band covers cash costs at {be['cash']:.0f} withdrawals a day and full cost at {be['full']:.0f}. The 100/0 full-cost line is {r['be']['100/0']['full']:.0f}. The 50/50 line is {r['be']['50/50']['full']:.0f}. Those thresholds do not change because the forecourt is a filling station. Only the number of paying withdrawals changes.</p>
<p>Two other formats are priced for sites that cannot carry a {short(r['high_all_in'])} machine. A cash-in kiosk has no surcharge. On the labelled VTpass stack from v5 it takes in {short(r['kiosk_revenue'])} a year and loses {short(abs(r['kiosk_cash']))} of cash against street costs of {short(r['kiosk_street'])}. A human change point uses the brief’s franchise fee of ₦150,000 to ₦300,000 and a 70/20/10 split. This paper assigns 70% to the attendant, 20% to CashEase and 10% to the host. That assignment is a reading of the brief, not a contract that was found. The change fee is the ₦100 assumption from the earlier studies. It is not a CBN charge.</p>
<p>No published series gives withdrawals per day at a Nigerian filling station, mall, supermarket, motor park or market. The paper therefore does not say how many sites clear. It says what would have to be true, and where a ten-machine count could find out.</p>

<h2>2. How many sites exist</h2>
<p><strong>Filling stations.</strong> NMDPRA’s 2025 downstream fact sheet puts registered retail outlets at approximately 22,681, with 256 product depots and more than 25,000 tanker trucks.<sup>1,2</sup> IPMAN’s depot chairmen said in April 2024 that the association’s members operate over 30,000 stations.<sup>3</sup> Those two figures are not added. The regulator’s count is the one used as the national stock. DAPPMAN is a depot association. The depot count is 256, not a retail-station count.</p>
<p>MEMAN’s 2024 member data, which is a subset, counts 3,293 retail fuel stations and gives the only zone split found.<sup>4</sup></p>
{table(
    ["Zone", "MEMAN member stations", "Largest state in that zone"],
    zones,
    "MEMAN members, 2024. This is not the NMDPRA total of about 22,681, and it is not a list of stations without an ATM.",
)}
<p>Company counts that could be tied to a filing or a named official: TotalEnergies Marketing Nigeria’s 2025 financial statements say the retail business has a network of 511 service stations.<sup>5</sup> MRS Oil Nigeria’s 2024 annual report says about 140 company-owned outlets and about 264 third-party outlets.<sup>6</sup> Mele Kyari told a House committee in September 2023 that NNPC Retail was in control of over 900 fuel stations, and that before the OVH deal the company owned 48 stations plus affiliates.<sup>7</sup> The 2022 announcement of the OVH deal said the purchase would add over 380 stations in Nigeria and Togo, on a journey toward 1,500. The 1,500 figure is a target.<sup>8</sup> Ardova and Conoil appear in secondary pieces with counts that do not match each other. Those counts are not used. NIPCO’s profile in the MEMAN report says about 250 branded outlets.<sup>4</sup></p>
<p><strong>Malls.</strong> No national census of shopping malls was found. ICSC was searched and did not yield a Nigeria mall total that this paper will treat as official. Named centres, not a population, include Ikeja City Mall, The Palms, Novare Lekki, Jabi Lake Mall and others that turn up in landlord and press descriptions. Ikeja City Mall’s own description says it has bank ATMs.<sup>9</sup></p>
<p><strong>Supermarkets.</strong> Nairametrics on 30 March 2025 ranked chains by store counts it said were on company websites: Bokku 124, Addide 44, Market Square 36, Justrite 31, Shoprite 26, FoodCo 22, Jendol 14, Spar 13, Roban 9, Prince Ebeano 8.<sup>10</sup> The ten sum to {r['chains_top10']}. Prince Ebeano’s eight stores were in Abuja and Lagos. A separate Ebeano count was not in that ranking. A July 2026 Nairametrics piece says Justrite has up to 40 stores, Market Square more than 40, Prince Ebeano 9, and Bokku over 150, and it says Bokku’s ownership could not be confirmed.<sup>11</sup> The March ranking is the one used as a stock. Premium Times describes Shoprite closures in Kano, Abuja, Ibadan and Ilorin, so 26 is not a live operating count.<sup>12</sup> This is a chain list, not every supermarket in Nigeria.</p>
<p><strong>Motor parks.</strong> No national census was found. Lagos State’s commissioner for transportation said in November 2024 that the state had 30 parks in its book and well over 100 that had not been regulated, and that well over 6,000 people come into Lagos daily.<sup>13</sup> A 2017 survey cited by PPIAF and LAMATA identified 145 inter-state bus parks in Lagos across 39 areas, including Ojota 6, Jibowu 8, Mile 2 8 and Ojuelegba 6.<sup>14</sup> Utako is in Abuja. No count for Utako was found. LASPARK is the Lagos parks-and-gardens agency. It is not the motor-park register. An older academic interview put NURTW in Lagos at 220 branches, with ten to twenty units in a branch, each running a park. That is an interview, not a register, and it is not multiplied into a national total.<sup>15</sup></p>
<p><strong>Markets.</strong> No national or state census of markets was found. Balogun, Alaba, Computer Village, Onitsha Main Market, Ariaria, Kurmi, Kantin Kwari, Wuse and Bodija are real places. None of them came with a published trader count or a published footfall in the sources read for this paper. They are not given a number.</p>

<h2>3. Footfall, and what it does not prove</h2>
<p>The stock of active ATMs in the first half of 2024 was 16,714.<sup>16</sup> ATM withdrawals in the first half of 2025 were ₦36.34 trillion and 858.80 million transactions.<sup>17</sup> Dividing the transactions by 181 days, the length of 1 January to 30 June, and then by 16,714 machines, gives about {r['per_atm_withdrawals']:.0f} withdrawals a day on the average existing ATM. The two published totals also imply an average ticket of about {short(r['avg_ticket'])}. The 181-day divisor and the mixing of a 2024 machine stock with 2025 volume are labelled. The average is real enough to test the founder’s claim. It is not a count at a filling station.</p>
<img src="../charts/fig_hurdle.png" alt="Full-cost withdrawal hurdle beside the national average ATM"/>
<p>At 70/30, full cost on the high band is {be['full']:.0f} withdrawals a day. That is about {be['share_of_avg_atm_full']*100:.0f}% of the national average. If a new machine captured a whole average ATM’s traffic, and about one in three of those withdrawals paid the ₦500 cap, the hurdle would be met. On-us withdrawals pay nothing to the deployer. The ₦100 never does. A station or a mall that already has the landlord bank’s ATM will send that bank’s cards through as on-us. The average of 284 is therefore an upper picture of traffic, not a forecast of CashEase income.</p>
<p>Ikeja City Mall is the one mall with a published shopper figure from a party that owned it. Actis, which exited in 2015, said the mall attracts up to 800,000 shoppers a month, and that opening day in December 2011 was 45,000 visitors.<sup>18</sup> Spreading 800,000 over an assumed 30-day month is about {r['mall_visitors_day']:,.0f} people a day. Full-cost break-even at 70/30 is one withdrawal for every {be['mall_visitors_per_withdrawal_full']:.0f} of those visitors, or {be['mall_conversion_full']*100:.2f}%. A 2019 exhibition rate card, reproduced on a document site rather than by the mall, says an average of 655,000 shoppers a month.<sup>19</sup> A 2025 advertising blog says over 35,000 visitors a week.<sup>20</sup> The three figures do not agree. The Actis figure is the one used in the arithmetic because it is the owner’s, and it is old. Even on that old high figure, the machine works only if roughly four in a thousand visitors take cash from this machine, at the cap, on another bank’s card. No mall ATM report was found to show whether that happens. Ikeja already advertises bank ATMs inside the building.<sup>9</sup></p>
<p>No vehicles-per-day figure for Nigerian filling stations was found. The founder’s belief that stations are busy is not contradicted by a census, because the census of vehicles was not published. It is also not confirmed. EFInA’s 2023 access survey does say something about cash in general. Among bank users, cash deposits and withdrawals are among the main transactions for 95%. Cash was still how 87% of adults mainly received income, up from 85% in 2020. And 97% of adults used cash to pay for goods and services.<sup>21</sup> The survey does not split those answers into malls, stations, parks or markets. NIBSS and CBN publish channel totals, not site types. Deployed POS terminals were 5.90 million at the end of March 2025.<sup>22</sup> A busy-agent blog anecdote of 80 to 100 transactions a day is not a NIBSS mean.<sup>23</sup></p>

<h2>4. Who is already there, and on what terms</h2>
<p>Bank ATMs are already a stated feature of Ikeja City Mall. Large malls are where banks put machines because the landlord can offer power, security and a crowd. A second machine is competing with that gallery. If the gallery is the cash-providing bank’s own machine, that bank’s customers are on-us and the ₦500 does not arise. The off-site cap applies to a machine that is not on a bank’s premises. A mall is off the bank’s premises. It is not an empty site.</p>
<p>Filling stations are the same shape of problem at forecourt scale. Total, NNPC Retail and MRS already operate hundreds of outlets. Many bank programmes put ATMs on dealer forecourts. A published count of those ATMs was not found, so this paper does not invent a share. The planning point is the one that can be checked on a visit: if a station already has a bank ATM, CashEase is the second machine.</p>
<p>POS agents are everywhere the 5.90 million terminals reach, including the shops inside stations and the stalls in markets. They take transfers and cash-out under the agent rules. A machine cannot be filed as an agent. Counsel on the October 2025 guidelines say non-human machines are barred as agents.<sup>24</sup> A human change point can be a person. A recycler cannot.</p>
<p>Host money is the gap. No Nigerian ATM host-rent tariff, and no revenue-share percent for a mall landlord or a station dealer, was found. v5’s rent assumption of ₦1.80 million a year sits inside the high-band street cost of {short(r['high_street'])} and is not a quote from Ikeja or from NNPC Retail. NURTW’s Lagos role, in the interview cited above, is collecting dues from drivers and negotiating with other actors in the park. A levy on a change booth was not stated. The 10% host share in the human-point arithmetic is the brief, not that interview.</p>

<h2>5. Unit economics by format</h2>
<p>The machine rows are the v5 high band. They are the same at a station, a mall, a park or a market. Site type does not change depreciation. Street cost is {short(r['high_street'])}. Full cost is {short(r['high_full'])}. The bank carries cash and cash-in-transit, as in v5. Effective days are 270. One withdrawal is one ₦20,000 block at the ₦500 cap, and every withdrawal pays.</p>
{table(
    ["Split", "Withdrawals a day", "Cash profit", "IRR", "Payback", "NPV at 28%"],
    [
        ["70/30", "60", short(m["60"]["cash"]), irr_s(m["60"]["irr"]), pb_s(m["60"]["payback"]), short(m["60"]["npv"])],
        ["70/30", "120", short(m["120"]["cash"]), irr_s(m["120"]["irr"]), pb_s(m["120"]["payback"]), short(m["120"]["npv"])],
        ["70/30", "200", short(m["200"]["cash"]), irr_s(m["200"]["irr"]), pb_s(m["200"]["payback"]), short(m["200"]["npv"])],
        ["100/0", "120", short(r["machines"]["100/0"]["120"]["cash"]), irr_s(r["machines"]["100/0"]["120"]["irr"]), pb_s(r["machines"]["100/0"]["120"]["payback"]), short(r["machines"]["100/0"]["120"]["npv"])],
        ["50/50", "200", short(r["machines"]["50/50"]["200"]["cash"]), irr_s(r["machines"]["50/50"]["200"]["irr"]), pb_s(r["machines"]["50/50"]["200"]["payback"]), short(r["machines"]["50/50"]["200"]["npv"])],
    ],
    "High-band recycler, surcharge only. 120 a day at 70/30 is the base. It makes cash and still misses 28%.",
)}
<p>The cheaper band, {short(r['low_all_in'])}, has a 70/30 full-cost break-even of {r['be']['70/30']['low_full']:.0f} withdrawals a day. At 120 a day that band cleared 28% in v5. The listing range is wide enough that the invoice decides the base case. This paper still plans on the high band until a proforma says otherwise.</p>
<p>The human point, at a ₦100 change fee, pays the attendant {short(r['humans']['60']['attendant'])} a year at 60 transactions a day, {short(r['humans']['120']['attendant'])} at 120, and {short(r['humans']['200']['attendant'])} at 200. CashEase’s 20% is {short(r['humans']['60']['cashease'])}, {short(r['humans']['120']['cashease'])} and {short(r['humans']['200']['cashease'])}. The host’s 10% is a tenth of the gross. If the franchise fee is income to CashEase and CashEase buys nothing else, the present value of one booth is positive. That result leaves out rent, float, union dues and the ₦25 million office. Ten booths at 120 transactions a day give CashEase {short(10 * r['humans']['120']['cashease'])} a year before the office. The office assumption is ₦25 million. The booths do not carry it. Whether the attendant can pay for a pitch out of {short(r['humans']['120']['attendant'])} is not knowable until a park names the rent.</p>
<p>The kiosk does not get a different answer in a mall or a market. Its income is commissions, not the surcharge. The loss of {short(abs(r['kiosk_cash']))} a year is the v5 high-band kiosk on the labelled stack. Footfall does not fix a format that does not sell withdrawals.</p>

<h2>6. How many sites clear</h2>
<p>None have been counted, because none have been measured. The national stocks are not a pass list.</p>
<ul>
  <li>Filling stations. About 22,681 registered outlets is the regulator’s stock. MEMAN’s 3,293 are the zoned subset. Zero of them have a published not-on-us withdrawal count. A station clears the high-band 70/30 hurdle only if this machine, not the bank ATM already on the forecourt, does about 97 paying withdrawals a day.</li>
  <li>Malls. No national total. Ikeja’s old “up to 800,000 a month” makes 97 withdrawals a small share of the crowd, and the mall already has bank ATMs. Other malls were not given a shopper figure.</li>
  <li>Supermarkets. {r['chains_top10']} stores in one March 2025 top ten, many of them small Bokku and Addide outlets. A {short(r['high_all_in'])} machine is not a corner-shop asset. Large Justrite, Market Square, Shoprite and Spar stores are mall-like and were not given separate footfall.</li>
  <li>Parks. Lagos has 30 registered interstate parks and well over 100 unregulated. The 2017 survey’s 145 is an older Lagos inter-state count, not a second universe to add. No park has a withdrawal count. The commissioner’s “well over 6,000” people a day is arrivals into Lagos, not cash taken out of a machine.</li>
  <li>Markets. No denominator, so no pass count.</li>
</ul>
<p>By zone, the only honest split is MEMAN’s station map. The South West has 1,392 member stations, 722 of them in Lagos. The North Central has 529, 200 of them in Abuja. The North East has 274. MEMAN’s own text offers security and lower activity as a possible reason for the thin northern and eastern counts. That is a reason to measure in Lagos and Abuja first. It is not a finding that a Kano station fails the hurdle. Kano was not measured.</p>

<h2>7. Format, sequence, money</h2>
{table(
    ["Site", "Format to test", "Format to leave"],
    [
        ["Filling station", "One recycler, only where no bank ATM is already dispensing", "Kiosk. Human booth on a fuel forecourt."],
        ["Mall", "One recycler if the lease allows a second, off-site machine", "A chain order. A kiosk beside the bank gallery."],
        ["Large supermarket", "Treat as a mall", "A recycler in a small mart."],
        ["Small supermarket", "Nothing until a change-fee test works elsewhere", "A ₦23 million machine."],
        ["Motor park", "Human change point, attendant keeps 70%", "A recycler, until a park count clears 97."],
        ["Market", "Same human point, after the park test", "A recycler or a kiosk on an uncounted site."],
    ],
    "Recommendation from the evidence in this paper. It is not a concession map.",
)}
<p>The sequence is a measurement, not a map of 22,681 forecourts. Month-one candidates are filling stations in Lagos and Abuja that a visit shows do not already have a bank ATM, plus one or two malls whose landlord will say in writing whether an ATM exclusivity exists. Parks come in as human booths, not as machines. Markets wait. The North East waits. Supermarket chains are not a year-one landlord.</p>
<p>The measurement set priced here is 12 high-band recyclers: ten stations and two malls. Capex is {short(r['test_fleet_12']['120']['capex'])}. Year 0, including the opening-office assumption, is {short(r['test_fleet_12']['120']['year0'])}. At 70/30 and 60 withdrawals the fleet’s annual cash is {short(r['test_fleet_12']['60']['annual'])} and the value at 28% is {short(r['test_fleet_12']['60']['npv'])}. At 120, annual cash is {short(r['test_fleet_12']['120']['annual'])}, the return is {irr_s(r['test_fleet_12']['120']['irr'])}, and the value is {short(r['test_fleet_12']['120']['npv'])}. At 200, the return is {irr_s(r['test_fleet_12']['200']['irr'])} and the value is {short(r['test_fleet_12']['200']['npv'])}. The set is worth buying only if the count is expected to land near 200 other-bank withdrawals, or the invoice comes in at the low band and the count lands near 120. It is not worth buying to discover a 60.</p>
<p>Funding for those 12 machines is equity, unless the sponsor bank pays half the invoice and still supplies the cash. v5 showed that halving the cheque on a 70/30 split at 120 withdrawals lifts the return and still leaves it under 28%. Franchisee capital fits the human booth, where the cheque is ₦150,000 to ₦300,000, and does not fit the recycler. No vendor rate was found. A ₦50 billion network is not a result of these site stocks.</p>

<h2>8. Security, cash, power, rules</h2>
<p><strong>Stations.</strong> Licence conditions described from the old DPR site rules include a pump at least 15 metres from the road edge, at least 400 metres between stations, a standby generator, and fire equipment.<sup>25</sup> Those rules govern the station. They do not grant or refuse an ATM. No NMDPRA sentence was found that places a cash machine inside or outside the hazardous area. A recycler full of notes, next to fuel, is a theft and fire problem the model’s ₦1.44 million security assumption does not price. The generator is a reason uptime may be better than at a park. It is not a reason to delete the power cost until the dealer agrees to supply it.</p>
<p><strong>Malls.</strong> The binding document is the landlord’s lease: rent, service charge, ATM exclusivity, and who insures the machine. None of those clauses was published for Ikeja or for any other mall. Power and guards are why malls are operable. They are also why a bank is often already there.</p>
<p><strong>Parks.</strong> Lagos is accrediting interstate parks and said the unions were in the room. The public-transport owners’ representative said the union had not reached a consensus.<sup>13</sup> A booth that the union has not accepted does not get a queue. Cash-in-transit at an open park is harder than at a mall. The human format keeps less cash in a machine and more cash in a person’s hands, which is a different theft risk, not a smaller one.</p>
<p><strong>Markets.</strong> The same union and theft issues, plus no landlord who can sign for the whole market. A single stall is a host. The rest of the market is not a contract.</p>
<p><strong>Rules that apply everywhere.</strong> A recycler is an off-site ATM of the sponsor bank, or it is an independent deployment with prior written CBN approval and a bank that provides the cash.<sup>26</sup> It is not an agent. The surcharge cap can be revised. EFInA’s cash findings say people still pay in cash. They do not say they will pay ₦500 to a new machine when a bank ATM or a POS agent is ten steps away.</p>

<h2>9. Verdict on each site, including stations and malls</h2>
<p><strong>Filling stations.</strong> The founder is right that this is a high-traffic candidate, and right that it should be tested. The regulator counts about 22,681 outlets, the major brands already cover hundreds to about 900, and the average existing ATM in the country does about 284 withdrawals a day, which is enough traffic to clear a {short(r['high_all_in'])} machine if enough of those withdrawals pay the cap. The founder is not yet right that the stations are a network. No station was shown to be free of a bank ATM, and no station was shown to deliver 97 other-bank withdrawals to a new deployer. Ordering for the 22,681 would be the opposite of a fair test.</p>
<p><strong>Malls.</strong> The founder is right that a crowd the size Actis described at Ikeja can spare 97 withdrawals without anyone noticing. Four in a thousand of that old monthly figure would do it. The founder is not yet right that malls are open sites. The published description of Ikeja includes bank ATMs, the shopper figures disagree with each other by a wide margin, and no national mall list exists. One or two malls are a fair test. A mall strategy is not.</p>
<p><strong>Supermarkets.</strong> Large stores are malls in smaller clothes and get the same answer. The hundreds of small chain outlets in the March 2025 ranking do not get a recycler. They also do not get a kiosk on the commission maths.</p>
<p><strong>Motor parks.</strong> Cash is plausible and unmeasured. The format that matches the evidence is a human booth with a small fee, in Lagos, where a register exists and the state is already forcing parks into accreditation. A recycler at Ojota or Ojuelegba is a guess.</p>
<p><strong>Markets.</strong> Same as parks, with less paper. Do not start there.</p>

<h2>10. Gates and twelve months</h2>
<p>Gate 1. The sponsor bank confirms in writing that a forecourt and a mall shop floor are off-site, that the bank will supply cash, and what happens to the bank’s own cards. If those cards are free, the test has to count only other banks.</p>
<p>Gate 2. A visit sheet for candidate stations: bank ATM already there or not, generator or not, dealer willing to host, and a rent or revenue share written down. Drop any station that already dispenses for a bank.</p>
<p>Gate 3. One mall landlord letter on exclusivity and rent. If the letter says the anchor bank has the ATM right, that mall is closed.</p>
<p>Gate 4. A proforma under the high band. Ten station machines and two mall machines are the ceiling for the year, and only if Gates 1 to 3 are open. At 120 withdrawals and 70/30 those 12 machines still miss 28%. Buy them to measure, and stop the second order unless the count is near 200 on the high band or near 120 on a low-band invoice.</p>
<p>Gate 5. Human booths are a separate test. Ten attendants, Lagos parks that are in the state’s book, fee ₦150,000 to ₦300,000, split written as 70/20/10. Stop if the attendant cannot cover the pitch, or if the union blocks the booth. Do not add markets in this year.</p>
<p>The twelve months: counsel and the bank in month 1; station visits and one mall letter in month 2; proforma and NIBSS papers in months 3 and 4, and no shipment before the certificates the May 2024 NIBSS note requires; install in months 5 to 8; publish the weekly count of paying withdrawals; decide in months 9 to 12. A pass is a count above the full-cost line for the signed split. Anything else is a stop. Kiosks stay off the order.</p>

<h2>11. Workings</h2>
<p>High-band and low-band costs, the 270-day year, the ₦500 cap and the 28% hurdle are the v5 model, read from its results file and not rebuilt. Average withdrawals a day = 858,800,000 / 181 / 16,714. Average ticket = 36.34 trillion / 858.80 million. Ikeja daily crowd = 800,000 / 30. Conversion = full-cost break-even / that crowd.</p>
<p>Human gross = withdrawals stand-in, here called transactions, × 270 × 100. CashEase takes 20%. The attendant takes 70%. The host takes 10%. The twelve-machine year 0 uses the v5 office assumptions: 40,000,000 plus 150,000 a machine at the start, and 25,000,000 plus 50,000 a machine a year. Recompute from <span class="small">model/site_model.py</span>.</p>

<h2>12. Sources</h2>
<ol class="sources">
  <li>NMDPRA, state of the downstream sector fact sheet, Q1–Q3 2025. Retail outlets approximately 22,681. Depots 256. https://alps.blob.core.windows.net/nmdprawebsite/Statistics/Upload-80c82709-7f84-4cea-959e-668d6e6d030e.pdf</li>
  <li>Punch, 10 December 2025, reporting the same NMDPRA fact sheet. https://punchng.com/nigeria-has-22681-filling-stations-25000-tankers-fg/</li>
  <li>Punch, IPMAN depot chairmen, over 30,000 stations, April 2024. An association claim, not the regulator’s count. https://punchng.com/ipman-to-shutdown-30000-filling-stations-over-n200bn-debt/</li>
  <li>MEMAN, 2024 Nigeria Energy Downstream Industry Report. Member retail stations 3,293, with the zone figures used above. NIPCO profile, about 250 branded outlets. https://moman.org/wp-content/uploads/2025/05/2024-Nigeria-Energy-Downstream-Industry-Report.pdf</li>
  <li>TotalEnergies Marketing Nigeria Plc, financial statements filed March 2026. “A nationwide network of 511 service stations.” https://doclib.ngxgroup.com/Financial_NewsDocs/46402_TOTALENERGIES_MARKETING_NIGERIA_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MARCH_2026.pdf</li>
  <li>MRS Oil Nigeria Plc, annual report for the year ended 31 December 2024. About 140 company-owned outlets and about 264 third-party outlets. https://doclib.ngxgroup.com/Financial_NewsDocs/43459_MRS_OIL_NIGERIA_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2024_FINANCIAL_STATEMENTS_MARCH_2025.pdf</li>
  <li>New Telegraph, 15 September 2023. Mele Kyari, NNPC Retail over 900 stations; 48 owned before OVH. https://newtelegraphng.com/nnpc-now-owns-900-fuel-stations-across-nigeria-kyari/</li>
  <li>Daily Trust, NNPC Ltd on the OVH acquisition: over 380 additional stations in Nigeria and Togo, toward 1,500. https://dailytrust.com/just-in-nnpc-ltd-acquires-380-oando-stations-other-assets-nationwide/</li>
  <li>Ikeja City Mall company description: shops, cinema, and different bank ATMs. https://www.linkedin.com/company/ikeja-city-mall-lagos</li>
  <li>Nairametrics, 30 March 2025, top ten supermarket chains by store count from figures the paper said were on company websites. https://nairametrics.com/2025/03/30/top-10-supermarket-chains-in-nigeria-by-store-count-dominating-the-retail-sector/</li>
  <li>Nairametrics, 18 July 2026, later store counts, including figures the paper said it could not verify for Bokku. https://nairametrics.com/2026/07/18/meet-the-founders-behind-nigerias-largest-supermarket-chains/</li>
  <li>Premium Times, Shoprite Nigeria store closures. https://www.premiumtimesng.com/business/business-news/829675-shoprite-nigeria-struggling-under-new-owners-as-shelves-go-empty-stores-close.html</li>
  <li>ThisDay, 9 November 2024. Lagos commissioner: 30 parks in the book, 100 unregulated, well over 6,000 people into Lagos daily. https://www.thisdaylive.com/2024/11/09/lagos-to-digitalise-regulate-interstate-transport-services-upgrade-100-motor-parks/</li>
  <li>PPIAF mega-terminals assessment, Planet Projects survey, December 2017: 145 Lagos inter-state bus parks. https://www.ppiaf.org/sites/default/files/documents/2023-07/Mega_Terminals_Assessment_Report_112419.pdf</li>
  <li>IFRA Nigeria, interview with Laurent Fourchard on NURTW in Lagos: 220 branches. Not a register. https://ifra-nigeria.org/component/content/article/497-interview-with-laurent-fourchard-studying-the-sociology-of-nurtw-members</li>
  <li>Central Bank of Nigeria, payment modes, 16,714 active ATMs in the first half of 2024. https://www.cbn.gov.ng/PaymentsSystem/modes.html</li>
  <li>Nairametrics, 19 January 2026. ATM withdrawals ₦36.34 trillion and 858.80 million transactions in the first half of 2025. https://nairametrics.com/2026/01/19/atm-transactions-surge-to-n36-34trn-in-six-months-despite-fresh-fees/</li>
  <li>Actis, Ikeja City Mall. Up to 800,000 shoppers a month. Opening day 45,000. Exit 2015. https://www.act.is/about-us/portfolio/ikeja-city-mall/</li>
  <li>2019 Ikeja City Mall exhibition rate card, as posted on a document site: average 655,000 shoppers a month. Not the mall’s own current page. https://www.scribd.com/document/442375137/2019-ICM-RATE-CARD</li>
  <li>Media.co.uk blog, December 2025, updated July 2026: over 35,000 visitors a week. An advertising page, in conflict with the older owner figure. https://www.media.co.uk/blogs/blog/ikeja-city-mall-lagos-business-district-shopping-advertising</li>
  <li>EFInA, Access to Financial Services in Nigeria 2023 survey report. Cash deposits and withdrawals among main transactions for 95% of bank users. Income mainly in cash for 87% of adults. Cash used by 97% of adults to pay for goods and services. https://a2f.ng/wp-content/uploads/2024/07/A2F-2023-SURVEY-REPORT-1.pdf</li>
  <li>New Telegraph, deployed POS 5.90 million at end-March 2025. https://newtelegraphng.com/nibss-more-nigerians-embrace-pos-as-deployed-terminals-up-119-4-to-5-90m/</li>
  <li>Turnet Finance, 80 to 100 transactions a day. A blog anecdote, not a mean. https://turnetfinance.ng/moniepoint-review/</li>
  <li>G. Elias, note on the October 2025 agent guidelines, including the bar on non-human machines. https://www.gelias.com/images/Central_Bank_of_Nigeria_Guidelines_on_the_Operations_of_Agent_Banking.pdf</li>
  <li>TheNigeriaLawyer, summary of DPR filling-station site and licence conditions, including the 15-metre pump setback, the 400-metre separation, and a standby generator. https://thenigerialawyer.com/requirements-for-filling-fuel-stations-in-nigeria/</li>
  <li>Nairametrics, 14 March 2026. Independent ATM deployers need prior written CBN approval and a bank for cash. https://nairametrics.com/2026/03/14/cbn-mandates-one-atm-per-7500-payment-cards-by-2028/</li>
</ol>
<p class="small">End of study. The v3, v4 and v5 files are unchanged.</p>
"""

    head = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CashEase Nigeria: Nationwide Site-Partnership Feasibility Study (Motor Parks, Markets, Malls, Filling Stations, Supermarkets)</title>
<style>
@page {
  size: A4;
  margin: 14mm 13mm 16mm 13mm;
  @bottom-center {
    content: "CashEase Nigeria · Site partnerships · October 2026";
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
            "--user-data-dir=/tmp/chrome-cashease-v6",
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
