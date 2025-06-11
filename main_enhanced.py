"""Production-grade FastAPI application with comprehensive features."""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import structlog

# Local imports
from config import get_settings
from core.logging import configure_logging, security_logger, performance_logger, agent_logger
from core.security import (
    SecurityManager, InputSanitizer, rate_limit_by_ip, rate_limit_by_user,
    require_api_key, log_security_event
)
from core.metrics import metrics_collector, MetricsMiddleware, create_metrics_endpoint
from mcp_server_enhanced import MCPServerEnhanced
from schemas import TaskRequest, TaskResponse, HealthResponse

# Configure logging
configure_logging()
logger = structlog.get_logger()

# Get settings
settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global MCP server instance
mcp_server = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global mcp_server
    
    logger.info("Starting NSAI Orchestrator MCP", version=settings.app.app_version)
    
    # Initialize MCP server
    mcp_server = MCPServerEnhanced()
    await mcp_server.start()
    
    # Start background tasks
    asyncio.create_task(periodic_health_check())
    asyncio.create_task(periodic_metrics_collection())
    
    logger.info("Application startup complete")
    
    yield
    
    # Cleanup
    logger.info("Shutting down application")
    if mcp_server:
        await mcp_server.stop()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app.app_name,
    description=settings.app.app_description,
    version=settings.app.app_version,
    debug=settings.app.debug,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(MetricsMiddleware)
app.add_middleware(SlowAPIMiddleware)

if settings.app.enable_gzip:
    app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted hosts in production
if settings.app.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )

# Rate limiting error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        metrics_collector.increment_websocket_connections()
        logger.info("WebSocket connected", client_id=client_id)
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            metrics_collector.decrement_websocket_connections()
            logger.info("WebSocket disconnected", client_id=client_id)
    
    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
            metrics_collector.record_websocket_message("outbound")
    
    async def broadcast(self, message: dict):
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
                metrics_collector.record_websocket_message("outbound")
            except Exception as e:
                logger.warning("Failed to send WebSocket message", client_id=client_id, error=str(e))


manager = ConnectionManager()


# Background tasks
async def periodic_health_check():
    """Periodic health check and system monitoring."""
    while True:
        try:
            health_status = metrics_collector.get_health_status()
            
            # Log health metrics
            logger.info("Health check", **health_status)
            
            # Alert on critical metrics
            if health_status.get("system", {}).get("cpu_percent", 0) > 90:
                logger.critical("High CPU usage detected", cpu_percent=health_status["system"]["cpu_percent"])
            
            if health_status.get("system", {}).get("memory_percent", 0) > 90:
                logger.critical("High memory usage detected", memory_percent=health_status["system"]["memory_percent"])
            
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            await asyncio.sleep(60)


async def periodic_metrics_collection():
    """Periodic metrics collection."""
    while True:
        try:
            metrics_collector.update_system_metrics()
            await asyncio.sleep(15)  # Collect every 15 seconds
        except Exception as e:
            logger.error("Metrics collection failed", error=str(e))
            await asyncio.sleep(30)


# Routes
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint."""
    return {
        "status": "running",
        "service": settings.app.app_name,
        "version": settings.app.app_version,
        "environment": settings.app.environment,
        "timestamp": time.time()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    health_status = metrics_collector.get_health_status()
    
    # Determine overall health
    is_healthy = (
        health_status.get("system", {}).get("cpu_percent", 0) < 95 and
        health_status.get("system", {}).get("memory_percent", 0) < 95 and
        health_status.get("system", {}).get("disk_percent", 0) < 95
    )
    
    status_code = 200 if is_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return create_metrics_endpoint()()


@app.post("/mcp", response_model=TaskResponse)
@rate_limit_by_ip(f"{settings.security.rate_limit_per_minute}/minute")
async def handle_mcp_request(
    request: TaskRequest,
    http_request: Request,
    api_key: str = Depends(require_api_key)
):
    """Handle MCP requests with security and monitoring."""
    start_time = time.time()
    
    try:
        # Log security event
        await log_security_event(
            "mcp_request",
            {"agent": request.params.get("agent"), "method": request.method},
            http_request
        )
        
        # Sanitize input
        sanitized_params = InputSanitizer.sanitize_dict(request.params)
        
        # Process request
        result = await mcp_server.handle_rpc({
            "method": request.method,
            "params": sanitized_params
        })
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log performance
        performance_logger.api_request(
            endpoint="/mcp",
            method="POST",
            duration_ms=duration_ms,
            status_code=200
        )
        
        # Record agent metrics
        agent_type = sanitized_params.get("agent", "unknown")
        metrics_collector.record_agent_task(agent_type, "success", duration_ms / 1000)
        
        return TaskResponse(
            success=True,
            result=result,
            duration_ms=duration_ms
        )
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        # Log error
        logger.error("MCP request failed", error=str(e), duration_ms=duration_ms)
        
        # Record failure metrics
        agent_type = request.params.get("agent", "unknown")
        metrics_collector.record_agent_task(agent_type, "error", duration_ms / 1000)
        
        # Security logging for potential attacks
        await log_security_event(
            "mcp_request_error",
            {"error": str(e), "params": request.params},
            http_request,
            severity="warning"
        )
        
        return TaskResponse(
            success=False,
            error=str(e),
            duration_ms=duration_ms
        )


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            metrics_collector.record_websocket_message("inbound")
            
            # Process WebSocket message
            if data.get("type") == "subscribe":
                # Subscribe to specific data streams
                subscription_type = data.get("subscription")
                logger.info("WebSocket subscription", client_id=client_id, type=subscription_type)
                
                # Send confirmation
                await manager.send_message({
                    "type": "subscription_confirmed",
                    "subscription": subscription_type
                }, client_id)
            
            elif data.get("type") == "ping":
                # Respond to ping
                await manager.send_message({"type": "pong"}, client_id)
            
            else:
                # Echo back for now
                await manager.send_message({
                    "type": "echo",
                    "data": data
                }, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error("WebSocket error", client_id=client_id, error=str(e))
        manager.disconnect(client_id)


@app.get("/memory/graph")
@rate_limit_by_ip("30/minute")
async def get_memory_graph(api_key: str = Depends(require_api_key)):
    """Get memory graph visualization data."""
    try:
        graph_data = await mcp_server.get_memory_graph()
        return {"success": True, "data": graph_data}
    except Exception as e:
        logger.error("Failed to get memory graph", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve memory graph")


@app.post("/memory/query")
@rate_limit_by_ip("60/minute")
async def query_memory(
    query: Dict[str, Any],
    api_key: str = Depends(require_api_key)
):
    """Query memory system."""
    try:
        sanitized_query = InputSanitizer.sanitize_dict(query)
        result = await mcp_server.query_memory(sanitized_query)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error("Memory query failed", error=str(e))
        raise HTTPException(status_code=500, detail="Memory query failed")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    await log_security_event(
        "http_exception",
        {"status_code": exc.status_code, "detail": exc.detail},
        request,
        severity="warning" if exc.status_code >= 400 else "info"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error("Unhandled exception", error=str(exc), endpoint=str(request.url))
    
    await log_security_event(
        "unhandled_exception",
        {"error": str(exc)},
        request,
        severity="critical"
    )
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_enhanced:app",
        host=settings.app.host,
        port=settings.app.port,
        workers=settings.app.workers,
        access_log=False,  # We handle logging ourselves
        server_header=False,  # Don't expose server version
        date_header=False     # Don't expose date header
    )