# SNLB Farms — Bankable Feasibility Study

Commercial tomato production on a leased 100-hectare master block in Ogun State, Nigeria, supplying Mile 12 International Market, Lagos.

| Document | Description |
| --- | --- |
| [SNLB_Farms_Bankable_Feasibility_Study.pdf](./SNLB_Farms_Bankable_Feasibility_Study.pdf) | Print-ready A4 information memorandum (22 pages) — send this to lenders |
| [SNLB_Farms_Bankable_Feasibility_Study.md](./SNLB_Farms_Bankable_Feasibility_Study.md) | Full information memorandum (credit snapshot, three-case financials, security package, conditions precedent, data-room index) |
| [model/financial_model.py](./model/financial_model.py) | Reproducible 5-year / 10-cycle model (promoter, credit, downside; optional ₦80m facility) |
| [model/build_pdf.py](./model/build_pdf.py) | Rebuild the PDF from the markdown |
| [model/outputs/](./model/outputs/) | JSON and CSV exports used in the IM |

**Edition:** Bankable v3.0 — August 2026  
**Entity:** SNLB Farms  
**Primary underwriting case:** Credit / bank base case (fully taxed, haircut prices and yields, complete cost stack)

Notion (credit snapshot + four section pages): https://app.notion.com/p/3bb952dc33be81d9856edaf100ca2ddf

Run the model:

```bash
python3 model/financial_model.py
```

Rebuild the PDF (requires `markdown` and `weasyprint`):

```bash
python3 model/build_pdf.py
```
