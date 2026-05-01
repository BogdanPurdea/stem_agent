"""Integration tests for the STEM Agent graph.

These tests require a running Ollama instance with the configured model.
"""

import os

from dotenv import load_dotenv

load_dotenv()

import pytest

from stem_agent.graph import graph

pytestmark = pytest.mark.anyio

if not os.getenv("OLLAMA_BASE_URL", "").startswith("http"):
    pytest.skip(
        "Set OLLAMA_BASE_URL to run integration tests.",
        allow_module_level=True,
    )


async def test_stem_agent_simple_task() -> None:
    """A simple prompt should flow through the full pipeline and produce a result."""
    result = await graph.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Write a Python function that checks if a number is even.",
                }
            ],
            "signal": None,
            "strategy": None,
            "plan": [],
            "tool_manifest": [],
            "execution_result": None,
            "consecutive_failures": 0,
            "circuit_breaker_tripped": False,
        }
    )

    # The pipeline should populate signal, strategy, and execution_result
    assert result.get("signal") is not None
    assert result.get("strategy") is not None
    assert result.get("execution_result") is not None
    assert len(result["execution_result"]) > 0
