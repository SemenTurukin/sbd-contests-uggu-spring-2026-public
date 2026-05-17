"""Дополнительные тесты доверенного управления миссией."""

import pytest

from src_solution.abu.tcb.mission_control import MissionController
from src_solution.abu.tcb.policies import SafetyPolicy


def test_tick_without_active_mission_raises_error():
    """Проверяем запрет шага без активной миссии."""
    controller = MissionController()

    with pytest.raises(RuntimeError, match="no active mission"):
        controller.tick()


def test_tick_returns_existing_non_running_mission():
    """Проверяем, что завершённая миссия не изменяется повторным шагом."""
    controller = MissionController()
    mission = controller.start_mission(0.5, 120.0)

    controller.tick(risk="low", suggested_rpm=120.0)
    assert mission.status == "completed"

    same_mission = controller.tick(risk="low", suggested_rpm=120.0)
    assert same_mission is mission
    assert same_mission.status == "completed"


def test_start_mission_caps_rpm_by_policy():
    """Проверяем ограничение стартовых оборотов политикой."""
    controller = MissionController(SafetyPolicy(max_rpm=100.0))
    mission = controller.start_mission(1.0, max_rpm=100.0)

    assert mission.rpm == 100.0


def test_tick_caps_suggested_rpm_by_policy():
    """Проверяем ограничение рекомендованных оборотов политикой."""
    controller = MissionController(SafetyPolicy(max_rpm=80.0))
    mission = controller.start_mission(2.0, max_rpm=80.0)

    controller.tick(risk="low", suggested_rpm=500.0)

    assert mission.rpm == 80.0


def test_tick_sets_emergency_status_on_high_risk():
    """Проверяем аварийный статус при высоком риске."""
    controller = MissionController()
    mission = controller.start_mission(10.0, 120.0)

    controller.tick(risk="high", suggested_rpm=120.0)

    assert mission.status == "emergency"


def test_start_mission_rejects_unsafe_depth():
    """Проверяем запрет запуска миссии с опасной глубиной."""
    controller = MissionController()

    with pytest.raises(ValueError, match="depth"):
        controller.start_mission(1000.0, 120.0)
