# Scenario A: notes

- **Origin:** STAND-IN. Written by the researcher to develop the engine. It is not LLM output
  and must not be reported as evidence. Replace `main.py` and `calc.py` with ChatGPT's output,
  then update `scenario.json` (`origin`, `defect`, `expected_calls`) and this file.
- **Table 3 category:** Intent conflict
- **Defect:** `calc.py` line 7 adds the discount to the subtotal instead of taking it off.
- **Occurred naturally or injected:** n/a (stand-in)
- **Manual list of cross-file calls** (for the accuracy check, also in `scenario.json`):
  1. `main.main` → `calc.basket_total`
  2. `main.main` → `calc.format_price`
