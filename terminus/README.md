# Interstate coach terminus — cost–benefit analysis

Private **state-to-state** station: rent bays and clock-slots to private fleets. Do not own the buses. Take rent plus a piece of the **station economy** (retail, parking, ads, layover) — not the ticket.

**Download (PDF):**  
[Interstate_Terminus_CBA.pdf](https://github.com/dotuneasy-spec/Booktagger/raw/cursor/interstate-terminus-cba-eeeb/terminus/Interstate_Terminus_CBA.pdf)

| Document | Description |
| --- | --- |
| [Interstate_Terminus_CBA.pdf](./Interstate_Terminus_CBA.pdf) | Print-ready A4 note |
| [Interstate_Terminus_CBA.md](./Interstate_Terminus_CBA.md) | Source |
| [model/cba_model.py](./model/cba_model.py) | Three-case unlevered model |
| [model/outputs/](./model/outputs/) | JSON / CSV |

**Prepared:** August 2026  
**Planning capital:** ₦2.57 billion (highway-edge Lagos–Ogun, ~2 ha)  
**Planning Y3:** ₦542m EBITDA · ₦310m NPAT · unlevered IRR **16%**

```bash
python3 model/cba_model.py
python3 model/build_pdf.py
```
