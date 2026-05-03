"""Unit tests for the STEM Agent."""

from langgraph.pregel import Pregel

from stem_agent.graph import graph
from stem_agent.nodes.adapt import adapt
from stem_agent.state import Signal, StemState

# ---------------------------------------------------------------------------
# Graph compilation
# ---------------------------------------------------------------------------


def test_graph_compiles() -> None:
    assert isinstance(graph, Pregel)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


def test_signal_model_validates() -> None:
    sig = Signal(domain="Security", complexity="complex", intent="review code")
    assert sig.domain == "Security"
    assert sig.complexity == "complex"


def test_signal_model_rejects_bad_complexity() -> None:
    import pytest

    with pytest.raises(Exception):  # noqa: B017
        Signal(domain="General", complexity="ultra", intent="test")


# ---------------------------------------------------------------------------
# Adapt (deterministic)
# ---------------------------------------------------------------------------


def test_adapt_simple() -> None:
    state: StemState = {
        "messages": [],
        "signal": {
            "domain": "General",
            "complexity": "simple",
            "intent": "test",
            "hints": [],
        },
        "strategy": None,
        "plan": [],
        "tool_manifest": [],
        "execution_result": None,
        "consecutive_failures": 0,
        "circuit_breaker_tripped": False,
    }
    result = adapt(state)
    assert result["strategy"]["reasoning_method"] == "react"
    assert result["strategy"]["max_iterations"] == 3


def test_adapt_medium() -> None:
    state: StemState = {
        "messages": [],
        "signal": {
            "domain": "Architecture",
            "complexity": "medium",
            "intent": "design",
            "hints": [],
        },
        "strategy": None,
        "plan": [],
        "tool_manifest": [],
        "execution_result": None,
        "consecutive_failures": 0,
        "circuit_breaker_tripped": False,
    }
    result = adapt(state)
    assert result["strategy"]["reasoning_method"] == "react"
    assert result["strategy"]["max_iterations"] == 5


def test_adapt_complex() -> None:
    state: StemState = {
        "messages": [],
        "signal": {
            "domain": "Security",
            "complexity": "complex",
            "intent": "audit",
            "hints": [],
        },
        "strategy": None,
        "plan": [],
        "tool_manifest": [],
        "execution_result": None,
        "consecutive_failures": 0,
        "circuit_breaker_tripped": False,
    }
    result = adapt(state)
    assert result["strategy"]["reasoning_method"] == "reflexion"
    assert result["strategy"]["max_iterations"] == 10
