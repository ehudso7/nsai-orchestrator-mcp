"""Production-grade structured logging."""

import sys
import logging
import structlog
from typing import Any, Dict
from datetime import datetime
from config import get_settings

settings = get_settings()


def configure_logging():
    """Configure structured logging for production."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.app.log_format == "json" 
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.app.log_level.upper())
    )


class SecurityLogger:
    """Specialized logger for security events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("security")
    
    def authentication_success(self, user_id: str, ip_address: str, **kwargs):
        """Log successful authentication."""
        self.logger.info(
            "Authentication successful",
            user_id=user_id,
            ip_address=ip_address,
            event_type="auth_success",
            **kwargs
        )
    
    def authentication_failure(self, attempt_data: Dict[str, Any], ip_address: str, **kwargs):
        """Log authentication failure."""
        self.logger.warning(
            "Authentication failed",
            ip_address=ip_address,
            event_type="auth_failure",
            attempt_data=attempt_data,
            **kwargs
        )
    
    def rate_limit_exceeded(self, ip_address: str, endpoint: str, **kwargs):
        """Log rate limit exceeded."""
        self.logger.warning(
            "Rate limit exceeded",
            ip_address=ip_address,
            endpoint=endpoint,
            event_type="rate_limit_exceeded",
            **kwargs
        )
    
    def suspicious_activity(self, description: str, ip_address: str, details: Dict[str, Any], **kwargs):
        """Log suspicious activity."""
        self.logger.critical(
            "Suspicious activity detected",
            description=description,
            ip_address=ip_address,
            details=details,
            event_type="suspicious_activity",
            **kwargs
        )
    
    def data_access(self, user_id: str, resource: str, action: str, **kwargs):
        """Log data access for audit trail."""
        self.logger.info(
            "Data access",
            user_id=user_id,
            resource=resource,
            action=action,
            event_type="data_access",
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )


class PerformanceLogger:
    """Logger for performance metrics."""
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
    
    def api_request(self, endpoint: str, method: str, duration_ms: float, status_code: int, **kwargs):
        """Log API request performance."""
        self.logger.info(
            "API request completed",
            endpoint=endpoint,
            method=method,
            duration_ms=duration_ms,
            status_code=status_code,
            **kwargs
        )
    
    def database_query(self, query_type: str, duration_ms: float, **kwargs):
        """Log database query performance."""
        self.logger.info(
            "Database query completed",
            query_type=query_type,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def memory_operation(self, operation: str, duration_ms: float, cache_hit: bool = None, **kwargs):
        """Log memory operation performance."""
        self.logger.info(
            "Memory operation completed",
            operation=operation,
            duration_ms=duration_ms,
            cache_hit=cache_hit,
            **kwargs
        )


class AgentLogger:
    """Logger for agent activities."""
    
    def __init__(self):
        self.logger = structlog.get_logger("agents")
    
    def agent_start(self, agent_type: str, session_id: str, task: str, **kwargs):
        """Log agent task start."""
        self.logger.info(
            "Agent task started",
            agent_type=agent_type,
            session_id=session_id,
            task=task,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def agent_complete(self, agent_type: str, session_id: str, duration_ms: float, success: bool, **kwargs):
        """Log agent task completion."""
        self.logger.info(
            "Agent task completed",
            agent_type=agent_type,
            session_id=session_id,
            duration_ms=duration_ms,
            success=success,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def agent_error(self, agent_type: str, session_id: str, error: str, **kwargs):
        """Log agent errors."""
        self.logger.error(
            "Agent task failed",
            agent_type=agent_type,
            session_id=session_id,
            error=error,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def memory_insert(self, agent_type: str, session_id: str, node_id: str, memory_type: str, **kwargs):
        """Log memory insertions."""
        self.logger.info(
            "Memory inserted",
            agent_type=agent_type,
            session_id=session_id,
            node_id=node_id,
            memory_type=memory_type,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )


# Global logger instances
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()
agent_logger = AgentLogger()


def get_logger(name: str = None):
    """Get structured logger instance."""
    return structlog.get_logger(name) if name else structlog.get_logger()