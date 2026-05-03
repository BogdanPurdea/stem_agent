"""Execute node for the STEM Agent.

The execute node builds the specialized system prompt and invokes the LLM.
"""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage

from stem_agent.configuration import CONFIG
from stem_agent.prompts import EXECUTE_PROMPT_TEMPLATE, PERSONAS
from stem_agent.state import StemState
from stem_agent.tools import get_tools_by_names


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
    strategy = state.get("strategy") or {}
    max_iters = strategy.get("max_iterations", 5)
    current_iters = state.get("iteration_count", 0)


    # Halt if the circuit breaker tripped
    if state.get("circuit_breaker_tripped"):
        return {
            "execution_result": (
                "Execution halted: circuit breaker tripped after "
                f"{state.get('consecutive_failures', 0)} consecutive tool failures."
            )
        }

    # Halt if we reached the max iteration budget
    if current_iters >= max_iters:
        return {
            "execution_result": (
                f"Execution halted: reached maximum iteration budget of {max_iters}."
            )
        }

    signal = state.get("signal") or {}
    plan = state.get("plan") or []

    # Use the system prompt pre-built by the Adapt node
    system_prompt = strategy.get("system_prompt")
    if system_prompt:
        # Inject the actual plan and skills content into the pre-built prompt
        system_prompt = system_prompt.replace(
            "(plan will be injected after the Plan node)", _format_plan(plan)
        )
        system_prompt = system_prompt.replace(
            "(skills will be injected after the Plan node)",
            state.get("skills_content") or "(no skills provided)",
        )
    else:
        # Fallback (should not be reached in normal flow)
        domain = signal.get("domain", "General")
        persona = PERSONAS.get(domain, PERSONAS["General"])
        reasoning_method = strategy.get("reasoning_method", "react")
        system_prompt = EXECUTE_PROMPT_TEMPLATE.format(
            persona_block=persona,
            reasoning_method=reasoning_method,
            skills_block=state.get("skills_content") or "(no skills provided)",
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

    updates: dict = {
        "messages": [response],
        "iteration_count": current_iters + 1,
    }

    # If the LLM produced no tool calls, treat its content as the final answer
    if not getattr(response, "tool_calls", None):
        updates["execution_result"] = response.content

    return updates

