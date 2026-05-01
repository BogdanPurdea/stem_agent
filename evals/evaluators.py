"""Evaluator functions for the STEM Agent benchmark.

Each evaluator follows the LangSmith signature:
    (inputs, outputs, reference_outputs) → score / dict
"""

from __future__ import annotations

from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT


# ---------------------------------------------------------------------------
# 1. Correctness — LLM-as-judge via openevals
# ---------------------------------------------------------------------------

_correctness_judge = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="openai:gpt-4o",
    feedback_key="correctness",
)


def correctness_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """Score whether the agent's answer is correct relative to the reference."""
    return _correctness_judge(
        inputs=inputs,
        outputs=outputs,
        reference_outputs=reference_outputs,
    )


# ---------------------------------------------------------------------------
# 2. Differentiation — did the agent pick the expected complexity?
# ---------------------------------------------------------------------------


def differentiation_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """Check that the perceived complexity matches the expected complexity."""
    expected = (reference_outputs or {}).get("expected_complexity")
    actual = (outputs or {}).get("perceived_complexity")

    if expected is None or actual is None:
        return {"key": "differentiation", "score": None, "comment": "missing data"}

    match = actual == expected
    return {
        "key": "differentiation",
        "score": 1.0 if match else 0.0,
        "comment": f"expected={expected}, actual={actual}",
    }
