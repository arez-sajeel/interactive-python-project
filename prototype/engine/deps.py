"""Dependency graph of imports and cross-file calls using ast and networkx (PFR1, PFR2).

Nodes are modules (their module-level code), top-level functions, classes and methods,
named like calc, calc.basket_total and shop.Basket.add. Known limitation: calls on
object instances (basket.add()) are not resolved, as the receiver's type is unknown.
"""
import ast
from pathlib import Path

import matplotlib
import networkx as nx

from engine.scenario import Scenario

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (backend must be set first)


def build_graph(scenario: Scenario) -> nx.DiGraph:
    graph = nx.DiGraph()
    trees = {}
    for path in scenario.source_files():
        module = scenario.module_name(path)
        trees[module] = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        graph.add_node(module, kind="module", module=module, line=1, file=path.name)
        for node in trees[module].body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                graph.add_node(f"{module}.{node.name}", kind=kind, module=module, line=node.lineno)
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        graph.add_node(f"{module}.{node.name}.{item.name}", kind="method",
                                       module=module, line=item.lineno)

    for module, tree in trees.items():
        aliases = _imports(module, tree, trees, graph)
        _CallVisitor(module, aliases, trees, graph).visit(tree)
    return graph


def _imports(module: str, tree: ast.Module, modules: dict, graph: nx.DiGraph) -> dict[str, str]:
    """Map each local name bound by an import to the scenario module or name it refers to."""
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in modules:
                    aliases[alias.asname or alias.name] = alias.name
                    graph.add_edge(module, alias.name, kind="import")
        elif isinstance(node, ast.ImportFrom) and node.module in modules:
            graph.add_edge(module, node.module, kind="import")
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return aliases


class _CallVisitor(ast.NodeVisitor):
    def __init__(self, module, aliases, modules, graph):
        self.scope = [module]
        self.module, self.aliases, self.modules, self.graph = module, aliases, modules, graph

    def _enter(self, node):
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _enter

    def visit_Call(self, node: ast.Call):
        target = self._resolve(node.func)
        if target:
            caller = self._caller()
            if target not in self.graph:  # called but never defined, e.g. a renamed function
                self.graph.add_node(target, kind="missing", module=target.rsplit(".", 1)[0], line=0)
            module_of = self.graph.nodes[target]["module"]
            self.graph.add_edge(caller, target, kind="call", line=node.lineno,
                                cross_file=module_of != self.module)
        self.generic_visit(node)

    def _caller(self) -> str:
        scope = list(self.scope)
        while ".".join(scope) not in self.graph:  # nested functions belong to their enclosing function
            scope.pop()
        return ".".join(scope)

    def _resolve(self, func: ast.expr) -> str | None:
        if isinstance(func, ast.Name):
            target = self.aliases.get(func.id)
            if target and target not in self.modules:
                return target
            local = f"{self.module}.{func.id}"
            return local if local in self.graph else None
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            module = self.aliases.get(func.value.id)
            if module in self.modules:
                return f"{module}.{func.attr}"
        return None


def cross_file_calls(graph: nx.DiGraph) -> set[tuple[str, str]]:
    return {(a, b) for a, b, d in graph.edges(data=True) if d["kind"] == "call" and d["cross_file"]}


def accuracy(graph: nx.DiGraph, expected: tuple[tuple[str, str], ...]) -> dict:
    """Compare the cross-file calls found against the hand-made list (PNFR3)."""
    found = cross_file_calls(graph)
    listed = set(expected)
    return {
        "found": len(found & listed),
        "listed": len(listed),
        "missed": sorted(listed - found),
        "extra": sorted(found - listed),
    }


INK, MUTED, FAINT, ACCENT, ERROR = "#1f2328", "#59636e", "#d1d9e0", "#0b62d6", "#cf222e"


def draw(graph: nx.DiGraph, out, executed_nodes=frozenset(), executed_edges=frozenset()) -> None:
    """Draw one column per file. If an executed path is given, highlight it (PFR5)."""
    modules = sorted({d["module"] for _, d in graph.nodes(data=True) if d["kind"] == "module"})
    # Order each column depth-first from the module-level code, so callees sit below their callers.
    calls = nx.DiGraph((a, b) for a, b, d in graph.edges(data=True) if d["kind"] == "call")
    calls.add_nodes_from(graph)
    rank = {}
    for module in modules:
        for node in nx.dfs_preorder_nodes(calls, module):
            rank.setdefault(node, len(rank))
    pos = {}
    for x, module in enumerate(modules):
        members = sorted((n for n, d in graph.nodes(data=True) if d["module"] == module),
                         key=lambda n: (rank.get(n, len(graph)), graph.nodes[n]["line"]))
        for y, node in enumerate(members):
            pos[node] = (x * 3.0, -y)
    rows = max(-y for _, y in pos.values()) + 1
    fig, ax = plt.subplots(figsize=(max(5.0, 3.2 * len(modules)), max(3.0, 0.9 * rows + 1.2)), dpi=150)
    overlay = bool(executed_nodes)

    for a, b, d in graph.edges(data=True):
        hit = (a, b) in executed_edges
        if d["kind"] == "import":
            style = dict(edge_color=FAINT, style="dashed", width=1.0, arrowstyle="-")
        else:
            colour = ACCENT if hit else (FAINT if overlay else (INK if d["cross_file"] else MUTED))
            style = dict(edge_color=colour, width=2.6 if hit else 1.2, arrowsize=14)
        skips_rows = pos[a][0] == pos[b][0] and abs(pos[a][1] - pos[b][1]) > 1
        nx.draw_networkx_edges(graph, pos, edgelist=[(a, b)], ax=ax, node_size=2600, arrows=True,
                               connectionstyle=f"arc3,rad={0.5 if skips_rows else 0.15}", **style)

    for node, d in graph.nodes(data=True):
        hit = node in executed_nodes
        missing = d["kind"] == "missing"
        face = "#e8f0fc" if hit else "white"
        edge = ERROR if missing else (ACCENT if hit else (FAINT if overlay else MUTED))
        label = d.get("file") or node.split(".", 1)[1] + ("()" if d["kind"] != "class" else "")
        ax.text(*pos[node], label + ("\nnot defined" if missing else ""), ha="center", va="center",
                fontsize=8.5, color=ERROR if missing else INK,
                fontweight="bold" if d["kind"] == "module" else "normal",
                bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.15", fc=face, ec=edge,
                          lw=2 if hit or missing else 1, ls="--" if missing else "-"))

    xs, ys = zip(*pos.values())
    ax.set_xlim(min(xs) - 1.3, max(xs) + 1.3)
    ax.set_ylim(min(ys) - 0.6, max(ys) + 0.8)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out, format="png")
    plt.close(fig)


def describe(graph: nx.DiGraph) -> str:
    """Plain-text listing of modules and their functions (PFR1)."""
    lines = []
    for module in sorted(n for n, d in graph.nodes(data=True) if d["kind"] == "module"):
        lines.append(f"{graph.nodes[module]['file']}")
        for node, d in sorted(graph.nodes(data=True), key=lambda x: x[1]["line"]):
            if d["module"] == module and d["kind"] in ("function", "class", "method"):
                lines.append(f"  {d['kind']:<8} {node.split('.', 1)[1]}  (line {d['line']})")
    return "\n".join(lines)


def save(graph: nx.DiGraph, path: Path, **highlight) -> Path:
    path.parent.mkdir(exist_ok=True)
    draw(graph, path, **highlight)
    return path
