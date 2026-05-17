from src_solution.abu.tcb.domain import Domain, DomainRequest
from src_solution.abu.tcb.security_monitor import SecurityMonitor, trusted_request


def test_monitor_allows_known_request():
    response = trusted_request(
        Domain.OTHER,
        "mission_tick",
        {"target_depth_m": 10.0, "depth_m": 1.0, "rpm": 100.0},
    )
    assert response.accepted is True
    assert response.reason == "allowed"


def test_monitor_rejects_domain_violation():
    monitor = SecurityMonitor()
    request = DomainRequest(Domain.OTHER, Domain.REGULATOR, "mission_tick", {})
    response = monitor.mediate(request)
    assert response.accepted is False
    assert response.reason == "domain_violation"


def test_monitor_rejects_rpm_policy_violation():
    response = trusted_request(
        Domain.OTHER,
        "mission_tick",
        {"target_depth_m": 10.0, "depth_m": 1.0, "rpm": 9999.0},
    )
    assert response.accepted is False
    assert response.reason == "rpm_policy_violation"
