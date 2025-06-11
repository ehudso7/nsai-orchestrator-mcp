import requests

print("Testing MCP orchestrator...")

base_url = "http://localhost:4141"
status = requests.get(base_url).json()
print("Health:", status)

resp = requests.post(base_url + "/mcp", json={
    "method": "execute",
    "params": {"agent": "codex", "task": "generate API client", "node": "codex-test"}
})
print("Codex Result:", resp.json())

resp = requests.post(base_url + "/mcp", json={
    "method": "analyze",
    "params": {"agent": "claude", "task": "summarize memory", "node": "codex-test"}
})
print("Claude Result:", resp.json())
