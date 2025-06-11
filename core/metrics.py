"""Production-grade metrics and monitoring."""

import time
import psutil
from typing import Dict, Any
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import structlog

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

AGENT_TASKS = Counter(
    'agent_tasks_total',
    'Total agent tasks executed',
    ['agent_type', 'status']
)

AGENT_DURATION = Histogram(
    'agent_task_duration_seconds',
    'Agent task duration in seconds',
    ['agent_type']
)

MEMORY_OPERATIONS = Counter(
    'memory_operations_total',
    'Total memory operations',
    ['operation_type', 'storage_type']
)

MEMORY_CACHE_HITS = Counter(
    'memory_cache_hits_total',
    'Total memory cache hits',
    ['cache_type']
)

MEMORY_CACHE_MISSES = Counter(
    'memory_cache_misses_total',
    'Total memory cache misses',
    ['cache_type']
)

# System metrics
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('memory_usage_percent', 'Memory usage percentage')
DISK_USAGE = Gauge('disk_usage_percent', 'Disk usage percentage')

# Connection pools
REDIS_CONNECTIONS = Gauge('redis_connections_active', 'Active Redis connections')
NEO4J_CONNECTIONS = Gauge('neo4j_connections_active', 'Active Neo4j connections')

# WebSocket metrics
WEBSOCKET_CONNECTIONS = Gauge('websocket_connections_active', 'Active WebSocket connections')
WEBSOCKET_MESSAGES = Counter('websocket_messages_total', 'Total WebSocket messages', ['direction'])


class MetricsCollector:
    """Centralized metrics collection."""
    
    def __init__(self):
        self.start_time = time.time()
        self.system_metrics_enabled = True
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_agent_task(self, agent_type: str, status: str, duration: float = None):
        """Record agent task metrics."""
        AGENT_TASKS.labels(agent_type=agent_type, status=status).inc()
        if duration is not None:
            AGENT_DURATION.labels(agent_type=agent_type).observe(duration)
    
    def record_memory_operation(self, operation_type: str, storage_type: str):
        """Record memory operation metrics."""
        MEMORY_OPERATIONS.labels(operation_type=operation_type, storage_type=storage_type).inc()
    
    def record_cache_hit(self, cache_type: str):
        """Record cache hit."""
        MEMORY_CACHE_HITS.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """Record cache miss."""
        MEMORY_CACHE_MISSES.labels(cache_type=cache_type).inc()
    
    def update_system_metrics(self):
        """Update system resource metrics."""
        if not self.system_metrics_enabled:
            return
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            DISK_USAGE.set(disk.percent)
            
        except Exception as e:
            logger.warning("Failed to collect system metrics", error=str(e))
    
    def update_connection_metrics(self, redis_pool=None, neo4j_driver=None):
        """Update connection pool metrics."""
        try:
            if redis_pool:
                # Redis connection pool metrics
                REDIS_CONNECTIONS.set(len(redis_pool._available_connections))
            
            if neo4j_driver:
                # Neo4j connection metrics would need driver-specific implementation
                pass
                
        except Exception as e:
            logger.warning("Failed to collect connection metrics", error=str(e))
    
    def increment_websocket_connections(self):
        """Increment active WebSocket connections."""
        WEBSOCKET_CONNECTIONS.inc()
    
    def decrement_websocket_connections(self):
        """Decrement active WebSocket connections."""
        WEBSOCKET_CONNECTIONS.dec()
    
    def record_websocket_message(self, direction: str):
        """Record WebSocket message."""
        WEBSOCKET_MESSAGES.labels(direction=direction).inc()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        try:
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": time.time() - self.start_time,
                "system": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent,
                },
                "services": {
                    "redis": "unknown",  # To be updated by Redis health check
                    "neo4j": "unknown",  # To be updated by Neo4j health check
                }
            }
        except Exception as e:
            logger.error("Failed to get health status", error=str(e))
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }


# Global metrics collector
metrics_collector = MetricsCollector()


def get_prometheus_metrics():
    """Get Prometheus metrics in text format."""
    return generate_latest()


class MetricsMiddleware:
    """Middleware to collect request metrics."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start_time
                method = scope["method"]
                path = scope["path"]
                status_code = message["status"]
                
                metrics_collector.record_request(method, path, status_code, duration)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def create_metrics_endpoint():
    """Create metrics endpoint for Prometheus scraping."""
    def metrics_endpoint():
        metrics_collector.update_system_metrics()
        return Response(get_prometheus_metrics(), media_type=CONTENT_TYPE_LATEST)
    
    return metrics_endpoint