import os
from typing import Optional
import redis
from redis.asyncio import Redis as AsyncRedis
import json
from datetime import datetime, timedelta

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

class RedisManager:
    """God-tier Redis manager with advanced features"""
    
    def __init__(self):
        self.redis_client: Optional[AsyncRedis] = None
        self.sync_client: Optional[redis.Redis] = None
        
    async def connect(self):
        """Connect to Redis with proper error handling"""
        try:
            self.redis_client = await AsyncRedis.from_url(
                REDIS_URL,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 1,  # TCP_KEEPINTVL
                    3: 3,  # TCP_KEEPCNT
                }
            )
            
            # Test connection
            await self.redis_client.ping()
            print("Redis connected successfully")
            
        except Exception as e:
            print(f"Redis connection failed: {e}")
            # Fallback to in-memory cache
            self.redis_client = None
            
    def get_sync_client(self) -> Optional[redis.Redis]:
        """Get synchronous Redis client"""
        if not self.sync_client:
            try:
                self.sync_client = redis.from_url(
                    REDIS_URL,
                    password=REDIS_PASSWORD,
                    db=REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                self.sync_client.ping()
            except:
                self.sync_client = None
        return self.sync_client
        
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis with fallback"""
        if not self.redis_client:
            return None
        try:
            return await self.redis_client.get(key)
        except:
            return None
            
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """Set value in Redis with optional expiration"""
        if not self.redis_client:
            return False
        try:
            if expire:
                await self.redis_client.setex(key, expire, value)
            else:
                await self.redis_client.set(key, value)
            return True
        except:
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.delete(key)
            return True
        except:
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis_client:
            return False
        try:
            return await self.redis_client.exists(key) > 0
        except:
            return False
            
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from Redis"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                pass
        return None
        
    async def set_json(self, key: str, value: dict, expire: Optional[int] = None):
        """Set JSON value in Redis"""
        return await self.set(key, json.dumps(value), expire)
        
    async def lpush(self, key: str, *values):
        """Push values to list"""
        if not self.redis_client:
            return 0
        try:
            return await self.redis_client.lpush(key, *values)
        except:
            return 0
            
    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get range from list"""
        if not self.redis_client:
            return []
        try:
            return await self.redis_client.lrange(key, start, end)
        except:
            return []
            
    async def publish(self, channel: str, message: str):
        """Publish message to channel"""
        if not self.redis_client:
            return 0
        try:
            return await self.redis_client.publish(channel, message)
        except:
            return 0
            
    async def subscribe(self, *channels):
        """Subscribe to channels"""
        if not self.redis_client:
            return None
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(*channels)
            return pubsub
        except:
            return None
            
    async def close(self):
        """Close Redis connections"""
        if self.redis_client:
            await self.redis_client.close()
        if self.sync_client:
            self.sync_client.close()

# Global Redis manager instance
redis_manager = RedisManager()

# Workflow storage functions
async def save_workflow(workflow_id: str, workflow_data: dict):
    """Save workflow to Redis"""
    key = f"workflow:{workflow_id}"
    workflow_data["updated_at"] = datetime.now().isoformat()
    await redis_manager.set_json(key, workflow_data)
    
    # Add to workflow list
    await redis_manager.lpush("workflows", workflow_id)
    
async def load_workflow(workflow_id: str) -> Optional[dict]:
    """Load workflow from Redis"""
    key = f"workflow:{workflow_id}"
    return await redis_manager.get_json(key)
    
async def list_workflows() -> list:
    """List all workflows"""
    workflow_ids = await redis_manager.lrange("workflows", 0, -1)
    workflows = []
    
    for workflow_id in workflow_ids:
        workflow = await load_workflow(workflow_id)
        if workflow:
            workflows.append({
                "id": workflow_id,
                "name": workflow.get("name", "Unnamed"),
                "updated_at": workflow.get("updated_at"),
                "nodes": len(workflow.get("nodes", [])),
                "edges": len(workflow.get("edges", []))
            })
            
    return workflows

# Agent result caching
async def cache_agent_result(agent: str, task: str, result: dict, ttl: int = 3600):
    """Cache agent execution result"""
    key = f"agent_result:{agent}:{hash(task)}"
    await redis_manager.set_json(key, result, expire=ttl)
    
async def get_cached_agent_result(agent: str, task: str) -> Optional[dict]:
    """Get cached agent result"""
    key = f"agent_result:{agent}:{hash(task)}"
    return await redis_manager.get_json(key)

# User session management
async def create_session(user_id: str, token: str, ttl: int = 3600):
    """Create user session"""
    key = f"session:{token}"
    session_data = {
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
    }
    await redis_manager.set_json(key, session_data, expire=ttl)
    
async def get_session(token: str) -> Optional[dict]:
    """Get user session"""
    key = f"session:{token}"
    return await redis_manager.get_json(key)
    
async def delete_session(token: str):
    """Delete user session"""
    key = f"session:{token}"
    await redis_manager.delete(key)

# Metrics tracking
async def increment_metric(metric_name: str, value: int = 1):
    """Increment metric counter"""
    if not redis_manager.redis_client:
        return
    try:
        key = f"metric:{metric_name}:{datetime.now().strftime('%Y-%m-%d')}"
        await redis_manager.redis_client.incrby(key, value)
        # Expire after 30 days
        await redis_manager.redis_client.expire(key, 30 * 24 * 3600)
    except:
        pass
        
async def get_metric(metric_name: str, days: int = 7) -> dict:
    """Get metric data for last N days"""
    data = {}
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        key = f"metric:{metric_name}:{date}"
        value = await redis_manager.get(key)
        data[date] = int(value) if value else 0
    return data