"""circuit_breaker.py - サーキットブレーカー"""
from enum import Enum
from typing import Callable, Any
from datetime import datetime, timedelta
from loguru import logger


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Simple circuit breaker"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Args:
            failure_threshold: Number of failures before opening
            timeout: Seconds before trying again (half-open)
            expected_exception: Exception type to count as failure
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info("Circuit breaker: attempting reset (half-open)")
                self.state = CircuitState.HALF_OPEN
            else:
                logger.warning("Circuit breaker: OPEN, rejecting call")
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try reset"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure > timedelta(seconds=self.timeout)
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            logger.success("Circuit breaker: reset to CLOSED")
        
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            logger.error(
                f"Circuit breaker: OPENING after {self.failure_count} failures"
            )
            self.state = CircuitState.OPEN
        else:
            logger.warning(
                f"Circuit breaker: failure {self.failure_count}/{self.failure_threshold}"
            )
    
    def get_state(self) -> str:
        """Get current state"""
        return self.state.value
