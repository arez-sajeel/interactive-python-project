# Scenario A: notes

**Origin:** GPT-6 (ChatGPT), attempt 1, with one line injected by hand. See PROMPT.md.

**Defect category:** Intent conflict

**Occurred naturally:** no. Neither attempt produced an intent conflict, so one was injected.

**Injected change:** `calc.py` line 12

```diff
-        subtotal *= Decimal("0.90")
+        subtotal -= Decimal("0.10")
```

The code still runs, but it takes 10p off instead of 10%, so the sample basket of £44.00
comes to £43.90 rather than £39.60. Attempt 1 was used because its sample basket is over
£40, so the faulty line runs. ChatGPT's original line is in `solution/calc.py`.

**Observations from ChatGPT's output:**

- Attempt 1 was correct. Bandit found nothing; pylint found 2 missing module docstrings.
  The threshold and rate are written inline as `Decimal("40")` and `Decimal("0.90")`, but
  pylint's magic value check (R2004) only looks at comparisons with a literal value, so it
  reports neither: `Decimal("40")` is a function call, and the rate is used in a multiplication.
- Attempt 2 was also correct, using floats instead of `Decimal`. pylint reported the
  magic value `40` in `subtotal >= 40` (R2004), but not `0.90` in `subtotal *= 0.90`.
  Its stated output (£34.20) contradicted its own explanation that the £38.00 subtotal
  gets no discount; the code correctly prints £38.00.
- After the injected change, Bandit and pylint still report nothing beyond missing
  docstrings, so neither tool detects the intent conflict.

**Expected cross-file calls:**

1. `main` (module level) → `calc.basket_total`
2. `main` (module level) → `calc.format_price`
