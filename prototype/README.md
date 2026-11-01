# Interactive Python Project: prototype

A proof of concept for the analysis engine behind the project. Given a small multi-file
Python project, it can:

- scan the code with Bandit and pylint
- build a dependency graph of imports and cross-file calls (ast and networkx)
- trace execution across files with `sys.settrace`
- highlight the executed path on the dependency graph
- run unit tests in a separate process with a 5 second time limit

There is also a simple Streamlit page that shows the code, graph and trace together.

## Requirements

- Python 3.11 or later (tested on Windows 11 with Python 3.14)

## Setup

```
cd prototype
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS or Linux
pip install -r requirements.txt
```

## Usage

```
python run.py list              # list the scenarios
python run.py all a             # run every step on scenario A
python run.py graph b           # or a single step: scan, graph, trace, overlay, test
python run.py timeout           # check the time limit stops an infinite loop
streamlit run app.py            # open the Streamlit page
```

Output files are written to `results/`, and each run adds a row to `results/metrics.csv`.

| Output | Contents |
|---|---|
| `bandit_<id>.json`, `pylint_<id>.txt`, `defects_<id>.csv` | Scan reports and findings grouped by defect category |
| `graph_<id>.png` | Dependency graph |
| `trace_<id>.txt`, `trace_<id>.jsonl` | Step-by-step trace: file, line, function and changed variables |
| `overlay_<id>.png` | Dependency graph with the executed path highlighted |
| `metrics.csv` | Timings, counts and test results for each run |

Graph and trace times are the median of 5 runs. The graph time covers parsing and building
the graph, not drawing it. The trace time includes starting the child process.

## Scenarios

| ID | Defect type | Files |
|---|---|---|
| A | Intent conflict: runs, but gives the wrong total | `main.py`, `calc.py` |
| B | Command injection (CWE-78) | `main.py`, `reports.py` |
| C | Broken dependency: calls a function that was renamed | `main.py`, `helpers.py` |

Each scenario folder contains:

```
main.py, ...        code to analyse
tests/              unit tests that fail before the fix and pass after
solution/           fixed version of the faulty file
scenario.json       entry point, defect location, expected cross-file calls, origin
PROMPT.md           prompt, model and date used to generate the code
NOTES.md            description of the defect
```

The current scenarios contain hand-written placeholder code (`"origin": "hand-written"`)
and will be replaced with LLM-generated code.

## Safety

Scenario code and tests run in a separate process with a time limit, and commands are
passed as argument lists rather than through a shell. Scenario B is the only place a shell
is used, and it only runs `echo`.

## Known limitations

- Method calls on object instances (for example `basket.add()`) are not detected by the graph.
- Packages with relative imports are treated as flat modules.
