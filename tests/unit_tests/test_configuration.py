"""Unit tests for the STEM Agent."""

from langgraph.pregel import Pregel

from stem_agent.graph import graph
from stem_agent.nodes.adapt import adapt
from stem_agent.skills import SkillInfo, load_skills, skills_description
from stem_agent.state import Signal, StemState
from stem_agent.tools import calculator, utc_now


# ---------------------------------------------------------------------------
# Graph compilation
# ---------------------------------------------------------------------------


def test_graph_compiles() -> None:
    assert isinstance(graph, Pregel)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


def test_calculator_tool() -> None:
    result = calculator.invoke({"expression": "2 + 3 * 4"})
    assert result == "14"


def test_utc_now_tool() -> None:
    result = utc_now.invoke({})
    assert isinstance(result, str)
    assert "T" in result


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
        "signal": {"domain": "General", "complexity": "simple", "intent": "test", "hints": []},
        "strategy": None,
        "plan": [],
        "tool_manifest": [],
        "execution_result": None,
        "consecutive_failures": 0,
        "circuit_breaker_tripped": False,
    }
    result = adapt(state)
    assert result["strategy"]["reasoning_method"] == "chain_of_thought"
    assert result["strategy"]["max_iterations"] == 1


def test_adapt_complex() -> None:
    state: StemState = {
        "messages": [],
        "signal": {"domain": "Security", "complexity": "complex", "intent": "audit", "hints": []},
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


# ---------------------------------------------------------------------------
# Skills loader
# ---------------------------------------------------------------------------


def test_skills_loader_empty_dir(tmp_path) -> None:
    """An empty directory returns no skills."""
    assert load_skills(str(tmp_path)) == []


def test_skills_loader_finds_skill(tmp_path) -> None:
    """A valid SKILL.md with frontmatter is discovered."""
    skill_dir = tmp_path / "my_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: A test skill.\n---\n\n# Test\n"
    )
    result = load_skills(str(tmp_path))
    assert len(result) == 1
    assert result[0].name == "test-skill"
    assert "test skill" in result[0].description.lower()


def test_skills_description_empty() -> None:
    assert skills_description([]) == "(no skills discovered)"


def test_skills_description_with_items() -> None:
    items = [SkillInfo(name="a", description="desc a", file_path="/x")]
    desc = skills_description(items)
    assert "**a**" in desc
