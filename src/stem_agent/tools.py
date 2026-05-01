"""Tool definitions and registry for the STEM Agent.

Every tool is a @tool-decorated function with a clear docstring — the LLM
uses the docstring to decide when to call it.
"""

from __future__ import annotations

import ast
import os
from datetime import datetime, timezone
from typing import Any

from langchain_core.tools import tool


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@tool
def utc_now() -> str:
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(tz=timezone.utc).isoformat()


@tool
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression safely.

    Supported operators: +, -, *, /, %, ** and parentheses.
    """
    parsed = ast.parse(expression, mode="eval")
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
    )
    for node in ast.walk(parsed):
        if not isinstance(node, allowed_nodes):
            raise ValueError("Expression contains unsupported syntax")

    result: Any = eval(  # noqa: S307 — safe: AST is validated above
        compile(parsed, "<calculator>", "eval"), {"__builtins__": {}}, {}
    )
    return str(result)


@tool
def file_reader(path: str) -> str:
    """Read and return the contents of a file at the given path.

    Use this tool when you need to inspect source code, configuration files,
    or documentation on disk.  The *path* should be relative to the project
    root or an absolute path.
    """
    resolved = os.path.abspath(path)
    if not os.path.isfile(resolved):
        return f"Error: '{path}' is not a file or does not exist."
    try:
        with open(resolved, encoding="utf-8", errors="replace") as fh:
            content = fh.read(50_000)  # cap at 50 KB for safety
        return content
    except Exception as exc:  # noqa: BLE001
        return f"Error reading file: {exc}"


@tool
def web_search(query: str) -> str:
    """Search the web for information related to *query*.

    NOTE: This is a **stub** for the MVP.  Replace the body with a real
    search API integration (e.g. Tavily, SerpAPI) when ready.
    """
    return (
        f"[web_search stub] No real results — query was: '{query}'.  "
        "Wire this tool to a search API for production use."
    )


# ---------------------------------------------------------------------------
# Registry — maps tool *name* → tool object so the Execute node can bind
# only the tools selected during planning.
# ---------------------------------------------------------------------------

ALL_TOOLS = [utc_now, calculator, file_reader, web_search]

TOOL_REGISTRY: dict[str, Any] = {t.name: t for t in ALL_TOOLS}


def get_tools_by_names(names: list[str]) -> list:
    """Return tool objects for the given list of tool names."""
    tools = []
    for name in names:
        if name in TOOL_REGISTRY:
            tools.append(TOOL_REGISTRY[name])
    return tools


def tools_description() -> str:
    """Return a human-readable summary of every registered tool."""
    lines: list[str] = []
    for t in ALL_TOOLS:
        lines.append(f"- **{t.name}**: {t.description}")
    return "\n".join(lines)
