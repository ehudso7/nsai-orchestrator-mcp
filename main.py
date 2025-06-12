from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from mcp_server import MCPServer
from typing import List, Optional
import json
import asyncio
from datetime import datetime, timedelta

app = FastAPI(title="NSAI Orchestrator MCP", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mcp_server = MCPServer()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_personal_message(json.dumps({
            "type": "connection",
            "message": "Connected to NSAI Orchestrator",
            "timestamp": datetime.now().isoformat()
        }), websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.on_event("startup")
async def on_start():
    await mcp_server.start()
    
    # Initialize Redis connection
    from core.redis_config import redis_manager
    await redis_manager.connect()

@app.post("/mcp")
async def route_rpc(payload: dict):
    return await mcp_server.handle_rpc(payload)

@app.get("/")
def root():
    return {"status": "MCP orchestrator running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "NSAI Orchestrator MCP"}

# Authentication endpoints
from core.auth import (
    Token, authenticate_user, create_access_token, 
    get_current_active_user, fake_users_db, User,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/api/agents/codex/execute")
async def execute_codex(request: dict):
    """Execute Codex agent for code generation."""
    from agents.codex_runner import run_codex_agent
    
    result = await run_codex_agent(request)
    
    # Broadcast to WebSocket clients
    await manager.broadcast(json.dumps({
        "type": "agent_response",
        "agent": "codex",
        "timestamp": datetime.now().isoformat(),
        "data": result
    }))
    
    return result

@app.post("/api/agents/claude/analyze")
async def analyze_claude(request: dict):
    """Execute Claude agent for analysis."""
    from agents.claude_analyst import run_claude_agent
    
    result = await run_claude_agent(request)
    
    # Broadcast to WebSocket clients
    await manager.broadcast(json.dumps({
        "type": "agent_response",
        "agent": "claude",
        "timestamp": datetime.now().isoformat(),
        "data": result
    }))
    
    return result

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or process commands
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Registration endpoint
@app.post("/api/auth/register")
async def register(username: str = Body(...), email: str = Body(...), password: str = Body(...)):
    """Register a new user."""
    from core.auth import fake_users_db, get_password_hash
    
    # Check if user already exists
    if username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    for user_data in fake_users_db.values():
        if user_data.get("email") == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    hashed_password = get_password_hash(password)
    fake_users_db[username] = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "disabled": False,
        "created_at": datetime.now().isoformat()
    }
    
    # Store in Redis if available
    from core.redis_config import redis_manager
    if redis_manager.redis_client:
        await redis_manager.redis_client.hset(
            "users",
            username,
            json.dumps(fake_users_db[username])
        )
    
    return {
        "username": username,
        "email": email,
        "message": "User registered successfully"
    }

# Additional agent endpoints
@app.post("/api/agents/orchestrator/execute")
async def execute_orchestrator(request: dict):
    """Execute orchestrator for multi-agent coordination."""
    from agents.orchestrator_agent import run_orchestrator_agent
    
    result = await run_orchestrator_agent(request)
    
    await manager.broadcast(json.dumps({
        "type": "orchestration",
        "timestamp": datetime.now().isoformat(),
        "data": result
    }))
    
    return result

@app.post("/api/agents/memory/query")
async def query_memory(request: dict):
    """Query memory graph."""
    from agents.memory_graph import run_memory_agent
    
    result = await run_memory_agent(request)
    
    return result

@app.post("/api/agents/webscraper/scrape")
async def scrape_web(request: dict):
    """Execute web scraper agent."""
    from agents.web_scraper import run_web_scraper_agent
    
    result = await run_web_scraper_agent(request)
    
    await manager.broadcast(json.dumps({
        "type": "agent_response",
        "agent": "webscraper",
        "timestamp": datetime.now().isoformat(),
        "data": result
    }))
    
    return result

@app.post("/api/agents/dataanalyzer/analyze")
async def analyze_data(request: dict):
    """Execute data analyzer agent."""
    from agents.data_analyzer import run_data_analyzer_agent
    
    result = await run_data_analyzer_agent(request)
    
    await manager.broadcast(json.dumps({
        "type": "agent_response",
        "agent": "dataanalyzer",
        "timestamp": datetime.now().isoformat(),
        "data": result
    }))
    
    return result

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics."""
    from core.redis_config import redis_manager, get_metric
    
    # Get metrics from Redis
    agent_calls = await get_metric("agent_calls", days=7)
    workflow_executions = await get_metric("workflow_executions", days=7)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "connections": len(manager.active_connections),
        "cache_keys": len(await redis_manager.redis_client.keys() if redis_manager.redis_client else []),
        "agents": {
            "claude": "active",
            "codex": "active",
            "orchestrator": "active",
            "memory": "active"
        },
        "metrics": {
            "agent_calls": agent_calls,
            "workflow_executions": workflow_executions
        }
    }

# Workflow management endpoints
@app.post("/api/workflows/save")
async def save_workflow_endpoint(workflow: dict):
    """Save workflow to Redis."""
    from core.redis_config import save_workflow, increment_metric
    
    workflow_id = workflow.get("id") or f"workflow_{datetime.now().timestamp()}"
    await save_workflow(workflow_id, workflow)
    await increment_metric("workflow_saves")
    
    return {"id": workflow_id, "status": "saved"}

@app.get("/api/workflows/{workflow_id}")
async def load_workflow_endpoint(workflow_id: str):
    """Load workflow from Redis."""
    from core.redis_config import load_workflow
    
    workflow = await load_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    return workflow

@app.get("/api/workflows")
async def list_workflows_endpoint():
    """List all workflows."""
    from core.redis_config import list_workflows
    
    workflows = await list_workflows()
    return {"workflows": workflows}

@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow_endpoint(workflow_id: str, context: dict = {}):
    """Execute a saved workflow."""
    from core.redis_config import load_workflow, increment_metric
    
    workflow = await load_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Track execution
    await increment_metric("workflow_executions")
    
    # Broadcast execution start
    await manager.broadcast(json.dumps({
        "type": "workflow_execution",
        "workflow_id": workflow_id,
        "status": "started",
        "timestamp": datetime.now().isoformat()
    }))
    
    # Execute workflow nodes
    results = []
    for node in workflow.get("nodes", []):
        if node["type"] == "agent":
            agent = node["data"].get("agent", "claude")
            task = node["data"].get("task", "")
            
            # Check cache first
            from core.redis_config import get_cached_agent_result, cache_agent_result
            cached = await get_cached_agent_result(agent, task)
            
            if cached:
                result = cached
            else:
                # Execute agent
                if agent == "claude":
                    from agents.claude_analyst import run_claude_agent
                    result = await run_claude_agent({"task": task, "context": context})
                elif agent == "codex":
                    from agents.codex_runner import run_codex_agent
                    result = await run_codex_agent({"task": task, "context": context})
                else:
                    result = {"status": "error", "message": "Unknown agent"}
                
                # Cache result
                await cache_agent_result(agent, task, result)
            
            results.append({
                "node_id": node["id"],
                "result": result
            })
            
            # Broadcast progress
            await manager.broadcast(json.dumps({
                "type": "workflow_progress",
                "workflow_id": workflow_id,
                "node_id": node["id"],
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }))
    
    # Broadcast completion
    await manager.broadcast(json.dumps({
        "type": "workflow_execution",
        "workflow_id": workflow_id,
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }))
    
    return {
        "workflow_id": workflow_id,
        "status": "completed",
        "results": results
    }

# Workflow Templates and Marketplace endpoints
@app.get("/api/marketplace/templates")
async def list_marketplace_templates(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "popular",
    price_filter: str = "all",
    limit: int = 50,
    offset: int = 0
):
    """List workflow templates in the marketplace."""
    # For demo, return mock data
    templates = [
        {
            "id": "1",
            "uuid": "template-1",
            "name": "Advanced Data Pipeline",
            "description": "Complete ETL pipeline with data validation",
            "category": "Data Analysis",
            "icon": "database",
            "author": {"id": 1, "username": "datamaster"},
            "price_usd": 0,
            "downloads_count": 1523,
            "rating": 4.8,
            "tags": ["ETL", "Data Processing"],
            "created_at": datetime.now().isoformat()
        }
    ]
    
    return {"total": len(templates), "templates": templates}

@app.post("/api/marketplace/templates/{template_id}/install")
async def install_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Install a workflow template."""
    return {
        "status": "success",
        "workflow_id": "new-workflow-123",
        "message": "Template installed successfully"
    }

# Run with:
# uvicorn main:app --reload --port 8000
