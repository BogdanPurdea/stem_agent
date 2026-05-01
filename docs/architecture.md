# STEM Agent
Initially, the idea is to implement one agent that acts in a similar fashion to stem cells.
A stem cell doesn't know what it will become. It reads signals from its environment and transforms — into a neuron, a muscle fiber, a blood cell. Whatever the body needs. If something goes wrong mid-transformation, built-in safeguards pull it back.

# Architecture
## Core Components

- **Perceive:** Reads signals from the environment. Our environment is the task provided through the user prompt, the signals are the task doman, the complexity and anything else that can determine how the agent should behave. E.g. if the task is to write an article about AI, the agent should try to use tools in the execution phase to gather as much information as possible about the topic.
- **Adapt/Reason:** Analyzes the signals and decides on it's persona, reasoning strategy and approach that can achieve the best future results after the execution phase.
- **Plan:** Checks available tools and skills (SKILL.md files that provide details about achieving a task) and creates a plan to achieve the goal that makes use of the tools deemed necessary.
- **Execute:** Executes the plan loop provided from the previous Plan Node.
- **Memory:** Stores information about the environment and the agent's state.
- **Tools:** Provides the agent with the ability to interact with the environment.
- **Safeguards:** Built-in checks to ensure the agent stays on track and doesn't go off the rails.

## Implementation Plan
 Initial Nodes: Perceive, Adapt/Reason, Plan, Execute
## Tools
    Initially, a set of tools relevant to the software development industry will be provided. These tools will be used by the agent to gather information and perform tasks related to the software development industry. In the plan phase, the agent will decide which tools are relevant to the task at hand and will use those tools to create a plan to achieve the goal. This will allow for the creation of agents that are specialized in specific areas of the software development industry.


## Skills
    Langchain/Langgraph SKILL.md files provide a structured way to define the skills of an agent. These files will be used by the agent to gather information and perform tasks related to the software development industry. In the plan phase, the agent will decide which skills are relevant to the task at hand and will use those skills to create a plan to achieve the goal. This will allow for the creation of agents that are specialized in specific areas of the software development industry. You will also use those to implement this agent.

## Chosen scope: Software Development Industry 
## Possible domains: Security, Software architecture and planning, Implementing agents in the software development industry
