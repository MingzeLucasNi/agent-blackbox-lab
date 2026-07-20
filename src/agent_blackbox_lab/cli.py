from __future__ import annotations

import argparse
import json
from pathlib import Path

from .attacks import run_template_attack
from .config import load_key_file, qwen_defaults
from .evaluator import evaluate_scenario
from .guardrails import build_guardrail
from .metrics import summarize_labels
from .models import build_model
from .scenarios import load_scenarios
from .targets import build_target


def _data_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "scenarios.json"


def _build_model(args: argparse.Namespace):
    load_key_file(args.key_file)
    api_model = args.api_model
    api_key = args.api_key
    api_base = args.api_base
    if args.provider == "qwen":
        api_model, api_key, api_base = qwen_defaults(api_model, api_key, api_base)
    return build_model(
        args.model,
        api_model=api_model,
        api_key=api_key,
        api_base=api_base,
        temperature=args.temperature,
    )


def run_one(args: argparse.Namespace) -> None:
    scenarios = {scenario["id"]: scenario for scenario in load_scenarios(args.scenarios)}
    scenario = scenarios[args.scenario]
    target = build_target(
        args.target,
        model=_build_model(args),
        guardrail=build_guardrail(args.guard),
        max_steps=args.max_steps,
    )
    run = target.run(scenario)
    label = evaluate_scenario(scenario, run.result, run.environment)
    print(json.dumps({"label": label, "trajectory": run.result.trajectory}, indent=2))


def run_eval(args: argparse.Namespace) -> None:
    rows = []
    target = build_target(
        args.target,
        model=_build_model(args),
        guardrail=build_guardrail(args.guard),
        max_steps=args.max_steps,
    )
    for scenario in load_scenarios(args.scenarios):
        run = target.run(scenario)
        rows.append(evaluate_scenario(scenario, run.result, run.environment))

    output = {"target": args.target, "model": args.model, "summary": summarize_labels(rows), "rows": rows}
    print(json.dumps(output, indent=2))


def run_attack(args: argparse.Namespace) -> None:
    scenarios = {scenario["id"]: scenario for scenario in load_scenarios(args.scenarios)}
    scenario = scenarios[args.scenario]
    target = build_target(
        args.target,
        model=_build_model(args),
        guardrail=build_guardrail(args.guard),
        max_steps=args.max_steps,
    )
    result = run_template_attack(target, scenario, budget=args.budget)
    print(json.dumps(result, indent=2))


def run_smoke(args: argparse.Namespace) -> None:
    target = build_target(
        args.target,
        model=_build_model(args),
        guardrail=build_guardrail(args.guard),
        max_steps=args.max_steps,
    )
    rows = []
    for scenario in load_scenarios(args.scenarios):
        run = target.run(scenario)
        label = evaluate_scenario(scenario, run.result, run.environment)
        rows.append(
            {
                "scenario_id": scenario["id"],
                "task_success": label["task_success"],
                "attack_success": label["attack_success"],
                "blocked": label["blocked"],
                "penetration_depth": label["penetration_depth"],
                "final_answer": label["final_answer"],
            }
        )
    passed = all(row["task_success"] for row in rows)
    print(json.dumps({"passed": passed, "target": args.target, "model": args.model, "rows": rows}, indent=2))


def _common_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--scenarios", type=Path, default=_data_path())
    common.add_argument("--target", default="toy-agent")
    common.add_argument(
        "--model",
        default="scripted-safe",
        choices=["scripted-safe", "scripted-vulnerable", "openai-compatible"],
    )
    common.add_argument("--guard", default="none", choices=["none", "redact-secrets"])
    common.add_argument("--max-steps", type=int, default=8)
    common.add_argument("--provider", default="generic", choices=["generic", "qwen"])
    common.add_argument("--api-model", default=None)
    common.add_argument("--api-key", default=None)
    common.add_argument("--api-base", default=None)
    common.add_argument("--key-file", type=Path, default=None)
    common.add_argument("--temperature", type=float, default=0.0)
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

    attack_parser = subparsers.add_parser(
        "attack",
        parents=[common],
        help="Run a black-box attack baseline against one scenario.",
    )
    attack_parser.add_argument("--scenario", default="inbox_indirect_injection")
    attack_parser.add_argument("--method", default="template-mutation", choices=["template-mutation"])
    attack_parser.add_argument("--budget", type=int, default=5)
    attack_parser.set_defaults(func=run_attack)

    smoke_parser = subparsers.add_parser(
        "smoke",
        parents=[common],
        help="Check whether a target can complete benign scenario tasks.",
    )
    smoke_parser.set_defaults(func=run_smoke)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
