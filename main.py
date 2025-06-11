from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp_server import MCPServer

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mcp_server = MCPServer()

@app.on_event("startup")
async def on_start():
    await mcp_server.start()

@app.post("/mcp")
async def route_rpc(payload: dict):
    return await mcp_server.handle_rpc(payload)

@app.get("/")
def root():
    return {"status": "MCP orchestrator running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "NSAI Orchestrator MCP"}

@app.post("/api/agents/codex/execute")
async def execute_codex(request: dict):
    """Execute Codex agent for code generation."""
    task = request.get("task", "Generate code")
    # Mock response for now
    result = f"// Codex Agent Response\n// Task: {task}\n\n"
    result += "function generateAPIClient() {\n"
    result += "  // Generated code would appear here\n"
    result += "  console.log('API client initialized');\n"
    result += "}"
    return {
        "result": result,
        "status": "success",
        "agent": "codex"
    }

@app.post("/api/agents/claude/analyze")
async def analyze_claude(request: dict):
    """Execute Claude agent for analysis."""
    task = request.get("task", "Analyze system")
    # Mock response for now
    result = f"Claude Analysis:\n\nTask: {task}\n\n"
    result += "System Status:\n"
    result += "- All services operational\n"
    result += "- Memory usage: Normal\n"
    result += "- Performance: Optimal\n"
    result += "- No issues detected"
    return {
        "result": result,
        "status": "success",
        "agent": "claude"
    }

# Run with:
# uvicorn main:app --reload --port 8000
