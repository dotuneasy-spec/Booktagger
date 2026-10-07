# CashEase Nigeria — feasibility study (v3)

Fresh study of self-service cash kiosks for Dotun in Lagos. It does not update or depend on any earlier CashEase file.

- PDF: `CashEase_Nigeria_Feasibility_Study.pdf`
- HTML source: `source/study.html`
- Model: `model/financial_model.py` (outputs `model/outputs/results.json`)
- Charts: `charts/`

Regenerate from this folder:

```bash
python3 source/build_study.py
```

Needs Python 3 with `matplotlib` (`model/requirements.txt`) and Google Chrome for the PDF step.

External facts are cited in the sources section of the study. Planning choices are tagged as assumptions inside the model and the PDF. The model is pre-tax, nominal, and flat. It is not a forecast of demand.
