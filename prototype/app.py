"""Streamlit page: code, dependency graph and trace on one page (PFR9).

Run with:  streamlit run app.py

Edits are made in a per-session copy of the scenario, so the originals never change.
The page never shows the defect location or the solution: it is what a student sees.
"""
import html
import io
import shutil
import tempfile
import time
from pathlib import Path

import streamlit as st

from engine import deps, metrics, runner
from engine.scenario import Scenario, all_scenarios
from engine.tracer import executed_path, trace

st.set_page_config(page_title="Interactive Python Project", layout="wide")
st.html("""
<style>
.block-container { padding-top: 2rem; max-width: 1400px; }
.stTextArea textarea { font-family: ui-monospace, Consolas, monospace; font-size: 0.85rem; }
.code { font-family: ui-monospace, Consolas, monospace; font-size: 0.85rem; line-height: 1.5;
        border: 1px solid rgba(128,128,128,0.3); border-radius: 4px; padding: 0.5rem 0; overflow-x: auto; }
.code div { white-space: pre; padding: 0 0.75rem; }
.code .n { display: inline-block; width: 2.5em; opacity: 0.5; user-select: none; }
.code .on { background: rgba(11,98,214,0.16); box-shadow: inset 3px 0 #0b62d6; }
</style>
""")

state = st.session_state


# ---- session helpers ---------------------------------------------------------

def workspace(s: Scenario) -> Scenario:
    """This session's working copy of the scenario, created on first open."""
    key = f"ws:{s.name}"
    if key not in state:
        state[key] = s.copy_to(Path(tempfile.mkdtemp(prefix=f"verify_{s.id}_")))
        state[f"start:{s.name}"] = time.monotonic()
        state.pop(f"solved:{s.name}", None)
    return state[key]


def reset(s: Scenario) -> None:
    if f"ws:{s.name}" in state:
        shutil.rmtree(state[f"ws:{s.name}"].path, ignore_errors=True)
    for key in [k for k in state if k.split(":", 1)[-1].startswith(s.name)]:
        del state[key]


def snapshot(ws: Scenario) -> tuple:
    """Current code, used to tell when a trace or test result is out of date."""
    return tuple(p.read_text(encoding="utf-8") for p in ws.source_files())


@st.cache_data(show_spinner=False, max_entries=32)
def graph_png(_ws: Scenario, code: tuple, nodes: tuple, edges: tuple) -> bytes:
    buf = io.BytesIO()
    deps.draw(deps.build_graph(_ws), buf, executed_nodes=set(nodes), executed_edges=set(edges))
    return buf.getvalue()


def code_block(text: str, active: int | None = None) -> str:
    rows = [
        f'<div class="{"on" if i == active else ""}"><span class="n">{i}</span>{html.escape(line)}</div>'
        for i, line in enumerate(text.splitlines(), 1)
    ]
    return f'<div class="code">{"".join(rows)}</div>'


def step(delta: int, total: int) -> None:
    state["step"] = min(max(1, state.get("step", 1) + delta), total)


# ---- page --------------------------------------------------------------------

scenarios = all_scenarios()
choice = st.columns([1, 2])[0].selectbox("Project", scenarios, format_func=lambda s: s.title)
ws = workspace(choice)
files = sorted((p.relative_to(ws.path).as_posix() for p in ws.source_files()),
               key=lambda f: f != ws.entry)  # entry point first

left, right = st.columns(2, gap="large")

with left:
    st.subheader("Code")
    current = st.radio("File", files, horizontal=True, key=f"file:{choice.name}",
                       label_visibility="collapsed")
    path = ws.path / current
    edited = st.text_area("Edit code", path.read_text(encoding="utf-8"), height=360,
                          key=f"edit:{choice.name}:{current}", label_visibility="collapsed")
    if edited != path.read_text(encoding="utf-8"):
        path.write_text(edited, encoding="utf-8")

    run_tests, run_trace, undo = st.columns([1, 1, 1])
    code = snapshot(ws)
    if run_tests.button("Run tests", type="primary", width="stretch"):
        with st.spinner("Running tests"):
            state[f"tests:{choice.name}"] = (runner.run_tests(ws.path), code)
    if run_trace.button("Run trace", width="stretch"):
        with st.spinner("Tracing"):
            state[f"trace:{choice.name}"] = (trace(ws), code)
            state["step"] = 1
    undo.button("Reset code", width="stretch", on_click=reset, args=(choice,),
                help="Discard your edits and restore the original files")

    if f"tests:{choice.name}" in state:
        result, tested = state[f"tests:{choice.name}"]
        if tested != code:
            st.caption("Code changed since the last test run.")
        elif result.ok:
            if f"solved:{choice.name}" not in state and code != snapshot(choice):
                seconds = time.monotonic() - state[f"start:{choice.name}"]
                state[f"solved:{choice.name}"] = seconds
                metrics.log(choice, "solve", "", seconds, f"{seconds / 60:.1f} min via Streamlit page")
            solved = state.get(f"solved:{choice.name}")
            note = f" Solved in {int(solved // 60)} min {int(solved % 60)} s." if solved else ""
            st.success(f"All {result.passed} tests pass.{note}")
        else:
            st.error(f"Tests: {result.summary()}.")
        if result.output:
            with st.expander("Test output"):
                st.code(result.output, language=None)

traced = state.get(f"trace:{choice.name}")
result = traced[0] if traced else None
stale = bool(traced) and traced[1] != code

with right:
    st.subheader("Dependency graph")
    nodes, edges = (), ()
    if result and result["events"] and not stale:
        n, e = executed_path(result["events"])
        nodes, edges = tuple(sorted(n)), tuple(sorted(e))
    st.image(graph_png(ws, code, nodes, edges), width="stretch")
    st.caption("Blue shows the path the code took in the last trace." if nodes
               else "Boxes are files and functions. Arrows are calls; dashed lines are imports.")

st.divider()
st.subheader("Trace")

if not result:
    st.caption("Run trace to step through the code as it runs.")
elif stale:
    st.caption("Code changed since the last trace. Run trace again to update it.")
elif result["timed_out"] or not result["events"]:
    st.error(f"The trace could not run: {result['error']}")
else:
    events = result["events"]
    total = len(events)
    state["step"] = min(state.get("step", 1), total)
    prev, slider, nxt = st.columns([1, 10, 1], vertical_alignment="bottom")
    prev.button("Back", on_click=step, args=(-1, total), width="stretch", disabled=state["step"] <= 1)
    nxt.button("Next", on_click=step, args=(1, total), width="stretch", disabled=state["step"] >= total)
    slider.slider("Step", 1, total, key="step")
    event = events[state["step"] - 1]

    where, detail = st.columns([3, 2], gap="large")
    with where:
        st.markdown(f"**{event['file']}** line {event['line']} in `{event['function']}`")
        st.markdown(code_block((ws.path / event["file"]).read_text(encoding="utf-8"), event["line"]),
                    unsafe_allow_html=True)
    with detail:
        labels = {"call": "Function called", "line": "Line run", "return": "Function returned",
                  "exception": "Error raised"}
        st.markdown(f"**{labels.get(event['event'], event['event'])}**")
        if event["changes"]:
            st.dataframe([{"Name": k, "Value": v} for k, v in event["changes"].items()],
                         hide_index=True, width="stretch")
        else:
            st.caption("No variables changed.")
        if result["output"]:
            st.markdown("**Program output**")
            st.code(result["output"].rstrip(), language=None)
        if result["error"]:
            st.warning(f"The program stopped with {result['error']}")
    if result["truncated"]:
        st.caption(f"Trace shortened to the first {total} steps.")
