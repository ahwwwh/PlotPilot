from interfaces.main import _daemon_circuit_breaker_wait_seconds


class _OpenBreaker:
    def is_open(self):
        return True

    def wait_seconds(self):
        return 12.5


class _ClosedBreaker:
    def is_open(self):
        return False

    def wait_seconds(self):
        return 0


class _Daemon:
    def __init__(self, breaker):
        self.circuit_breaker = breaker


def test_daemon_circuit_breaker_wait_seconds_returns_wait_when_open():
    assert _daemon_circuit_breaker_wait_seconds(_Daemon(_OpenBreaker())) == 12.5


def test_daemon_circuit_breaker_wait_seconds_returns_none_when_closed_or_missing():
    assert _daemon_circuit_breaker_wait_seconds(_Daemon(_ClosedBreaker())) is None
    assert _daemon_circuit_breaker_wait_seconds(_Daemon(None)) is None
