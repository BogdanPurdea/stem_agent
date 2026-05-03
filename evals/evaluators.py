"""Evaluator functions for the STEM Agent benchmark.

Each evaluator follows the LangSmith signature:
    (inputs, outputs, reference_outputs) → score / dict
"""

from __future__ import annotations

from openevals.llm import create_llm_as_judge

# ---------------------------------------------------------------------------
# 1. Correctness — LLM-as-judge via openevals
# ---------------------------------------------------------------------------

CUSTOM_CORRECTNESS_PROMPT = """\
You are an expert software engineer judging the correctness of an AI agent's response.

## Input Task
{task}

## Reference Answer
{reference_answer}

## Agent Execution Context
- **Tools Available**: {tool_manifest}
- **Skills Content**: 
{skills_content}

## Agent Output
{result}

## Evaluation Criteria
Does the agent's response accurately address the user task and match the substance of the reference answer?
Note that the agent had limited tools and specific technical skills (provided above). Evaluate its correctness based on what it was able to do with those resources.

Respond with:
- **score**: 1 if correct, 0.5 if partially correct, 0 if incorrect.
- **comment**: A brief explanation of your decision.
"""

_correctness_judge = create_llm_as_judge(
    prompt=CUSTOM_CORRECTNESS_PROMPT,
    model="openai:gpt-4o",
    feedback_key="correctness",
)


def correctness_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """Score whether the agent's answer is correct relative to the reference."""
    # Merge all data into a single context for the prompt
    context = {
        **inputs,
        **outputs,
        **(reference_outputs or {}),
    }
    return _correctness_judge(**context)


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

# ---------------------------------------------------------------------------
# 3. Tool Efficiency — precision and recall on tool selection
# ---------------------------------------------------------------------------

def tool_efficiency_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """Calculate Precision and Recall for tool usage.
    Precision = (Correct Tools Called) / (Total Tools Called)
    Recall = (Correct Tools Called) / (Total Expected Tools)
    """
    expected = set((reference_outputs or {}).get("expected_tools", []))
    actual = set((outputs or {}).get("actual_tools", []))

    # If no tools were expected and no tools were called, perfect score
    if not expected and not actual:
        return {"key": "tool_precision", "score": 1.0, "comment": "No tools needed, none called."}

    correct_tools_called = len(actual.intersection(expected))

    # Precision
    precision = correct_tools_called / len(actual) if len(actual) > 0 else 1.0
    
    # Recall
    recall = correct_tools_called / len(expected) if len(expected) > 0 else 1.0

    # We can return multiple metrics by returning a list of dicts, or just return one combined.
    # LangSmith supports returning a dictionary or list of metric dicts.
    return [
        {"key": "tool_precision", "score": float(precision), "comment": f"Expected: {expected}, Actual: {actual}"},
        {"key": "tool_recall", "score": float(recall), "comment": f"Expected: {expected}, Actual: {actual}"}
    ]

