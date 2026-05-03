"""Shared state schema and Pydantic models for the STEM Agent pipeline."""

from __future__ import annotations

from typing import Annotated, Literal

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ---------------------------------------------------------------------------
# Pydantic models — used for structured LLM output, then stored as dicts
# ---------------------------------------------------------------------------


class Signal(BaseModel):
    """Output of the Perceive node: environmental signals extracted from the user prompt."""

    domain: str = Field(
        description="Task domain. One of: Security, Architecture, AgentDev, General."
    )
    complexity: Literal["simple", "medium", "complex"] = Field(
        description="Estimated task complexity."
    )
    intent: str = Field(
        description="Concise description of what the user wants to achieve."
    )
    hints: list[str] = Field(
        default_factory=list,
        description="Keywords or contextual signals extracted from the prompt.",
    )


class PlanStep(BaseModel):
    """A single step in the execution plan."""

    step_number: int
    description: str
    tools: list[str] = Field(
        default_factory=list,
        description="Tool names to use in this step.",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="Skill names to use in this step.",
    )


class ExecutionPlan(BaseModel):
    """Structured output of the Plan node."""

    steps: list[PlanStep]
    selected_tools: list[str] = Field(
        default_factory=list,
        description="All unique tool names required for the plan.",
    )
    selected_skills: list[str] = Field(
        default_factory=list,
        description="All unique skill names required for the plan.",
    )


# ---------------------------------------------------------------------------
# Graph state
# ---------------------------------------------------------------------------

# Strategy is built deterministically in the Adapt node, so a plain dict
# with known keys is sufficient (no need for structured LLM output).
# Keys: reasoning_method, persona, system_prompt, max_iterations


class StemState(TypedDict):
    """Shared state flowing through every node of the STEM Agent graph."""

    # Conversation history — uses add_messages reducer (append, dedup by ID)
    messages: Annotated[list[AnyMessage], add_messages]

    # Perceive output
    signal: dict | None  # serialised Signal

    # Adapt output
    strategy: dict | None  # {reasoning_method, persona, system_prompt, max_iterations}

    # Plan output
    plan: list[dict]  # list of serialised PlanStep
    tool_manifest: list[str]  # tool names selected for execution
    skill_manifest: list[str]  # skill names selected for execution
    skills_content: str | None  # Loaded markdown content of the selected skills

    # Execute output
    execution_result: str | None

    # Safeguards
    consecutive_failures: int
    iteration_count: int
    circuit_breaker_tripped: bool

