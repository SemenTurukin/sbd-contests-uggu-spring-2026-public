"""Тесты моделей доменов, политик и служебной проверки ДВБ."""

from src_solution.abu.tcb.domain import Domain, DomainRequest, DomainResponse
from src_solution.abu.tcb.placeholder import tcb_health
from src_solution.abu.tcb.policies import DEFAULT_POLICY, SafetyPolicy


def test_domain_values_are_stable():
    """Проверяем машинные значения доменов."""
    assert Domain.TCB.value == "tcb"
    assert Domain.OTHER.value == "other"
    assert Domain.DIGITAL_MINE.value == "digital_mine"
    assert Domain.REGULATOR.value == "regulator"


def test_domain_request_defaults_payload():
    """Проверяем payload по умолчанию у междоменного запроса."""
    request = DomainRequest(Domain.OTHER, Domain.TCB, "status")
    assert request.payload == {}


def test_domain_response_defaults_payload():
    """Проверяем payload по умолчанию у ответа монитора."""
    response = DomainResponse(True, "allowed")
    assert response.payload == {}


def test_default_policy_contains_required_actions():
    """Проверяем обязательные действия политики."""
    assert "start_mission" in DEFAULT_POLICY.allowed_actions
    assert "mission_tick" in DEFAULT_POLICY.allowed_actions
    assert "ai_suggest" in DEFAULT_POLICY.allowed_actions
    assert "status" in DEFAULT_POLICY.allowed_actions


def test_default_policy_contains_required_edges():
    """Проверяем разрешённые границы доверия."""
    assert (Domain.OTHER, Domain.TCB) in DEFAULT_POLICY.allowed_edges
    assert (Domain.DIGITAL_MINE, Domain.TCB) in DEFAULT_POLICY.allowed_edges


def test_custom_policy_can_be_created():
    """Проверяем создание отдельной политики безопасности."""
    policy = SafetyPolicy(max_depth_m=10.0, max_rpm=20.0)
    assert policy.max_depth_m == 10.0
    assert policy.max_rpm == 20.0


def test_tcb_health_probe():
    """Проверяем служебную проверку доступности ДВБ."""
    assert tcb_health() == "ok"
