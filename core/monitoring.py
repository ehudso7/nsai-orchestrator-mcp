import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from contextlib import contextmanager, asynccontextmanager
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
import logging
import json
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

# Prometheus metrics
registry = CollectorRegistry()

# Counters
agent_requests_total = Counter(
    'agent_requests_total',
    'Total number of agent requests',
    ['agent_type', 'status'],
    registry=registry
)

api_calls_total = Counter(
    'api_calls_total',
    'Total number of API calls',
    ['endpoint', 'method', 'status_code'],
    registry=registry
)

errors_total = Counter(
    'errors_total',
    'Total number of errors',
    ['error_type', 'severity'],
    registry=registry
)

# Histograms
agent_duration_seconds = Histogram(
    'agent_duration_seconds',
    'Agent execution duration in seconds',
    ['agent_type'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
    registry=registry
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['endpoint', 'method'],
    registry=registry
)

# Gauges
active_workflows = Gauge(
    'active_workflows',
    'Number of currently active workflows',
    registry=registry
)

memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    'Current memory usage in bytes',
    registry=registry
)

cpu_usage_percent = Gauge(
    'cpu_usage_percent',
    'Current CPU usage percentage',
    registry=registry
)

redis_connections = Gauge(
    'redis_connections_active',
    'Number of active Redis connections',
    registry=registry
)

# Summary
agent_tokens_used = Summary(
    'agent_tokens_used',
    'Number of tokens used by agents',
    ['agent_type'],
    registry=registry
)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    memory_start_mb: Optional[float] = None
    memory_end_mb: Optional[float] = None
    memory_peak_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def finalize(self):
        """Calculate final metrics"""
        if self.end_time is None:
            self.end_time = time.time()
        
        self.duration_ms = (self.end_time - self.start_time) * 1000
        
        if self.memory_end_mb and self.memory_start_mb:
            self.memory_delta_mb = self.memory_end_mb - self.memory_start_mb

class PerformanceMonitor:
    """Monitors and tracks performance metrics"""
    
    def __init__(self):
        self.metrics_buffer: List[PerformanceMetrics] = []
        self.agent_metrics: Dict[str, List[float]] = defaultdict(list)
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._monitor_system_resources())
    
    async def _monitor_system_resources(self):
        """Monitor system resources in the background"""
        while True:
            try:
                # Update system metrics
                memory_usage_bytes.set(psutil.virtual_memory().used)
                cpu_usage_percent.set(psutil.cpu_percent(interval=1))
                
                # Update Redis connections if available
                try:
                    from core.redis_config import redis_manager
                    if redis_manager.redis_client:
                        info = await redis_manager.redis_client.info()
                        redis_connections.set(info.get('connected_clients', 0))
                except:
                    pass
                
                await asyncio.sleep(10)  # Update every 10 seconds
            except Exception as e:
                logger.error(f"Error monitoring system resources: {e}")
                await asyncio.sleep(60)  # Back off on error
    
    @contextmanager
    def measure_performance(self, operation_name: str, **metadata):
        """Context manager to measure performance of a code block"""
        
        metrics = PerformanceMetrics(
            start_time=time.time(),
            memory_start_mb=psutil.Process().memory_info().rss / 1024 / 1024,
            metadata={**metadata, "operation": operation_name}
        )
        
        try:
            yield metrics
            
        except Exception as e:
            metrics.error = str(e)
            raise
            
        finally:
            # Finalize metrics
            process = psutil.Process()
            metrics.memory_end_mb = process.memory_info().rss / 1024 / 1024
            metrics.cpu_percent = process.cpu_percent()
            metrics.finalize()
            
            # Store metrics
            self.metrics_buffer.append(metrics)
            if len(self.metrics_buffer) > 1000:
                self.metrics_buffer = self.metrics_buffer[-500:]  # Keep last 500
            
            # Log if slow
            if metrics.duration_ms > 5000:
                logger.warning(
                    f"Slow operation '{operation_name}' took {metrics.duration_ms:.0f}ms"
                )
    
    @asynccontextmanager
    async def measure_agent_performance(self, agent_type: str, **metadata):
        """Async context manager for measuring agent performance"""
        
        start_time = time.time()
        
        try:
            # Record request
            agent_requests_total.labels(agent_type=agent_type, status="started").inc()
            
            metrics = PerformanceMetrics(
                start_time=start_time,
                memory_start_mb=psutil.Process().memory_info().rss / 1024 / 1024,
                metadata={**metadata, "agent_type": agent_type}
            )
            
            yield metrics
            
            # Success metrics
            agent_requests_total.labels(agent_type=agent_type, status="success").inc()
            
        except Exception as e:
            # Error metrics
            agent_requests_total.labels(agent_type=agent_type, status="error").inc()
            errors_total.labels(error_type=type(e).__name__, severity="high").inc()
            raise
            
        finally:
            # Record duration
            duration = time.time() - start_time
            agent_duration_seconds.labels(agent_type=agent_type).observe(duration)
            
            # Record tokens if available
            if hasattr(metrics, 'tokens_used') and metrics.tokens_used:
                agent_tokens_used.labels(agent_type=agent_type).observe(metrics.tokens_used)
            
            # Store in buffer
            metrics.finalize()
            self.agent_metrics[agent_type].append(metrics.duration_ms)
            
            # Keep only recent metrics
            if len(self.agent_metrics[agent_type]) > 100:
                self.agent_metrics[agent_type] = self.agent_metrics[agent_type][-50:]
    
    def get_agent_statistics(self, agent_type: str) -> Dict[str, Any]:
        """Get performance statistics for a specific agent"""
        
        if agent_type not in self.agent_metrics or not self.agent_metrics[agent_type]:
            return {
                "agent_type": agent_type,
                "sample_count": 0,
                "message": "No data available"
            }
        
        durations = self.agent_metrics[agent_type]
        
        return {
            "agent_type": agent_type,
            "sample_count": len(durations),
            "avg_duration_ms": np.mean(durations),
            "median_duration_ms": np.median(durations),
            "p95_duration_ms": np.percentile(durations, 95),
            "p99_duration_ms": np.percentile(durations, 99),
            "min_duration_ms": np.min(durations),
            "max_duration_ms": np.max(durations),
            "std_deviation": np.std(durations)
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        
        process = psutil.Process()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            "process": {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "thread_count": process.num_threads(),
                "open_files": len(process.open_files()) if hasattr(process, 'open_files') else None
            },
            "agents": {
                agent_type: self.get_agent_statistics(agent_type)
                for agent_type in self.agent_metrics.keys()
            }
        }
    
    def export_prometheus_metrics(self) -> bytes:
        """Export metrics in Prometheus format"""
        
        return generate_latest(registry)
    
    async def analyze_performance_trends(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Get metrics from database
        from core.database import SessionLocal
        from core.models import AgentExecution
        
        with SessionLocal() as db:
            recent_executions = db.query(AgentExecution).filter(
                AgentExecution.started_at >= cutoff_time
            ).all()
        
        if not recent_executions:
            return {"message": "No recent executions found"}
        
        # Analyze by agent type
        agent_analysis = defaultdict(lambda: {
            "total_executions": 0,
            "successful": 0,
            "failed": 0,
            "avg_duration_ms": 0,
            "total_tokens": 0,
            "total_cost": 0,
            "durations": []
        })
        
        for execution in recent_executions:
            agent_type = execution.agent_type
            analysis = agent_analysis[agent_type]
            
            analysis["total_executions"] += 1
            
            if execution.status.value == "completed":
                analysis["successful"] += 1
            else:
                analysis["failed"] += 1
            
            if execution.duration_ms:
                analysis["durations"].append(execution.duration_ms)
            
            if execution.tokens_used:
                analysis["total_tokens"] += execution.tokens_used
            
            if execution.cost_usd:
                analysis["total_cost"] += execution.cost_usd
        
        # Calculate averages
        for agent_type, analysis in agent_analysis.items():
            if analysis["durations"]:
                analysis["avg_duration_ms"] = np.mean(analysis["durations"])
                analysis["p95_duration_ms"] = np.percentile(analysis["durations"], 95)
            
            analysis["success_rate"] = (
                analysis["successful"] / analysis["total_executions"] * 100
                if analysis["total_executions"] > 0 else 0
            )
            
            # Remove raw durations from output
            del analysis["durations"]
        
        return {
            "time_window_hours": time_window_hours,
            "analysis_time": datetime.utcnow().isoformat(),
            "total_executions": sum(a["total_executions"] for a in agent_analysis.values()),
            "by_agent": dict(agent_analysis),
            "recommendations": self._generate_recommendations(agent_analysis)
        }
    
    def _generate_recommendations(self, agent_analysis: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on analysis"""
        
        recommendations = []
        
        for agent_type, metrics in agent_analysis.items():
            # Check success rate
            if metrics["success_rate"] < 90:
                recommendations.append(
                    f"Low success rate for {agent_type} ({metrics['success_rate']:.1f}%). "
                    "Consider reviewing error logs and retry logic."
                )
            
            # Check performance
            if metrics.get("avg_duration_ms", 0) > 30000:  # 30 seconds
                recommendations.append(
                    f"{agent_type} has high average execution time "
                    f"({metrics['avg_duration_ms']:.0f}ms). Consider optimization."
                )
            
            # Check cost
            if metrics.get("total_cost", 0) > 100:
                recommendations.append(
                    f"High cost for {agent_type} (${metrics['total_cost']:.2f}). "
                    "Review token usage and consider caching."
                )
        
        if not recommendations:
            recommendations.append("All agents performing within normal parameters.")
        
        return recommendations

# Global monitor instance
performance_monitor = PerformanceMonitor()

# Middleware for automatic API monitoring
async def monitor_api_performance(request, call_next):
    """FastAPI middleware for monitoring API performance"""
    
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    
    api_request_duration.labels(
        endpoint=request.url.path,
        method=request.method
    ).observe(duration)
    
    api_calls_total.labels(
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code
    ).inc()
    
    # Add performance headers
    response.headers["X-Response-Time"] = f"{duration:.3f}"
    
    return response