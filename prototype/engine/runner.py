"""Run a scenario's unit tests in a separate process with a timeout (PFR6, PNFR2).

Commands are passed as argument lists (never through a shell), and the child
process is killed if it runs longer than TIMEOUT_S.
"""
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

TIMEOUT_S = 5


@dataclass
class TestResult:
    passed: int
    failed: int
    timed_out: bool
    seconds: float
    output: str

    @property
    def ok(self) -> bool:
        return not self.timed_out and self.failed == 0 and self.passed > 0

    def summary(self) -> str:
        if self.timed_out:
            return f"Stopped after {self.seconds:.1f} s (time limit {TIMEOUT_S} s)"
        return f"{self.passed} passed, {self.failed} failed"


def run_tests(folder: Path) -> TestResult:
    """Run pytest on the tests/ folder inside a scenario folder (or a copy of one)."""
    cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", "tests"]
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    start = perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=folder, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=TIMEOUT_S, env=env, check=False)
    except subprocess.TimeoutExpired:
        return TestResult(0, 0, True, perf_counter() - start, "")
    seconds = perf_counter() - start
    counts = {kind: int(n) for n, kind in re.findall(r"(\d+) (passed|failed|errors?)\b", proc.stdout)}
    failed = counts.get("failed", 0) + counts.get("error", 0) + counts.get("errors", 0)
    if proc.returncode not in (0, 1) and not failed:  # collection error, e.g. a broken import
        failed = 1
    return TestResult(counts.get("passed", 0), failed, False, seconds, proc.stdout + proc.stderr)


def timeout_check() -> TestResult:
    """Run a test that never ends, to show the time limit stops runaway code (Q6)."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        tests = Path(tmp) / "tests"
        tests.mkdir()
        (tests / "test_loop.py").write_text("def test_loop():\n    while True:\n        pass\n", encoding="utf-8")
        return run_tests(Path(tmp))
