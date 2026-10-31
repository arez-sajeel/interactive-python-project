"""Run Bandit and pylint on a scenario and map findings to Table 3 (PFR7)."""
import csv
import json
import subprocess
import sys
from collections import Counter

from engine.scenario import RESULTS, Scenario

# Rule -> (Table 3 defect category, fault type). Intent conflicts and logic faults
# cannot be found statically, so they are recorded by hand in each scenario's NOTES.md.
TABLE3 = {
    **dict.fromkeys(["B602", "B604", "B605", "B609"], ("Security Flaws", "Command Injection (CWE-78)")),
    **dict.fromkeys(["B105", "B106", "B107"], ("Security Flaws", "Hardcoded Credentials (CWE-798)")),
    "W0613": ("Syntactic & Stylistic", "Unused Parameters"),
    "R2004": ("Syntactic & Stylistic", "Magic Constants"),
    **dict.fromkeys(["E0401", "E0611", "E0602", "E1101", "E1120", "E1121", "E1123"],
                    ("Repository Level", "Broken Dependencies")),
}


def scan(scenario: Scenario) -> dict:
    RESULTS.mkdir(exist_ok=True)
    files = [str(p.relative_to(scenario.path)) for p in scenario.source_files()]
    bandit_out = RESULTS / f"bandit_{scenario.id}.json"
    pylint_txt = RESULTS / f"pylint_{scenario.id}.txt"
    pylint_json = RESULTS / f"pylint_{scenario.id}.json"

    subprocess.run([sys.executable, "-m", "bandit", "-q", "-f", "json", "-o", str(bandit_out), *files],
                   cwd=scenario.path, capture_output=True, check=False, timeout=120)
    subprocess.run([sys.executable, "-m", "pylint", "--load-plugins=pylint.extensions.magic_value",
                    f"--output-format=text:{pylint_txt},json2:{pylint_json}", *files],
                   cwd=scenario.path, capture_output=True, check=False, timeout=120)

    findings = [
        ("bandit", r["test_id"], r["issue_text"], f"{r['filename']}:{r['line_number']}")
        for r in json.loads(bandit_out.read_text(encoding="utf-8"))["results"]
    ] + [
        ("pylint", m["messageId"], m["message"], f"{m['path']}:{m['line']}")
        for m in json.loads(pylint_json.read_text(encoding="utf-8"))["messages"]
    ]

    with (RESULTS / f"table3_{scenario.id}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "fault_type", "tool", "rule", "message", "location"])
        for tool, rule, message, location in findings:
            if rule in TABLE3:
                writer.writerow([*TABLE3[rule], tool, rule, message, location])

    return {
        "bandit": Counter(rule for tool, rule, *_ in findings if tool == "bandit"),
        "pylint": Counter(rule for tool, rule, *_ in findings if tool == "pylint"),
        "table3": sorted({TABLE3[rule][1] for _, rule, *_ in findings if rule in TABLE3}),
    }
