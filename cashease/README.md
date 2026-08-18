# CashEase Nigeria — Feasibility Study

**Download the study (PDF):**  
[CashEase_Feasibility_Study.pdf](https://github.com/dotuneasy-spec/Booktagger/raw/cursor/cashease-feasibility-study-eeeb/cashease/CashEase_Feasibility_Study.pdf)

If that asks you to log in, open the same file from the pull request: [PR #3](https://github.com/dotuneasy-spec/Booktagger/pull/3) → Files changed → `cashease/CashEase_Feasibility_Study.pdf`.

Owned multi-service cash kiosks on livelihood paths in Nigeria: note-breaking, POS cash-out, airtime and bills. The company owns the machines; a bank supplies float. One machine per counted pitch. Opening plan: **350 kiosks, ₦1.85 billion**, then **2,000** with an ₦8–12 billion facility.

| Document | Description |
| --- | --- |
| [CashEase_Feasibility_Study.pdf](./CashEase_Feasibility_Study.pdf) | Print-ready A4 study — the document to circulate |
| [CashEase_Feasibility_Study.md](./CashEase_Feasibility_Study.md) | Source memorandum |
| [charts/](./charts/) | Figures used in the study |
| [model/financial_model.py](./model/financial_model.py) | Six-year model |
| [model/generate_charts.py](./model/generate_charts.py) | Rebuild figures |
| [model/build_pdf.py](./model/build_pdf.py) | Rebuild the PDF |
| [model/outputs/](./model/outputs/) | JSON and CSV extracts |

**Prepared:** August 2026 (v2.3)  
**Opening plan:** 350 kiosks · ₦1.85 billion equity  
**First operating scale:** 2,000 kiosks with ₦8–12 billion facility after Phase 1 data

```bash
python3 model/financial_model.py
python3 model/generate_charts.py
python3 model/build_pdf.py
```

`matplotlib`, `markdown` and `weasyprint` are required (`pip install -r model/requirements.txt`).
