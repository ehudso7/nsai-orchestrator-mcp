from memory.graph_driver import GraphMemory
from memory.memory_cache import RedisMemory

async def run_codex_agent(params):
    task = params.get("task", "no task")
    node = params.get("node", "codex-node")

    redis = RedisMemory()
    redis.set(node, task)

    graph = GraphMemory()
    graph.insert_context(node, "CodexTask", task)
    graph.close()

    return {"result": f"Codex executed task '{task}' and stored in memory."}
