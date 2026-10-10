#!/usr/bin/env python3
"""China-machine redo of the path to 50 billion naira. Does not rewrite earlier studies."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(ROOT / "source"))

from charts import draw  # noqa: E402
from china_path import main  # noqa: E402

PDF_NAME = "CashEase_China_Machine_Path.pdf"


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


def pb(v) -> str:
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


def case_row(label, row) -> list[str]:
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


def unit_cells(row) -> list[str]:
    return [short(row["revenue"]), short(row["cash"]), irr_s(row["irr"]), pb(row["payback"]), short(row["npv"])]


def build() -> None:
    r = main()
    draw(r, ROOT / "charts")
    plain = r["boxes"]["hz4800_plain"]
    custom = r["boxes"]["hz4800_custom"]
    small = r["boxes"]["hz5500_custom"]
    high = r["boxes"]["high_band"]
    be = r["custom"]["be"]
    be_p = r["plain"]["be"]
    u = r["custom"]["units"]
    c = r["cases"]
    rec = c["custom_100_200"]["fleet"]
    t12, t100, t500, t_all = r["tranches"]
    sweep = r["reinvest"]
    p120 = r["proof_120"]
    cut = c["high_100_200"]["fleet"]["year0"] - rec["year0"]
    fewer = c["high_100_200"]["machines"] - c["custom_100_200"]["machines"]

    body = f"""
<div class="cover">
  <p class="kicker">Feasibility study · October 2026</p>
  <h1>CashEase Nigeria: The Path If the Machines Come from China</h1>
  <p class="sub">The machine is the Hongzhou cash in/out kiosk at the published 10-plus price of US$4,800, landed on the same sheet as the earlier papers. A naira-template stand-in of US$1,800 is still in the cheque until a proforma drops it.</p>
  <div class="verdict">
    <p><strong>The path.</strong> Order the China machine, not the US$7,850 listing. With the template stand-in it lands at {short(custom['all_in_ngn'])}. Keep the whole ₦500. Count 200 other-bank withdrawals a day. Open {c['custom_100_200']['machines']:,} of them. The cheque is {short(rec['year0'])}, cash profit is {short(rec['annual'])} a year, and the value at 28% is {short(rec['npv'])}. That is {pct(rec['share_of_national'])} of Nigeria’s recent daily ATM withdrawals. A 70/30 split at 120 a day still does not reach ₦50 billion. Twelve machines, at {short(t12['year0'])}, come before the cheque.</p>
  </div>
</div>

<h2>1. Which China price is being used</h2>
<p>Shenzhen Hongzhou’s own page prints US$5,500 for one to nine cash in/out kiosks and US$4,800 for ten or more. The page names a cash recycler. A second Hongzhou page says the firm customises denominations for Nigeria and quotes 30 to 35 working days. It prints no fee for that work. The only published per-unit “Customized” line found on a bill-recycler kiosk is US$1,800, and that listing does not say the line is a naira template. It stays in the working cheque as a stand-in. The US$3,650 floor of a different listing sits below this factory price. It is not used.</p>
<img src="../charts/fig_landed.png" alt="Landed cost of the China machine beside the high band"/>
{table(
    ["Invoice", "Ex-works", "Landed, first machine"],
    [
        ["US$4,800, ten or more, no adder", short(plain["exworks_ngn"]), short(plain["all_in_ngn"])],
        ["US$4,800 plus the US$1,800 stand-in", short(custom["exworks_ngn"]), short(custom["all_in_ngn"])],
        ["US$5,500, one to nine, plus the stand-in", short(small["exworks_ngn"]), short(small["all_in_ngn"])],
        ["Earlier high band, US$7,850 plus the stand-in", short(high["exworks_ngn"]), short(high["all_in_ngn"])],
    ],
    "High freight, ten kiosks to a container, 5% duty as a representative rate and not a customs ruling, VAT 7.5%, SON shared by the box, install and software ₦8 million, NIBSS ₦500,000 once.",
)}
<p>The working machine is the second row, {short(custom['all_in_ngn'])}. The first row, {short(plain['all_in_ngn'])}, is the invoice if Hongzhou’s Nigeria line is already inside the US$4,800. The one-to-nine price does not apply to a twelve-machine proof. Street cost on the working machine is {short(r['streets']['hz4800_custom'])} a year. Full cost, adding depreciation over seven years, is {short(r['fulls']['hz4800_custom'])}. The bank still carries the cash and the transit. Effective days are 270. One withdrawal is one ₦20,000 block at the ₦500 cap.</p>

<h2>2. What one machine earns</h2>
<p>At a 70/30 split the working machine covers cash costs at {be['70/30']['cash']:.0f} withdrawals a day and full cost at {be['70/30']['full']:.0f}. On the dearer band those lines were 61 and 97. Keeping the whole surcharge, the lines are {be['100/0']['cash']:.0f} and {be['100/0']['full']:.0f}. If the adder is not on the invoice, the 70/30 lines are {be_p['70/30']['cash']:.0f} and {be_p['70/30']['full']:.0f}. China moves the hurdle down. It does not remove it.</p>
{table(
    ["Split", "Withdrawals a day", "Revenue", "Cash profit", "Return", "Payback", "Value at 28%"],
    [
        ["Keep all", "60", *unit_cells(u["100/0"]["60"])],
        ["Keep all", "120", *unit_cells(u["100/0"]["120"])],
        ["Keep all", "200", *unit_cells(u["100/0"]["200"])],
        ["Bank takes 30%", "60", *unit_cells(u["70/30"]["60"])],
        ["Bank takes 30%", "120", *unit_cells(u["70/30"]["120"])],
        ["Bank takes 30%", "200", *unit_cells(u["70/30"]["200"])],
    ],
    "One Hongzhou machine at US$4,800 plus the US$1,800 stand-in. Cash profit is after street cost. The value is of that one machine, with no head office.",
)}
<p>Keeping the whole surcharge, 120 a day now clears 28%: the return is {irr_s(u['100/0']['120']['irr'])} and the value is {short(u['100/0']['120']['npv'])}. Giving the bank 30% at 120 a day earns {irr_s(u['70/30']['120']['irr'])} and the value is still {short(u['70/30']['120']['npv'])}. China does not make that split clear the hurdle. At 200 a day the 70/30 machine does clear it, at {irr_s(u['70/30']['200']['irr'])}.</p>

<h2>3. The fleet that is worth ₦50 billion</h2>
<img src="../charts/fig_fleets.png" alt="China fleets that reach 50 billion naira"/>
{table(
    ["Plan", "Machines", "Opening cheque", "Cash profit a year", "Share of ATM withdrawals", "Return"],
    [
        case_row("US$4,800 plain, 200 a day, keep all", c["plain_100_200"]),
        case_row("US$4,800 plus adder, 200 a day, keep all", c["custom_100_200"]),
        case_row("High band, 200 a day, keep all", c["high_100_200"]),
        case_row("US$4,800 plus adder, 120 a day, keep all", c["custom_100_120"]),
        case_row("US$4,800 plus adder, 200 a day, bank takes 30%", c["custom_70_200"]),
        case_row("US$4,800 plus adder, 120 a day, bank takes 30%", c["custom_70_120"]),
        case_row("US$4,800 plus adder, 200 a day, split 50/50", c["custom_50_200"]),
    ],
    "Smallest opening fleet whose value at 28%, after the cheque and the office, clears ₦50 billion. Share is of 858.80 million ATM withdrawals in the first half of 2025, over 181 days.",
)}
<p>The plan this paper will walk is the second row. {c['custom_100_200']['machines']:,} machines, cheque {short(rec['year0'])}, cash profit {short(rec['annual'])} a year, value {short(rec['npv'])}, return {irr_s(rec['irr'])}, payback {pb(rec['payback'])}. The withdrawals are {pct(rec['share_of_national'])} of the national daily total. The dearer band needed {c['high_100_200']['machines']:,} machines and {short(c['high_100_200']['fleet']['year0'])}. China cuts the cheque by {short(cut)} and the fleet by {fewer:,} machines. It does not cut the 200 withdrawals.</p>
<p>If the proforma has no adder, the same plan is {c['plain_100_200']['machines']:,} machines and {short(c['plain_100_200']['fleet']['year0'])}. Use that cheque the day the invoice says the naira template is inside the US$4,800.</p>
<p>A 70/30 split at 120 a day does not reach ₦50 billion at any fleet up to 40,000. Giving the bank 30% and doing 200 a day does reach, at {c['custom_70_200']['machines']:,} machines, a cheque of {short(c['custom_70_200']['fleet']['year0'])}, and {pct(c['custom_70_200']['fleet']['share_of_national'])} of national withdrawals. A 50/50 split reaches only by taking {pct(c['custom_50_200']['fleet']['share_of_national'])} of the country’s ATM withdrawals. That row is not a plan.</p>

<h2>4. How the cheque is staged</h2>
{table(
    ["Opening fleet", "Cheque", "Cash profit a year", "Value at 28%", "Return"],
    [
        [f"{t12['n']:,}", short(t12["year0"]), short(t12["annual"]), short(t12["npv"]), irr_s(t12["irr"])],
        [f"{t100['n']:,}", short(t100["year0"]), short(t100["annual"]), short(t100["npv"]), irr_s(t100["irr"])],
        [f"{t500['n']:,}", short(t500["year0"]), short(t500["annual"]), short(t500["npv"]), irr_s(t500["irr"])],
        [f"{t_all['n']:,}", short(t_all["year0"]), short(t_all["annual"]), short(t_all["npv"]), irr_s(t_all["irr"])],
    ],
    "Each row is bought at the start and run for seven years at 200 paying withdrawals, on the US$4,800 plus US$1,800 machine.",
)}
<p>Twelve machines are the proof: cheque {short(t12['year0'])}. If they do 200 a day the value is {short(t12['npv'])} and the return is {irr_s(t12['irr'])}. If they do only 120, and CashEase still keeps the whole surcharge, the same twelve are worth {short(p120['npv'])} and earn {irr_s(p120['irr'])}. That twelve-machine result is a business. Ordering the {c['custom_100_120']['machines']:,} machines that 120 a day needs for a ₦50 billion value would be {pct(c['custom_100_120']['fleet']['share_of_national'])} of national withdrawals. This paper does not walk that order.</p>
<p>Sweeping every naira of profit into the next machine, with no new equity, grows the twelve to {sweep['end']:,} by year 7. The value of that sweep on a fixed seven-year clock, with nothing left to sell at the end, is {short(sweep['npv'])}. The late machines do not earn their cost. The ₦50 billion comes from buying the {c['custom_100_200']['machines']:,} early, after the count.</p>

<h2>5. What does not change because the box is Chinese</h2>
<p>No forecourt has published 200 other-bank withdrawals. The rate is what this value needs. The machines still go on filling stations a visit shows are empty of a bank ATM. NMDPRA’s 22,681 outlets can hold {c['custom_100_200']['machines']:,} of them. MEMAN’s South West members alone are 1,392. Malls stay a two-site test. Parks and markets stay off the machine order.</p>
<p>The bank still has to give up the surcharge. Branding that makes the sponsor’s own cards free removes the ₦500 on those cards. The 200 in this plan are paying withdrawals. Whether a third-party machine counts toward the issuer’s one-ATM-per-7,500-cards duty is still a question for counsel. The existing 16,714 ATMs already cover 125.4 million cards at that ratio.</p>
<p>NIBSS, SON and a CBN approval are still a cost and a wait. The Hongzhou page’s EMV and PCI sentences are a manufacturer’s description, not a certificate NIBSS has issued. Duty at 5% is a representative rate, not a Nigeria Customs ruling. Ten kiosks in a container is an assumption. Cash-in kiosks on the commission stack still lose about ₦2.29 million a year. Human booths still need about 22,700 pitches at 120 changes a day to be worth ₦50 billion.</p>

<h2>6. Twelve months</h2>
<p>Month 1. The term sheet asks for 100% of the surcharge, the bank carrying cash and transit. A 70/30 sheet is the fallback only if the count is aimed at 200 a day and the raise can cover {short(c['custom_70_200']['fleet']['year0'])}. A 50/50 sheet is refused.</p>
<p>Month 2. Visit empty forecourts in Lagos and Abuja, plus one mall letter on ATM exclusivity.</p>
<p>Months 3 and 4. A Hongzhou proforma at the ten-plus price, with the naira template either inside the US$4,800 or priced as a line. No shipment before the NIBSS certificates. Do not average this invoice with the US$7,850 listing.</p>
<p>Months 5 to 8. Install 12 machines. Cheque {short(t12['year0'])}. Publish paying withdrawals each week, apart from the sponsor’s own cards.</p>
<p>Months 9 to 12. A median of 200 opens the raise, first toward 100 machines, then 500, then {c['custom_100_200']['machines']:,} only when the money is in. A median of 120 keeps the twelve and stops the ₦50 billion order. Below the full-cost line of the signed split, stop.</p>

<h2>7. Workings</h2>
<p>Landing uses the v5 function: ocean freight divided by 10, duty 5% of CIF, VAT 7.5% of CIF plus duty, SON US$85 a machine, terminal and clearing charges divided by 10, then ₦8 million of install and software, then ₦500,000 of NIBSS on the first machine only. FX is ₦1,331.6875. Street cost is rent ₦1.80 million, power, security, connectivity, maintenance at 10% of ex-works, and insurance at 1.5% of the landed cost. Office is ₦40 million plus ₦150,000 a machine at the start, and ₦25 million plus ₦50,000 a machine a year. Recompute from <span class="small">model/china_path.py</span>.</p>

<h2>8. Sources</h2>
<ol class="sources">
  <li>Shenzhen Hongzhou, HZ-3326 cash in/out kiosk. US$5,500 and US$4,800. https://hongzhou2.en.made-in-china.com/product/HnfURoZyAMhj/China-Bank-Government-Cash-in-out-Kiosk-Cash-Recycler-ATM-Machine-Bulk-Cash-Deposit-Payment-Kiosk.html</li>
  <li>Hongzhou, through-the-wall page. Nigeria is named under denomination customisation. No fee. 30 to 35 working days. https://www.hongzhousmart.com/through-the-wall-cdm.html</li>
  <li>Alibaba listing. “Customized + US$1,800/unit” on a bill-recycler kiosk. The line does not say it is a naira template. https://www.alibaba.com/product-detail/Customized-SDK-Enabled-Cash-POS-Self_1601385352394.html</li>
  <li>v5 landing sheet in this repository: freight, duty, VAT, SON, install, NIBSS, and the surcharge rules.</li>
  <li>Nairametrics, 19 January 2026. ATM withdrawals ₦36.34 trillion and 858.80 million transactions in the first half of 2025. https://nairametrics.com/2026/01/19/atm-transactions-surge-to-n36-34trn-in-six-months-despite-fresh-fees/</li>
  <li>Central Bank of Nigeria. 16,714 active ATMs in the first half of 2024. https://www.cbn.gov.ng/PaymentsSystem/modes.html</li>
  <li>NMDPRA fact sheet, Q1–Q3 2025. About 22,681 retail outlets. https://alps.blob.core.windows.net/nmdprawebsite/Statistics/Upload-80c82709-7f84-4cea-959e-668d6e6d030e.pdf</li>
  <li>MEMAN 2024 report. 1,392 member stations in the South West. https://moman.org/wp-content/uploads/2025/05/2024-Nigeria-Energy-Downstream-Industry-Report.pdf</li>
</ol>
<p class="small">End of study. Earlier CashEase files are unchanged. The 200 withdrawals a day are the rate this value needs. They are not a count from a Nigerian forecourt.</p>
"""

    head = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CashEase Nigeria: The Path If the Machines Come from China</title>
<style>
@page {
  size: A4;
  margin: 14mm 13mm 16mm 13mm;
  @bottom-center {
    content: "CashEase Nigeria · China machines · October 2026";
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
            "--user-data-dir=/tmp/chrome-cashease-v8",
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
    print("pdf", pdf_path.stat().st_size if pdf_path.exists() else 0)


if __name__ == "__main__":
    build()
