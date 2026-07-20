from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agent import AgentResult, ToolUsingAgent
from .guardrails import Guardrail
from .models import ModelPolicy
from .tools import ToolEnvironment


@dataclass
class TargetRun:
    result: AgentResult
    environment: ToolEnvironment


class AgentTarget:
    name = "base"

    def run(self, scenario: dict[str, Any]) -> TargetRun:
        raise NotImplementedError


class ToyAgentTarget(AgentTarget):
    name = "toy-agent"

    def __init__(
        self,
        model: ModelPolicy,
        guardrail: Guardrail | None = None,
        max_steps: int = 8,
    ) -> None:
        self.model = model
        self.guardrail = guardrail
        self.max_steps = max_steps

    def run(self, scenario: dict[str, Any]) -> TargetRun:
        environment = ToolEnvironment.from_scenario(scenario)
        agent = ToolUsingAgent(
            model=self.model,
            environment=environment,
            guardrail=self.guardrail,
            max_steps=self.max_steps,
        )
        return TargetRun(result=agent.run(scenario["user_task"]), environment=environment)


class ExternalTargetPlaceholder(AgentTarget):
    """Documents the integration point for mature public agents.

    AgentDojo, InjecAgent, mini-SWE-agent, and OpenHands can be wrapped by
    implementing this interface and converting their trajectories to the common
    AgentResult format.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def run(self, scenario: dict[str, Any]) -> TargetRun:
        raise NotImplementedError(
            f"{self.name} is a placeholder. Add an adapter that returns TargetRun."
        )


def build_target(
    name: str,
    model: ModelPolicy,
    guardrail: Guardrail | None,
    max_steps: int,
) -> AgentTarget:
    if name == "toy-agent":
        return ToyAgentTarget(model=model, guardrail=guardrail, max_steps=max_steps)
    if name in {"agentdojo", "injectagent", "mini-swe-agent", "openhands"}:
        return ExternalTargetPlaceholder(name)
    raise ValueError(f"Unknown target: {name}")
