"""Security-тесты для покрытия сертифицируемого кода АБУ."""

from pathlib import Path

import pytest

from src_solution.abu.other.analytics import (
    anomaly_vibration as other_anomaly_vibration,
    regime_suggest,
    risk_flag,
    smooth_vibration_window,
)
from src_solution.abu.other.numpy_workflow import smooth_vibration_window as np_smooth
from src_solution.abu.other.pseudo_ai import anomaly_vibration as ai_anomaly
from src_solution.abu.tcb.domain import Domain, DomainRequest
from src_solution.abu.tcb.event_log import EventLevel, EventLog
from src_solution.abu.tcb.mission_control import MissionController
from src_solution.abu.tcb.placeholder import tcb_health
from src_solution.abu.tcb.policies import DEFAULT_POLICY
from src_solution.abu.tcb.safety import (
    anomaly_vibration,
    clamp_non_negative,
    enforce_depth_cap,
    enforce_rpm_cap,
    should_emergency_stop,
)
from src_solution.abu.tcb.security_monitor import SecurityMonitor, trusted_request


pytestmark = pytest.mark.security


def test_security_certification_covers_tcb_and_other_paths(tmp_path: Path) -> None:
    """Проверяет основные безопасные и запрещённые ветки сертифицируемого кода."""

    # Проверяем доверенный журнал событий.
    event_log = EventLog(log_dir=tmp_path, ring_size=2)
    event_log.record(EventLevel.INFO, "обычное событие")
    event_log.record(EventLevel.WARNING, "строка\nс переносом")
    event_log.record(EventLevel.ERROR, "ошибка")

    ring = event_log.ring_snapshot()
    assert len(ring) == 2
    assert "с переносом" in event_log.read_full_tail()
    assert "\nс переносом" not in event_log.read_full_tail()

    # Проверяем базовые доверенные функции безопасности.
    assert clamp_non_negative(-10.0) == 0.0
    assert enforce_depth_cap(10.0, 20.0)
    assert not enforce_depth_cap(30.0, 20.0)
    assert enforce_rpm_cap(100.0, DEFAULT_POLICY.max_rpm)
    assert not enforce_rpm_cap(500.0, DEFAULT_POLICY.max_rpm)

    assert anomaly_vibration([]) == 1.0
    assert anomaly_vibration([0.1]) == 0.0
    assert 0.0 <= anomaly_vibration([0.1, 0.2, 0.3]) <= 1.0
    assert should_emergency_stop("high", [0.1])
    assert not should_emergency_stop("low", [0.1])

    # Проверяем монитор безопасности: разрешённые и запрещённые запросы.
    monitor = SecurityMonitor(event_log=event_log)

    allowed = monitor.mediate(
        DomainRequest(
            source=Domain.DIGITAL_MINE,
            target=Domain.TCB,
            action="start_mission",
            payload={
                "target_depth_m": 10.0,
                "depth_m": 0.0,
                "rpm": 100.0,
            },
        )
    )
    assert allowed.accepted

    bad_domain = monitor.mediate(
        DomainRequest(
            source=Domain.OTHER,
            target=Domain.REGULATOR,
            action="status",
            payload={},
        )
    )
    assert not bad_domain.accepted
    assert bad_domain.reason == "domain_violation"

    bad_action = monitor.mediate(
        DomainRequest(
            source=Domain.REGULATOR,
            target=Domain.TCB,
            action="delete_all",
            payload={},
        )
    )
    assert not bad_action.accepted
    assert bad_action.reason == "action_not_allowed"

    bad_depth = monitor.mediate(
        DomainRequest(
            source=Domain.DIGITAL_MINE,
            target=Domain.TCB,
            action="start_mission",
            payload={
                "target_depth_m": DEFAULT_POLICY.max_depth_m + 1.0,
                "depth_m": 0.0,
                "rpm": 100.0,
            },
        )
    )
    assert not bad_depth.accepted
    assert bad_depth.reason == "depth_policy_violation"

    bad_rpm = monitor.mediate(
        DomainRequest(
            source=Domain.DIGITAL_MINE,
            target=Domain.TCB,
            action="start_mission",
            payload={
                "target_depth_m": 10.0,
                "depth_m": 0.0,
                "rpm": DEFAULT_POLICY.max_rpm + 1.0,
            },
        )
    )
    assert not bad_rpm.accepted
    assert bad_rpm.reason == "rpm_policy_violation"

    status_response = trusted_request(Domain.REGULATOR, "status", {"ok": True})
    assert status_response.accepted
    assert status_response.payload == {"ok": True}

    # Проверяем доверенный контроллер миссии.
    controller = MissionController()
    mission = controller.start_mission(target_depth_m=1.0, max_rpm=120.0)
    assert mission.status == "running"
    assert mission.rpm == 120.0

    mission = controller.tick(risk="low", suggested_rpm=110.0)
    assert mission.depth_m == 0.5
    assert mission.status == "running"

    mission = controller.tick(risk="low", suggested_rpm=110.0)
    assert mission.depth_m == 1.0
    assert mission.status == "completed"

    emergency_controller = MissionController()
    emergency_controller.start_mission(target_depth_m=5.0, max_rpm=120.0)
    emergency = emergency_controller.tick(risk="high", suggested_rpm=100.0)
    assert emergency.status == "emergency"

    with pytest.raises(RuntimeError):
        MissionController().tick()

    assert tcb_health() == "ok"

    # Покрываем недоверенную аналитику, чтобы cert coverage не падал на abu/other.
    assert smooth_vibration_window([1.0, 2.0, 3.0], window=2) == 2.5
    assert np_smooth([], window=2) == 0.0
    assert np_smooth([1.0, 2.0, 3.0], window=3) == 2.0

    assert ai_anomaly([]) == 1.0
    assert ai_anomaly([0.2]) == 0.0
    assert 0.0 <= ai_anomaly([0.1, 0.2, 0.4]) <= 1.0
    assert 0.0 <= other_anomaly_vibration([0.1, 0.2, 0.4]) <= 1.0

    rpm, feed = regime_suggest(depth_m=10.0, torque_nm=6000.0)
    assert rpm > 0
    assert feed > 0

    assert risk_flag(vibration=0.1, pressure=100.0, depth_m=10.0) == "low"
    assert risk_flag(vibration=0.8, pressure=100.0, depth_m=10.0) == "medium"
    assert risk_flag(vibration=0.8, pressure=200.0, depth_m=100.0) == "high"