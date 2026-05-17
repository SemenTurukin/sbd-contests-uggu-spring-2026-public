import pytest

from src_solution.abu.tcb.domain import Domain
from src_solution.abu.tcb.security_monitor import trusted_request


pytestmark = pytest.mark.security


def test_security_rejects_unknown_action():
    response = trusted_request(Domain.OTHER, "write_raw_actuator", {"rpm": 10.0})
    assert response.accepted is False
    assert response.reason == "action_not_allowed"
