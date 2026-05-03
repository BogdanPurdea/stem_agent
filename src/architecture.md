# STEM Agent
The STEM agent follows a stem-cell-inspired pattern: it first interprets task signals, then adapts its reasoning mode and persona, plans a task-specific approach, and executes with selective tool/skill use. Safeguards can halt execution if tool failures repeat.

## Current architecture
The runtime is a LangGraph state machine with this flow:
1. Perceive
2. Adapt
3. Plan
4. Load skills (only when selected by planning)
5. Execute
6. Call tool (when execute produces tool calls), then loop back to Execute

Routing behavior:
- After **Plan**: go to **Load skills** if any skills were selected, otherwise go directly to **Execute**.
- After **Execute**: go to **Call tool** if the latest model message contains tool calls; otherwise stop.
- After **Call tool**: return to **Execute** unless the circuit breaker is tripped.

## Core runtime behavior
### 1) Perceive
The agent classifies the incoming request into a structured signal:
- `domain`: Security, Architecture, AgentDev, or General
- `complexity`: simple, medium, or complex
- `intent`: concise goal summary
- `hints`: extracted context cues

### 2) Adapt
Adaptation is deterministic (no model call). It maps complexity to reasoning style and iteration budget:
- simple → `react`, budget: 3
- medium → `react`, budget: 5
- complex → `reflexion`, budget: 10


It also selects a domain persona and builds the primary execution prompt skeleton (`system_prompt`), which includes placeholders for the plan and skills to be filled in later.

### 3) Plan
Planning uses structured output to produce:
- ordered plan steps (`step_number`, `description`, `tools`, `skills`)
- `tool_manifest` (tools selected for runtime binding)
- `skill_manifest` (skills to load into context)

Planning prompt context includes domain/intent, reasoning method, discovered tools, and discovered skills.

### 4) Skill loading
When skills are selected, their full `SKILL.md` contents are loaded into the state and injected into execution context. YAML frontmatter is stripped before prompt injection.

### 5) Execute
Execution node retrieves the pre-built `system_prompt` from the strategy state and populates it with:
- loaded skills content (replacing the skills placeholder)
- formatted plan (replacing the plan placeholder)

Only tools in `tool_manifest` are bound to the model for that run. Each execution superstep increments an `iteration_count`. If this count reaches the budget defined during Adaptation, execution halts and returns a budget-exhausted result.


### 6) Tool calling and safeguards
Tool calls are executed one by one. Unknown tools and runtime errors are captured as tool messages. A consecutive-failure counter is maintained:
- success resets failures to 0
- failure increments the counter
- when failures reach `CIRCUIT_BREAKER_THRESHOLD`, execution halts and a circuit-breaker result is returned

## State and memory model
State carries:
- message history
- signal, strategy, plan
- selected tool/skill manifests
- loaded skills content
- final execution result
- safeguard fields (`consecutive_failures`, `iteration_count`, `circuit_breaker_tripped`)


There is no separate long-term memory subsystem yet; memory is represented by graph state and message accumulation.

## Tooling and skill system
Built-in tools:
- `utc_now`
- `calculator` (safe AST-based arithmetic)
- `file_reader`
- `file_search`
- `web_search` (Tavily-backed, requires API key)

Skill discovery scans the configured skills directory for `SKILL.md` files, extracts frontmatter metadata (name/description), and makes selected skill content available at execution time.

## Tests
### Unit tests
Current unit tests validate:
- graph compilation and signal schema validation
- deterministic Adapt mappings for simple/complex tasks
- skill frontmatter parsing and discovery behavior (including nested directories and fallback naming)
- tool behavior (calculator safety, file read/search paths, tool registry lookup, web search behavior with/without API key)

### Integration tests
One end-to-end async graph test verifies the full pipeline for a simple coding request and checks that signal, strategy, and final output are populated.

Integration execution is environment-gated and skipped when model credentials/runtime are not available.

## Evaluation
Evaluation is LangSmith-based with a benchmark dataset and custom evaluators.

### Dataset
`evals/create_dataset.py` creates **STEM Agent Benchmark** with tasks across simple, medium, and complex cases. Each example includes:
- `expected_complexity`
- `reference_answer`
- `expected_tools`

### Evaluators
`evals/evaluators.py` defines:
- **correctness**: LLM-as-judge via OpenEvals, provided with full execution context (the tools and skills available to the agent).
- **differentiation**: match between perceived complexity and expected complexity
- **tool efficiency**: tool precision and recall against expected tools

### Runs
- `evals/run_eval.py` evaluates STEM Agent with correctness + differentiation + tool efficiency.
- `evals/run_baseline_eval.py` evaluates a baseline ReAct agent (all tools exposed) with correctness + tool efficiency.

Both runs report through LangSmith experiments for side-by-side comparison.

## Scope
Current scope is software-development assistance across Security, Architecture, AgentDev, and General engineering tasks.
