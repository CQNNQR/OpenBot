import os
import time
from typing import Any, Dict, List

import litellm


def _get_openai_client(api_key: str, model: str):
    return litellm.OpenAI(model=model, api_key=api_key)


def _get_anthropic_client(api_key: str, model: str):
    return litellm.Anthropic(model=model, api_key=api_key)


def generate_response(messages: List[Dict[str, Any]], model_config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a response from a configured model.

    Args:
        messages: List of messages in the format [{"role": "user"|"assistant", "content": "..."}].
        model_config: Dict with keys: provider, model, temperature.

    Returns:
        Dict with keys: response (dict with role/content), trace (metadata).
    """

    provider = model_config.get("provider")
    model = model_config.get("model")
    temperature = float(model_config.get("temperature", 0.7))

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        client = _get_openai_client(api_key, model)
        call_method = client.chat_completion
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        client = _get_anthropic_client(api_key, model)
        call_method = client.chat_completion
    else:
        raise ValueError(f"Unknown provider: {provider}")

    start = time.perf_counter()
    result = call_method(messages=messages, temperature=temperature)
    duration_ms = int((time.perf_counter() - start) * 1000)

    # LiteLLM returns an object with `.choices` (OpenAI style) or `.response`.
    # We'll attempt to normalize common patterns.
    content = None
    if isinstance(result, dict):
        content = result.get("content") or result.get("text")
        if not content and "choices" in result:
            first = result["choices"][0]
            if isinstance(first, dict):
                content = first.get("message", {}).get("content") or first.get("text")
    else:
        # Try to access attributes
        content = getattr(result, "content", None) or getattr(result, "text", None)
        if not content and hasattr(result, "choices"):
            first = result.choices[0]
            content = getattr(first, "message", None)
            if isinstance(content, dict):
                content = content.get("content")
            if not content:
                content = getattr(first, "text", None)

    if not content:
        content = "(no response)"

    return {
        "response": {"role": "assistant", "content": content},
        "trace": {
            "model_used": f"{provider}:{model}",
            "duration_ms": duration_ms,
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "messages": len(messages),
            "last_user": messages[-1]["content"] if messages and messages[-1].get("role") == "user" else None,
        },
    }
