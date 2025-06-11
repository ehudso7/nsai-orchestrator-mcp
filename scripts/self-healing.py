#!/usr/bin/env python3
"""
Self-Healing System for NSAI Orchestrator
Automatically detects and resolves common issues
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
import redis.asyncio as redis
from kubernetes import client, config
from prometheus_client.parser import text_string_to_metric_families
import psutil
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SelfHealingSystem:
    """Automated self-healing for production systems"""
    
    def __init__(self):
        self.redis_client = None
        self.k8s_v1 = None
        self.k8s_apps_v1 = None
        self.prometheus_url = os.getenv('PROMETHEUS_URL', 'http://prometheus:9090')
        self.namespace = os.getenv('NAMESPACE', 'production')
        self.healing_actions = {
            'high_memory': self._heal_high_memory,
            'high_cpu': self._heal_high_cpu,
            'pod_crash': self._heal_pod_crash,
            'slow_response': self._heal_slow_response,
            'connection_pool_exhausted': self._heal_connection_pool,
            'disk_full': self._heal_disk_full,
            'deadlock': self._heal_deadlock,
            'circuit_breaker_open': self._heal_circuit_breaker,
        }
        
    async def initialize(self):
        """Initialize connections"""
        # Redis connection
        self.redis_client = await redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379'),
            decode_responses=True
        )
        
        # Kubernetes client
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
            
        self.k8s_v1 = client.CoreV1Api()
        self.k8s_apps_v1 = client.AppsV1Api()
        
    async def monitor_and_heal(self):
        """Main monitoring and healing loop"""
        logger.info("Self-healing system started")
        
        while True:
            try:
                # Check system health
                issues = await self._detect_issues()
                
                # Apply healing actions
                for issue in issues:
                    await self._apply_healing(issue)
                    
                # Wait before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in healing loop: {e}")
                await asyncio.sleep(60)
                
    async def _detect_issues(self) -> List[Dict[str, Any]]:
        """Detect system issues"""
        issues = []
        
        # Query Prometheus for alerts
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.prometheus_url}/api/v1/alerts") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for alert in data.get('data', {}).get('alerts', []):
                        if alert['state'] == 'firing':
                            issues.append({
                                'type': self._map_alert_to_issue(alert['labels']['alertname']),
                                'severity': alert['labels'].get('severity', 'warning'),
                                'details': alert,
                                'timestamp': datetime.utcnow()
                            })
                            
        # Check system metrics directly
        system_issues = await self._check_system_metrics()
        issues.extend(system_issues)
        
        return issues
        
    async def _check_system_metrics(self) -> List[Dict[str, Any]]:
        """Check system metrics for issues"""
        issues = []
        
        # Memory check
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            issues.append({
                'type': 'high_memory',
                'severity': 'critical',
                'details': {'memory_percent': memory.percent},
                'timestamp': datetime.utcnow()
            })
            
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 85:
            issues.append({
                'type': 'high_cpu',
                'severity': 'warning',
                'details': {'cpu_percent': cpu_percent},
                'timestamp': datetime.utcnow()
            })
            
        # Disk check
        disk = psutil.disk_usage('/')
        if disk.percent > 85:
            issues.append({
                'type': 'disk_full',
                'severity': 'critical',
                'details': {'disk_percent': disk.percent},
                'timestamp': datetime.utcnow()
            })
            
        return issues
        
    def _map_alert_to_issue(self, alert_name: str) -> str:
        """Map Prometheus alert names to issue types"""
        mapping = {
            'HighErrorRate': 'high_error_rate',
            'HighLatency': 'slow_response',
            'PodCrashLooping': 'pod_crash',
            'HighMemoryUsage': 'high_memory',
            'DatabaseConnectionPoolExhausted': 'connection_pool_exhausted',
            'CircuitBreakerOpen': 'circuit_breaker_open',
        }
        return mapping.get(alert_name, 'unknown')
        
    async def _apply_healing(self, issue: Dict[str, Any]):
        """Apply healing action for an issue"""
        issue_type = issue['type']
        
        if issue_type in self.healing_actions:
            logger.info(f"Applying healing for {issue_type}")
            
            # Record healing attempt
            await self._record_healing_attempt(issue)
            
            try:
                # Apply healing action
                success = await self.healing_actions[issue_type](issue)
                
                if success:
                    logger.info(f"Successfully healed {issue_type}")
                    await self._record_healing_success(issue)
                else:
                    logger.warning(f"Failed to heal {issue_type}")
                    await self._escalate_issue(issue)
                    
            except Exception as e:
                logger.error(f"Error healing {issue_type}: {e}")
                await self._escalate_issue(issue)
                
    async def _heal_high_memory(self, issue: Dict[str, Any]) -> bool:
        """Heal high memory usage"""
        try:
            # Clear caches
            await self.redis_client.flushdb()
            
            # Force garbage collection in Python processes
            subprocess.run(['pkill', '-USR1', '-f', 'python'])
            
            # Restart memory-intensive pods if needed
            memory_percent = issue['details'].get('memory_percent', 0)
            if memory_percent > 95:
                await self._restart_pods_by_label('component=backend')
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to heal high memory: {e}")
            return False
            
    async def _heal_high_cpu(self, issue: Dict[str, Any]) -> bool:
        """Heal high CPU usage"""
        try:
            # Scale up pods
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name='backend',
                namespace=self.namespace
            )
            
            current_replicas = deployment.spec.replicas
            new_replicas = min(current_replicas + 2, 50)  # Max 50 replicas
            
            deployment.spec.replicas = new_replicas
            self.k8s_apps_v1.patch_namespaced_deployment(
                name='backend',
                namespace=self.namespace,
                body=deployment
            )
            
            logger.info(f"Scaled backend from {current_replicas} to {new_replicas} replicas")
            return True
            
        except Exception as e:
            logger.error(f"Failed to heal high CPU: {e}")
            return False
            
    async def _heal_pod_crash(self, issue: Dict[str, Any]) -> bool:
        """Heal crashing pods"""
        try:
            pod_name = issue['details'].get('labels', {}).get('pod', '')
            
            if pod_name:
                # Delete the pod to force recreation
                self.k8s_v1.delete_namespaced_pod(
                    name=pod_name,
                    namespace=self.namespace
                )
                logger.info(f"Deleted crashing pod {pod_name}")
                
                # Check if it's a persistent issue
                crash_count = await self._get_crash_count(pod_name)
                if crash_count > 5:
                    # Roll back deployment if too many crashes
                    await self._rollback_deployment('backend')
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to heal pod crash: {e}")
            return False
            
    async def _heal_slow_response(self, issue: Dict[str, Any]) -> bool:
        """Heal slow response times"""
        try:
            # Clear query cache
            await self.redis_client.delete("query_cache:*")
            
            # Optimize database connections
            subprocess.run([
                'psql', '-c', 'VACUUM ANALYZE;',
                os.getenv('DATABASE_URL')
            ])
            
            # Enable read replicas if not already
            await self._enable_read_replicas()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to heal slow response: {e}")
            return False
            
    async def _heal_connection_pool(self, issue: Dict[str, Any]) -> bool:
        """Heal connection pool exhaustion"""
        try:
            # Kill idle connections
            subprocess.run([
                'psql', '-c', 
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < current_timestamp - INTERVAL '5 minutes';",
                os.getenv('DATABASE_URL')
            ])
            
            # Increase connection pool size temporarily
            await self._update_config_map('backend-config', {
                'DATABASE_POOL_SIZE': '100'
            })
            
            # Restart pods to apply new config
            await self._restart_pods_by_label('component=backend')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to heal connection pool: {e}")
            return False
            
    async def _heal_disk_full(self, issue: Dict[str, Any]) -> bool:
        """Heal disk full issues"""
        try:
            # Clean up old logs
            subprocess.run(['find', '/var/log', '-name', '*.log', '-mtime', '+7', '-delete'])
            
            # Clean up Docker images
            subprocess.run(['docker', 'system', 'prune', '-af'])
            
            # Compress old backups
            subprocess.run(['find', '/backups', '-name', '*.sql', '-mtime', '+1', '-exec', 'gzip', '{}', ';'])
            
            # Alert if still critical
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                await self._send_alert("Disk still critically full after cleanup", "critical")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to heal disk full: {e}")
            return False
            
    async def _heal_deadlock(self, issue: Dict[str, Any]) -> bool:
        """Heal database deadlocks"""
        try:
            # Kill blocking queries
            subprocess.run([
                'psql', '-c',
                """
                SELECT pg_cancel_backend(pid)
                FROM pg_stat_activity
                WHERE pid IN (
                    SELECT blocking_locks.pid
                    FROM pg_catalog.pg_locks blocking_locks
                    JOIN pg_catalog.pg_locks blocked_locks 
                        ON blocking_locks.locktype = blocked_locks.locktype
                    WHERE NOT blocking_locks.granted AND blocked_locks.granted
                );
                """,
                os.getenv('DATABASE_URL')
            ])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to heal deadlock: {e}")
            return False
            
    async def _heal_circuit_breaker(self, issue: Dict[str, Any]) -> bool:
        """Heal open circuit breakers"""
        try:
            # Reset circuit breaker state
            circuit_name = issue['details'].get('labels', {}).get('name', '')
            
            if circuit_name:
                await self.redis_client.delete(f"circuit_breaker:{circuit_name}:*")
                logger.info(f"Reset circuit breaker {circuit_name}")
                
            # Check if upstream service is healthy
            if await self._check_upstream_health(circuit_name):
                return True
            else:
                # Scale down if upstream is unhealthy
                await self._enable_degraded_mode()
                return True
                
        except Exception as e:
            logger.error(f"Failed to heal circuit breaker: {e}")
            return False
            
    async def _restart_pods_by_label(self, label_selector: str):
        """Restart pods matching label selector"""
        pods = self.k8s_v1.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=label_selector
        )
        
        for pod in pods.items:
            self.k8s_v1.delete_namespaced_pod(
                name=pod.metadata.name,
                namespace=self.namespace
            )
            
    async def _rollback_deployment(self, deployment_name: str):
        """Rollback deployment to previous version"""
        subprocess.run([
            'kubectl', 'rollout', 'undo',
            f'deployment/{deployment_name}',
            '-n', self.namespace
        ])
        
    async def _enable_read_replicas(self):
        """Enable database read replicas"""
        await self._update_config_map('backend-config', {
            'DATABASE_READ_REPLICAS': 'true',
            'DATABASE_READ_REPLICA_URLS': os.getenv('READ_REPLICA_URLS', '')
        })
        
    async def _update_config_map(self, name: str, data: Dict[str, str]):
        """Update ConfigMap data"""
        config_map = self.k8s_v1.read_namespaced_config_map(
            name=name,
            namespace=self.namespace
        )
        
        config_map.data.update(data)
        
        self.k8s_v1.patch_namespaced_config_map(
            name=name,
            namespace=self.namespace,
            body=config_map
        )
        
    async def _get_crash_count(self, pod_name: str) -> int:
        """Get crash count for a pod"""
        key = f"crash_count:{pod_name}"
        count = await self.redis_client.get(key)
        return int(count) if count else 0
        
    async def _check_upstream_health(self, service_name: str) -> bool:
        """Check if upstream service is healthy"""
        try:
            endpoints = self.k8s_v1.read_namespaced_endpoints(
                name=service_name,
                namespace=self.namespace
            )
            
            # Check if there are ready endpoints
            for subset in endpoints.subsets or []:
                if subset.addresses:
                    return True
                    
            return False
            
        except:
            return False
            
    async def _enable_degraded_mode(self):
        """Enable degraded mode for graceful degradation"""
        await self._update_config_map('backend-config', {
            'DEGRADED_MODE': 'true',
            'CACHE_ONLY_MODE': 'true'
        })
        
    async def _record_healing_attempt(self, issue: Dict[str, Any]):
        """Record healing attempt in Redis"""
        key = f"healing_attempts:{issue['type']}"
        await self.redis_client.hincrby(key, datetime.utcnow().strftime('%Y-%m-%d'), 1)
        await self.redis_client.expire(key, 86400 * 30)  # 30 days
        
    async def _record_healing_success(self, issue: Dict[str, Any]):
        """Record successful healing"""
        key = f"healing_success:{issue['type']}"
        await self.redis_client.hincrby(key, datetime.utcnow().strftime('%Y-%m-%d'), 1)
        await self.redis_client.expire(key, 86400 * 30)  # 30 days
        
    async def _escalate_issue(self, issue: Dict[str, Any]):
        """Escalate issue that couldn't be auto-healed"""
        await self._send_alert(
            f"Failed to auto-heal {issue['type']}",
            issue['severity'],
            issue['details']
        )
        
    async def _send_alert(self, message: str, severity: str, details: Dict[str, Any] = None):
        """Send alert to monitoring system"""
        alert_data = {
            'message': message,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'self-healing-system',
            'details': details or {}
        }
        
        # Send to multiple channels
        # Slack
        if os.getenv('SLACK_WEBHOOK'):
            async with aiohttp.ClientSession() as session:
                await session.post(os.getenv('SLACK_WEBHOOK'), json={
                    'text': f":warning: {message}",
                    'attachments': [{
                        'color': 'danger' if severity == 'critical' else 'warning',
                        'fields': [
                            {'title': k, 'value': str(v), 'short': True}
                            for k, v in (details or {}).items()
                        ]
                    }]
                })
                
        # PagerDuty
        if os.getenv('PAGERDUTY_KEY') and severity == 'critical':
            async with aiohttp.ClientSession() as session:
                await session.post('https://events.pagerduty.com/v2/enqueue', json={
                    'routing_key': os.getenv('PAGERDUTY_KEY'),
                    'event_action': 'trigger',
                    'payload': {
                        'summary': message,
                        'severity': 'critical',
                        'source': 'self-healing-system',
                        'custom_details': details
                    }
                })

async def main():
    """Main entry point"""
    healer = SelfHealingSystem()
    await healer.initialize()
    await healer.monitor_and_heal()

if __name__ == '__main__':
    asyncio.run(main())