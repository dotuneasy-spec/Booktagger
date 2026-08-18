# CashEase Nigeria — Feasibility Study

**Download the study (PDF):**  
[CashEase_Feasibility_Study.pdf](https://github.com/dotuneasy-spec/Booktagger/raw/cursor/cashease-feasibility-study-eeeb/cashease/CashEase_Feasibility_Study.pdf)

If that asks you to log in, open the same file from the pull request: [PR #3](https://github.com/dotuneasy-spec/Booktagger/pull/3) → Files changed → `cashease/CashEase_Feasibility_Study.pdf`.

Independent multi-service cash kiosks (note-breaking, POS cash-out, airtime and bills) in Nigeria.

This folder is the **feasibility study document** for CashEase: own the machines, do not sell them to banks or the CBN, partner with banks only for cash and settlement, one machine per counted pitch, density before nationwide, and treat 20,000 kiosks / ₦90 billion as an earned option (revenue possible; profit and a single ₦90bn loan are outside the model).

| Document | Description |
| --- | --- |
| [CashEase_Feasibility_Study.pdf](./CashEase_Feasibility_Study.pdf) | Print-ready A4 study — the document to circulate |
| [CashEase_Feasibility_Study.md](./CashEase_Feasibility_Study.md) | Source memorandum |
| [charts/](./charts/) | Figures used in the study |
| [model/financial_model.py](./model/financial_model.py) | Six-year model (stress / planning / promoter, hold cases, BOI overlays) |
| [model/generate_charts.py](./model/generate_charts.py) | Rebuild figures |
| [model/build_pdf.py](./model/build_pdf.py) | Rebuild the PDF |
| [model/outputs/](./model/outputs/) | JSON and CSV extracts |

**Prepared:** August 2026 (v1.2)  
**Planning first commitment:** 350 kiosks · ₦1.85 billion equity  
**Verdict:** The model is feasible. Phase 1 is the only present commitment. ₦90 billion **profit** or a **single ₦90bn loan** is outside the model. ₦90bn+ **revenue** is an earned 20,000-site option.

```bash
python3 model/financial_model.py
python3 model/generate_charts.py
python3 model/build_pdf.py
```

`matplotlib`, `markdown` and `weasyprint` are required (`pip install -r model/requirements.txt`).
