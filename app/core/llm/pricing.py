from __future__ import annotations

from typing import Any


# USD per 1M tokens (input, output). Free models default to 0.
_MODEL_PRICING: dict[str, tuple[float, float]] = {
    "google/gemma-4-31b-it:free": (0.0, 0.0),
    "google/gemma-4-26b-a4b-it:free": (0.0, 0.0),
    "openai/gpt-oss-20b:free": (0.0, 0.0),
    "nvidia/nemotron-3-nano-30b-a3b:free": (0.0, 0.0),
}


def estimate_cost_usd(model: str | None, usage: dict[str, Any] | None) -> float | None:
    if not model or not usage:
        return None
    prompt = _int_token(usage.get("prompt_tokens"))
    completion = _int_token(usage.get("completion_tokens"))
    if prompt is None and completion is None:
        total = _int_token(usage.get("total_tokens"))
        if total is None:
            return None
        prompt = total
        completion = 0
    prompt = prompt or 0
    completion = completion or 0
    in_rate, out_rate = _MODEL_PRICING.get(model, (0.0, 0.0))
    cost = (prompt / 1_000_000) * in_rate + (completion / 1_000_000) * out_rate
    return round(cost, 6)


def _int_token(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
