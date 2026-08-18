# SNLB Farms — Comprehensive Feasibility Study

Commercial tomato production on a leased 100-hectare master block in Ogun State, Nigeria, supplying Mile 12 International Market, Lagos.

| Document | Description |
| --- | --- |
| [SNLB_Farms_Comprehensive_Feasibility_Study.pdf](./SNLB_Farms_Comprehensive_Feasibility_Study.pdf) | Print-ready A4 study (charts, three scenarios, DCF) — the document to circulate |
| [SNLB_Farms_Comprehensive_Feasibility_Study.md](./SNLB_Farms_Comprehensive_Feasibility_Study.md) | Source memorandum |
| [model/financial_model.py](./model/financial_model.py) | 5-year / 10-cycle model (base, upside, stress; optional ₦80m facility) |
| [model/generate_charts.py](./model/generate_charts.py) | Rebuild figures |
| [model/build_pdf.py](./model/build_pdf.py) | Rebuild the PDF |
| [FarmPark_Partner_File.md](./FarmPark_Partner_File.md) | Public desk file on the intended FMC (King’s Deck, Chevron, Lekki) and the gaps still open |

**Prepared:** August 2026  
**Entity:** SNLB Farms  
**Opening capital:** ₦8,000,000 (₦3.0m CapEx + ₦5.0m Cycle 1 working capital)  
**Planning case:** Regular first at non-glut Mile 12 prices — 20/18 t/ha, ₦33,000 / ₦145,000 baskets, full cost stack, NTA 2025 tax

Notion: https://app.notion.com/p/643182fa58b845f88534f33c5d5316f3

```bash
python3 model/financial_model.py
python3 model/generate_charts.py
python3 model/build_pdf.py
```
