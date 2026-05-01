"""Adapt node — maps the perception Signal to a reasoning Strategy.

This node is intentionally deterministic (no LLM call) so it is fast,
predictable, and easy to test.
"""

from __future__ import annotations

from stem_agent.prompts import EXECUTE_PROMPT_TEMPLATE, PERSONAS
from stem_agent.state import StemState

# ---------------------------------------------------------------------------
# Mapping tables
# ---------------------------------------------------------------------------

_COMPLEXITY_TO_METHOD: dict[str, str] = {
    "simple": "chain_of_thought",
    "medium": "react",
    "complex": "reflexion",
}

_COMPLEXITY_TO_ITERS: dict[str, int] = {
    "simple": 1,
    "medium": 5,
    "complex": 10,
}


def adapt(state: StemState) -> dict:
    """Translate the perception signal into a concrete execution strategy."""
    signal = state["signal"] or {}

    complexity: str = signal.get("complexity", "medium")
    domain: str = signal.get("domain", "General")

    reasoning_method = _COMPLEXITY_TO_METHOD.get(complexity, "react")
    max_iterations = _COMPLEXITY_TO_ITERS.get(complexity, 5)
    persona = PERSONAS.get(domain, PERSONAS["General"])

    # Build the system prompt that the Execute node will use
    system_prompt = EXECUTE_PROMPT_TEMPLATE.format(
        persona_block=persona,
        reasoning_method=reasoning_method,
        plan_block="(plan will be injected after the Plan node)",
    )

    return {
        "strategy": {
            "reasoning_method": reasoning_method,
            "persona": persona,
            "system_prompt": system_prompt,
            "max_iterations": max_iterations,
        }
    }
