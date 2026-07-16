"""LLM client — calls OpenAI-compatible API (OpenRouter free tier) to generate pipeline code."""

import json
import httpx
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuration for the LLM API call."""
    api_key: str
    model: str = "tencent/hy3:free"
    base_url: str = "https://openrouter.ai/api/v1"
    max_tokens: int = 8000
    temperature: float = 0.3


# Free models ranked by coding ability (July 2026)
FREE_MODELS = {
    "tencent/hy3:free": "Tencent Hy3 — 295B MoE, best overall free model",
    "nvidia/nemotron-3-ultra-550b-a55b:free": "NVIDIA Nemotron 3 Ultra — 550B MoE, strong reasoning",
    "poolside/laguna-m.1:free": "Poolside Laguna — coding-focused, Apache 2.0",
    "google/gemini-3-flash-lite-preview:free": "Google Gemini 3 Flash — fast, 256K context",
}


def call_llm(
    prompt: str,
    system: str = "",
    config: LLMConfig | None = None,
) -> str:
    """Call an OpenAI-compatible LLM API and return the response text.

    Args:
        prompt: The user message to send.
        system: Optional system message.
        config: LLM config. Falls back to OPENROUTER_API_KEY env var.

    Returns:
        The model's response text.
    """
    if config is None:
        import os
        config = LLMConfig(api_key=os.environ.get("OPENROUTER_API_KEY", ""))

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/muhammadzakriarasool/autopipeline",
        "X-Title": "AutoPipeline",
    }

    payload = {
        "model": config.model,
        "messages": messages,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
    }

    with httpx.Client(timeout=120) as client:
        resp = client.post(
            f"{config.base_url}/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

    if "error" in data:
        raise RuntimeError(f"LLM API error: {data['error']}")

    return data["choices"][0]["message"]["content"]


def generate_pipeline_with_llm(
    prompt: str,
    api_key: str,
    model: str = "tencent/hy3:free",
) -> str:
    """High-level helper: send a pipeline generation prompt and return the LLM response."""
    config = LLMConfig(api_key=api_key, model=model)
    return call_llm(
        prompt=prompt,
        system=(
            "You are an expert data engineer. Generate production-quality pipeline code "
            "based on the provided DataHub metadata context. Use CTEs, proper type casting, "
            "column descriptions, and dbt best practices. Output ONLY the code — "
            "no explanations, no markdown fences."
        ),
        config=config,
    )
