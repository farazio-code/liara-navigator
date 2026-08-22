import pytest
from app.domain.errors import AppError, ErrorCode
from app.providers.ai.resilience import CircuitBreaker


def test_circuit_opens_after_bounded_failures_and_recovers() -> None:
    now = [100.0]
    circuit = CircuitBreaker(failure_threshold=2, recovery_seconds=10, clock=lambda: now[0])

    circuit.failure()
    circuit.check()
    circuit.failure()
    with pytest.raises(AppError) as caught:
        circuit.check()
    assert caught.value.code == ErrorCode.AI_RATE_LIMITED

    now[0] = 111.0
    circuit.check()
    circuit.success()
