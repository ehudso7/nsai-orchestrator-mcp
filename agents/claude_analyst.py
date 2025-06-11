from memory.graph_driver import GraphMemory
from memory.memory_cache import RedisMemory

async def run_claude_agent(params):
    task = params.get("task", "no task")
    node = params.get("node", "claude-node")

    redis = RedisMemory()
    cache = redis.get(node) or "No cache found"

    graph = GraphMemory()
    graph.insert_context(node, "ClaudeNote", f"Reviewed: {cache} | {task}")
    graph.close()

    return {"result": f"Claude analyzed '{task}' with memory: {cache}"}
