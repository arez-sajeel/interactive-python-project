"""Researcher CLI: run each prototype step on a scenario and log metrics.

    python run.py list
    python run.py all a           every step below, in build order
    python run.py scan a          Bandit and pylint (PFR7)
    python run.py graph a         dependency graph and accuracy (PFR1, PFR2, PNFR3)
    python run.py trace a         execution trace (PFR3, PFR4)
    python run.py overlay a       executed path on the graph (PFR5)
    python run.py test a          tests before and after the fix (PFR6)
    python run.py timeout         infinite loop stopped by the time limit (Q6)

Graph and trace times are the median of 5 runs (PNFR1).
"""
import argparse
import json
import statistics
import sys
from time import perf_counter

from engine import deps, metrics, overlay, runner, scan
from engine.scenario import RESULTS, Scenario, all_scenarios, load
from engine.tracer import format_trace, trace

RUNS = 5
TARGET_S = 2.5


def median_time(fn) -> tuple[float, object]:
    times, result = [], None
    for _ in range(RUNS):
        start = perf_counter()
        result = fn()
        times.append(perf_counter() - start)
    return statistics.median(times), result


def check(ok: bool) -> str:
    return "yes" if ok else "NO"


def do_scan(s: Scenario):
    result = scan.scan(s)
    for tool in ("bandit", "pylint"):
        found = result[tool]
        print(f"{tool}: {sum(found.values())} findings  {dict(found.most_common())}")
        metrics.log(s, f"scan_{tool}", sum(found.values()), notes=json.dumps(dict(found)))
    print(f"Table 3 types found: {', '.join(result['table3']) or 'none'}")
    metrics.log(s, "scan_table3", len(result["table3"]), notes="; ".join(result["table3"]))
    print(f"Saved bandit_{s.id}.json, pylint_{s.id}.txt and table3_{s.id}.csv")


def do_graph(s: Scenario):
    seconds, graph = median_time(lambda: deps.build_graph(s))
    acc = deps.accuracy(graph, s.expected_calls)
    path = deps.save(graph, RESULTS / f"graph_{s.id}.png")
    print(deps.describe(graph))
    print(f"\nCross-file calls found: {acc['found']} of {acc['listed']} listed by hand")
    for a, b in acc["missed"]:
        print(f"  missed: {a} -> {b}")
    for a, b in acc["extra"]:
        print(f"  not in manual list: {a} -> {b}")
    print(f"Build time (median of {RUNS}): {seconds:.3f} s  under {TARGET_S} s: {check(seconds < TARGET_S)}")
    print(f"Saved {path.name}")
    metrics.log(s, "graph_build", acc["found"], seconds,
                f"{acc['found']}/{acc['listed']} listed calls found; {len(acc['extra'])} extra; "
                f"{graph.number_of_nodes()} nodes; median of {RUNS}; ast+networkx only, drawing excluded")
    return graph


def do_trace(s: Scenario):
    seconds, result = median_time(lambda: trace(s))
    if result["timed_out"] or not result["events"]:
        print(f"Trace failed: {result['error']}")
        metrics.log(s, "trace", 0, seconds, f"failed: {result['error']}")
        return result
    (RESULTS / f"trace_{s.id}.jsonl").write_text(
        "\n".join(json.dumps(e) for e in result["events"]) + "\n", encoding="utf-8")
    text = format_trace(result["events"], mark=(s.defect_file, s.defect_line))
    (RESULTS / f"trace_{s.id}.txt").write_text(text + "\n", encoding="utf-8")
    print(text)
    if result["output"]:
        print(f"\nProgram output:\n{result['output'].rstrip()}")
    if result["error"]:
        print(f"Program stopped with {result['error']}")
    print(f"\nEvents: {result['raw_events']} before filtering, {result['kept_events']} after"
          f"{' (capped)' if result['truncated'] else ''}")
    print(f"Files crossed: {len(result['files_crossed'])} ({', '.join(result['files_crossed'])})")
    print(f"Defect line {s.defect_file}:{s.defect_line} reached: {check(result['defect_reached'])}")
    print(f"Trace time (median of {RUNS}): {seconds:.3f} s  under {TARGET_S} s: {check(seconds < TARGET_S)}")
    print(f"Saved trace_{s.id}.jsonl and trace_{s.id}.txt")
    metrics.log(s, "trace", result["kept_events"], seconds,
                f"raw {result['raw_events']}; files crossed {len(result['files_crossed'])}; "
                f"defect line reached {check(result['defect_reached'])}; median of {RUNS}; includes process start")
    return result


def do_overlay(s: Scenario, graph=None, result=None):
    graph = graph or deps.build_graph(s)
    result = result or trace(s)
    path = RESULTS / f"overlay_{s.id}.png"
    counts = overlay.save(graph, result["events"], path)
    print(f"Highlighted {counts['nodes']} nodes and {counts['edges']} calls "
          f"({counts['cross_file_edges']} cross-file). Saved {path.name}")
    metrics.log(s, "overlay", counts["nodes"], notes=f"{counts['edges']} calls highlighted, "
                f"{counts['cross_file_edges']} cross-file")


def do_test(s: Scenario):
    for label, fixed in (("before fix", False), ("after fix", True)):
        with s.workspace(fixed=fixed) as copy:
            result = runner.run_tests(copy.path)
        print(f"Tests {label}: {result.summary()} in {result.seconds:.2f} s")
        metrics.log(s, f"tests_{label.replace(' ', '_')}", result.passed, result.seconds, result.summary())


def do_timeout():
    result = runner.timeout_check()
    print(f"Infinite loop stopped by the time limit: {check(result.timed_out)} "
          f"({result.seconds:.2f} s, limit {runner.TIMEOUT_S} s)")
    metrics.log(None, "timeout_check", "", result.seconds, result.summary())


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=["list", "all", "scan", "graph", "trace", "overlay", "test", "timeout"])
    parser.add_argument("scenario", nargs="?", help="scenario id (a) or folder name")
    args = parser.parse_args()

    if args.step == "list":
        for s in all_scenarios():
            print(f"{s.id}  {s.name:<24} {s.title:<20} origin: {s.origin}")
        return
    if args.step == "timeout":
        do_timeout()
        return
    if not args.scenario:
        parser.error("this step needs a scenario, e.g. python run.py graph a")

    s = load(args.scenario)
    if s.is_stand_in:
        print(f"Note: {s.name} is a stand-in, not LLM output. Do not report its results as evidence.\n")
    steps = {"scan": do_scan, "graph": do_graph, "trace": do_trace, "overlay": do_overlay, "test": do_test}
    if args.step != "all":
        steps[args.step](s)
        return
    print("== Scan ==")
    do_scan(s)
    print("\n== Graph ==")
    graph = do_graph(s)
    print("\n== Trace ==")
    result = do_trace(s)
    print("\n== Overlay ==")
    do_overlay(s, graph, result)
    print("\n== Tests ==")
    do_test(s)
    print("\n== Timeout ==")
    do_timeout()


if __name__ == "__main__":
    main()
