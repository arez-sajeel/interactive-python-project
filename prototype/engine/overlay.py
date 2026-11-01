"""Highlight the traced path on the dependency graph."""
from pathlib import Path

import networkx as nx

from engine import deps
from engine.tracer import executed_path


def overlay(graph: nx.DiGraph, events: list[dict], out) -> dict:
    nodes, edges = executed_path(events)
    nodes &= set(graph.nodes)
    edges &= set(graph.edges)
    deps.draw(graph, out, executed_nodes=nodes, executed_edges=edges)
    return {"nodes": len(nodes), "edges": len(edges),
            "cross_file_edges": sum(1 for e in edges if graph.edges[e].get("cross_file"))}


def save(graph: nx.DiGraph, events: list[dict], path: Path) -> dict:
    path.parent.mkdir(exist_ok=True)
    return overlay(graph, events, path)
