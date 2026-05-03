"""Run the Baseline ReAct Agent evaluation against the LangSmith benchmark dataset.

Usage:  python -m evals.run_baseline_eval
"""

from __future__ import annotations

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langsmith.evaluation import evaluate

from evals.evaluators import correctness_evaluator, differentiation_evaluator, tool_efficiency_evaluator
from stem_agent.configuration import CONFIG
from stem_agent.tools import ALL_TOOLS


def target(inputs: dict) -> dict:
    """Invoke the Baseline ReAct Agent and return outputs for the evaluator."""
    # Initialize the LLM
    llm = init_chat_model(CONFIG.model)
    
    # Create a standard universal agent with ALL tools available
    agent = create_react_agent(llm, tools=ALL_TOOLS)
    
    # Run the agent
    result = agent.invoke({"messages": [("user", inputs["task"])]})
    
    # The final message is the AIMessage output
    final_message = result["messages"][-1].content
    actual_tools = []
    for msg in result.get("messages", []):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                actual_tools.append(tc["name"])
    
    return {
        "result": final_message,
        "perceived_complexity": None,  # Baseline agent does not differentiate
        "actual_tools": actual_tools,
        "tool_manifest": [t.name for t in ALL_TOOLS],
        "skills_content": "(no specialized skills provided to baseline agent)",
    }


def main() -> None:
    evaluate(
        target,
        data="STEM Agent Benchmark",
        evaluators=[correctness_evaluator, tool_efficiency_evaluator],
        experiment_prefix="react-baseline-eval",
        max_concurrency=2,
    )
    print("Baseline evaluation complete — check LangSmith UI for results.")


if __name__ == "__main__":
    main()
