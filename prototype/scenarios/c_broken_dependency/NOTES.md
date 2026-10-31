# Scenario C: notes

- **Origin:** STAND-IN. Written by the researcher to develop the engine. It is not LLM output
  and must not be reported as evidence. Replace `main.py` and `helpers.py` with ChatGPT's
  output, then update `scenario.json` (`origin`, `defect`, `expected_calls`) and this file.
- **Table 3 category:** Broken dependencies
- **Defect:** `main.py` line 6 calls `helpers.make_slug`, but `helpers.py` defines `slugify`.
- **Occurred naturally or injected:** n/a (stand-in)
- **Manual list of cross-file calls:**
  1. `main.summarise` → `helpers.word_count`
  2. `main.summarise` → `helpers.make_slug` (no matching definition)
