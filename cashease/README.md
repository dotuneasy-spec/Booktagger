# CashEase Nigeria — Feasibility Study

Independent multi-service cash kiosks (note-breaking, POS cash-out, airtime and bills) in Nigeria.

This folder turns the **progressed final plan** from a shared Grok conversation (February–May 2026) into a feasibility study: own the machines, do not sell them to banks or the CBN, partner with banks only for cash and settlement, and treat 20,000 kiosks / ₦90 billion as an earned option.

| Document | Description |
| --- | --- |
| [CashEase_Feasibility_Study.md](./CashEase_Feasibility_Study.md) | The study — model, market, operations, three-case financials, BOI/DSCR, go/no-go |
| [charts/](./charts/) | Figures used in the study |
| [model/financial_model.py](./model/financial_model.py) | Six-year model (stress / planning / promoter, hold cases, BOI overlays) |
| [model/generate_charts.py](./model/generate_charts.py) | Rebuild figures |
| [model/outputs/](./model/outputs/) | JSON and CSV extracts |

**Prepared:** August 2026  
**Planning first commitment:** 350 kiosks · ₦1.85 billion equity  
**Verdict:** The model is feasible. Phase 1 is the only present commitment. ₦90 billion on a 20,000-kiosk sprint is not bankable on planning economics.

```bash
python3 model/financial_model.py
python3 model/generate_charts.py
```

`matplotlib` is required for charts (`pip install -r model/requirements.txt`).
