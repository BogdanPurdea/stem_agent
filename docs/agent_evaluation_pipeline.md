# LangGraph & LangSmith: Development to Evaluation Pipeline

This guide outlines a step-by-step workflow for developing, debugging, and evaluating the STEM Agent using the LangGraph CLI and LangSmith Studio.

## 0. Fixing Python Environment Issues
If you encounter `Cannot find module 'langsmith'` while running your agent, your terminal is likely using the system's global Python (e.g., Homebrew's Python) instead of your Conda environment.

**To fix this:**
Make sure you have activated the environment in your terminal before running scripts:
```bash
conda activate stem
pip install -r requirements.txt
```
If your IDE (like VSCode) is running scripts, ensure the Python Interpreter is set to your `stem` conda environment.

---

## 1. Prerequisites & Installation

To run the local Studio server, you need the **LangGraph CLI**.

**Install the CLI (with in-memory server support):**
```bash
pip install --upgrade "langgraph-cli[inmem]"
```
*(Also ensure `langsmith`, `openevals`, and `openai`/`langchain-ollama` are installed).*

**Environment Variables:**
Ensure your `.env` file in the project root contains your LangSmith credentials:
```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_...  # Your LangSmith API Key
OLLAMA_BASE_URL=http://localhost:11434  # If using local Ollama
```

---

## 2. Agent Configuration (`langgraph.json`)

The LangGraph CLI needs a configuration file to know where your compiled graph is located. This has already been added to your project:

```json
{
  "dependencies": ["."],
  "graphs": {
    "my_agent": "./src/graph.py:compiled_agent"
  },
  "env": "./.env"
}
```
*Note: `compiled_agent` refers to the compiled `StateGraph` object exposed in `src/graph.py`.*

---

## 3. Local Development with LangSmith Studio

LangSmith Studio provides a visual interface for developing and testing your LangGraph agents from your local machine.

**Start the development server:**
```bash
langgraph dev
```
*(Note: If you use Safari, it blocks localhost connections to Studio. Use `--tunnel` instead: `langgraph dev --tunnel`)*

**View your agent:**
1. Once running, open your browser and navigate to: `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`
2. You can interact with your agent in real-time, view the state graph, trace the exact prompt/tool invocations, and modify code.
3. **Hot-reloading:** The server listens for code changes in your Python files and restarts automatically.

---

## 4. Evaluation Pipeline

Evaluations are a quantitative way to measure the performance of your agent over time.

### A. Creating a Dataset
You can create a dataset visually via the **LangSmith UI -> Datasets & Testing**, or programmatically.

```python
from langsmith import Client

client = Client()
dataset = client.create_dataset(
    dataset_name="STEM Agent Benchmark",
    description="Dataset for testing differentiation and correctness."
)

client.create_examples(
    dataset_id=dataset.id,
    examples=[
        {"inputs": {"task": "Write a Python palindrome checker"}, "outputs": {"complexity": "simple"}},
        {"inputs": {"task": "Review this code for security vulnerabilities"}, "outputs": {"complexity": "complex"}}
    ]
)
```

### B. Defining an Evaluator
You can use `openevals` to create an LLM-as-a-judge that will score the agent's responses against the dataset reference outputs.

```python
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

judge = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="openai:gpt-4o",  # The model to use as a judge
    feedback_key="correctness",
)

def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    return judge(
        inputs=inputs,
        outputs=outputs,
        reference_outputs=reference_outputs
    )
```

### C. Running the Evaluation
Using the `evaluate` function from `langsmith.evaluation`, you can run your graph against the dataset:

```python
from langsmith.evaluation import evaluate
from src.graph import build_graph

agent = build_graph()

def target(inputs: dict) -> dict:
    # Run the graph using the input
    initial_state = {
        "messages": [("user", inputs["task"])],
        "signal": None,
        "strategy": None,
        "plan": [],
        "tool_manifest": [],
        "execution_result": None,
        "consecutive_failures": 0,
        "circuit_breaker_tripped": False,
        "maturation_score": None,
        "reflexion_iterations": 0,
    }
    result = agent.invoke(initial_state)
    return {"result": result.get("execution_result")}

# Run evaluation
evaluate(
    target,
    data="STEM Agent Benchmark",
    evaluators=[correctness_evaluator],
    experiment_prefix="stem-eval-run",
)
```
### D. Viewing Results
After running the evaluation script, open the **LangSmith UI**. Navigate to your dataset and view the generated **Experiment**. You'll see side-by-side results of the agent's performance, the evaluator's scores, and tracing metadata.
