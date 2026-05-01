"""Execute node and tool-handler node for the STEM Agent.

The execute/handle_tools pair implements a ReAct-style loop with a circuit
breaker that halts after too many consecutive tool failures.
"""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage

from stem_agent.configuration import CONFIG
from stem_agent.prompts import EXECUTE_PROMPT_TEMPLATE, PERSONAS
from stem_agent.state import StemState
from stem_agent.tools import TOOL_REGISTRY, get_tools_by_names


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_plan(plan: list[dict]) -> str:
    """Render the plan as a numbered list for the system prompt."""
    if not plan:
        return "(no plan — answer the user directly)"
    lines: list[str] = []
    for step in plan:
        tools_str = ", ".join(step.get("tools", [])) or "none"
        lines.append(
            f"{step.get('step_number', '?')}. {step.get('description', '')} "
            f"[tools: {tools_str}]"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Execute node — calls the LLM (with bound tools)
# ---------------------------------------------------------------------------


def execute(state: StemState) -> dict:
    """Call the LLM with the strategy-specific system prompt and bound tools."""
    # Short-circuit if the circuit breaker already tripped
    if state.get("circuit_breaker_tripped"):
        return {
            "execution_result": (
                "Execution halted: circuit breaker tripped after "
                f"{state.get('consecutive_failures', 0)} consecutive tool failures."
            )
        }

    strategy = state.get("strategy") or {}
    signal = state.get("signal") or {}
    plan = state.get("plan") or []

    # Build a one-shot system prompt incorporating persona + plan
    domain = signal.get("domain", "General")
    persona = PERSONAS.get(domain, PERSONAS["General"])
    reasoning_method = strategy.get("reasoning_method", "react")

    system_prompt = EXECUTE_PROMPT_TEMPLATE.format(
        persona_block=persona,
        reasoning_method=reasoning_method,
        plan_block=_format_plan(plan),
    )

    # Construct local message list (system prompt is NOT stored in state)
    local_messages = [SystemMessage(content=system_prompt)] + list(state["messages"])

    # Bind only the tools the Plan node selected
    tools = get_tools_by_names(state.get("tool_manifest") or [])
    llm = init_chat_model(CONFIG.model)
    if tools:
        llm = llm.bind_tools(tools)

    response = llm.invoke(local_messages)

    updates: dict = {"messages": [response]}

    # If the LLM produced no tool calls, treat its content as the final answer
    if not getattr(response, "tool_calls", None):
        updates["execution_result"] = response.content

    return updates


# ---------------------------------------------------------------------------
# Handle-tools node — executes tool calls, manages circuit breaker
# ---------------------------------------------------------------------------


def handle_tools(state: StemState) -> dict:
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
            tool_results.append(
                ToolMessage(content=str(result), tool_call_id=tc["id"])
            )
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
