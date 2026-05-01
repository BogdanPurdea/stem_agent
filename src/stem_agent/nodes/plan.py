"""Plan node — builds an ordered execution plan using available tools and skills."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage

from stem_agent.configuration import CONFIG
from stem_agent.prompts import PLAN_PROMPT_TEMPLATE, PERSONAS
from stem_agent.skills import load_skills, skills_description
from stem_agent.state import ExecutionPlan, StemState
from stem_agent.tools import tools_description


def plan(state: StemState) -> dict:
    """Create a step-by-step execution plan and select the tools needed."""
    signal = state["signal"] or {}
    strategy = state["strategy"] or {}

    # Build the planning prompt with tool/skill context
    prompt_text = PLAN_PROMPT_TEMPLATE.format(
        domain=signal.get("domain", "General"),
        intent=signal.get("intent", "unknown"),
        reasoning_method=strategy.get("reasoning_method", "react"),
        domains_section=PERSONAS.keys(),
        tools_section=tools_description(),
        skills_section=skills_description(load_skills()),
    )
    llm = init_chat_model(CONFIG.model).with_structured_output(ExecutionPlan)

    result: ExecutionPlan = llm.invoke(
        [SystemMessage(content=prompt_text)] + list(state["messages"])
    )
    return {
        "plan": [step.model_dump() for step in result.steps],
        "tool_manifest": result.selected_tools,
        "skill_manifest": result.selected_skills,
    }
