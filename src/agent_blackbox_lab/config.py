from __future__ import annotations

import os
from pathlib import Path


QWEN_CHAT_COMPLETIONS_BASE = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
QWEN_DEFAULT_MODEL = "qwen3.7-plus"


def load_key_file(path: Path | None) -> None:
    if path is None:
        return
    if not path.exists():
        raise FileNotFoundError(f"Key file does not exist: {path}")

    raw_lines = path.read_text(encoding="utf-8").splitlines()
    entries = [line.strip() for line in raw_lines if line.strip() and not line.strip().startswith("#")]
    if not entries:
        return

    if any("=" in entry for entry in entries):
        for entry in entries:
            if "=" not in entry:
                continue
            key, value = entry.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and value and key not in os.environ:
                os.environ[key] = value
        return

    raw_key = entries[0]
    os.environ.setdefault("DASHSCOPE_API_KEY", raw_key)
    os.environ.setdefault("MODEL_API_KEY", raw_key)


def qwen_defaults(
    api_model: str | None,
    api_key: str | None,
    api_base: str | None,
) -> tuple[str, str | None, str]:
    resolved_model = api_model or os.environ.get("MODEL_NAME") or QWEN_DEFAULT_MODEL
    resolved_key = api_key or os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("MODEL_API_KEY")
    resolved_base = api_base or os.environ.get("MODEL_API_BASE") or QWEN_CHAT_COMPLETIONS_BASE
    return resolved_model, resolved_key, resolved_base
