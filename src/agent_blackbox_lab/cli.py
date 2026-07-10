from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import ToolUsingAgent
from .evaluator import evaluate_scenario
from .guardrails import build_guardrail
from .models import build_model
from .scenarios import load_scenarios
from .tools import ToolEnvironment


def _data_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "scenarios.json"


def run_one(args: argparse.Namespace) -> None:
    scenarios = {scenario["id"]: scenario for scenario in load_scenarios(args.scenarios)}
    scenario = scenarios[args.scenario]
    environment = ToolEnvironment.from_scenario(scenario)
    agent = ToolUsingAgent(
        model=build_model(args.model),
        environment=environment,
        guardrail=build_guardrail(args.guard),
        max_steps=args.max_steps,
    )
    result = agent.run(scenario["user_task"])
    label = evaluate_scenario(scenario, result, environment)
    print(json.dumps({"label": label, "trajectory": result.trajectory}, indent=2))


def run_eval(args: argparse.Namespace) -> None:
    rows = []
    for scenario in load_scenarios(args.scenarios):
        environment = ToolEnvironment.from_scenario(scenario)
        agent = ToolUsingAgent(
            model=build_model(args.model),
            environment=environment,
            guardrail=build_guardrail(args.guard),
            max_steps=args.max_steps,
        )
        result = agent.run(scenario["user_task"])
        rows.append(evaluate_scenario(scenario, result, environment))

    print(json.dumps(rows, indent=2))


def _common_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--scenarios", type=Path, default=_data_path())
    common.add_argument("--model", default="scripted-safe", choices=["scripted-safe", "scripted-vulnerable"])
    common.add_argument("--guard", default="none", choices=["none", "redact-secrets"])
    common.add_argument("--max-steps", type=int, default=8)
    return common


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Agent Blackbox Lab.")
    common = _common_parser()

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run",
        parents=[common],
        help="Run one scenario and print its trajectory.",
    )
    run_parser.add_argument("--scenario", default="inbox_indirect_injection")
    run_parser.set_defaults(func=run_one)

    eval_parser = subparsers.add_parser(
        "eval",
        parents=[common],
        help="Evaluate all scenarios.",
    )
    eval_parser.set_defaults(func=run_eval)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
