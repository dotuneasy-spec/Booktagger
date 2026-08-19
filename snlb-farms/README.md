# SNLB Farms — Comprehensive Feasibility Study

Commercial tomato production on a leased 100-hectare master block in Ogun State, Nigeria, supplying Mile 12 International Market, Lagos.

**Download the circulating study (PDF):**  
https://github.com/dotuneasy-spec/Booktagger/raw/cursor/snlb-bankable-feasibility-3a17/snlb-farms/SNLB_Farms_Comprehensive_Feasibility_Study.pdf

| Document | Description |
| --- | --- |
| [SNLB_Farms_Comprehensive_Feasibility_Study.pdf](./SNLB_Farms_Comprehensive_Feasibility_Study.pdf) | Print-ready A4 study (charts, three scenarios, DCF) — the document to circulate |
| [SNLB_Farms_Comprehensive_Feasibility_Study.md](./SNLB_Farms_Comprehensive_Feasibility_Study.md) | Source memorandum |
| [model/financial_model.py](./model/financial_model.py) | 5-year / 10-cycle model (base, upside, stress; optional ₦80m facility) |
| [model/generate_charts.py](./model/generate_charts.py) | Rebuild figures |
| [model/build_pdf.py](./model/build_pdf.py) | Rebuild the PDF |
| [charts/](./charts/) | Figures used in the study |
| [FarmPark_Partner_File.md](./FarmPark_Partner_File.md) | How FarmPark operates, public track record (Epe, *Sun* interview, no audited accounts), capital-at-work visuals, tomato-farm RACI, remaining DD gaps |
| [Cycle1_8m_Spend_Rundown.md](./Cycle1_8m_Spend_Rundown.md) | Model 1-ha tomato plan + August 2026 line-item uses for the ₦8 million pack |
| [legal/SNLB_ENTERPRISE_CAC_BN_6922259.pdf](./legal/SNLB_ENTERPRISE_CAC_BN_6922259.pdf) | CAC business-name certificate (31 March 2023) |

**Prepared:** August 2026  
**Entity:** SNLB ENTERPRISE (CAC BN 6922259) → proposed **SNLB Farms Limited** (§2.1 of the study)  
**Opening capital:** ₦8,000,000 (₦3.0m CapEx + ₦5.0m Cycle 1 working capital)  
**Planning case:** Regular first at non-glut Mile 12 prices — 20/18 t/ha, ₦33,000 / ₦145,000 baskets, full cost stack, NTA 2025 tax

Notion: https://app.notion.com/p/643182fa58b845f88534f33c5d5316f3

```bash
python3 model/financial_model.py
python3 model/generate_charts.py
python3 model/build_pdf.py
```
