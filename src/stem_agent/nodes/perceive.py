"""Perceive node — classifies the user prompt into a structured Signal."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage

from stem_agent.configuration import CONFIG
from stem_agent.prompts import PERCEIVE_PROMPT
from stem_agent.state import Signal, StemState


def perceive(state: StemState) -> dict:
    """Classify the incoming user message into domain, complexity, intent, and hints."""
    llm = init_chat_model(CONFIG.model).with_structured_output(Signal)

    result: Signal = llm.invoke(
        [SystemMessage(content=PERCEIVE_PROMPT)] + list(state["messages"])
    )

    return {"signal": result.model_dump()}
