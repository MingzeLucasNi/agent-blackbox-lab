from __future__ import annotations

from enum import Enum


class LayerEvent(str, Enum):
    INPUT_ACCEPTED = "input_accepted"
    UNTRUSTED_CONTEXT_OBSERVED = "untrusted_context_observed"
    MODEL_ACTION_PROPOSED = "model_action_proposed"
    TOOL_CALL_PROPOSED = "tool_call_proposed"
    TOOL_CALL_BLOCKED = "tool_call_blocked"
    TOOL_EXECUTED = "tool_executed"
    HARMFUL_STATE_CHANGE = "harmful_state_change"
    OUTPUT_BLOCKED = "output_blocked"


LAYER_DEPTHS = {
    LayerEvent.INPUT_ACCEPTED.value: 0,
    LayerEvent.UNTRUSTED_CONTEXT_OBSERVED.value: 1,
    LayerEvent.MODEL_ACTION_PROPOSED.value: 2,
    LayerEvent.TOOL_CALL_PROPOSED.value: 2,
    LayerEvent.TOOL_CALL_BLOCKED.value: 3,
    LayerEvent.TOOL_EXECUTED.value: 2,
    LayerEvent.HARMFUL_STATE_CHANGE.value: 5,
    LayerEvent.OUTPUT_BLOCKED.value: 5,
}


DEPTH_LABELS = {
    0: "input",
    1: "context",
    2: "model_policy",
    3: "planner_or_tool_guardrail",
    4: "tool_execution",
    5: "environment_state",
    6: "dual_success",
}
