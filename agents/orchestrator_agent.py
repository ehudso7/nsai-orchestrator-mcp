from utils.llm_client import call_claude

async def run_orchestrator_agent(params):
    high_level_task = params.get("task", "Analyze system")
    system_prompt = f"Break this task into codex and claude subtasks: {high_level_task}"
    plan = await call_claude(system_prompt)
    return {"plan": plan, "status": "task decomposed"}
