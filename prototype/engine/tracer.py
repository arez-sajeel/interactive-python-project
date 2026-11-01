"""Cross-file execution tracer using sys.settrace.

The scenario runs in a child process with a timeout, so a runaway script cannot
hang the engine. Only frames from the scenario's own files are kept (no standard
library, tests or solution), and the trace is capped at MAX_EVENTS.
"""
import inspect
import json
import os
import runpy
import subprocess
import sys
import tempfile
import types
from pathlib import Path
from time import perf_counter

from engine.scenario import ROOT, Scenario

MAX_EVENTS = 2000
TIMEOUT_S = 5
REPR_LIMIT = 80


def trace(scenario: Scenario) -> dict:
    """Trace the scenario's entry point and return its events and a summary."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        out = Path(tmp) / "trace.json"
        cmd = [sys.executable, "-m", "engine.tracer", str(scenario.path), str(out),
               scenario.entry, *scenario.argv]
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
        start = perf_counter()
        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", env=env, timeout=TIMEOUT_S, check=False)
        except subprocess.TimeoutExpired:
            return {"events": [], "timed_out": True, "seconds": perf_counter() - start,
                    "error": f"Stopped after {TIMEOUT_S} s", "output": ""}
        seconds = perf_counter() - start
        if not out.exists():
            return {"events": [], "timed_out": False, "seconds": seconds,
                    "error": proc.stderr.strip() or "Tracer failed", "output": proc.stdout}
        result = json.loads(out.read_text(encoding="utf-8"))
    result.update(timed_out=False, seconds=seconds, output=proc.stdout)
    files = {e["file"] for e in result["events"]}
    result["files_crossed"] = sorted(files)
    result["defect_reached"] = any(
        e["file"] == scenario.defect_file and e["line"] == scenario.defect_line for e in result["events"]
    )
    return result


def executed_path(events: list[dict]) -> tuple[set[str], set[tuple[str, str]]]:
    """Graph nodes and call edges that were executed (used by the overlay)."""
    nodes = {e["node"] for e in events}
    edges = {(e["caller"], e["node"]) for e in events if e["event"] == "call" and e["caller"]}
    return nodes, edges


def format_trace(events: list[dict], mark: tuple[str, int] | None = None) -> str:
    """One readable line per step: step, event, file:line, function, changed variables."""
    lines = [f"{'step':>5}  {'event':<9} {'location':<16} {'function':<20} changes"]
    for i, e in enumerate(events, 1):
        changes = ", ".join(f"{k}={v}" for k, v in e["changes"].items())
        flag = "  <- defect line" if mark and (e["file"], e["line"]) == mark and e["event"] == "line" else ""
        lines.append(f"{i:>5}  {e['event']:<9} {e['file'] + ':' + str(e['line']):<16} "
                     f"{e['function']:<20} {changes}{flag}")
    return "\n".join(lines)


# Everything below runs inside the child process

def _safe_repr(value) -> str:
    try:
        text = repr(value)
    except Exception:  # pylint: disable=broad-except
        text = f"<{type(value).__name__}>"
    return text if len(text) <= REPR_LIMIT else text[:REPR_LIMIT - 3] + "..."


def _visible(name: str, value) -> bool:
    # ".0" is the hidden iterator argument of a generator expression
    return not name.startswith(("__", ".")) and not isinstance(
        value, (types.ModuleType, types.FunctionType, types.BuiltinFunctionType, type))


def _record(root: Path, entry: str, argv: list[str]) -> dict:
    files = {}  # normalised path -> relative file name, for the scenario's own files only
    for path in root.rglob("*.py"):
        rel = path.relative_to(root)
        if not {"tests", "solution"} & set(rel.parts[:-1]):
            files[os.path.normcase(str(path.resolve()))] = rel.as_posix()

    events, snapshots, last_line = [], {}, {}
    counts = {"raw": 0, "kept": 0}
    scope = {}  # code object -> (file, module) or None, cached

    def where(code):
        if code not in scope:
            rel = files.get(os.path.normcase(os.path.abspath(code.co_filename)))
            scope[code] = (rel, rel[:-3].replace("/", ".")) if rel else None
        return scope[code]

    def node(frame):
        _, module = where(frame.f_code)
        name = frame.f_code.co_qualname.split(".<locals>")[0]
        return module if name == "<module>" else f"{module}.{name}"

    def tracer(frame, event, arg):
        counts["raw"] += 1
        here = where(frame.f_code)
        if here is None:
            return tracer
        counts["kept"] += 1
        if len(events) >= MAX_EVENTS:
            return tracer

        # A line event fires before its line runs, so any variables changed since the
        # previous event belong to the previous line of this frame.
        key = id(frame)
        current = {k: _safe_repr(v) for k, v in dict(frame.f_locals).items() if _visible(k, v)}
        before = snapshots.get(key, {})
        changed = {k: v for k, v in current.items() if before.get(k) != v}
        snapshots[key] = current
        if key in last_line:
            last_line[key]["changes"].update(changed)

        caller, changes = None, {}
        if event == "call":
            back = frame.f_back
            caller = node(back) if back and where(back.f_code) else None
            changes = changed  # the arguments passed in
        elif event == "return":
            changes = {"return": _safe_repr(arg)}
        elif event == "exception":
            changes = {"raised": _safe_repr(arg[1])}

        record = {"event": event, "file": here[0], "line": frame.f_lineno or 1,
                  "function": frame.f_code.co_qualname, "node": node(frame),
                  "caller": caller, "changes": changes}
        events.append(record)
        if event == "line":
            last_line[key] = record
        elif event == "return":
            last_line.pop(key, None)
            if not frame.f_code.co_flags & inspect.CO_GENERATOR:  # generators resume later
                snapshots.pop(key, None)
        return tracer

    sys.path.insert(0, str(root))
    sys.argv = [str(root / entry), *argv]
    error = None
    sys.settrace(tracer)
    try:
        runpy.run_path(str(root / entry), run_name="__main__")
    except SystemExit as exc:
        if exc.code not in (None, 0):
            error = f"SystemExit: {exc.code}"
    except BaseException as exc:  # pylint: disable=broad-except
        error = f"{type(exc).__name__}: {exc}"
    finally:
        sys.settrace(None)
    return {"events": events, "raw_events": counts["raw"], "kept_events": counts["kept"],
            "truncated": counts["kept"] > MAX_EVENTS, "error": error}


if __name__ == "__main__":
    scenario_dir, out_file, entry_file, *args = sys.argv[1:]
    data = _record(Path(scenario_dir).resolve(), entry_file, args)
    Path(out_file).write_text(json.dumps(data), encoding="utf-8")
