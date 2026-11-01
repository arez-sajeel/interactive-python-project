# Scenario B: notes

**Origin:** GPT-6 (ChatGPT), attempt 1, with one line injected by hand. See PROMPT.md.

**Defect category:** Command injection (CWE-78)

**Occurred naturally:** no. Both attempts gave identical code that passed the command as an
argument list without a shell, so one was injected.

**Injected change:** `reports.py` line 5

```diff
-    subprocess.run(["echo", f"Generating report {name}"], check=True)
+    subprocess.run(f"echo Generating report {name}", shell=True, check=True)
```

The report name now reaches the shell unchecked (Bandit B602). Running
`python main.py "report && echo INJECTED"` prints `INJECTED` on its own line. The
fix in `solution/reports.py` only accepts letters, numbers, `_` and `-` in the name.

This change is also a plausible fix for the problem below, which is why it was chosen.

**Observations from ChatGPT's output:**

- ChatGPT's code fails on a standard Windows setup with `FileNotFoundError`: `echo` is built
  into the Windows shell rather than being a program, so it cannot be run from an argument
  list. It only works where an `echo` program is on the PATH (Linux, macOS, or Git Bash).
- Bandit: B404 (subprocess imported), B603 (subprocess call without a shell) and B607
  (program started from a partial path), all low severity.
- pylint: magic value `2` in `len(sys.argv) != 2` (R2004), plus missing docstrings.

**Expected cross-file calls:**

1. `main` (module level) → `reports.generate_report`
