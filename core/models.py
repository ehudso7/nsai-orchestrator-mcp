from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Float, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum
from datetime import datetime
import uuid

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class WorkflowStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

class ExecutionStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Profile fields
    full_name = Column(String(100))
    company = Column(String(100))
    avatar_url = Column(String(500))
    preferences = Column(JSON, default={})
    
    # Usage tracking
    api_calls_count = Column(Integer, default=0)
    workflows_count = Column(Integer, default=0)
    storage_used_mb = Column(Float, default=0.0)
    
    # Relationships
    workflows = relationship("Workflow", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="user")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_role', 'role'),
    )

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT, nullable=False)
    
    # Workflow definition
    nodes = Column(JSON, nullable=False)  # Array of node objects
    edges = Column(JSON, nullable=False)  # Array of edge objects
    config = Column(JSON, default={})     # Additional configuration
    
    # Versioning
    version = Column(Integer, default=1)
    parent_workflow_id = Column(Integer, ForeignKey("workflows.id"))
    is_template = Column(Boolean, default=False)
    
    # Metadata
    tags = Column(JSON, default=[])
    category = Column(String(50))
    is_public = Column(Boolean, default=False)
    stars_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_executed_at = Column(DateTime(timezone=True))
    
    # Performance metrics
    avg_execution_time_ms = Column(Float)
    success_rate = Column(Float)
    total_executions = Column(Integer, default=0)
    
    # Relationships
    owner = relationship("User", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    versions = relationship("Workflow", backref="parent")
    
    # Indexes
    __table_args__ = (
        Index('idx_workflow_owner_status', 'owner_id', 'status'),
        Index('idx_workflow_template', 'is_template', 'is_public'),
        Index('idx_workflow_category', 'category'),
    )

class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Execution details
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    input_data = Column(JSON, default={})
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)
    
    # Resource usage
    total_tokens_used = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    
    # Debugging
    execution_log = Column(JSON, default=[])
    debug_info = Column(JSON)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    user = relationship("User", back_populates="executions")
    agent_executions = relationship("AgentExecution", back_populates="workflow_execution", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_execution_workflow_status', 'workflow_id', 'status'),
        Index('idx_execution_user_time', 'user_id', 'started_at'),
    )

class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False)
    
    # Agent details
    agent_type = Column(String(50), nullable=False)  # claude, codex, etc.
    node_id = Column(String(100), nullable=False)    # Node ID in workflow
    
    # Execution details
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)
    
    # Resource usage
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    
    # Retry information
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Relationships
    workflow_execution = relationship("WorkflowExecution", back_populates="agent_executions")
    
    # Indexes
    __table_args__ = (
        Index('idx_agent_execution_workflow', 'workflow_execution_id'),
        Index('idx_agent_execution_type_status', 'agent_type', 'status'),
    )

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Key details
    key_hash = Column(String(64), unique=True, nullable=False)  # SHA-256 hash
    key_prefix = Column(String(8), nullable=False)  # First 8 chars for identification
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Permissions
    scopes = Column(JSON, default=["read", "write"])  # API scopes
    rate_limit = Column(Integer, default=1000)  # Requests per hour
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Indexes
    __table_args__ = (
        Index('idx_api_key_prefix', 'key_prefix'),
        Index('idx_api_key_user_active', 'user_id', 'is_active'),
    )

class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    
    # Template info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    icon = Column(String(50))
    
    # Template definition
    nodes = Column(JSON, nullable=False)
    edges = Column(JSON, nullable=False)
    default_config = Column(JSON, default={})
    
    # Marketplace
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price_usd = Column(Float, default=0.0)  # 0 = free
    downloads_count = Column(Integer, default=0)
    rating = Column(Float)
    
    # Metadata
    tags = Column(JSON, default=[])
    preview_image_url = Column(String(500))
    documentation_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_template_category', 'category'),
        Index('idx_template_author', 'author_id'),
        Index('idx_template_price', 'price_usd'),
    )