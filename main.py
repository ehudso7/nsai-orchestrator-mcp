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

# Run with:
# uvicorn main:app --reload --port 4141
