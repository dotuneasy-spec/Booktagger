# SNLB Farms
# Bankable Feasibility Study & Information Memorandum

**Commercial Tomato Farming on a Leased 100-Hectare Master Block**  
Ogun State, Nigeria — supplying Mile 12 International Market, Lagos

| Field | Detail |
| --- | --- |
| Entity (trading) | SNLB Farms |
| Document | Bankable Feasibility Study & Information Memorandum |
| Edition | v3.0 — Bankable |
| Date | August 2026 |
| Horizon | 5 years / 10 production cycles (build-out in Years 1–3; steady state Years 4–5) |
| Currency | Nigerian naira (₦), nominal |
| Primary underwriting case | **Credit / bank base case** |
| Classification | Confidential — for promoters, professional advisors, and prospective lenders/DFIs |
| Model | `model/financial_model.py` (reproducible; three cases + optional ₦80m facility) |

**Purpose.** This edition converts the August 2026 operating study into a document a credit committee, Bank of Agriculture (BOA) SME desk, NIRSAL-guaranteed commercial lender, or development-finance reviewer can underwrite. It keeps the same agronomic concept and expansion path, then (i) fills previously omitted costs, (ii) phases irrigation and packhouse capital expenditure as hectares come into production, (iii) applies Nigeria Tax Act 2025 rules, (iv) publishes an explicit discounted-cash-flow schedule, and (v) presents a promoter case, a credit case, and a stacked downside case side by side.

**Disclaimer.** Figures are illustrative projections on stated assumptions. They are not guarantees. This document is not financial, legal, tax, or investment advice. Independent technical, legal, tax, and insurance due diligence is a condition of any capital commitment.

---

## Contents

1. [Credit committee snapshot](#1-credit-committee-snapshot)
2. [What makes this edition bankable](#2-what-makes-this-edition-bankable)
3. [Three-case underwriting framework](#3-three-case-underwriting-framework)
4. [Sponsor, legal entity and governance](#4-sponsor-legal-entity-and-governance)
5. [Business model and capital allocation](#5-business-model-and-capital-allocation)
6. [Market analysis](#6-market-analysis)
7. [Site, agronomy and technical plan](#7-site-agronomy-and-technical-plan)
8. [Operations, offtake and organisation](#8-operations-offtake-and-organisation)
9. [Growth roadmap and implementation](#9-growth-roadmap-and-implementation)
10. [Financial plan](#10-financial-plan)
11. [Financing structure and optional facility](#11-financing-structure-and-optional-facility)
12. [Security, insurance and covenants](#12-security-insurance-and-covenants)
13. [Risk assessment (credit view)](#13-risk-assessment-credit-view)
14. [Environmental, social and governance](#14-environmental-social-and-governance)
15. [Conditions precedent and data room](#15-conditions-precedent-and-data-room)
16. [Conclusion and recommendations](#16-conclusion-and-recommendations)
17. [Appendices](#17-appendices)

---

## 1. Credit committee snapshot

### 1.1 The project in one paragraph

SNLB Farms will produce hybrid, drip-irrigated tomatoes on a contiguous Ogun State block, two cycles per year, and sell into Mile 12 (≈1.5 hours) rather than the 36–48 hour northern long-haul chain. Cultivation starts at 1 hectare and is intended to reach 100 hectares in six cycles (three years), funded primarily from retained earnings. Peak (July–November) cycles are the margin engine; Regular (December–June) cycles establish operations and cash. From Cycle 5, about 70% of volume is contracted in bulk to de-risk spot-market absorption.

### 1.2 Credit recommendation (internal)

| Item | Position |
| --- | --- |
| Feasibility (credit case) | **Bankable as a self-funding agribusiness, subject to CPs in Section 15** |
| Stated opening equity | ₦8.0 million (promoter) |
| **Recommended paid-in equity at first planting** | **₦12.0 million** — the credit-case Cycle 1 cash cost stack plus ₦3.5m initial CapEx exceeds ₦8.0m |
| External debt required to reach 100 ha? | **No**, if Peak-cycle execution holds and the 45 ha/cycle operating ceiling is respected |
| Optional facility (not required) | ₦80 million BOA-style production / irrigation term loan from Year 2, 9% interest, 36-month amortisation after Year-2 interest-only; **minimum DSCR 68.7×** in the credit case, **4.0×** in stacked downside |
| Binding constraint | Operational (land prep, irrigation build-out, staffing), not capital, from Cycle 4 |
| Single most important underwriting risk | Peak-season price realisation and Cycle 1 Regular-season cash tightness |
| Single most important structural advantage | Ogun–Lagos proximity (spoilage <5% vs 40%+ north) plus two-cycle calendar |

### 1.3 Credit-case headline numbers (fully taxed, haircut prices)

Opening equity in the model remains the promoter’s stated ₦8.0 million so that the funding gap is visible. Results below are the **credit / bank base case**.

| Metric | Year 1 | Year 2 | Year 3 | Year 5 (steady) |
| --- | --- | --- | --- | --- |
| Cultivated area (year-end) | 3 ha | 27 ha | 100 ha | 100 ha |
| Production | 66 t | 702 t | 2,896 t | 3,400 t |
| Revenue | ₦94.3m | ₦896.4m | ₦3.21bn | ₦3.41bn |
| EBITDA | ₦71.4m | ₦686.7m | ₦2.33bn | ₦2.16bn |
| EBIT margin | 74.8% | 76.0% | 72.0% | 62.5% |
| Tax (NTA 2025 full rate) | ₦24.0m | ₦231.5m | ₦785.8m | ₦725.9m |
| NPAT | ₦46.5m | ₦449.4m | ₦1.53bn | ₦1.41bn |
| Net margin | 49.3% | 50.1% | 47.5% | 41.3% |
| CapEx (incl. opening irrigation) | ₦5.5m | ₦38.0m | ₦113.0m | ₦0 |
| Unlevered FCF | ₦42.0m | ₦417.2m | ₦1.44bn | ₦1.44bn |
| Closing cash | ₦50.0m | ₦467.1m | ₦1.90bn | ₦4.86bn |
| Cumulative 50% buffer | ₦23.3m | ₦248.0m | ₦1.01bn | ₦2.46bn |

**Investment metrics (credit case, 5-year unlevered FCF, t=0 = −₦8.0m):**

| Metric | Value |
| --- | --- |
| NPV @ 10% (no terminal value) | ₦3.39 billion |
| NPV @ 18% agri-risk discount (no TV) | ₦2.62 billion |
| NPV @ 10% with Gordon TV (g = 3%) | ₦16.50 billion |
| NPV @ 18% with Gordon TV (g = 3%) | ₦6.93 billion |
| Project IRR (5-year, no TV) | Very high (>1,000%) — an artefact of tiny t=0 equity vs Cycle 2 cash; **do not use IRR as the decision metric** |
| Simple payback on ₦8m (credit FCF) | ≈2 months of operations (Cycle 2 Peak), **not** Cycle 1 |
| Cycle 1 break-even basket price | ₦18,262 vs ₦22,000 credit Regular price (**17.0% margin of safety**) |
| Optional ₦80m facility — minimum DSCR | **68.7×** (Year 3); still **4.0×** in stacked downside |

### 1.4 Three-case comparison (Year 3, first year the block is full)

| | Promoter (holiday) | **Credit (full tax)** | Downside (stacked) |
| --- | --- | --- | --- |
| Regular / Peak yield | 20 / 18 t/ha | **18 / 16 t/ha** | 15.0 / 13.5 t/ha |
| Regular / Peak price | ₦33,000 / ₦145,000 | **₦22,000 / ₦90,000** | ₦15,000 / ₦55,000 |
| Year 3 revenue | ₦5.74bn | **₦3.21bn** | ₦1.68bn |
| Year 3 NPAT | ₦4.91bn | **₦1.53bn** | ₦387m |
| Year 3 net margin | 85.5% | **47.5%** | 23.0% |
| 5-yr NPV @ 18% (no TV) | ₦8.79bn | **₦2.62bn** | ₦429m |
| Cycle 1 cash result | Profitable (MoS 52%) | **Profitable (MoS 17%)** | **Loss of ₦2.76m (MoS −61%)** |
| Y5 EBIT margin (inflation vs flat prices) | 80.5% | **62.5%** | **5.0%** |

The downside Year 5 margin compression is intentional: costs inflate at 17% while sale prices are held flat. It is the cleanest illustration that **long-run bankability depends on some price pass-through or cost control after Year 3**, not on Peak spikes alone.

### 1.5 Sources and uses — opening (t = 0)

**Promoter-stated pack**

| Sources | ₦ | Uses | ₦ |
| --- | --- | --- | --- |
| Owner equity | 8,000,000 | Initial CapEx (borehole share, 1 ha drip, crates, tools, legal) | 3,500,000 |
| | | Cycle 1 working capital | 4,500,000 |
| **Total** | **8,000,000** | **Total** | **8,000,000** |

**Credit-case cash requirement at first planting (recommended)**

| Uses | ₦ | Note |
| --- | --- | --- |
| Initial CapEx | 3,500,000 | Solar-capable borehole + 1 ha drip + crates + tools + counsel |
| Cycle 1 cash operating costs (ex-D&A) | 6,199,000 | Production, logistics, lease, NAIC, contingency, management |
| Pre-ops (soil test, CAC, insurance bind, nursery deposit) | 800,000 | Not in the original ₦8m pack |
| Opening cash buffer (one shock) | 1,501,000 | Covers a weak Regular price toward ₦15,000 |
| **Recommended paid-in equity** | **12,000,000** | Close the ₦4.0m gap before transplanting |

No debt, grants, or external equity are required in the base path once Cycle 2 Peak cash is realised. The ₦4.0m opening gap is a **conditions-precedent item**, not a reason to reject the project.

---

## 2. What makes this edition bankable

The prior expanded study was an operating plan. Lenders will not underwrite it as written for seven specific reasons. This edition closes each of them.

| Gap in the prior study | Why a credit officer rejects it | How this edition treats it |
| --- | --- | --- |
| Irrigation CapEx of ₦3m for a path to 100 ha | Drip does not scale at zero marginal cost | Incremental **₦1.0m/ha** drip plus borehole / packhouse / cold-room triggers (total **₦156.5m** CapEx through Year 3) |
| 90% gross margins, ₦9,650 Cycle 1 break-even | Incomplete cost stack (no NAIC, payroll, D&A, holding rent, contingency) | Full stack; credit-case Cycle 1 BE **₦18,262** |
| NPV/IRR stated as “order of magnitude” with no schedule | Cannot be reproduced or sensitised | Explicit 5-year FCF, NPV at 10% and 18%, with and without terminal value |
| CIT at legacy 0/20/30% bands | Nigeria Tax Act 2025 is in force from 1 Jan 2026 | Credit case: **30% CIT + 4% Development Levy** once turnover > ₦50m; promoter case: **5-year agri income-tax holiday** (s.163 / 13th Schedule) as statutory upside, not the underwriting base |
| VAT 7.5% treated as pass-through on tomatoes | Fresh produce is typically VAT-exempt / zero-rated | Sales modelled **VAT-exempt**; input VAT on CapEx to be recovered where eligible |
| “No external financing at any stage” as a virtue | Leaves no security package, DSCR, or CP list if a lender is later needed | Self-fund remains the base path; **optional ₦80m facility** fully scheduled with DSCR |
| Master-lease rent only on cultivated hectares, while claiming the whole 100 ha is locked on day one | Either the unused 99 ha is unpaid (tenure risk) or it is paid (cash risk) | **Staged lease + holding fee** (₦200k/ha/year cultivated; ₦25k/ha/year unused) — the bankable land structure |
| No promoter KYC, collateral, offtake evidence, or data room | File is incomplete for BOA / NIRSAL / ACGSF | Sections 4, 8, 12 and 15 |

**What is unchanged (and still the investment thesis):** two-cycle calendar; 50/50 buffer/reinvestment rule; 1 → 3 → 15 → 27 → 72 → 100 ha path with a 45 ha/cycle operating ceiling; Mile 12 proximity; NIHORT-anchored yields at or below the intensive 20–40 t/ha range.

---

## 3. Three-case underwriting framework

| | Promoter case | Credit / bank base case | Downside / stacked stress |
| --- | --- | --- | --- |
| Purpose | Show statutory upside if Peak prices and the agri tax holiday both hold | **The case a lender should underwrite** | Survival test |
| Yield (Regular / Peak) | 20 / 18 t/ha | 18 / 16 t/ha | 15.0 / 13.5 t/ha (−25% vs original) |
| Price (Regular / Peak per 50 kg basket) | ₦33,000 / ₦145,000 | ₦22,000 / ₦90,000 | ₦15,000 / ₦55,000 |
| Base production cost | ₦3.4m / ₦3.8m per ha | ₦3.6m / ₦4.2m per ha | ₦4.25m / ₦4.75m per ha |
| Logistics | ₦900 / basket | ₦1,100 / basket | ₦1,300 / basket |
| Cost inflation | 12% p.a. | 12% p.a. | 17% p.a. (near May 2026 NBS food inflation) |
| Sale prices | Flat nominal | Flat nominal | Flat nominal |
| Tax | 5-year agri holiday | 34% (30% + 4% levy) from Year 1 (turnover ₦94m > ₦50m) | Full tax from Year 2; Year 1 small-company 0% (turnover ₦49m) |
| All cases include | Phased CapEx, NAIC 2%, cargo 1.5%, management payroll, 5% contingency, D&A, holding-fee lease, 7% bulk haircut from Cycle 5, mechanization discounts 7/14/20% | same | same |

Prices are deliberately **not** grown with inflation. That is conservative for Years 1–3 (Peak spikes have historically more than offset inflation) and **harsh** for Years 4–5, which is why the downside Year 5 EBIT margin falls to 5%. A credit paper should assume some Mid-cycle price reset in any facility that extends past Year 4.

---

## 4. Sponsor, legal entity and governance

### 4.1 Entity (to be completed before first disbursement / first planting)

| Item | Status | Bankable requirement |
| --- | --- | --- |
| Trading name | SNLB Farms | Keep as brand |
| Legal form | To be incorporated | **Private company limited by shares** (CAC) with agriculture in the objects clause |
| CAC documents | Outstanding | Certificate of incorporation; CAC Status Report (shareholders/directors); MEMART with **express borrowing power**; paid-up capital ≥ 25% of any BOA loan (BOA SME rule) |
| TIN / FIRS | Outstanding | TIN issued before Cycle 1 sales |
| Registered office | Outstanding | Ogun or Lagos address on CAC file |
| Bank accounts | Outstanding | Operating account plus **proceeds / collection account**; 3–6 months statements before any DFI filing |
| BVN / NIN of directors | Outstanding | All directors and authorised signatories |
| Beneficial ownership | Outstanding | PSC register; PEP declaration |

Until incorporation, the venture is not a bankable borrower. Cycle 1 can legally be started by a promoter as a sole trader, but **every subsequent cycle that a lender might refinance should sit in the company**. Recommendation: incorporate before transplanting Cycle 1 so the first P&L is already the borrower’s.

### 4.2 Suggested share capital and reserved matters

- Authorised share capital: at least ₦20 million (headroom for the recommended ₦12 million paid-in plus later lease-to-own or equipment).
- Board: promoter + one independent with agribusiness or audit experience from Cycle 3 (15 ha).
- Reserved matters (MEMART / shareholders’ agreement): new debt above ₦10 million; related-party leases; change of 50/50 allocation policy; sale of the master-lease interest; any offtake > 40% of a cycle with a single counterparty without board note.
- External accountant from Cycle 1; **audited financial statements from Year 1** (statement of affairs is acceptable only for a BOA file in the first months).
- Cycle-close pack within 21 days of last sale: tonnes, baskets, average realised price, spoilage %, cash, 50/50 split, next-cycle planting plan.

### 4.3 Management (minimum acceptable to a lender)

| Role | When | Bankable minimum |
| --- | --- | --- |
| Promoter / MD | Day 0 | KYC; time commitment; personal guarantee for any facility |
| Farm manager | Day 0 | CV with irrigated horticulture (tomato or equivalent); 2-year reference |
| Farm-management company | Day 0 advisory; rental from 5 ha | Written SLA (uptime, mobilisation lead time, spare-parts) |
| Logistics / Mile 12 coordinator | Cycle 3 | Named buyer list; daily price log |
| Finance / admin | Cycle 3 | Bookkeeping + tax filings; not owner-only from 15 ha |
| Agronomist (retainer) | Day 0 | NIHORT / private; IPM protocol signed before Peak Cycle 2 |

Payroll used in the model (then inflated): ₦70,000/month (Cycles 1–2); ₦550,000/month (Cycles 3–4); ₦2.6 million/month (Cycle 5+). PAYE, pension (Pension Reform Act), and NSITF/ITF are to be costed by advisors; they are **not** fully modelled inside the ₦70k starter line and should be treated as a small additional opex item in the first audit.

### 4.4 Related-party and land conflicts

Any lease with a promoter, family member, or affiliate must be at documented arm’s-length rent, with an independent valuation or three comparable Ogun horticultural rents, and disclosed in the data room. Hidden related-party land is a standard reason BOA and commercial agricultural desks decline files.

---

## 5. Business model and capital allocation

### 5.1 Concept

The company leases (or options) a contiguous 100-hectare Ogun block, irrigates it parcel by parcel, and runs **two cycles per year** on every hectare under cultivation:

- **Regular season (first cycle is Regular):** planted to harvest in the December–June window. National dry-season supply is abundant; prices are lower; demand is stable. This is the establishing and relationship-building cycle.
- **Peak / scarcity season:** planted to harvest in July–November, when northern rain-fed supply and *Tuta absoluta* pressure historically collapse and Mile 12 spikes.

Produce moves Ogun → Mile 12 in about 1.5 hours, in stackable plastic crates, on insulated or refrigerated trucks. Sales unit is the 50 kg “big basket” until Cycle 5, when ≈70% of volume converts to per-tonne contracts at a 10% discount to spot (7% blended haircut, built into every case).

### 5.2 The 50/50 rule (credit-relevant)

At every cycle close, NPAT is split:

- **50% buffer** — cash or near-cash, not committed to new hectares. This is the loss-absorbing capacity a lender wants to see.
- **50% reinvestment** — next-cycle working capital, drip extension, and triggered shared infrastructure.

Land is added only up to what the reinvestment pool can fund **and** never more than **+45 ha in one cycle**. From Cycle 4 the operating ceiling, not cash, binds. By Cycle 6 the credit-case reinvestment pool still has unused capacity after the block is full.

A lender should take a **negative pledge** over a change to this rule without consent, and a **minimum cash covenant** equal to the greater of ₦10 million or 25% of the next cycle’s cash operating costs.

### 5.3 Mechanization (asset-light, rented)

| Stage | Trigger | Approach | Production-cost discount |
| --- | --- | --- | --- |
| 0 Manual | < 5 ha | Advisory farm-management company | 0% |
| 1 Rented core | 5–24 ha | Tractors/tillers rented per cycle | 7% |
| 2 Bulk + fleet | 25–59 ha | Bulk inputs + multi-plot rented fleet | 14% |
| 3 Master contract | ≥ 60 ha | Master service contract; optional owned implements | 20% |

Discounts are applied to **base production cost only**, not to logistics, lease, or insurance. That is stricter than treating them as a blanket opex saving.

### 5.4 Why the economics can survive a credit haircut

Four structural features remain after prices and yields are cut:

1. **Proximity.** 1.5 hours vs 36–48 hours. Spoilage target <5% vs 40%+ for northern loads.
2. **Seasonality as a feature.** Peak cycles dominate value; Regular cycles are not required to carry the enterprise alone (and in the downside case, they do not).
3. **Intensity vs smallholder baseline.** Credit-case 16–18 t/ha vs national rain-fed 4–10 t/ha, still at the low end of NIHORT’s 20–40 t/ha intensive range and below Olam-Caraway’s reported 30–40 t/ha.
4. **Absorption at full scale.** Year 5 credit-case output is 3,400 t/year. Mile 12 is cited at 1,000+ t/day. Full-year SNLB volume is about **3–4 days of terminal throughput**, material to a handful of wholesalers, not to the market as a whole — provided Cycle 5 bulk contracts exist.

---

## 6. Market analysis

### 6.1 National tomato balance

Nigeria is Africa’s second-largest tomato producer (≈3.7 million tonnes) and still a large net importer of paste (commonly cited **US$350–400 million** per year). Tomatoes are a staple vegetable with inelastic household demand. The paradox — large output, large imports, violent retail spikes — is explained by:

- smallholder, rain-fed yields of 4–10 t/ha;
- 40–50% post-harvest loss on the north–south corridor;
- recurring *Tuta absoluta* (“tomato Ebola”) events that can destroy 50–100% of affected northern fields and reprice Mile 12 by several multiples within weeks.

Policy backdrop is supportive rather than decisive: NATIP 2022–2027, ACGSF (up to 75% guarantee on qualifying agricultural loans), FX frictions on some paste imports, and Ogun State’s Special Agro-Industrial Processing Zone (SAPZ). None of these is assumed as a cash grant in the model.

### 6.2 Mile 12 — the price-setting hub

Mile 12 is West Africa’s largest fresh-produce terminal, serving Lagos (20+ million). Price discovery is daily, auction-style, in 50 kg baskets. Selected verified points used in the prior study (not a continuous series; gaps are not interpolated):

| Period | 50 kg big-basket price | Context |
| --- | --- | --- |
| Aug 2024 | ₦50,000 | Seven-month low; down 58% from Jan/Feb 2024 ~₦120,000 peak |
| Dec 2024 | ₦35,000–₦55,000 | Dry-season glut, quality-dependent |
| **Jan 2025** | **₦13,000–₦15,000** | Deep glut — **downside Regular-season floor** |
| Feb 2025 | ₦40,000 | Recovery |
| Oct 2025 | Small basket ₦22,000 (from ₦14,000) | Tightening signal |
| Mid-May 2026 | Easing from ~₦110,000 | Scarcity starting to soften |
| Late May / early Jun 2026 | ₦60,000–₦70,000 | Inter-peak trough |
| Early Jul 2026 | ₦120,000–₦150,000 | Spike; **validates scarcity peaks, not a 12-month average** |

**Pricing discipline in this IM:**

- Promoter Peak ₦145,000 sits inside the July 2026 print; it is **not** used for underwriting.
- Credit Peak ₦90,000 sits between the May–June 2026 trough (₦60–70k) and the July spike — a mid-scarcity realisation, not a headline high.
- Credit Regular ₦22,000 sits above the January 2025 crash and below the ₦33,000 promoter assumption.
- Downside Regular ₦15,000 **is** the January 2025 crash. Cycle 1 loses money in that case. The project still survives because Cycle 2 Peak, even at ₦55,000, more than repairs the year.

A lender should require a **weekly Mile 12 price log** from Cycle 1 as a reporting covenant, and should not treat ₦145,000 as a forward curve.

### 6.3 Competitive landscape

| Cohort | Position vs SNLB |
| --- | --- |
| Northern smallholders + aggregators | Dominant national volume; high spoilage; create the scarcity SNLB sells into |
| Large northern commercial (e.g. Olam-Caraway, Jigawa) | Higher demonstrated yields (30–40 t/ha); still long-haul to Lagos; more processing-oriented |
| Southern / peri-Lagos intensive growers | Currently limited scale; ₦3.6–4.2m/ha working-capital wall plus two-cycle know-how is the barrier |
| Processors (Dangote Tomato, Tomato Jos, paste importers) | Structurally short of consistent, graded fresh fruit; **Cycle 5+ offtake**, not Cycle 1 cash |

### 6.4 Addressable offtake (credit view)

At 100 ha, credit-case annual output is 3,400 tonnes (Year 4–5). That is too large for informal basket trading alone and too small to “fill” Mile 12. The bankable offtake design is therefore:

| Channel | Share from Cycle 5 | Role |
| --- | --- | --- |
| Standing wholesale contracts (named Mile 12 dealers) | ~50% of volume | Core cash; 10% discount to spot |
| Processor / institutional (Dangote, Tomato Jos, catering, retail DC) | ~20% | Grade and volume stability; may be lower price |
| Mile 12 spot baskets | ~30% | Price discovery and overflow |

**Conditions subsequent (not modelled as already signed):** at least two written letters of intent before Cycle 3; at least one bulk term sheet (volume, quality spec, payment T+3 to T+7, reject protocol) before Cycle 5 planting. Until those exist, a prudent lender treats Cycle 5–6 Regular-season cash as spot-only and would haircut Regular prices toward the downside case.

---

## 7. Site, agronomy and technical plan

### 7.1 Site (items a technical lender will send an agronomist to verify)

| Topic | Base-study statement | Bankable evidence still required |
| --- | --- | --- |
| Location | Ogun State, ≈1.5 h to Mile 12 | Survey plan, coordinates, access-road photos, flood history |
| Soils | Deep, well-drained, suitable | **Independent soil test** (pH, EC, NPK, micronutrients, nematodes) per 10 ha block |
| Water | Borehole / SAPZ corridor | Yield test (L/s), water quality (salinity, iron), recharge, WR licence if required |
| Tenure | 100 ha master lease | See §7.2 |
| Power | Unspecified | Diesel vs solar hybrid; generator sizing; NEPA/DisCo if any |
| Environment | OGEPA likely relevant | Screening letter; see Section 14 |

Until the soil and borehole tests exist, **yield is an assumption, not a fact**. The credit case already sits 10% below the original intensive yield; it does not replace a site report.

### 7.2 Bankable land structure (recommended)

Do **not** pay ₦20 million/year (₦200,000 × 100 ha) from day one on 1 hectare of production. Do **not** claim a 100 ha lock-up with zero holding cost.

**Recommended structure (used in the model):**

1. **Master option / right of first refusal** over the contiguous 100 ha, 5–10 year term, assignable to a lender, consent to mortgage of the leasehold interest.
2. **Cultivation lease** that steps in as parcels are developed, at **₦200,000/ha/year** (₦100,000 per cycle).
3. **Holding fee** of **₦25,000/ha/year** on undeveloped option land so the owner is paid not to shop the block.
4. **Lease-to-own** window from Year 2, funded from the buffer, creating collateral.
5. Counsel opinion on Governor’s consent, Land Use Act, family/chieftaincy claims, and whether the lessor actually holds C of O or a registrable instrument.

Cycle 1 credit-case lease cash (1 ha cultivated + 99 ha holding) is ₦1.34 million — expensive relative to 1 ha, and a reason opening equity should be ₦12 million. An even tighter Year-1 variant is to option the 100 ha but **lease only 10 ha** until Cycle 3; that is a negotiation item, not a model change.

### 7.3 Hybrid seed and yield

| Source | Yield | Use in this IM |
| --- | --- | --- |
| Nigerian smallholder rain-fed | 4–10 t/ha | Not used |
| NIHORT intensive guidance | 20–40 t/ha | Ceiling |
| NIHORT HortiTom4 / HortiTom5 (2025) | 21.7–27.2 t/ha reported potential | Upside only |
| Olam-Caraway (Jigawa) | 30 t/ha out-grower; up to 40 t/ha company fields | Precedent, different ecology |
| **Promoter case** | **20 / 18 t/ha** | Operating plan |
| **Credit case** | **18 / 16 t/ha** | **Underwriting** |
| **Downside** | **15.0 / 13.5 t/ha** | Stress |

Cultivars: Eva F1 / Platinum F1, with HortiTom lines on a side-by-side trial plot from Cycle 2. Peak yield is 10–12% below Regular for rainy-season disease pressure. Unit convention: 1 tonne = 20 baskets of 50 kg.

Each cycle is 60–90 days transplant to harvest. Nursery is on-farm or contracted with a named seedling supplier; a 15–20% extra seedling buffer is inside the seed line.

### 7.4 Crop calendar (indicative)

| Week | Regular (example: Dec transplant) | Peak (example: Jul transplant) |
| --- | --- | --- |
| −4 to −1 | Land prep, soil amendment, drip lay, nursery | Same; heavier IPM setup |
| 0 | Transplant | Transplant |
| 1–3 | Establishment, gap fill | Establishment; fungal watch |
| 4–6 | Vegetative / first flower | Vegetative; *Tuta* traps |
| 7–10 | Fruit set / ripening | Fruit set; more sprays |
| 11–13 | Harvest, crate, night/early haul to Mile 12 | Harvest (more frequent picks) |
| 14 | Cycle close, 50/50, next-parcel prep | Cycle close |

Exact planting weeks must be reverse-engineered from the target Mile 12 window, not from a generic “Dec–Jun” label. **Peak harvest that misses the scarcity window is the principal operational way to destroy the credit case.**

### 7.5 Irrigation, IPM, water

- **System:** drip + fertigation on every productive hectare. Shared mainlines across the master block.
- **CapEx:** ₦3.5 million opening (headworks + 1 ha); **₦1.0 million per additional hectare** of on-plot kit; second borehole ₦6 million at 15 ha; packhouse / cold room / third borehole ₦40 million at 72 ha; packing shed ₦8 million at 27 ha.
- **Opex:** diesel/solar, filters, emitter replacement — inside per-ha production cost (8% mix).
- **IPM:** resistant hybrids, pheromone traps, scouting, biologicals where feasible, targeted chemistry. Ogun is geographically insulated from the main northern *Tuta* belt; Peak season is still modelled as higher cost and lower yield.
- **Water duty (indicative, to be replaced by the agronomist):** 4,000–6,000 m³/ha/cycle under drip for tomato is a planning range; borehole design must cover Peak (higher ET plus wash-down) at 100 ha before Cycle 5, not after.

### 7.6 Post-harvest and logistics

- Plastic crates from Cycle 1 (not raffia). Spoilage target **<5%**; model sells **100% of harvested yield** — i.e. yields are already net of a small field loss. A credit officer may apply a further 3–5% spoilage haircut; the downside yield cut more than covers that.
- Insulated / refrigerated trucking, ₦1,100/basket in the credit case (fuel, handling, packaging, Ogun–Mile 12).
- Grading: size, colour, firmness, defects. Processor offtake will need a written spec (brix, rot %, green shoulder).
- No cold-chain **ownership** until the Cycle 5 packhouse trigger; until then, speed-to-market is the cold chain.

### 7.7 Production cost build-up (credit case, Year 1 prices, pre-mechanization discount)

| Line (share of base) | Regular ₦/ha | Peak ₦/ha |
| --- | --- | --- |
| Hybrid seed & seedlings (30%) | 1,080,000 | 1,260,000 |
| Fertilizer & fertigation (20%) | 720,000 | 840,000 |
| IPM / crop protection (12%) | 432,000 | 504,000 |
| Seasonal labour (18%) | 648,000 | 756,000 |
| Irrigation operating cost (8%) | 288,000 | 336,000 |
| Staking, twine, mulch (7%) | 252,000 | 294,000 |
| Nursery & miscellaneous (5%) | 180,000 | 210,000 |
| **Base production cost** | **3,600,000** | **4,200,000** |

Quotations (seed, drip kit, fertilizer) should replace these shares before a BOA appraisal. NAIC arable cover is **2% of production cost** on top, not inside the table.

---

## 8. Operations, offtake and organisation

### 8.1 Staffing ramp (binding constraint)

| Role | Cycles 1–2 (1–3 ha) | Cycles 3–4 (15–27 ha) | Cycles 5–6 (72–100 ha) |
| --- | --- | --- | --- |
| Farm manager | 1 | 1 | 1 senior |
| Field supervisors | 0 | 1–2 | 4–6 |
| Logistics / Mile 12 | Owner | 1 | 2 |
| Finance & admin | Owner | 1 | 2–3 |
| Modelled monthly management payroll | ₦70,000 | ₦550,000 | ₦2,600,000 |

Seasonal field labour sits inside per-hectare production cost. The **45 ha/cycle ceiling** exists because a ₦400 million reinvestment pool cannot hire and house 45 hectares of drip, labour and supervision in six months without a professional farm-management partner and a mobilisation plan signed **before Cycle 4**.

### 8.2 Go-to-market, Cycles 1–4

1. Identify 8–12 Mile 12 wholesalers who already handle quality southern vegetables.
2. Sell Cycle 1 as a **reference lot**: consistent crate weight, dawn delivery, WhatsApp photo of harvest the previous evening.
3. Keep a price book (date, buyer, baskets, ₦/basket, rejects).
4. By Cycle 3, convert two buyers into **standing weekly offtake** (even if still basket-denominated).
5. By Cycle 4, open processor conversations with volume and spec, not with a cold call at 72 ha.

### 8.3 Buyer concentration limit

From Cycle 5, no single counterparty above **40% of cycle volume** without board (and, if a facility is live, lender) consent. The 30% spot sleeve is the liquidity valve if a contractor defaults.

---

## 9. Growth roadmap and implementation

### 9.1 Expansion path (all cases; cash-checked in the credit run)

| Cycle | Season | Added | Cultivated | Mech. stage | Credit revenue | Credit EBIT | Credit NPAT | Cycle CapEx |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Regular | start | 1 ha | 0 | ₦7.9m | ₦1.35m | ₦0.89m | ₦0 (opening at t=0) |
| C2 | Peak | +2 | 3 ha | 0 | ₦86.4m | ₦69.2m | ₦45.7m | ₦2.0m drip |
| C3 | Regular | +12 | 15 ha | 1 | ₦118.8m | ₦42.9m | ₦28.3m | ₦18.0m (drip + borehole) |
| C4 | Peak | +12 | 27 ha | 2 | ₦777.6m | ₦638.0m | ₦421.1m | ₦20.0m (drip + shed) |
| C5 | Regular | +45 | 72 ha | 3 | ₦530.3m | ₦174.9m | ₦115.4m | ₦85.0m (drip + packhouse) |
| C6 | Peak | +28 | 100 ha | 3 | ₦2.68bn | ₦2.14bn | ₦1.41bn | ₦28.0m drip |
| C7–C8 | Y4 both | — | 100 ha | 3 | ₦3.41bn yr | ₦2.27bn yr | ₦1.50bn yr | ₦0 |
| C9–C10 | Y5 both | — | 100 ha | 3 | ₦3.41bn yr | ₦2.13bn yr | ₦1.41bn yr | ₦0 |

Peak cycles are 70%+ of lifetime value. Regular cycles at scale (C5, C7, C9) remain profitable in the credit case but are working-capital heavy. **Do not plant +45 ha Regular in Cycle 5 unless bulk offtake for that Regular harvest is contracted** — otherwise slide the +45 ha to the following Peak (a one-cycle delay, still inside three-and-a-half years).

### 9.2 Implementation timeline

| Phase | Timing | Activities | Gate to proceed |
| --- | --- | --- | --- |
| Pre-ops | Months −4 to 0 | Incorporate; TIN; master option/lease; soil + borehole tests; insurance bind; farm-manager hire; input quotations; ₦12m paid-in | Counsel memo on tenure; soil/water pass; equity in escrow/account |
| Cycle 1 Regular | Months 0–6 | 1 ha; buyer log; cycle-close audit pack | Cycle 1 cash cost covered; no unpaid statutory filings |
| Cycle 2 Peak | Months 6–12 | 3 ha; first scarcity harvest; +12 ha prep | Realised Peak price ≥ ₦55,000 blended **or** buffer still covers C3 WC |
| Year 2 (C3–C4) | Months 12–24 | 15 → 27 ha; Stage 1–2 mech; finance hire; offtake LOIs; optional ₦80m facility | SLA with mechanization partner; two LOIs |
| Year 3 (C5–C6) | Months 24–36 | 72 → 100 ha; packhouse; 70/30 bulk/spot | Bulk term sheet; 45 ha mobilisation plan |
| Steady | Year 4+ | Yield/cost improvement; lease-to-own; optional processing | Board strategy paper |

### 9.3 Optional Year 4+ uses of surplus buffer (not in the base NPV)

- Lease-to-own conversion (collateral).
- Adjacent block or out-grower scheme (Olam-Caraway analogue).
- Paste / puree for off-grade fruit (only with a separate feasibility; do not mix into this IM’s NPV).
- Owned cold rooms beyond the ₦40m Cycle 5 trigger.

---

## 10. Financial plan

All figures in this section are from `model/financial_model.py` unless labelled “illustrative / not modelled”. The **credit case is the default**.

### 10.1 Key assumptions (credit case)

| Assumption | Value |
| --- | --- |
| Regular yield / price | 18 t/ha (360 baskets) @ ₦22,000 |
| Peak yield / price | 16 t/ha (320 baskets) @ ₦90,000 |
| Production cost Regular / Peak | ₦3.6m / ₦4.2m per ha before mech. discount |
| Logistics | ₦1,100 / basket |
| Lease | ₦100,000/ha cultivated per cycle + ₦12,500/ha unused per cycle |
| NAIC | 2% of production cost |
| Cargo insurance | 1.5% of logistics |
| Other insurance | ₦180,000 + ₦8,000/ha per cycle |
| Contingency | 5% of production cost |
| Management | See §8.1, inflated |
| D&A | Straight-line 6 years on gross PPE |
| Inflation on costs | 12% p.a. compounding by calendar year |
| Sale prices | Flat |
| Bulk haircut | 7% of revenue from 55 ha (Cycle 5+) |
| Mechanization discount | 0 / 7 / 14 / 20% at <5 / 5 / 25 / 60 ha |
| Tax | 30% CIT + 4% Development Levy on EBT (Year 1 turnover ₦94.3m > ₦50m small-company test) |
| VAT on output | Exempt (fresh produce) |
| Opening equity / opening CapEx | ₦8.0m / ₦3.5m in the engine (see §1.5 for the ₦12m recommendation) |

### 10.2 Credit-case annual P&L

| ₦ million | Y1 | Y2 | Y3 | Y4 | Y5 |
| --- | --- | --- | --- | --- | --- |
| Revenue | 94.3 | 896.4 | 3,208.7 | 3,415.0 | 3,415.0 |
| Production | 16.2 | 165.5 | 681.6 | 876.7 | 981.9 |
| Logistics | 1.5 | 17.3 | 79.9 | 105.1 | 117.7 |
| Lease, insurance, contingency, management | 5.2 | 26.6 | 122.3 | 150.7 | 168.8 |
| D&A | 0.9 | 5.8 | 23.9 | 26.3 | 26.3 |
| **EBIT** | **70.5** | **680.9** | **2,311.1** | **2,269.3** | **2,135.0** |
| EBIT margin | 74.8% | 76.0% | 72.0% | 66.5% | 62.5% |
| Tax @ 34% | 24.0 | 231.5 | 785.8 | 771.6 | 725.9 |
| **NPAT** | **46.5** | **449.4** | **1,525.3** | **1,497.7** | **1,409.1** |
| Net margin | 49.3% | 50.1% | 47.5% | 43.9% | 41.3% |
| 50% buffer (annual) | 23.3 | 224.7 | 762.6 | 748.9 | 704.5 |
| Cumulative buffer | 23.3 | 248.0 | 1,010.6 | 1,759.5 | 2,464.1 |

Gross margin (revenue − production − logistics) declines from 81.3% (Y1) to 67.8% (Y5) as inflation compounds against flat prices. That path is still wide. The promoter case, with tax holiday and higher prices, prints 80%+ net margins — **those numbers are not for the credit paper**.

### 10.3 Credit-case cash flow

| ₦ million | Y1 | Y2 | Y3 | Y4 | Y5 |
| --- | --- | --- | --- | --- | --- |
| NPAT + D&A (CFO proxy) | 47.5 | 455.2 | 1,549.2 | 1,524.0 | 1,435.3 |
| CapEx | (5.5) | (38.0) | (113.0) | — | — |
| Owner equity | 8.0 | — | — | — | — |
| **Closing cash** | **50.0** | **467.1** | **1,903.3** | **3,427.3** | **4,862.7** |

Mile 12 is modelled as **cash sales** (T+0 to T+3). If bulk contracts move to T+14, add a receivables line equal to ~2 weeks of Cycle 5+ revenue (order of ₦50–100 million at full Peak) and fund it from the buffer — do not add bank overdraft until that is measured.

### 10.4 Credit-case balance sheet (year-end)

| ₦ million | Y1 | Y2 | Y3 | Y4 | Y5 |
| --- | --- | --- | --- | --- | --- |
| Cash | 50.0 | 467.1 | 1,903.3 | 3,427.3 | 4,862.7 |
| Net PPE | 5.6 | 37.8 | 126.9 | 100.7 | 74.4 |
| **Total assets** | **55.5** | **505.0** | **2,030.3** | **3,528.0** | **4,937.1** |
| Debt | — | — | — | — | — |
| Equity | 55.5 | 505.0 | 2,030.3 | 3,528.0 | 4,937.1 |

PPE is irrigation, boreholes, packing shed and packhouse/cold room, depreciated over six years. Land remains off-balance-sheet until lease-to-own exercises.

### 10.5 CapEx schedule (all cases; ₦)

| Trigger | Item | Amount |
| --- | --- | --- |
| t = 0 | Headworks, 1 ha drip, crates, tools, legal | 3,500,000 |
| 3 ha (C2) | +2 ha drip @ ₦1.0m | 2,000,000 |
| 15 ha (C3) | +12 ha drip + second borehole | 18,000,000 |
| 27 ha (C4) | +12 ha drip + packing shed | 20,000,000 |
| 72 ha (C5) | +45 ha drip + packhouse / cold room / third borehole | 85,000,000 |
| 100 ha (C6) | +28 ha drip | 28,000,000 |
| **Total through Year 3** | | **156,500,000** |

This single table is the largest numerical change versus the prior study’s ₦3.0 million lifetime CapEx. It is fully funded from operating cash in the credit case **after Cycle 2**. Cycle 5’s ₦85 million spike is why Peak Cycle 4 must not be missed.

### 10.6 Working capital by cycle (credit case, cash opex excluding D&A)

| Cycle | Ha | Cash opex | Funded from | Comment |
| --- | --- | --- | --- | --- |
| C1 | 1 | ₦6.20m | Opening WC (tight vs ₦4.5m residual of an ₦8m pack) | **Raise ₦12m equity or a ₦5m input facility** |
| C2 | 3 | ₦16.7m | C1 reinvestment + cash | Covered once C1 closes; Peak inputs bought before C1 cash fully returns — keep ₦5–8m liquidity |
| C3 | 15 | ₦73.8m | C2 Peak NPAT ₦45.7m is not enough **alone** for opex + ₦18m CapEx; use Y1 cash ₦50m | Liquidity planning, not a structural hole |
| C4 | 27 | ₦135.8m | C3 + cash | Comfortable after C2 |
| C5 | 72 | ₦407.8m + ₦85m CapEx | C4 NPAT ₦421m + cash | Gate: do not build packhouse without C4 cash in the bank |
| C6 | 100 | ₦528.6m + ₦28m CapEx | C5 + cash | Ceiling binds; cash does not |

### 10.7 Break-even (Cycle 1 Regular — the tightest test)

| | Promoter | **Credit** | Downside |
| --- | --- | --- | --- |
| Cycle 1 baskets | 400 | **360** | 300 |
| Cash + D&A cost | ₦6.32m | **₦6.57m** | ₦7.26m |
| Break-even ₦/basket | ₦15,810 | **₦18,262** | ₦24,213 |
| Assumed selling price | ₦33,000 | **₦22,000** | ₦15,000 |
| Margin of safety | 52.1% | **17.0%** | **−61.4%** |
| Cycle 1 NPAT | Positive | **₦0.89m** | **−₦2.76m** |

The prior study’s ₦9,650 break-even and “payback inside Cycle 1” **do not survive** a complete cost stack. Credit-case payback is **Cycle 2 Peak**, still inside Year 1. Downside Cycle 1 is a planned loss; Year 1 as a whole remains NPAT-positive (₦22.8m) because Peak ₦55,000 on 3 ha repairs it.

### 10.8 DCF (credit case)

Unlevered FCF = EBIT × (1 − 34%) + D&A − CapEx. t = 0 is −₦8.0 million. Year 1 FCF excludes double-counting of opening CapEx already in t = 0 equity.

| | t=0 | Y1 | Y2 | Y3 | Y4 | Y5 |
| --- | --- | --- | --- | --- | --- | --- |
| FCF (₦m) | (8.0) | 45.5 | 417.2 | 1,436.2 | 1,524.0 | 1,435.3 |

| Discount / terminal | NPV |
| --- | --- |
| 10%, no TV | ₦3.39bn |
| 18%, no TV | ₦2.62bn |
| 10%, Gordon TV on Y5 FCF (g=3%) | ₦16.50bn |
| 18%, Gordon TV (g=3%) | ₦6.93bn |

**How to read IRR.** Project IRR on this path is above 1,000%. That is mathematically consistent with putting ₦8 million to work against a ₦86 million Peak Cycle 2, and it is **not** a useful covenant or IC metric. Use **NPV at 18%**, **Cycle 1 cash coverage**, and **DSCR** if any debt is introduced.

Promoter-case NPV @ 18% no TV is ₦8.79bn (tax holiday + high Peak price). Downside NPV @ 18% no TV is still **₦429 million** — the project remains value-accretive after a stacked shock, provided Peak cycles still run.

### 10.9 Sensitivity (directional, credit-case logic)

| Shock | Effect |
| --- | --- |
| Peak price −30% (₦90k → ₦63k) | Still above downside Peak ₦55k; Year 3 remains strongly profitable |
| Regular price at ₦15,000 | Cycle 1 loss as in downside; Year 1 still saved by Peak |
| Yield −20% | Inside the downside yield set |
| Cost +30% on top of 12% inflation | Similar to moving toward downside opex; Peak still carries the year |
| Cost inflation 17% + flat prices through Year 5 | Downside Y5 EBIT margin **5%** — **do not extend a long facility without a price-reset clause** |
| Missed Peak window (Peak price = Regular price) | The actual kill scenario: treat as a default-style stress and hold one full Peak NPAT in the buffer before +45 ha |

### 10.10 Promoter case (statutory upside — not the credit base)

If (i) the 5-year agricultural income-tax exemption under NTA 2025 applies to this crop-production company from commencement, and (ii) Mile 12 realises promoter prices, Year 3 NPAT is ₦4.91bn on ₦5.74bn revenue, and 5-year NPV @ 18% is ₦8.79bn. **Counsel and tax advisors must confirm commencement date, 13th Schedule activity, and whether the Development Levy still attaches.** Until a written tax opinion exists, underwrite at 34%.

### 10.11 KPIs a lender should receive every cycle

| KPI | Credit Y1 | Credit Y3 | Covenant idea |
| --- | --- | --- | --- |
| Tonnes sold | 66 | 2,896 | ≥ 80% of that cycle’s plan |
| Average realised ₦/basket vs model | — | — | Peak ≥ ₦55,000 blended; Regular ≥ ₦15,000 |
| Spoilage % | <5% | <5% | <8% |
| Cash / next-cycle cash opex | — | — | ≥ 1.25× |
| Buffer / model buffer | ₦23.3m | ₦1.01bn | No distribution that cuts buffer > 25% |
| External debt | 0 | 0 | If any, DSCR ≥ 1.50× |

---

## 11. Financing structure and optional facility

### 11.1 Base path: 100% equity, self-fund after opening

This is still the intended path. After the ₦12 million paid-in recommendation, no lender is required to reach 100 ha if Peak Cycle 2 prints anywhere near the credit case.

### 11.2 Why talk to a bank anyway

- Cycle 1 WC gap vs the stated ₦8 million.
- Cycle 5 packhouse (₦85 million in one Regular season) concentrates execution and cash.
- ACGSF / NIRSAL Credit Risk Guarantee can convert an unsecured SME into a priced commercial loan later (cold chain, processing).
- Establishing a **clean account history** from Cycle 1 is cheaper than a distressed first approach in Year 3.

### 11.3 Institutional map (Nigeria, 2026)

| Institution | Fit | What they will ask for |
| --- | --- | --- |
| **Bank of Agriculture** | Production loan @ **9%** + 0.5% appraisal + 0.5% commitment + 1% p.a. management; NAIC 2% of material inputs (arable) | CAC, MEMART borrowing clause, paid-up ≥ 25% of loan, 2 copies of this IM, 6-month statements, CVs, lease, security (realty / cash / guarantee), board resolution, TIN |
| **NIRSAL Plc CRG** | Guarantee to a commercial bank; field risk management | Bankable plan, offtake, insurance, KYC |
| **NIRSAL MFB** | Smaller tickets (typically up to ~₦10m AGSMEIS-type), 5% class, EDI certificate | Too small for 100 ha; useful only for Cycle 1 inputs |
| **Deposit-money bank + ACGSF** | Up to 75% CBN guarantee on qualifying agri loans | Same file as BOA plus bank’s own collateral schedule |
| **Ogun SAPZ / state** | Infrastructure, not cash in this model | Locate inside / adjacent if it shortens power and roads |
| **DFI / AfDB-type** | Only after 2 audited cycles and offtake | ESIA, gender/jobs, climate-smart irrigation |

BOA production-loan pricing is used for the optional facility below because it is public, agri-specific, and conservative relative to a 5% intervention window that may not be available.

### 11.4 Optional ₦80 million facility (credit case)

| Term | Illustration |
| --- | --- |
| Amount | ₦80,000,000 |
| Purpose | Year 2 irrigation expansion, second borehole, packing shed, Cycle 3–4 WC top-up |
| Draw | Start of Year 2 (Cycle 3) |
| Rate | 9% p.a. interest + 1% p.a. management fee + 0.5% one-off appraisal |
| Shape | Year 2 interest-only; Years 3–5 amortising (₦26.7m principal per year) |
| Security | See Section 12 |
| Equity | ₦12m paid-in recommended before draw |

| Year | EBITDA | Interest | Fees | Principal | Debt service | DSCR | Debt YE |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ₦71.4m | — | — | — | — | n/a | — |
| 2 | ₦686.7m | ₦7.2m | ₦1.2m | — | ₦8.4m | **81.7×** | ₦80.0m |
| 3 | ₦2,335.0m | ₦6.6m | ₦0.7m | ₦26.7m | ₦34.0m | **68.7×** | ₦53.3m |
| 4 | ₦2,295.6m | ₦4.2m | ₦0.5m | ₦26.7m | ₦31.3m | **73.3×** | ₦26.7m |
| 5 | ₦2,161.2m | ₦1.8m | ₦0.2m | ₦26.7m | ₦28.7m | **75.4×** | — |

Minimum DSCR in the **downside** case on the same facility is **4.02×**, still above a typical 1.50× agri covenant. The project is not debt-constrained; the facility is a **liquidity and discipline tool**, not a solvency requirement.

A smaller **₦5–10 million Cycle 1 input facility** (NIRSAL MFB or BOA micro/SME) is the more honest first ticket if promoters cannot close ₦12 million equity.

### 11.5 Use of proceeds — optional ₦80m (Year 2)

| Use | ₦m |
| --- | --- |
| Drip extension and second borehole (C3) | 18.0 |
| Drip + packing shed (C4) | 20.0 |
| Cycle 3–4 working-capital reserve | 30.0 |
| Prepaid NAIC + interest reserve (6 months) | 8.0 |
| Contingency / appraisal & fees | 4.0 |
| **Total** | **80.0** |

Self-fund would pay the same CapEx from C2 Peak cash; the loan simply avoids draining the buffer before the first audited year is closed.

---

## 12. Security, insurance and covenants

### 12.1 Security package (if any facility is raised)

| Rank | Asset | Comment |
| --- | --- | --- |
| 1 | All-asset debenture over the company | Standard |
| 2 | Assignment of master lease / option; lender consent to mortgage | Requires lessor cooperation — **negotiate in the lease now** |
| 3 | Charge over drip, pumps, packhouse | Serial-numbered; insured |
| 4 | Assignment of offtake proceeds into a collection account | From Cycle 5 contracts; earlier, Mile 12 is cash |
| 5 | Lien on NAIC proceeds | Loss-payee clause |
| 6 | Personal guarantee of promoter | Expected on first facility |
| 7 | Cash collateral / BOA lien deposit | BOA SME: often **10–20%** lien deposit of loan volume — budget ₦8–16m on an ₦80m ticket **in addition to** equity |
| 8 | NIRSAL CRG or ACGSF | Reduces bank risk weights; does not replace (1)–(6) |

Unencumbered Year 2 cash in the credit case (₦467m) would more than cash-collateralise an ₦80m loan. That is the cleanest security story — **after** Cycle 2, not before Cycle 1.

### 12.2 Insurance (costed)

| Cover | Basis in model | Bind |
| --- | --- | --- |
| NAIC (or equivalent) arable / weather-index crop | 2% of production cost per cycle | Every cycle before transplant |
| Goods-in-transit | 1.5% of logistics | Every haul |
| Public / product liability + key person | ₦180,000 + ₦8,000/ha per cycle | Cycle 1 |
| Asset all-risks on drip, pumps, packhouse | Inside “other insurance” order-of-magnitude; get quotes | At installation |
| Employer’s liability / NSITF | Statutory; extra to model | First employee |

BOA publicly cites **NAIC arable at 2% of material inputs** — aligned with the model. Bind crop cover **before** Peak Cycle 2; a lender will not take rainy-season pest risk naked.

### 12.3 Illustrative covenants (if geared)

- Minimum DSCR 1.50× (trailing two cycles).
- Minimum cash ₦10 million or 25% of next-cycle cash opex.
- No dividends until Cycle 4 close **or** buffer ≥ ₦100 million, whichever later.
- 50/50 rule maintained; related-party lease changes require consent.
- Annual audit within 120 days; cycle management accounts in 21 days.
- Hedging not required (naira costs, naira revenue). Report FX exposure on imported seed/drip quarterly.

---

## 13. Risk assessment (credit view)

Likelihood × impact after mitigation. Residual “High” items are execution, not solvency, in the credit case.

### 13.1 Market and price

| Risk | L | I | Residual | Mitigation |
| --- | --- | --- | --- | --- |
| Peak price below ₦90,000 | M | H | M | Credit case already at ₦90k; downside ₦55k still Year-profitable; buffer |
| Regular glut at ₦13–15k | M | M | M | Cycle 1 may lose money; do not size Year 1 debt off Regular |
| Self-cannibalisation at 72–100 ha | M | H | M | 70% bulk from C5 **must be contracted**, not hoped |
| Buyer default on bulk | L | M | L | 40% concentration cap; 30% spot sleeve |
| New southern intensive entrants | L | M | L | 18-month relationship lead time; capital wall |

### 13.2 Operational and tenure

| Risk | L | I | Residual | Mitigation |
| --- | --- | --- | --- | --- |
| Missed Peak harvest window | M | **H** | H | Calendar reverse-engineered from Mile 12; farm manager KPI |
| Staffing / +45 ha mobilisation | **H** | **H** | H | Hard ceiling; FMC SLA; option to delay C5 add to next Peak |
| Irrigation failure | L | H | M | Spares, dual borehole from 15 ha, yield is drip-dependent |
| *Tuta* / Peak disease | M | H | M | IPM; lower Peak yield already; NAIC |
| Lease defective / family claim | L | **H** | M | Counsel opinion; Governor’s consent; holding fee + option |
| Water insufficient at 100 ha | M | H | M | Pumping test sized to 100 ha **before C5** |

### 13.3 Financial, tax, FX

| Risk | L | I | Residual | Mitigation |
| --- | --- | --- | --- | --- |
| Opening ₦8m too small | **H** | M | L if CP met | **₦12m paid-in** or ₦5–10m input loan |
| Inflation 17% vs flat prices to Y5 | M | H | M | Short facilities; offtake with review clause; downside Y5 still +EBIT |
| Agri tax holiday denied | M | M | L | Credit case already fully taxed |
| Imported seed/drip FX | H | M | M | Early procurement; naira quotes; bulk Stage 2 |
| No lender if C5 packhouse slips | L | M | L | Buffer after C4 is ₦248m+ in credit case — larger than the packhouse |

### 13.4 Overall credit view

The enterprise is **high-margin, Peak-dependent, and operationally constrained**. It is not a thin-margin row-crop that dies at a 10% price move. It **can** die from (i) planting 72 ha Regular without offtake, (ii) missing the scarcity window, (iii) a bad lease, or (iv) starting Cycle 1 with ₦8 million against a ₦6.2 million cash cost plus ₦3.5 million CapEx. Those four items are all capable of being closed in the CP list. After Cycle 2, the credit case is cash-rich even if a lender never appears.

---

## 14. Environmental, social and governance

### 14.1 ESIA screening (IFC Performance Standards — light)

| PS | Relevance | Action |
| --- | --- | --- |
| PS1 Assessment | Greenfield irrigation | OGEPA screening; simple ESMP for 1–15 ha; escalate before packhouse |
| PS2 Labour | Seasonal harvest crews | Written terms, no child labour, PPE, potable water, first aid |
| PS3 Resource efficiency | Drip vs flood; pesticide | IPM log; fuel/solar log; no untreated pesticide container dumping |
| PS4 Community | Spray drift, truck traffic | Buffer to dwellings; haul hours |
| PS5 Land | Lease / displacement | Counsel + community minutes if any occupiers |
| PS6 Biodiversity | Unlikely if already farmland | Confirm not wetland / forest reserve |
| PS7/8 Indigenous / heritage | Site-specific | Chance-find procedure |

A full ESIA is unlikely at 1 ha and likely at packhouse / 72 ha. Budget time in Year 2.

### 14.2 Environmental operating claims (do not over-claim)

- Drip reduces water per tonne vs rain-fed waste and flood irrigation.
- Short haul cuts embedded loss vs northern corridor.
- IPM aims to cut blanket insecticide vs high-pressure northern systems.
- Quantified water (m³/t) and pesticide (kg ai/ha) KPIs start Cycle 2, not Cycle 1 marketing.

### 14.3 Social

Direct seasonal jobs scale with hectares; permanent staff follow the organogram. Skills transfer via the farm-management company. Pension Reform Act compliance for formal staff. Prefer local labour for harvest. No processing-plant community impact until a separate project.

### 14.4 Governance

Cycle-level close, 50/50 rule, audit from Year 1, related-party lease disclosure, and (if geared) collection-account discipline are the governance package. They are also what makes the next facility cheap.

---

## 15. Conditions precedent and data room

### 15.1 Conditions precedent to first planting (and to any Cycle 1 facility)

1. CAC incorporation, TIN, MEMART with agri objects and borrowing power.
2. ₦12.0 million paid-in equity in the operating account **or** ₦8.0 million plus a bound ₦5.0 million input facility.
3. Executed master option/lease in the recommended structure, with assignment language.
4. Independent soil test and borehole yield/quality test on the first 10 ha.
5. Named farm manager (CV in file) and FMC advisory letter.
6. NAIC (or equivalent) crop cover bound for Cycle 1; GIT quote.
7. Seed and drip quotations (three each, or two plus a named exclusive supplier).
8. Promoter KYC (NIN, BVN, ID, PEP form).
9. Tax engagement letter (NTA 2025 holiday vs 34% — written view).
10. Cycle 1 budget signed against the credit-case cash opex of ≈₦6.2 million.

### 15.2 Conditions subsequent

| Deadline | Item |
| --- | --- |
| End of Cycle 1 | Management accounts; buyer log; spoilage % |
| Before Cycle 2 transplant | Peak IPM protocol; crop cover rebound |
| Before Cycle 3 | Two offtake LOIs; finance officer or outsourced accountant |
| Before Cycle 4 | Mechanization SLA; 100 ha water-resource note |
| Before Cycle 5 | Bulk term sheet ≥ 50% of planned Regular volume **or** delay the +45 ha |
| Year 1 + 120 days | First audit |

### 15.3 Data-room index

| Folder | Contents |
| --- | --- |
| 00. IM | This document; model `.py` + `model_results.json` |
| 01. Corporate | CAC, MEMART, TIN, PSC, board minutes, signatories |
| 02. Land | Lease/option, survey, photos, counsel opinion, C of O chain |
| 03. Technical | Soil, water, drip design, seed specs, IPM, crop calendar |
| 04. Market | Mile 12 price log, buyer names (confidential), draft LOIs |
| 05. Financial | Bank statements, cycle packs, tax filings, insurance binders |
| 06. ESG | OGEPA correspondence, labour policy, pesticide logs |
| 07. Security | Asset register, valuations, guarantee forms |
| 08. Quotes | Seed, fertilizer, drip, crates, transport, packhouse BoQ |

---

## 16. Conclusion and recommendations

### 16.1 Verdict

SNLB Farms is **commercially feasible and, after the gaps in the prior study are closed, creditworthy**.

Under the **credit case** — 18/16 t/ha, ₦22,000 / ₦90,000 baskets, complete opex, ₦156.5 million phased CapEx, and full NTA 2025 tax — the venture still reaches 100 hectares in six cycles, pays back opening equity on Cycle 2 Peak, and generates ₦2.62 billion NPV at an 18% discount rate without terminal value. A stacked downside (January 2025 glut prices, −25% yield, +25% costs, 17% inflation) remains NPV-positive at 18%, but **Cycle 1 loses money** and Year 5 margins compress to 5% EBIT. That is the honest envelope.

The original ₦8 million / ₦9,650 break-even / “no CapEx after Year 1” story should not be shown to a credit committee. The investment thesis does not need it.

### 16.2 Critical success factors

1. **Peak harvest timing** into the July–November scarcity window.
2. **₦12 million paid-in** (or ₦8 million + input loan) before Cycle 1 transplant.
3. **Bankable lease/option** with assignment rights and a holding fee, not an unpaid 100 ha promise.
4. **50/50 rule** and the **45 ha/cycle ceiling**.
5. **Bulk offtake signed before the +45 ha Regular step.**
6. **Cycle-level books from harvest one** (the cheapest future loan is an audit trail).
7. **Irrigation integrity** — yields are not rain-fed.

### 16.3 Recommendations to promoters

1. Incorporate SNLB Farms as a limited company; open a dedicated operating account; pay in ₦12 million.
2. Instruct counsel on the master option/lease before paying drip suppliers.
3. Commission soil and borehole tests on the first 10 ha this month.
4. Bind NAIC and GIT; hire the farm manager; engage an FMC on advisory terms.
5. Run Cycle 1 as a **proof cycle**, not a scale cycle. Use Cycle 2 Peak to fill the buffer.
6. Keep the promoter price deck in a management presentation; send lenders **this** IM and the credit-case tables.
7. Optional: after Cycle 2 audit pack, raise an ₦80 million BOA/NIRSAL-wrapped facility only if it accelerates packhouse quality — not because the model needs it.
8. Obtain a tax opinion on the 5-year agri holiday; do not spend the tax cash before the opinion.
9. Do not commit to processing, export, or a second 100 ha inside this NPV.

### 16.4 Final statement

The opportunity is real: a structural tomato deficit, a 1.5-hour corridor to the price-setting market, and a two-cycle calendar that turns national volatility into a P&L feature. The prior study proved the *idea*. This edition sizes the *cash*, the *CapEx*, the *tax*, and the *opening hole* so that a lender — or a disciplined self-funding promoter — can say yes with conditions, rather than yes with hope.

---

## 17. Appendices

### A. Glossary

| Term | Meaning |
| --- | --- |
| Regular season | Dec–Jun glut-aligned cycle |
| Peak / scarcity season | Jul–Nov cycle aligned with northern supply collapse |
| 50/50 rule | NPAT split: 50% cash buffer, 50% reinvestment |
| Master block | Contiguous 100 ha under option/lease |
| Credit case | Bank underwriting case in the model |
| DSCR | EBITDA / (interest + fees + principal) |
| NTA 2025 | Nigeria Tax Act 2025 (in force 1 Jan 2026) |
| NAIC | Nigerian Agricultural Insurance Corporation (or equivalent crop cover) |
| BOA | Bank of Agriculture |
| ACGSF | Agricultural Credit Guarantee Scheme Fund |
| SAPZ | Special Agro-Industrial Processing Zone |

### B. Model files

- Engine: `snlb-farms/model/financial_model.py`
- Full JSON: `snlb-farms/model/outputs/model_results.json`
- Credit cycle P&L: `snlb-farms/model/outputs/credit_cycle_pnl.csv`
- Credit annual: `snlb-farms/model/outputs/credit_annual.csv`
- Optional facility DSCR: `snlb-farms/model/outputs/credit_debt_dscr.csv`

### C. Primary sources and benchmarks

- NIHORT production guidance and HortiTom4 / HortiTom5 release notes (21.7–27.2 t/ha potential).
- Olam-Caraway public reporting (≈30 t/ha out-grower; higher on company fields, Jigawa).
- Mile 12 price points compiled from Businessday, Nairametrics, Vanguard and related reporting, Aug 2024 – Jul 2026 (see §6.2).
- NBS food inflation (May 2026: 16.96% y/y) — reference for 12% (credit) and 17% (downside) cost inflation.
- Nigeria Tax Act 2025: small-company test (₦50m turnover / ₦250m fixed assets); 30% CIT; 4% Development Levy; 5-year agri income-tax exemption for qualifying crop production (13th Schedule / s.163 as summarised by KPMG, UUBO, professional commentary). Confirm with counsel.
- BOA published production-loan charges: 9% interest, 0.5% appraisal, 0.5% commitment, 1% p.a. management, NAIC arable 2% of material inputs; SME documentary list (CAC, MEMART, CVs, lease, security, 10–20% lien deposit by product).
- ACGSF: up to 75% guarantee on qualifying agricultural loans.
- Industry estimates: national output ≈3.7 Mt; post-harvest loss 40–50%; paste imports US$350–400m.
- Drip kit / solar irrigation Nigerian retail ranges (2024–2026 dealer quotes, order of ₦0.25–1.5m per acre equivalent) — model uses **₦1.0m/ha incremental** plus shared headworks, i.e. mid-to-conservative commercial, not the cheapest kit.

### D. Open diligence log (not closed by this IM)

| # | Item | Owner | Closes |
| --- | --- | --- | --- |
| 1 | Exact block coordinates and survey | Promoter | Pre-ops |
| 2 | Soil laboratory report | Agronomist | Pre-ops |
| 3 | Borehole yield test to 100 ha duty | Irrigation engineer | Before C5; first 10 ha before C1 |
| 4 | Executed lease/option | Counsel | Pre-ops |
| 5 | CAC / TIN | Promoter | Pre-ops |
| 6 | Tax opinion (holiday vs 34%) | Tax adviser | Year 1 filing |
| 7 | Named farm manager | Promoter | Pre-ops |
| 8 | Three drip and seed quotations | Procurement | Pre-ops |
| 9 | NAIC proposal | Broker | Cycle 1 |
| 10 | Two Mile 12 LOIs | Commercial | Before C3 |
| 11 | Bulk term sheet | Commercial | Before C5 |
| 12 | OGEPA screening | ESG | Pre-ops / packhouse |
| 13 | Personal-guarantee capacity if a facility is sought | Promoter | Before term sheet |
| 14 | Related-party land affidavit | Counsel | Pre-ops |

### E. Document control

| Version | Date | Notes |
| --- | --- | --- |
| Operating study | Aug 2026 | 1–100 ha self-fund thesis; incomplete CapEx/tax/DCF |
| Expanded v1.1 | Aug 2026 | SWOT, ESG, implementation, still promoter economics |
| **Bankable v3.0** | **Aug 2026** | Three cases, phased CapEx, NTA 2025, DCF, DSCR, CP/data room |

Prepared for SNLB Farms. Not for general circulation. Replace this IM’s credit tables with live quotations and the site report before any binding credit application.
