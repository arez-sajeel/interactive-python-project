"""Append one row per run to results/metrics.csv."""
import csv
from datetime import datetime

from engine.scenario import RESULTS, Scenario

METRICS = RESULTS / "metrics.csv"
FIELDS = ["timestamp", "scenario", "origin", "step", "count", "time_s", "notes"]


def log(scenario: Scenario | None, step: str, count="", time_s: float | str = "", notes: str = "") -> None:
    RESULTS.mkdir(exist_ok=True)
    new = not METRICS.exists()
    with METRICS.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, FIELDS)
        if new:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "scenario": scenario.name if scenario else "",
            "origin": scenario.origin if scenario else "",
            "step": step,
            "count": count,
            "time_s": f"{time_s:.3f}" if isinstance(time_s, float) else time_s,
            "notes": notes,
        })
