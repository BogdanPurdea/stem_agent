"""STEM Agent graph — assembles the Perceive → Adapt → Plan → Execute pipeline.

This module builds a LangGraph StateGraph, wires the nodes and edges, and
exports the compiled graph as ``graph`` for ``langgraph.json`` to reference.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from stem_agent.nodes.adapt import adapt
from stem_agent.nodes.execute import execute
from stem_agent.nodes.perceive import perceive
from stem_agent.nodes.plan import plan
from stem_agent.nodes.load_skills import load_skills
from stem_agent.nodes.call_tool import call_tool
from stem_agent.state import StemState


# ---------------------------------------------------------------------------
# Routing functions
# ---------------------------------------------------------------------------

def _route_after_plan(state: StemState) -> str:
    """Decide whether to loop back for tool handling or finish."""
    if not state.get("skill_manifest"):
        return "execute"
    return "load_skills"


def _route_after_execute(state: StemState) -> str:
    """Decide whether to loop back for tool handling or finish."""
    if state.get("circuit_breaker_tripped"):
        return END

    last_msg = state["messages"][-1]
    if getattr(last_msg, "tool_calls", None):
        return "call_tool"

    return END


def _route_after_tools(state: StemState) -> str:
    """After tool execution, check circuit breaker before looping back."""
    if state.get("circuit_breaker_tripped"):
        return END
    return "execute"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def build_graph() -> StateGraph:
    """Construct and return the uncompiled STEM Agent graph."""
    builder = StateGraph(StemState)

    # --- Nodes ---
    builder.add_node("perceive", perceive)
    builder.add_node("adapt", adapt)
    builder.add_node("plan", plan)
    builder.add_node("load_skills", load_skills)
    builder.add_node("execute", execute)
    builder.add_node("call_tool", call_tool)

    # --- Edges: linear pipeline ---
    builder.add_edge(START, "perceive")
    builder.add_edge("perceive", "adapt")
    builder.add_edge("adapt", "plan")
    builder.add_edge("load_skills","execute")
    # --- Edges: plan ↔ skills ↔ execute loop ---
    builder.add_conditional_edges(
        "plan",
        _route_after_plan,
        ["load_skills", "execute"],
    )
    builder.add_conditional_edges(
        "execute",
        _route_after_execute,
        ["call_tool", END],
    )
    builder.add_conditional_edges(
        "call_tool",
        _route_after_tools,
        ["execute", END],
    )

    return builder


# Compiled graph — the entrypoint referenced by langgraph.json
graph = build_graph().compile()
