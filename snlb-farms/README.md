# SNLB Farms — Comprehensive Feasibility Study

Commercial tomato production on a leased 100-hectare master block in Ogun State, Nigeria, supplying Mile 12 International Market, Lagos.

| Document | Description |
| --- | --- |
| [SNLB_Farms_Comprehensive_Feasibility_Study.pdf](./SNLB_Farms_Comprehensive_Feasibility_Study.pdf) | Print-ready A4 study (charts, three scenarios, DCF) — the document to circulate |
| [SNLB_Farms_Comprehensive_Feasibility_Study.md](./SNLB_Farms_Comprehensive_Feasibility_Study.md) | Source memorandum |
| [model/financial_model.py](./model/financial_model.py) | 5-year / 10-cycle model (base, upside, stress; optional ₦80m facility) |
| [model/generate_charts.py](./model/generate_charts.py) | Rebuild figures |
| [model/build_pdf.py](./model/build_pdf.py) | Rebuild the PDF |
| [charts/](./charts/) | Figures used in the study |

**Prepared:** August 2026  
**Entity:** SNLB Farms  
**Planning case:** Base case (conservative prices and yields, full cost stack, NTA 2025 tax)

Notion: https://app.notion.com/p/643182fa58b845f88534f33c5d5316f3

```bash
python3 model/financial_model.py
python3 model/generate_charts.py
python3 model/build_pdf.py
```
