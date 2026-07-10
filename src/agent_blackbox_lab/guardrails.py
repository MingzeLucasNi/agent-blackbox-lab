from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .tools import ToolEnvironment


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    reason: str | None = None


class Guardrail:
    def check_tool_call(
        self,
        tool_name: str,
        args: dict[str, Any],
        environment: ToolEnvironment,
    ) -> GuardrailDecision:
        return GuardrailDecision(True)

    def check_final(self, final_answer: str, environment: ToolEnvironment) -> GuardrailDecision:
        return GuardrailDecision(True)


class SecretRedactionGuardrail(Guardrail):
    """Blocks tool calls or final answers that contain the scenario secret."""

    def check_tool_call(
        self,
        tool_name: str,
        args: dict[str, Any],
        environment: ToolEnvironment,
    ) -> GuardrailDecision:
        serialized = repr(args)
        if environment.secret and environment.secret in serialized:
            return GuardrailDecision(False, "secret_detected_in_tool_call")
        return GuardrailDecision(True)

    def check_final(self, final_answer: str, environment: ToolEnvironment) -> GuardrailDecision:
        if environment.secret and environment.secret in final_answer:
            return GuardrailDecision(False, "secret_detected_in_final_answer")
        return GuardrailDecision(True)


def build_guardrail(name: str) -> Guardrail | None:
    if name == "none":
        return None
    if name == "redact-secrets":
        return SecretRedactionGuardrail()
    raise ValueError(f"Unknown guardrail: {name}")

