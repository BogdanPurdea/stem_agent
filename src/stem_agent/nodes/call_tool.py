"""Tools node for the STEM Agent.

This node executes the tool calls requested by the LLM and manages the 
consecutive failure count for the circuit breaker.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, ToolMessage

from stem_agent.configuration import CONFIG
from stem_agent.state import StemState
from stem_agent.tools import TOOL_REGISTRY


def call_tool(state: StemState) -> dict:
    """Execute pending tool calls and update the circuit-breaker counter."""
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    tool_results: list[ToolMessage | AIMessage] = []
    failures: int = state.get("consecutive_failures", 0)

    for tc in tool_calls:
        tool_fn = TOOL_REGISTRY.get(tc["name"])
        if tool_fn is None:
            failures += 1
            tool_results.append(
                ToolMessage(
                    content=f"Error: unknown tool '{tc['name']}'",
                    tool_call_id=tc["id"],
                )
            )
            continue

        try:
            result = tool_fn.invoke(tc["args"])
            tool_results.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
            failures = 0  # reset on success
        except Exception as exc:  # noqa: BLE001
            failures += 1
            tool_results.append(
                ToolMessage(
                    content=f"Tool error: {exc}",
                    tool_call_id=tc["id"],
                )
            )

    tripped = failures >= CONFIG.circuit_breaker_threshold

    updates: dict = {
        "messages": tool_results,
        "consecutive_failures": failures,
        "circuit_breaker_tripped": tripped,
    }

    if tripped:
        updates["execution_result"] = (
            "Execution halted: circuit breaker tripped after "
            f"{failures} consecutive tool failures."
        )

    return updates
