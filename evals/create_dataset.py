"""Create the 'STEM Agent Benchmark' dataset in LangSmith.

Run once:  python -m evals.create_dataset
"""

from langsmith import Client
from dotenv import load_dotenv

def main() -> None:
    load_dotenv()
    client = Client()

    dataset = client.create_dataset(
        dataset_name="STEM Agent v2 Benchmark",
        description="Tasks spanning simple→complex for testing agent differentiation.",
    )

    examples = [
        # Simple — single-pass, no tools needed
        {
            "inputs": {"task": "Write a Python function that checks if a string is a palindrome."},
            "outputs": {
                "expected_complexity": "simple",
                "reference_answer": (
                    "A function that reverses the string and compares it to the original, "
                    "returning True/False."
                ),
            },
        },
        {
            "inputs": {"task": "Explain what the SOLID principles are in one paragraph."},
            "outputs": {
                "expected_complexity": "simple",
                "reference_answer": (
                    "SOLID stands for Single Responsibility, Open/Closed, Liskov Substitution, "
                    "Interface Segregation, and Dependency Inversion — five design principles "
                    "for maintainable object-oriented software."
                ),
            },
        },
        # Medium — benefits from tool use
        {
            "inputs": {"task": "What is the current UTC time? Then calculate 17 * 23."},
            "outputs": {
                "expected_complexity": "medium",
                "reference_answer": "The current UTC time and the result 391.",
            },
        },
        {
            "inputs": {
                "task": (
                    "Read the file 'pyproject.toml' in this project and summarise "
                    "its dependencies."
                )
            },
            "outputs": {
                "expected_complexity": "medium",
                "reference_answer": (
                    "A summary listing the project's Python dependencies from pyproject.toml."
                ),
            },
        },
        # Complex — requires multi-step reasoning
        {
            "inputs": {
                "task": (
                    "Review the following Python code for security vulnerabilities and "
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
                    "unsanitised user input to subprocess with shell=True.  Fixes include "
                    "using subprocess.run with a list of args and shell=False, input "
                    "validation, and least-privilege execution."
                ),
            },
        },
        {
            "inputs": {
                "task": (
                    "Design a microservice architecture for a real-time chat application "
                    "that supports 10k concurrent users.  Include service boundaries, "
                    "communication protocols, and a data-storage strategy."
                )
            },
            "outputs": {
                "expected_complexity": "complex",
                "reference_answer": (
                    "An architecture with separate services for auth, messaging, presence, "
                    "and notifications using WebSockets for real-time delivery, a message "
                    "broker (e.g. Kafka/Redis Streams) for inter-service comms, and a "
                    "combination of a relational DB for users and a time-series/NoSQL store "
                    "for messages."
                ),
            },
        },
    ]

    client.create_examples(dataset_id=dataset.id, examples=examples)
    print(f"✅ Created dataset '{dataset.name}' with {len(examples)} examples.")


if __name__ == "__main__":
    main()
