# Scenario B: notes

- **Origin:** STAND-IN. Written by the researcher to develop the engine. It is not LLM output
  and must not be reported as evidence. Replace `main.py` and `reports.py` with ChatGPT's
  output, then update `scenario.json` (`origin`, `defect`, `expected_calls`) and this file.
- **Table 3 category:** Command injection (CWE-78), Bandit B602
- **Defect:** `reports.py` line 10 passes the unsanitised name to a shell (`shell=True`).
  The input `report && echo INJECTED` runs a second command. `&&` works in both cmd.exe and sh.
- **Occurred naturally or injected:** n/a (stand-in)
- **Manual list of cross-file calls:**
  1. `main.main` → `reports.generate_report`
