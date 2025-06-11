"""Pydantic schemas for request/response validation."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class TaskRequest(BaseModel):
    """Request schema for MCP tasks."""
    
    method: str = Field(..., description="The method to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the method")
    
    @validator("method")
    def validate_method(cls, v):
        allowed_methods = ["execute", "analyze", "orchestrate", "query"]
        if v not in allowed_methods:
            raise ValueError(f"Method must be one of: {allowed_methods}")
        return v
    
    @validator("params")
    def validate_params(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Params must be a dictionary")
        
        # Check for required agent parameter
        if "agent" not in v:
            raise ValueError("Agent parameter is required")
        
        return v


class TaskResponse(BaseModel):
    """Response schema for MCP tasks."""
    
    success: bool = Field(..., description="Whether the task was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration_ms: float = Field(..., description="Task duration in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Check timestamp")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    system: Dict[str, float] = Field(..., description="System metrics")
    services: Dict[str, str] = Field(..., description="Service statuses")


class AgentInfo(BaseModel):
    """Agent information schema."""
    
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type")
    status: str = Field(..., description="Agent status")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")


class MemoryNode(BaseModel):
    """Memory node schema."""
    
    id: str = Field(..., description="Node ID")
    label: str = Field(..., description="Node label/type")
    content: str = Field(..., description="Node content")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    ttl: Optional[int] = Field(None, description="Time to live in seconds")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    tags: List[str] = Field(default_factory=list, description="Node tags")


class MemoryEdge(BaseModel):
    """Memory edge schema."""
    
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: str = Field(..., description="Relationship type")
    weight: float = Field(default=1.0, description="Edge weight")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")


class MemoryGraph(BaseModel):
    """Memory graph schema."""
    
    nodes: List[MemoryNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[MemoryEdge] = Field(default_factory=list, description="Graph edges")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Graph metadata")


class MemoryQuery(BaseModel):
    """Memory query schema."""
    
    query_type: str = Field(..., description="Type of query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Query filters")
    limit: int = Field(default=100, description="Result limit")
    offset: int = Field(default=0, description="Result offset")
    
    @validator("query_type")
    def validate_query_type(cls, v):
        allowed_types = ["search", "neighbors", "path", "subgraph"]
        if v not in allowed_types:
            raise ValueError(f"Query type must be one of: {allowed_types}")
        return v


class UserSession(BaseModel):
    """User session schema."""
    
    session_id: str = Field(..., description="Session ID")
    user_id: Optional[str] = Field(None, description="User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    last_active: datetime = Field(default_factory=datetime.utcnow, description="Last activity time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")


class APIKey(BaseModel):
    """API key schema."""
    
    key_id: str = Field(..., description="Key ID")
    name: str = Field(..., description="Key name")
    prefix: str = Field(..., description="Key prefix")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    last_used: Optional[datetime] = Field(None, description="Last used timestamp")
    permissions: List[str] = Field(default_factory=list, description="Key permissions")
    rate_limit: Optional[int] = Field(None, description="Custom rate limit")


class SecurityEvent(BaseModel):
    """Security event schema."""
    
    event_type: str = Field(..., description="Event type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    client_ip: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    endpoint: str = Field(..., description="Endpoint accessed")
    method: str = Field(..., description="HTTP method")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event details")
    severity: str = Field(default="info", description="Event severity")
    
    @validator("severity")
    def validate_severity(cls, v):
        allowed_severities = ["info", "warning", "critical"]
        if v not in allowed_severities:
            raise ValueError(f"Severity must be one of: {allowed_severities}")
        return v


class AgentMetrics(BaseModel):
    """Agent metrics schema."""
    
    agent_type: str = Field(..., description="Agent type")
    total_tasks: int = Field(default=0, description="Total tasks executed")
    successful_tasks: int = Field(default=0, description="Successful tasks")
    failed_tasks: int = Field(default=0, description="Failed tasks")
    average_duration_ms: float = Field(default=0.0, description="Average task duration")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


class SystemMetrics(BaseModel):
    """System metrics schema."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    disk_percent: float = Field(..., description="Disk usage percentage")
    active_connections: int = Field(default=0, description="Active connections")
    request_rate: float = Field(default=0.0, description="Requests per second")


class WebSocketMessage(BaseModel):
    """WebSocket message schema."""
    
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    client_id: Optional[str] = Field(None, description="Client ID")


class PluginManifest(BaseModel):
    """Plugin manifest schema."""
    
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    agent_type: str = Field(..., description="Agent type this plugin implements")
    capabilities: List[str] = Field(default_factory=list, description="Plugin capabilities")
    dependencies: List[str] = Field(default_factory=list, description="Plugin dependencies")
    entry_point: str = Field(..., description="Plugin entry point")
    config_schema: Dict[str, Any] = Field(default_factory=dict, description="Configuration schema")


class ConfigValidation(BaseModel):
    """Configuration validation schema."""
    
    valid: bool = Field(..., description="Whether configuration is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    config: Dict[str, Any] = Field(default_factory=dict, description="Validated configuration")