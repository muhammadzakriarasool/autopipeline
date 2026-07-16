"""LLM client — OpenAI-compatible API for OpenRouter free models."""

import httpx


def call_llm(prompt: str, system: str = "", api_key: str = "", model: str = "openrouter/free",
             base_url: str = "https://openrouter.ai/api/v1", max_tokens: int = 8000) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    with httpx.Client(timeout=120) as client:
        resp = client.post(
            f"{base_url}/chat/completions",
            json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2},
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/muhammadzakriarasool/autopipeline",
                "X-Title": "AutoPipeline",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    if "error" in data:
        raise RuntimeError(f"LLM API error: {data['error']}")
    return data["choices"][0]["message"]["content"]
