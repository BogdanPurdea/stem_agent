# Stem Agent: Self-Adapting Cognitive Pipeline

The **Stem Agent** is an autonomous software-development agent inspired by the biological metaphor of a stem cell. Just as a stem cell differentiates based on environmental signals, this agent dynamically adapts its persona, reasoning strategy, and toolset based on the perceived domain and complexity of the task.

## The Architecture

The agent operates through a deterministic pipeline that transforms the initial task into a specialized execution context:

1.  **Perceive**: Extracts environmental signals (domain, complexity, intent) from the user prompt.
2.  **Adapt**: Determines the optimal reasoning strategy (e.g., ReAct) and persona (e.g., Security Analyst) for the task.
3.  **Plan**: Drafts a step-by-step execution blueprint and selects the required tools and specialized skills.
4.  **Load Skills**: Deterministically loads the full markdown content of technical procedures (Skills) from the registry.
5.  **Execute**: Invokes the LLM within the specialized context to achieve the goal via a tool-calling loop.
6.  **Call Tool**: Executes actions and manages a circuit-breaker safeguard to prevent infinite loops on failure.

---

## Setup

### 1. Prerequisites
- [uv](https://github.com/astral-sh/uv) installed on your machine.
- OpenAI API Key.
- Tavily API Key (for the web search tool, free tier available at https://tavily.com).

### 2. Installation
Sync the project dependencies:
```bash
make dev
```

### 3. Configuration
Copy the template and fill in your API keys:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
- `OPENAI_API_KEY`
- `TAVILY_API_KEY`
- `LANGSMITH_API_KEY` (optional, for tracing and evaluation)

---

## Usage

### Running the Local Agent
Start the LangGraph development server to interact with the agent via the Studio:
```bash
make run
```

### Adding New Skills
The agent can "specialize" by reading markdown files in the `src/skills/` directory. Each skill should be a directory containing a `SKILL.md` file with YAML frontmatter.

---

## Evaluation Pipeline

The project includes a minimal evaluation suite to compare the STEM Agent against a standard ReAct baseline.

1.  **Create Dataset**: Upload the benchmark dataset to LangSmith.
    ```bash
    make create-dataset
    ```
2.  **Run STEM Evaluation**: Run the pipeline and score using `openevals`.
    ```bash
    make eval
    ```
3.  **Run Baseline Evaluation**: Run the standard ReAct agent for comparison.
    ```bash
    make eval-baseline
    ```

---

## Quality Assurance

### Testing
Run unit and integration tests:
```bash
make test
make integration-tests
```

### Linting & Formatting
Ensure code quality with Ruff:
```bash
make lint
make format
```

---

## Reference Documentation
- [Writeup](writeup.md)
- [Evaluation Experiments](https://smith.langchain.com/public/d15b97f0-2119-4354-a901-1fb6744703d0/d)
- [Architecture Docs](src/architecture.md)
