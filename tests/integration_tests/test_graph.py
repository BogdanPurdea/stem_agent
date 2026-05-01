"""Integration tests for the STEM Agent graph.

These tests require a running Ollama instance with the configured model.
"""

import os
import pytest
from dotenv import load_dotenv
from stem_agent.graph import graph

from stem_agent.configuration import CONFIG

load_dotenv()
pytestmark = pytest.mark.anyio


# Basic check to skip if environment is not set up
def _should_skip() -> bool:
    model = CONFIG.model
    if "ollama" in model and not os.getenv("OLLAMA_BASE_URL", "").startswith("http"):
        return True
    if "openai" in model and not os.getenv("OPENAI_API_KEY"):
        return True
    return False


if _should_skip():
    pytest.skip(
        "Missing environment configuration for the active model.",
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
