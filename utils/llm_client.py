import os
import httpx

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def call_claude(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        r = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
        return r.json()["content"][0]["text"]

async def call_codex(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        payload = {
            "model": "gpt-4-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        r = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        return r.json()["choices"][0]["message"]["content"]
