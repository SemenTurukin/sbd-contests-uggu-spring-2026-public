"""Доверенные проверки безопасности."""

from __future__ import annotations

RiskLevel = str


def clamp_non_negative(value: float) -> float:
    """Нормализует отрицательные значения телеметрии
    до безопасного неотрицательного значения."""
    return max(0.0, float(value))


def enforce_depth_cap(depth_m: float, max_depth_m: float) -> bool:
    """Возвращает True, если текущая глубина находится в доверенном пределе."""
    return clamp_non_negative(depth_m) <= float(max_depth_m)


def enforce_rpm_cap(rpm: float, max_rpm: float) -> bool:
    return clamp_non_negative(rpm) <= float(max_rpm)


def anomaly_vibration(samples: list[float]) -> float:
    """Выполняет простую доверенную проверку аномалии вибрации"""
    if not samples:
        return 1.0
    if len(samples) == 1:
        return 0.0
    window = [float(x) for x in samples[-5:]]
    mean = sum(window) / len(window)
    spread = max(abs(x - mean) for x in window) or 1e-9
    raw = abs(window[-1] - mean) / spread
    return max(0.0, min(1.0, raw))


def should_emergency_stop(
    risk: RiskLevel,
    vib_samples: list[float],
    vib_threshold: float = 0.9,
) -> bool:
    """Возвращает True, если требуется доверенная
    варийная остановка."""
    if risk == "high":
        return True
    return (
        bool(vib_samples)
        and anomaly_vibration(vib_samples) >= vib_threshold
    )
