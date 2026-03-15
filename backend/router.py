from typing import Any, Dict

# A simple model preference map. This should be configurable (JSON/DB) in the future.
MODEL_MAP: Dict[str, Dict[str, Any]] = {
    "fast": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.6},
    "creative": {"provider": "openai", "model": "gpt-4o", "temperature": 0.9},
    "logical": {"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.2},
}

# If a different agent is selected, these are the override models.
AGENT_MODEL_MAP: Dict[str, Dict[str, Dict[str, Any]]] = {
    "openai": MODEL_MAP,
    "anthropic": {
        "fast": {"provider": "anthropic", "model": "claude-3-intl", "temperature": 0.6},
        "creative": {"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.9},
        "logical": {"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.2},
    },
    "minimax": {
        "fast": {"provider": "minimax", "model": "minimax-2.5", "temperature": 0.6},
        "creative": {"provider": "minimax", "model": "minimax-2.5", "temperature": 0.9},
        "logical": {"provider": "minimax", "model": "minimax-2.5", "temperature": 0.2},
    },
}

# For minimax mode, this maps a base preference to a stronger / validation model.
MINIMAX_MAP: Dict[str, str] = {
    "fast": "creative",
    "creative": "logical",
    "logical": "creative",
}


def resolve_model(preference: str, agent: str | None = None) -> Dict[str, Any]:
    """Resolve a model preference tag to a concrete model configuration."""

    if agent and agent in AGENT_MODEL_MAP:
        return AGENT_MODEL_MAP[agent].get(preference, AGENT_MODEL_MAP[agent]["fast"])

    return MODEL_MAP.get(preference, MODEL_MAP["fast"])


def resolve_minimax_model(preference: str) -> Dict[str, Any]:
    """Resolve a second model to use for minimax validation.

    Returns a complementary model configuration for the given preference.
    """

    target = MINIMAX_MAP.get(preference, "creative")
    return resolve_model(target)
