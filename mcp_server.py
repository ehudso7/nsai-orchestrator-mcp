import asyncio
from typing import Dict, Callable, Any
from agents.codex_runner import run_codex_agent
from agents.claude_analyst import run_claude_agent

class MCPServer:
    def __init__(self):
        self.agents: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    async def start(self):
        print("MCP Server initialized.")
        self.agents["codex"] = run_codex_agent
        self.agents["claude"] = run_claude_agent

    async def handle_rpc(self, payload: dict) -> dict:
        method = payload.get("method")
        params = payload.get("params", {})
        agent = params.get("agent")
        if agent not in self.agents:
            return {"error": f"Unknown agent: {agent}"}
        return await self.agents[agent](params)
