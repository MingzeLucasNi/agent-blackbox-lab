# Agent Blackbox Lab

A small, readable lab for studying black-box attacks against tool-using LLM
agents. The project is inspired by benchmarks such as AgentDojo and InjecAgent,
but is intentionally minimal so researchers can quickly modify the agent,
tools, attacks, guardrails, and hard-label evaluator.

The default setup runs without any API key. It includes two scripted model
policies:

- `scripted-safe`: ignores malicious tool output and completes the user task.
- `scripted-vulnerable`: follows injected tool output and leaks a secret through
  an external tool.

This makes the full experiment pipeline testable before you connect a real LLM.

## Research Question

In an agent setting, the target is not only a prompt or one model. The target is
the composition of:

- a language model policy,
- tool outputs from trusted and untrusted sources,
- action parsing,
- environment state,
- guardrails,
- and task success criteria.

This repo treats the whole agent as a black box. The evaluator only observes
hard labels such as task success, attack success, blocked action, and timeout.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m agent_blackbox_lab eval --model scripted-safe
python -m agent_blackbox_lab eval --model scripted-vulnerable
python -m agent_blackbox_lab eval --model scripted-vulnerable --guard redact-secrets
```

Run one scenario and print the trajectory:

```bash
python -m agent_blackbox_lab run --scenario inbox_indirect_injection --model scripted-vulnerable
```

## Repository Layout

```text
.
├── data/scenarios.json              # Small benchmark scenarios
├── src/agent_blackbox_lab/
│   ├── agent.py                     # Tool-using agent loop
│   ├── cli.py                       # Command-line interface
│   ├── evaluator.py                 # Hard-label evaluator
│   ├── guardrails.py                # Optional policy hooks
│   ├── models.py                    # Model interface and scripted models
│   ├── scenarios.py                 # Scenario loader
│   └── tools.py                     # Tool definitions and environment state
└── tests/                           # Unit tests for the lab
```

## Threat Model

The user asks the agent to complete a benign task. During execution, the agent
may read untrusted content from a tool, such as an inbox message or note. An
attacker embeds instructions inside that content. The attacker wins if the agent
violates policy, for example by sending a secret to an external recipient.

The evaluator does not need logits or model internals. It assigns hard labels:

- `task_success`: did the agent complete the user task?
- `attack_success`: did the attacker objective happen?
- `blocked`: did a guardrail block an unsafe action?
- `steps`: how many agent steps were used?

## Extending the Lab

Useful modifications:

1. Add a new tool in `src/agent_blackbox_lab/tools.py`.
2. Add a new scenario in `data/scenarios.json`.
3. Add a new guardrail in `src/agent_blackbox_lab/guardrails.py`.
4. Add a real LLM adapter in `src/agent_blackbox_lab/models.py`.
5. Replace the scripted attacks with a query-based black-box optimizer.

## Relation to Existing Benchmarks

This is not a replacement for AgentDojo or InjecAgent. It is a compact research
scaffold for developing methods before scaling them to larger public
benchmarks.

- AgentDojo: dynamic security benchmark for prompt injection attacks and
  defenses in tool-using agents.
- InjecAgent: benchmark for indirect prompt injection in tool-integrated agents.

Recommended workflow:

1. Prototype attack ideas here.
2. Transfer promising methods to AgentDojo.
3. Re-test on InjecAgent or a more realistic open-source agent framework.
