"""Дополнительные тесты доверенных safety-проверок."""

from src_solution.abu.tcb.safety import (
    anomaly_vibration,
    clamp_non_negative,
    enforce_depth_cap,
    enforce_rpm_cap,
    should_emergency_stop,
)


def test_clamp_non_negative():
    """Проверяем нормализацию отрицательных значений."""
    assert clamp_non_negative(-10.0) == 0.0
    assert clamp_non_negative(5.0) == 5.0


def test_enforce_depth_cap():
    """Проверяем ограничение глубины."""
    assert enforce_depth_cap(10.0, 20.0) is True
    assert enforce_depth_cap(30.0, 20.0) is False


def test_enforce_rpm_cap():
    """Проверяем ограничение оборотов."""
    assert enforce_rpm_cap(100.0, 300.0) is True
    assert enforce_rpm_cap(500.0, 300.0) is False


def test_trusted_anomaly_vibration_edges():
    """Проверяем граничные случаи доверенной проверки вибрации."""
    assert anomaly_vibration([]) == 1.0
    assert anomaly_vibration([0.5]) == 0.0


def test_should_emergency_stop_by_high_risk():
    """Проверяем аварийную остановку при высоком риске."""
    assert should_emergency_stop("high", [0.1, 0.2]) is True


def test_should_emergency_stop_by_vibration():
    """Проверяем аварийную остановку по вибрации."""
    assert should_emergency_stop(
        "low",
        [0.1, 0.1, 0.1, 0.1, 10.0],
        vib_threshold=0.5,
    ) is True


def test_should_not_emergency_stop_normal_case():
    """Проверяем отсутствие аварийной остановки в нормальном режиме."""
    assert should_emergency_stop("low", []) is False
