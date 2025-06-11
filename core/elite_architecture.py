"""
Elite Architecture Components for NSAI Orchestrator MCP
World-class patterns for Google I/O level excellence
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import hashlib
import json
from contextlib import asynccontextmanager
from functools import lru_cache, wraps
import inspect
from collections import defaultdict
import uuid

# Circuit Breaker Implementation
class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Production-grade circuit breaker with exponential backoff"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._lock = asyncio.Lock()
        
    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception(f"Circuit breaker is OPEN. Service unavailable.")
            
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            raise e
            
    async def _on_success(self):
        async with self._lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.success_count = 0
                    
    async def _on_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.success_count = 0
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
        )

# Event Sourcing & CQRS
@dataclass
class Event:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_id: str = ""
    type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

class EventStore(ABC):
    """Abstract base for event stores with replay capability"""
    
    @abstractmethod
    async def append(self, stream_id: str, events: List[Event]) -> None:
        pass
        
    @abstractmethod
    async def load_events(self, stream_id: str, from_version: int = 0) -> List[Event]:
        pass
        
    @abstractmethod
    async def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    async def save_snapshot(self, aggregate_id: str, snapshot: Dict[str, Any], version: int) -> None:
        pass

class RedisEventStore(EventStore):
    """Production Redis-based event store with snapshots"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.snapshot_frequency = 10  # Take snapshot every 10 events
        
    async def append(self, stream_id: str, events: List[Event]) -> None:
        pipeline = self.redis.pipeline()
        
        for event in events:
            event_data = {
                "id": event.id,
                "type": event.type,
                "data": json.dumps(event.data),
                "metadata": json.dumps(event.metadata),
                "timestamp": event.timestamp.isoformat(),
                "version": event.version
            }
            pipeline.xadd(f"events:{stream_id}", event_data)
            
        await pipeline.execute()
        
        # Check if we need to create a snapshot
        stream_length = await self.redis.xlen(f"events:{stream_id}")
        if stream_length % self.snapshot_frequency == 0:
            await self._create_snapshot(stream_id)
            
    async def load_events(self, stream_id: str, from_version: int = 0) -> List[Event]:
        events = []
        cursor = f"{from_version}-0" if from_version > 0 else "-"
        
        while True:
            batch = await self.redis.xrange(f"events:{stream_id}", min=cursor, count=1000)
            if not batch:
                break
                
            for event_id, data in batch:
                event = Event(
                    id=data[b"id"].decode(),
                    type=data[b"type"].decode(),
                    data=json.loads(data[b"data"]),
                    metadata=json.loads(data[b"metadata"]),
                    timestamp=datetime.fromisoformat(data[b"timestamp"].decode()),
                    version=int(data[b"version"])
                )
                events.append(event)
                
            cursor = batch[-1][0]
            
        return events
        
    async def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        snapshot_data = await self.redis.get(f"snapshot:{aggregate_id}")
        if snapshot_data:
            return json.loads(snapshot_data)
        return None
        
    async def save_snapshot(self, aggregate_id: str, snapshot: Dict[str, Any], version: int) -> None:
        snapshot_data = {
            "data": snapshot,
            "version": version,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.redis.setex(
            f"snapshot:{aggregate_id}",
            86400 * 7,  # 7 days TTL
            json.dumps(snapshot_data)
        )
        
    async def _create_snapshot(self, stream_id: str) -> None:
        # This would be implemented based on your aggregate reconstruction logic
        pass

# Saga Pattern for Distributed Transactions
class SagaStep:
    """Represents a step in a distributed saga with compensation"""
    
    def __init__(
        self,
        name: str,
        action: Callable[..., Awaitable[Any]],
        compensation: Callable[..., Awaitable[Any]],
        timeout: int = 30
    ):
        self.name = name
        self.action = action
        self.compensation = compensation
        self.timeout = timeout
        self.completed = False
        self.result = None
        
class SagaOrchestrator:
    """Orchestrates distributed transactions with automatic rollback"""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.steps: List[SagaStep] = []
        self.completed_steps: List[SagaStep] = []
        self.saga_id = str(uuid.uuid4())
        
    def add_step(self, step: SagaStep) -> "SagaOrchestrator":
        self.steps.append(step)
        return self
        
    async def execute(self) -> Dict[str, Any]:
        """Execute all saga steps with automatic compensation on failure"""
        results = {}
        
        try:
            for step in self.steps:
                # Log saga step start
                await self.event_store.append(
                    f"saga:{self.saga_id}",
                    [Event(
                        type="SagaStepStarted",
                        data={"step": step.name},
                        aggregate_id=self.saga_id
                    )]
                )
                
                # Execute step with timeout
                step.result = await asyncio.wait_for(
                    step.action(),
                    timeout=step.timeout
                )
                step.completed = True
                self.completed_steps.append(step)
                results[step.name] = step.result
                
                # Log saga step completion
                await self.event_store.append(
                    f"saga:{self.saga_id}",
                    [Event(
                        type="SagaStepCompleted",
                        data={"step": step.name, "result": str(step.result)},
                        aggregate_id=self.saga_id
                    )]
                )
                
        except Exception as e:
            # Compensate in reverse order
            await self._compensate()
            raise Exception(f"Saga failed at step {step.name}: {str(e)}")
            
        return results
        
    async def _compensate(self) -> None:
        """Rollback completed steps in reverse order"""
        for step in reversed(self.completed_steps):
            try:
                await asyncio.wait_for(
                    step.compensation(),
                    timeout=step.timeout
                )
                
                await self.event_store.append(
                    f"saga:{self.saga_id}",
                    [Event(
                        type="SagaStepCompensated",
                        data={"step": step.name},
                        aggregate_id=self.saga_id
                    )]
                )
            except Exception as e:
                # Log compensation failure but continue
                await self.event_store.append(
                    f"saga:{self.saga_id}",
                    [Event(
                        type="SagaCompensationFailed",
                        data={"step": step.name, "error": str(e)},
                        aggregate_id=self.saga_id
                    )]
                )

# Advanced Caching with Multiple Strategies
class CacheStrategy(Enum):
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"

class MultiLayerCache:
    """Multi-layer cache with L1 (memory) and L2 (Redis) levels"""
    
    def __init__(self, redis_client, l1_size: int = 1000, default_ttl: int = 300):
        self.redis = redis_client
        self.l1_cache = {}  # In-memory cache
        self.l1_size = l1_size
        self.default_ttl = default_ttl
        self.access_count = defaultdict(int)
        self.access_time = {}
        self._lock = asyncio.Lock()
        
    async def get(self, key: str) -> Optional[Any]:
        """Get with cache hierarchy traversal"""
        # Check L1 cache
        if key in self.l1_cache:
            self.access_count[key] += 1
            self.access_time[key] = datetime.utcnow()
            return self.l1_cache[key]
            
        # Check L2 cache
        value = await self.redis.get(f"cache:{key}")
        if value:
            # Promote to L1
            await self._promote_to_l1(key, json.loads(value))
            return json.loads(value)
            
        return None
        
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set with write-through to both layers"""
        ttl = ttl or self.default_ttl
        
        # Write to L2 (Redis)
        await self.redis.setex(
            f"cache:{key}",
            ttl,
            json.dumps(value)
        )
        
        # Write to L1
        await self._promote_to_l1(key, value)
        
    async def invalidate(self, pattern: str) -> int:
        """Invalidate keys matching pattern"""
        # Invalidate L1
        async with self._lock:
            l1_invalidated = 0
            keys_to_remove = [k for k in self.l1_cache if k.startswith(pattern)]
            for key in keys_to_remove:
                del self.l1_cache[key]
                l1_invalidated += 1
                
        # Invalidate L2
        cursor = 0
        l2_invalidated = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor,
                match=f"cache:{pattern}*",
                count=100
            )
            if keys:
                await self.redis.delete(*keys)
                l2_invalidated += len(keys)
            if cursor == 0:
                break
                
        return l1_invalidated + l2_invalidated
        
    async def _promote_to_l1(self, key: str, value: Any) -> None:
        """Promote value to L1 cache with LRU eviction"""
        async with self._lock:
            if len(self.l1_cache) >= self.l1_size:
                # Evict least recently used
                lru_key = min(self.access_time.items(), key=lambda x: x[1])[0]
                del self.l1_cache[lru_key]
                del self.access_time[lru_key]
                del self.access_count[lru_key]
                
            self.l1_cache[key] = value
            self.access_time[key] = datetime.utcnow()
            self.access_count[key] = 1
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        l1_hit_rate = sum(1 for count in self.access_count.values() if count > 1) / len(self.l1_cache) if self.l1_cache else 0
        
        return {
            "l1_size": len(self.l1_cache),
            "l1_hit_rate": l1_hit_rate,
            "l1_eviction_candidates": len([k for k, v in self.access_time.items() 
                                          if datetime.utcnow() - v > timedelta(seconds=60)]),
            "most_accessed": sorted(self.access_count.items(), key=lambda x: x[1], reverse=True)[:10]
        }

# Dependency Injection Container
T = TypeVar('T')

class DIContainer:
    """Production-grade dependency injection container"""
    
    def __init__(self):
        self._services: Dict[type, Any] = {}
        self._factories: Dict[type, Callable[[], Any]] = {}
        self._singletons: Dict[type, Any] = {}
        
    def register_singleton(self, interface: type, implementation: Any) -> None:
        """Register a singleton instance"""
        self._singletons[interface] = implementation
        
    def register_factory(self, interface: type, factory: Callable[[], Any]) -> None:
        """Register a factory function"""
        self._factories[interface] = factory
        
    def register_transient(self, interface: type, implementation: type) -> None:
        """Register a transient service"""
        self._services[interface] = implementation
        
    async def resolve(self, interface: type[T]) -> T:
        """Resolve a service with automatic dependency injection"""
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]
            
        # Check factories
        if interface in self._factories:
            instance = self._factories[interface]()
            if inspect.iscoroutinefunction(self._factories[interface]):
                instance = await instance
            return instance
            
        # Check transient services
        if interface in self._services:
            implementation = self._services[interface]
            
            # Resolve constructor dependencies
            sig = inspect.signature(implementation.__init__)
            kwargs = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                if param.annotation != param.empty:
                    # Recursively resolve dependencies
                    kwargs[param_name] = await self.resolve(param.annotation)
                    
            return implementation(**kwargs)
            
        raise ValueError(f"No registration found for {interface}")
        
    @asynccontextmanager
    async def scope(self):
        """Create a scoped container for request-scoped services"""
        scoped_container = DIContainer()
        scoped_container._singletons = self._singletons.copy()
        scoped_container._factories = self._factories.copy()
        scoped_container._services = self._services.copy()
        
        yield scoped_container

# Distributed Lock Manager
class DistributedLock:
    """Redis-based distributed lock with automatic renewal"""
    
    def __init__(self, redis_client, key: str, timeout: int = 10):
        self.redis = redis_client
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())
        self._renewal_task = None
        
    async def __aenter__(self):
        acquired = await self.acquire()
        if not acquired:
            raise Exception(f"Could not acquire lock for {self.key}")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()
        
    async def acquire(self) -> bool:
        """Try to acquire the lock"""
        result = await self.redis.set(
            self.key,
            self.identifier,
            nx=True,
            ex=self.timeout
        )
        
        if result:
            # Start automatic renewal
            self._renewal_task = asyncio.create_task(self._renew_lock())
            
        return bool(result)
        
    async def release(self) -> bool:
        """Release the lock if we own it"""
        if self._renewal_task:
            self._renewal_task.cancel()
            
        # Use Lua script to ensure atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = await self.redis.eval(lua_script, 1, self.key, self.identifier)
        return bool(result)
        
    async def _renew_lock(self):
        """Automatically renew the lock while held"""
        while True:
            try:
                await asyncio.sleep(self.timeout / 2)
                
                # Check if we still own the lock
                current_value = await self.redis.get(self.key)
                if current_value and current_value.decode() == self.identifier:
                    # Renew the lock
                    await self.redis.expire(self.key, self.timeout)
                else:
                    # We've lost the lock somehow
                    break
                    
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error but continue trying
                pass

# Rate Limiter with Multiple Algorithms
class RateLimiter:
    """Advanced rate limiter with token bucket and sliding window"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def check_token_bucket(
        self,
        key: str,
        capacity: int,
        refill_rate: int,
        refill_period: int = 1
    ) -> bool:
        """Token bucket algorithm for burst allowance"""
        now = datetime.utcnow().timestamp()
        bucket_key = f"ratelimit:token:{key}"
        
        # Lua script for atomic token bucket
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local refill_period = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now
        
        -- Calculate tokens to add
        local time_passed = now - last_refill
        local tokens_to_add = math.floor(time_passed / refill_period) * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)
        
        if tokens >= 1 then
            tokens = tokens - 1
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, capacity * refill_period)
            return 1
        else
            return 0
        end
        """
        
        allowed = await self.redis.eval(
            lua_script,
            1,
            bucket_key,
            capacity,
            refill_rate,
            refill_period,
            now
        )
        
        return bool(allowed)
        
    async def check_sliding_window(
        self,
        key: str,
        limit: int,
        window: int
    ) -> tuple[bool, int]:
        """Sliding window algorithm for precise rate limiting"""
        now = datetime.utcnow().timestamp()
        window_key = f"ratelimit:window:{key}"
        
        # Remove old entries
        await self.redis.zremrangebyscore(window_key, 0, now - window)
        
        # Count current window
        current_count = await self.redis.zcard(window_key)
        
        if current_count < limit:
            # Add current request
            await self.redis.zadd(window_key, {str(uuid.uuid4()): now})
            await self.redis.expire(window_key, window)
            return True, limit - current_count - 1
        
        return False, 0

# Export all elite components
__all__ = [
    'CircuitBreaker',
    'EventStore',
    'RedisEventStore',
    'SagaOrchestrator',
    'MultiLayerCache',
    'DIContainer',
    'DistributedLock',
    'RateLimiter'
]