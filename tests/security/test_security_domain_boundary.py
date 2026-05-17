import pytest

from src_solution.abu.tcb.domain import Domain, DomainRequest
from src_solution.abu.tcb.security_monitor import SecurityMonitor


pytestmark = pytest.mark.security


def test_security_rejects_forbidden_domain_edge():
    monitor = SecurityMonitor()
    response = monitor.mediate(DomainRequest(Domain.OTHER, Domain.REGULATOR, "status", {}))
    assert response.accepted is False
    assert response.reason == "domain_violation"
