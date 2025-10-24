"""test_circuit_breaker.py"""
import pytest
from nfops_inference.core.circuit_breaker import CircuitBreaker, CircuitState


class TestCircuitBreaker:
    def test_closed_state(self):
        """Test circuit breaker in closed state"""
        cb = CircuitBreaker(failure_threshold=3)
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
    
    def test_opens_after_failures(self):
        """Test circuit breaker opens after failures"""
        cb = CircuitBreaker(failure_threshold=3)
        
        def fail_func():
            raise Exception("Error")
        
        # Fail multiple times
        for _ in range(3):
            try:
                cb.call(fail_func)
            except:
                pass
        
        # Should be open
        assert cb.state == CircuitState.OPEN
        
        # Should reject calls
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(fail_func)
