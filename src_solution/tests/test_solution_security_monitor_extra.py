"""Дополнительные тесты монитора безопасности."""

from pathlib import Path

from src_solution.abu.tcb.domain import Domain, DomainRequest
from src_solution.abu.tcb.event_log import EventLog
from src_solution.abu.tcb.policies import SafetyPolicy
from src_solution.abu.tcb.security_monitor import SecurityMonitor


def make_monitor(tmp_path: Path) -> SecurityMonitor:
    """Создаёт монитор с изолированным журналом для теста."""
    return SecurityMonitor(event_log=EventLog(tmp_path))


def test_monitor_allows_status_request(tmp_path: Path):
    """Проверяем разрешённый status-запрос."""
    monitor = make_monitor(tmp_path)
    response = monitor.mediate(
    DomainRequest(
        Domain.REGULATOR,
        Domain.TCB,
        "status",
    )
    )

    assert response.accepted is True
    assert response.reason == "allowed"


def test_monitor_rejects_unknown_action_and_logs(tmp_path: Path):
    """Проверяем отклонение неизвестного действия и запись в журнал."""
    monitor = make_monitor(tmp_path)
    response = monitor.mediate(
        DomainRequest(Domain.OTHER, Domain.TCB, "write_raw_actuator"),
    )

    assert response.accepted is False
    assert response.reason == "action_not_allowed"
    assert "policy_violation" in monitor.event_log.read_full_tail()


def test_monitor_rejects_target_depth_over_policy(tmp_path: Path):
    """Проверяем отклонение цели глубины выше политики."""
    monitor = make_monitor(tmp_path)
    response = monitor.mediate(
        DomainRequest(
            Domain.OTHER,
            Domain.TCB,
            "mission_tick",
            {"target_depth_m": 1000.0, "depth_m": 1.0, "rpm": 100.0},
        ),
    )

    assert response.accepted is False
    assert response.reason == "depth_policy_violation"


def test_monitor_rejects_current_depth_over_policy(tmp_path: Path):
    """Проверяем отклонение текущей глубины выше политики."""
    monitor = make_monitor(tmp_path)
    response = monitor.mediate(
        DomainRequest(
            Domain.OTHER,
            Domain.TCB,
            "mission_tick",
            {"target_depth_m": 100.0, "depth_m": 300.0, "rpm": 100.0},
        ),
    )

    assert response.accepted is False
    assert response.reason == "depth_policy_violation"


def test_monitor_rejects_depth_cap_bypass(tmp_path: Path):
    """Проверяем отклонение обхода целевой глубины."""
    monitor = make_monitor(tmp_path)
    response = monitor.mediate(
        DomainRequest(
            Domain.OTHER,
            Domain.TCB,
            "mission_tick",
            {"target_depth_m": 10.0, "depth_m": 11.0, "rpm": 100.0},
        ),
    )

    assert response.accepted is False
    assert response.reason == "depth_cap_violation"


def test_monitor_rejects_rpm_over_policy(tmp_path: Path):
    """Проверяем отклонение превышения оборотов."""
    monitor = make_monitor(tmp_path)
    response = monitor.mediate(
        DomainRequest(
            Domain.OTHER,
            Domain.TCB,
            "mission_tick",
            {"target_depth_m": 10.0, "depth_m": 1.0, "rpm": 999.0},
        ),
    )

    assert response.accepted is False
    assert response.reason == "rpm_policy_violation"


def test_monitor_allows_valid_mission_payload(tmp_path: Path):
    """Проверяем разрешение корректного payload миссии."""
    monitor = make_monitor(tmp_path)
    response = monitor.mediate(
        DomainRequest(
            Domain.OTHER,
            Domain.TCB,
            "mission_tick",
            {"target_depth_m": 10.0, "depth_m": 1.0, "rpm": 100.0},
        ),
    )

    assert response.accepted is True
    assert response.reason == "allowed"
    assert response.payload["rpm"] == 100.0


def test_monitor_uses_custom_policy(tmp_path: Path):
    """Проверяем работу монитора с пользовательской политикой."""
    policy = SafetyPolicy(max_depth_m=5.0, max_rpm=50.0)
    monitor = SecurityMonitor(policy=policy, event_log=EventLog(tmp_path))

    response = monitor.mediate(
        DomainRequest(
            Domain.OTHER,
            Domain.TCB,
            "mission_tick",
            {"target_depth_m": 10.0, "depth_m": 1.0, "rpm": 100.0},
        ),
    )

    assert response.accepted is False
    assert response.reason == "depth_policy_violation"
