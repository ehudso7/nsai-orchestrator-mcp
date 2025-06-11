import os
import requests
import redis
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()

REDIS_HOST = "localhost"
NEO4J_URI = "bolt://localhost:7687"
BACKEND_URL = "http://localhost:4141"
CLAUDE_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def check_env():
    print("🔍 Environment Variables:")
    assert CLAUDE_KEY, "❌ Missing ANTHROPIC_API_KEY"
    assert OPENAI_KEY, "❌ Missing OPENAI_API_KEY"
    print("✅ Claude + OpenAI keys found")

def check_backend():
    print("🔍 Backend FastAPI Route:")
    r = requests.get(f"{BACKEND_URL}/")
    assert r.status_code == 200 and "status" in r.json(), "❌ MCP root route failed"
    print("✅ Backend MCP endpoint is live")

def check_mcp_rpc():
    print("🔍 MCP Codex Agent RPC:")
    try:
        r = requests.post(f"{BACKEND_URL}/mcp", json={
            "method": "execute",
            "params": { "agent": "codex", "task": "integrity test", "node": "test-node" }
        })
        print("📥 Codex response:", r.status_code)
        print("📦 Payload:\n", r.text)
        r.raise_for_status()
        result = r.json()
        assert "result" in result, f"❌ Codex agent returned no result: {result}"
        print("✅ Codex agent RPC passed")
    except Exception as e:
        raise RuntimeError(f"❌ Codex agent failed: {e}")

def check_redis():
    print("🔍 Redis:")
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    r.set("healthcheck", "alive")
    assert r.get("healthcheck") == "alive", "❌ Redis not storing values"
    print("✅ Redis operational")

def check_neo4j():
    print("🔍 Neo4j:")
    driver = GraphDatabase.driver(NEO4J_URI, auth=("neo4j", "password"))
    with driver.session() as session:
        session.run("MERGE (n:HealthCheck {id: 'ping'}) SET n.status = 'ok'")
    print("✅ Neo4j write successful")

def main():
    try:
        check_env()
        check_backend()
        check_redis()
        check_neo4j()
        check_mcp_rpc()
        print("\n🎉 MCP Orchestrator is fully functional.")
    except Exception as e:
        print(f"\n❌ System check failed: {e}")

if __name__ == "__main__":
    main()
