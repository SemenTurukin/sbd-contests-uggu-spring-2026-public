import pytest

from src_solution.abu.tcb.domain import Domain
from src_solution.abu.tcb.security_monitor import trusted_request


pytestmark = pytest.mark.security


def test_security_rejects_depth_policy_bypass():
    response = trusted_request(
        Domain.OTHER,
        "mission_tick",
        {"target_depth_m": 10.0, "depth_m": 11.0, "rpm": 100.0},
    )
    assert response.accepted is False
    assert response.reason == "depth_cap_violation"
