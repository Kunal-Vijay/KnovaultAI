from __future__ import annotations

from dataclasses import dataclass

_STRUCTURED_FALLBACKS: tuple[str, ...] = (
    "openai/gpt-oss-20b:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
)


@dataclass(frozen=True, slots=True)
class ModelPlug:
    name: str
    model: str
    fallbacks: tuple[str, ...] = ()
    description: str = ""


def _fallbacks_excluding(*exclude: str) -> tuple[str, ...]:
    blocked = set(exclude)
    return tuple(m for m in _STRUCTURED_FALLBACKS if m not in blocked)


MODEL_PLUGS: dict[str, ModelPlug] = {
    "gemma-31b": ModelPlug(
        name="gemma-31b",
        model="google/gemma-4-31b-it:free",
        fallbacks=_fallbacks_excluding("google/gemma-4-31b-it:free"),
        description="Gemma 4 31B instruct — strong instruction following.",
    ),
    "gemma-26b": ModelPlug(
        name="gemma-26b",
        model="google/gemma-4-26b-a4b-it:free",
        fallbacks=_fallbacks_excluding("google/gemma-4-26b-a4b-it:free"),
        description="Gemma 4 26B MoE — fast / efficient.",
    ),
    "gpt-oss-20b": ModelPlug(
        name="gpt-oss-20b",
        model="openai/gpt-oss-20b:free",
        fallbacks=_fallbacks_excluding("openai/gpt-oss-20b:free"),
        description="OpenAI gpt-oss-20b free tier.",
    ),
    "nemotron-nano": ModelPlug(
        name="nemotron-nano",
        model="nvidia/nemotron-3-nano-30b-a3b:free",
        fallbacks=_fallbacks_excluding("nvidia/nemotron-3-nano-30b-a3b:free"),
        description="Nemotron 3 Nano — lighter model.",
    ),
}


def get_model_plug(name: str) -> ModelPlug:
    key = name.strip().lower()
    try:
        return MODEL_PLUGS[key]
    except KeyError as exc:
        available = ", ".join(sorted(MODEL_PLUGS))
        raise ValueError(f"Unknown model plug {name!r}. Available: {available}") from exc
