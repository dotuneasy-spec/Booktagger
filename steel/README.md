# Ashlar Steel — Billet and Semi-Finished Steel CBA

**Download the study (PDF):**  
[Billet_Semifinished_Steel_CBA.pdf](https://github.com/dotuneasy-spec/Booktagger/raw/cursor/steel-billets-cba-eeeb/steel/Billet_Semifinished_Steel_CBA.pdf)

Independent plan for two Nigerian companies under one holding: a **150 kt longs rolling mill** (rebar, wire rod, merchant bar) and a **200 kt captive billet melt shop**. Ogun industrial corridor. Phase 1 first; melt only after utilisation and gas gates. Not Ajaokuta. Not a ₦100 billion-profit opening case.

| Document | Description |
| --- | --- |
| [Billet_Semifinished_Steel_CBA.pdf](./Billet_Semifinished_Steel_CBA.pdf) | Print-ready A4 cost–benefit analysis |
| [Billet_Semifinished_Steel_CBA.md](./Billet_Semifinished_Steel_CBA.md) | Source memorandum |
| [charts/](./charts/) | Figures used in the study |
| [model/cba_model.py](./model/cba_model.py) | Ten-year three-case model + concession + 1.0 Mt option |
| [model/generate_charts.py](./model/generate_charts.py) | Rebuild figures |
| [model/build_pdf.py](./model/build_pdf.py) | Rebuild the PDF |
| [model/outputs/](./model/outputs/) | JSON and CSV extracts |

**Prepared:** September 2026 (v1.0)  
**Opening plan:** Ashlar Longs Ltd — 150 kt, ₦82 billion plant, ₦28.7 billion equity  
**Gated second company:** Ashlar Billets Ltd — 200 kt captive EAF, ₦163 billion plant

```bash
python3 model/cba_model.py
python3 model/generate_charts.py
python3 model/build_pdf.py
```

`matplotlib`, `markdown` and `weasyprint` are required (`pip install -r model/requirements.txt`).
