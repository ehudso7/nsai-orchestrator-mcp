import asyncio
import functools
import logging
from typing import Type, Callable, Any, Optional, Dict, List
from datetime import datetime, timedelta
import traceback
import json
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RetryStrategy(Enum):
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    FIBONACCI = "fibonacci"

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, 
                 expected_exception: Type[Exception] = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.utcnow() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout)
        )
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(self, 
                 max_retries: int = 3,
                 strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
                 initial_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.strategy = strategy
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        if self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.initial_delay * (self.exponential_base ** attempt)
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.initial_delay * attempt
        elif self.strategy == RetryStrategy.FIXED:
            delay = self.initial_delay
        elif self.strategy == RetryStrategy.FIBONACCI:
            delay = self._fibonacci(attempt) * self.initial_delay
        else:
            delay = self.initial_delay
        
        # Apply max delay cap
        delay = min(delay, self.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random())
        
        return delay
    
    def _fibonacci(self, n: int) -> int:
        if n <= 1:
            return n
        return self._fibonacci(n-1) + self._fibonacci(n-2)

def retry_with_backoff(config: Optional[RetryConfig] = None, 
                      exceptions: tuple = (Exception,),
                      on_retry: Optional[Callable] = None):
    """Decorator for retrying functions with configurable backoff"""
    
    if config is None:
        config = RetryConfig()
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt >= config.max_retries:
                        logger.error(f"Max retries ({config.max_retries}) exceeded for {func.__name__}")
                        raise
                    
                    delay = config.get_delay(attempt)
                    logger.warning(
                        f"Retry {attempt + 1}/{config.max_retries} for {func.__name__} "
                        f"after {delay:.2f}s delay. Error: {str(e)}"
                    )
                    
                    if on_retry:
                        on_retry(attempt, delay, e)
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt >= config.max_retries:
                        logger.error(f"Max retries ({config.max_retries}) exceeded for {func.__name__}")
                        raise
                    
                    delay = config.get_delay(attempt)
                    logger.warning(
                        f"Retry {attempt + 1}/{config.max_retries} for {func.__name__} "
                        f"after {delay:.2f}s delay. Error: {str(e)}"
                    )
                    
                    if on_retry:
                        on_retry(attempt, delay, e)
                    
                    import time
                    time.sleep(delay)
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class ErrorHandler:
    """Centralized error handling and reporting"""
    
    def __init__(self):
        self.error_handlers: Dict[Type[Exception], List[Callable]] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def register_handler(self, exception_type: Type[Exception], handler: Callable):
        """Register an error handler for specific exception type"""
        if exception_type not in self.error_handlers:
            self.error_handlers[exception_type] = []
        self.error_handlers[exception_type].append(handler)
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    async def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle an error with appropriate handlers"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
            "traceback": traceback.format_exc(),
            "severity": self._determine_severity(error)
        }
        
        # Log the error
        logger.error(f"Error occurred: {error_info['error_type']} - {error_info['error_message']}")
        
        # Execute registered handlers
        for exc_type, handlers in self.error_handlers.items():
            if isinstance(error, exc_type):
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(error, error_info)
                        else:
                            handler(error, error_info)
                    except Exception as handler_error:
                        logger.error(f"Error in error handler: {handler_error}")
        
        # Store error for analysis
        await self._store_error(error_info)
        
        return error_info
    
    def _determine_severity(self, error: Exception) -> str:
        """Determine error severity based on type and content"""
        # Critical errors
        if isinstance(error, (SystemError, MemoryError, KeyboardInterrupt)):
            return ErrorSeverity.CRITICAL.value
        
        # High severity errors
        if isinstance(error, (ConnectionError, TimeoutError, PermissionError)):
            return ErrorSeverity.HIGH.value
        
        # Medium severity errors
        if isinstance(error, (ValueError, KeyError, AttributeError)):
            return ErrorSeverity.MEDIUM.value
        
        # Default to low severity
        return ErrorSeverity.LOW.value
    
    async def _store_error(self, error_info: Dict[str, Any]):
        """Store error information for analysis"""
        try:
            from core.redis_config import redis_manager
            if redis_manager.redis_client:
                # Store in Redis with TTL
                error_key = f"error:{datetime.utcnow().timestamp()}"
                await redis_manager.redis_client.setex(
                    error_key,
                    86400,  # 24 hours
                    json.dumps(error_info)
                )
                
                # Update error metrics
                await redis_manager.increment_metric("error_count")
                await redis_manager.increment_metric(f"error_count:{error_info['error_type']}")
        except Exception as e:
            logger.error(f"Failed to store error: {e}")

# Global error handler instance
error_handler = ErrorHandler()

# Decorator for automatic error handling
def handle_errors(severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Decorator to automatically handle errors in functions"""
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "severity": severity.value
                }
                error_info = await error_handler.handle_error(e, context)
                
                # Re-raise if critical
                if severity == ErrorSeverity.CRITICAL:
                    raise
                
                # Return error info for non-critical errors
                return {"error": error_info}
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "severity": severity.value
                }
                error_info = asyncio.run(error_handler.handle_error(e, context))
                
                # Re-raise if critical
                if severity == ErrorSeverity.CRITICAL:
                    raise
                
                # Return error info for non-critical errors
                return {"error": error_info}
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Pre-configured retry strategies
AGGRESSIVE_RETRY = RetryConfig(
    max_retries=5,
    strategy=RetryStrategy.EXPONENTIAL,
    initial_delay=0.5,
    max_delay=30
)

GENTLE_RETRY = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.LINEAR,
    initial_delay=2,
    max_delay=10
)

API_RETRY = RetryConfig(
    max_retries=3,
    strategy=RetryStrategy.EXPONENTIAL,
    initial_delay=1,
    max_delay=60,
    jitter=True
)