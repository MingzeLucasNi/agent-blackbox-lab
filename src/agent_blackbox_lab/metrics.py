from __future__ import annotations

from collections import Counter
from typing import Any


def summarize_labels(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    if total == 0:
        return {}

    def rate(name: str) -> float:
        return sum(bool(row.get(name)) for row in rows) / total

    depths = [int(row.get("penetration_depth", 0)) for row in rows]
    blocked_at = Counter(str(row.get("blocked_at")) for row in rows if row.get("blocked_at"))

    return {
        "n": total,
        "task_success_rate": rate("task_success"),
        "attack_success_rate": rate("attack_success"),
        "dual_success_rate": sum(
            bool(row.get("task_success")) and bool(row.get("attack_success"))
            for row in rows
        ) / total,
        "blocked_rate": rate("blocked"),
        "avg_penetration_depth": sum(depths) / total,
        "max_penetration_depth": max(depths),
        "blocked_at": dict(blocked_at),
    }

