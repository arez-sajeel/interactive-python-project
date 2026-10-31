# Interactive Python Project: proof of concept (Section 3.7)

Engine behind RQ1 and RQ2: dependency graph (ast and networkx), cross-file tracer
(sys.settrace), executed-path overlay, and a test runner with a time limit. There is also a
minimal Streamlit page. Requirement IDs (PFR, PNFR) refer to the prototype brief.

## Set up (Windows, Python 3.11 or later, no Docker)

```powershell
cd prototype
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```powershell
python run.py list          # scenarios and their origin
python run.py all a         # scan, graph, trace, overlay, tests and timeout for Scenario A
python run.py graph b       # or one step at a time: scan, graph, trace, overlay, test
python run.py timeout       # infinite loop stopped by the 5 s limit
streamlit run app.py        # code, graph and trace on one page
```

Outputs go to `results/`, and every run adds a row to `results/metrics.csv`.

| File | Question | Requirement |
|---|---|---|
| `bandit_<id>.json`, `pylint_<id>.txt`, `table3_<id>.csv` | Q1 | PFR7 |
| `graph_<id>.png`, accuracy row in `metrics.csv` | Q2, Q5 | PFR1, PFR2, PNFR3 |
| `trace_<id>.jsonl`, `trace_<id>.txt` (Diagram 6) | Q3, Q5 | PFR3, PFR4, PNFR4 |
| `overlay_<id>.png` (Diagram 5) | Q4 | PFR5 |
| `tests_before_fix`, `tests_after_fix`, `timeout_check` rows | Q6 | PFR6, PNFR2 |
| `solve` row, logged by the Streamlit page when your edit makes the tests pass | Q7 | UC6 |

Graph and trace times are the median of 5 runs. Graph time covers parsing and building only,
not drawing. Trace time includes starting the child process.

## Scenarios

```
scenarios/<id>_<name>/
├── main.py, ...        code under study (the entry point is set in scenario.json)
├── tests/              unit tests: fail before the fix, pass after
├── solution/           fixed files, copied over a temporary copy for "after fix"
├── scenario.json       entry point, arguments, defect file and line, manual call list, origin
├── PROMPT.md           ChatGPT prompt, model, date and output
└── NOTES.md            defect, Table 3 category, natural or injected
```

**The three scenarios here are stand-ins written by hand**, so the engine could be built and
checked. They are labelled `"origin": "stand-in"`, the CLI warns when you run them, and
`metrics.csv` records the origin on every row. Do not report their results as evidence.

To replace one with real LLM output (UC1):

1. Run the prompt in `PROMPT.md` in ChatGPT. Save the reply, model and date in `PROMPT.md`.
2. Replace the `.py` files with the output. Write or adapt `tests/` and add the fix to `solution/`.
3. Update `scenario.json`: `origin` (`llm` or `llm+injected`), `defect`, and `expected_calls`.
   Write `expected_calls` by reading the code, before running the graph, so the accuracy check
   stays independent.
4. Record in `NOTES.md` whether the defect occurred naturally or was injected.
5. Run `python run.py all <id>` and commit.

## Safety (PNFR2)

Scenario code and tests run in a separate process, with an argument list (never a shell) and
a 5 s limit. The only shell call is inside Scenario B, and it runs `echo`.

## Known limitations

- Calls on object instances (`basket.add()`) are not resolved by the static graph.
- Relative imports in packages are treated as flat modules; the scenarios are flat.
