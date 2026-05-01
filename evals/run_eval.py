"""Run the STEM Agent evaluation against the LangSmith benchmark dataset.

Usage:  python -m evals.run_eval
"""

from __future__ import annotations

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from langsmith.evaluation import evaluate
from stem_agent.graph import graph
from evals.evaluators import correctness_evaluator, differentiation_evaluator
from dotenv import load_dotenv

def target(inputs: dict) -> dict:
    """Invoke the STEM Agent graph and return outputs for the evaluator."""
    initial_state = {
        "messages": [("user", inputs["task"])],
        "signal": None,
        "strategy": None,
        "plan": [],
        "tool_manifest": [],
        "execution_result": None,
        "consecutive_failures": 0,
        "circuit_breaker_tripped": False,
    }

    result = graph.invoke(initial_state)

    return {
        "result": result.get("execution_result"),
        "perceived_complexity": (result.get("signal") or {}).get("complexity"),
    }


def main() -> None:
    load_dotenv()
    evaluate(
        target,
        data="STEM Agent v2 Benchmark",
        evaluators=[correctness_evaluator, differentiation_evaluator],
        experiment_prefix="stem-eval",
        max_concurrency=2,
    )
    print("Evaluation complete — check LangSmith UI for results.")


if __name__ == "__main__":
    main()
