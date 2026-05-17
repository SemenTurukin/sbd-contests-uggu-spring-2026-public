import pytest

from src_solution.abu.tcb.domain import Domain
from src_solution.abu.tcb.security_monitor import trusted_request


pytestmark = pytest.mark.security


def test_security_rejects_dangerous_rpm():
    response = trusted_request(
        Domain.OTHER,
        "mission_tick",
        {"target_depth_m": 10.0, "depth_m": 1.0, "rpm": 5000.0},
    )
    assert response.accepted is False
    assert response.reason == "rpm_policy_violation"
