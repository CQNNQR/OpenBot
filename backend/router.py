from typing import Any, Dict

# A simple model preference map. This should be configurable (JSON/DB) in the future.
MODEL_MAP: Dict[str, Dict[str, Any]] = {
    "fast": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.6},
    "creative": {"provider": "openai", "model": "gpt-4o", "temperature": 0.9},
    "logical": {"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.2},
}


def resolve_model(preference: str) -> Dict[str, Any]:
    """Resolve a model preference tag to a concrete model configuration."""

    return MODEL_MAP.get(preference, MODEL_MAP["fast"])
