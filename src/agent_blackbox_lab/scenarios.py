from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        scenarios = json.load(handle)
    if not isinstance(scenarios, list):
        raise ValueError("Scenario file must contain a list.")
    return scenarios

