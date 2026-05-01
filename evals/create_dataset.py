"""Create the 'STEM Agent Benchmark' dataset in LangSmith.

Run once:  python -m evals.create_dataset
"""

from stem_agent.tools import file_reader
from langsmith import Client
from dotenv import load_dotenv

def main() -> None:
    load_dotenv()
    client = Client()

    dataset = client.create_dataset(
        dataset_name="STEM Agent Benchmark",
        description="Tasks spanning from simple to complex for testing agents.",
    )

    examples = [
        # Simple — tests basic tool use and LLM-as-a-judge edge cases
        {
            "inputs": {"task": "What is the current UTC time? Then calculate 17 * 23."},
            "outputs": {
                "expected_complexity": "simple",
                "reference_answer": "The current UTC time and the result 391.",
                "expected_tools": ["utc_now", "calculator"],
            },
        },
        # Medium — benefits from tool use (filesystem, web search)
        {
            "inputs": {
                "task": (
                    "Search the web for the latest documentation on the langgraph openevals and tavily mcp. "
                    "Summarize how to initialize the client and perform a basic search."
                )
            },
            "outputs": {
                "expected_complexity": "medium",
                "reference_answer": (
                    "A summary showing how to access openevals and tavily mcp."
                ),
                "expected_tools": ["web_search"],
            },
        },
        {
            "inputs": {
                "task": (
                    "Review this project's graph.py file. "
                )
            },
            "outputs": {
                "expected_complexity": "medium",
                "reference_answer": (
                    "A code review of the graph.py file, with comments on its efficiency and correctness."
                ),
                "expected_tools": ["file_search", "file_reader"],
            },
        },
        # Complex — requires multi-step reasoning, skills, and tools
        {
            "inputs": {
                "task": (
                    "Find security vulnerabilities and "
                    "suggest fixes:\n\n"
                    "import os, subprocess\n"
                    "def run(cmd):\n"
                    "    return subprocess.call(cmd, shell=True)\n\n"
                    "user_input = input('Enter command: ')\n"
                    "run(user_input)\n"
                )
            },
            "outputs": {
                "expected_complexity": "complex",
                "reference_answer": (
                    "The code has a command-injection vulnerability because it passes "
                    "unsanitized user input to subprocess with shell=True.  Fixes include "
                    "using subprocess.run with a list of args and shell=False, input "
                    "validation, and least-privilege execution."
                ),
                "expected_tools": [],
            },
        },
        {
            "inputs": {
                "task": (
                    "Design an architecture and implementation plan for a new LangGraph agent "
                    "that acts as a customer support bot. It needs to route queries to either "
                    "a billing node, a technical support node, or a human escalation node."
                )
            },
            "outputs": {
                "expected_complexity": "complex",
                "reference_answer": (
                    "An architecture plan detailing a StateGraph with nodes for routing, billing, "
                    "tech support, and human-in-the-loop. Includes state definitions and conditional edges."
                ),
                "expected_tools": [],
            },
        },
        {
            "inputs": {
                "task": (
                    "Perform a code review and suggest refactoring for a massive monolithic "
                    "Python file containing both database access, HTML rendering, and business logic. "
                    "How should this be structured?"
                )
            },
            "outputs": {
                "expected_complexity": "complex",
                "reference_answer": (
                    "If such a file exists suggestions to apply the Single Responsibility Principle and MVC/Clean Architecture, "
                    "separating the code into models (DB), views (HTML), and controllers (business logic)."
                ),
                "expected_tools": ["file_search", "file_reader"],
            },
        },
    ]

    client.create_examples(dataset_id=dataset.id, examples=examples)
    print(f"Created dataset '{dataset.name}' with {len(examples)} examples.")


if __name__ == "__main__":
    main()
