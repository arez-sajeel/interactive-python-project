"""Highlight the traced path on the dependency graph, up to a chosen step."""
from pathlib import Path

import networkx as nx

from engine import deps
from engine.tracer import executed_path


def overlay(graph: nx.DiGraph, events: list[dict], out, step: int | None = None) -> dict:
    """Draw the path taken by trace steps 1 to step (all steps if None), marking the current one."""
    step = step or len(events)
    nodes, edges = executed_path(events[:step])
    nodes &= set(graph.nodes)
    edges &= set(graph.edges)
    event = events[step - 1]
    deps.draw(graph, out, executed_nodes=nodes, executed_edges=edges, current=(event["node"], event["line"]))
    return {"step": step, "nodes": len(nodes), "edges": len(edges),
            "cross_file_edges": sum(1 for e in edges if graph.edges[e].get("cross_file"))}


def save(graph: nx.DiGraph, events: list[dict], path: Path, step: int | None = None) -> dict:
    path.parent.mkdir(exist_ok=True)
    return overlay(graph, events, path, step)
