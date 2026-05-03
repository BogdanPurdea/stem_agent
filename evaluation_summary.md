# Evaluation Report: Stem Agent vs Baseline

This report summarizes the evaluation results for the **Stem Agent** (which adds perceive, adapt, plan before the ReAct execution loop) compared against a **Baseline ReAct Agent** (which only has the ReAct execution loop), based on experiments tracked in LangSmith.

## Evaluation Metrics

| Metric | Description | Scoring Method |
| :--- | :--- | :--- |
| **Correctness** | Measures the accuracy and completeness of the agent's response relative to the reference answer. | 1 - correct, 0.5 - partially correct, 0 - incorrect |
| **Tool Precision** | The ratio of relevant tool calls to the total number of tools used. | (Correct Tools Called) / (Total Tools Called) |
| **Tool Recall** | The ratio of relevant tool calls to the total number of tools required for the task. | (Correct Tools Called) / (Total Expected Tools) |
| **Differentiation** | Assess the agent's ability to select the correct persona/strategy or handle complex instruction branches. | 1 - correct, 0 - incorrect |
| **Latency (through Langsmith)** | Benchmarking the speed of response generation (P50/P99). | Time measurement |

## Pipeline Details

- **Dataset**: `STEM Agent Benchmark`
- **Experimental Setup**:
    - **Stem Agent**: Multi-stage graph architecture (Perceive -> Adapt -> Plan -> Execute) with specialized skills.
    - **Baseline Agent**: Standard ReAct loop with access to the same toolset and knowledge base.
- **Evaluator**: Automated LLM-as-a-judge (OpenEvals) with context-aware correctness and differentiation prompts. Tool-use precision and tool-use recall are calculated using utility functions.

## Comparison Results

Results are publicly available on [LangSmith](https://smith.langchain.com/) at [this link](https://smith.langchain.com/public/d15b97f0-2119-4354-a901-1fb6744703d0/d).
The following metrics are averages across 9 runs for each agent type.

| Metric | Stem Agent | Baseline Agent |
| :--- | :--- | :--- |
| **Correctness Average** | **0.81** | **0.81** |
| **Tool Precision** | **1.00** | **1.00** |
| **Tool Recall** | **0.88** | 0.75 |
| **Differentiation** | **0.83** | N/A |

### Observations
1. **Better Tool Utilization**: The Stem Agent achieved higher **Tool Recall** (0.88 vs 0.75), confirming that its structured planning phase identifies and uses the necessary tools more reliably than a generic ReAct loop.
2. **Ability to differentiate tasks**: The Stem Agent demonstrates strong **Differentiation** (0.83), adapting its persona and strategy to the task, the baseline agent lacks this capability.
3. **Correctness**: Both agents oscillated throughout the experiments, but ultimately converged on the same average correctness of **0.81**. This indicates that the Stem Agent's added orchestration complexity does not degrade the final output accuracy compared to a direct ReAct approach.
4. **Latency**: The increased latency of the Stem agent does not justify it's adoption over the simple and fast baseline ReAct agent.

As a next step to provide a more thorough evaluation, a complementation of the evaluation metrics and an improved dataset with more complex tasks could reveal the true potential of this Stem Agent architecture.
