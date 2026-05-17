"""Недоверенные эвристики псевдо-ИИ.

Модуль находится вне. Его рекомендации не применяются напрямую:
они должны проходить через доверенные политики и монитор безопасности.
"""

from __future__ import annotations

from typing import Literal

RiskLevel = Literal["low", "medium", "high"]


def anomaly_vibration(samples: list[float]) -> float:
    """Оценивает аномалию вибрации в недоверенном аналитическом домене."""
    if not samples:
        return 1.0
    if len(samples) == 1:
        return 0.0
    window = samples[-5:]
    mean = sum(window) / len(window)
    spread = max(abs(x - mean) for x in window) or 1e-9
    raw = abs(window[-1] - mean) / spread
    return max(0.0, min(1.0, raw))


def regime_suggest(depth_m: float, torque_nm: float) -> tuple[float, float]:
    """Рекомендует обороты и подачу;
    результат всё равно проверяется монитором."""
    rpm = 120.0 + min(float(depth_m) * 2.0, 80.0)
    if float(torque_nm) > 5000:
        rpm *= 0.85
    feed = 0.2 + min(float(depth_m) * 0.01, 0.15)
    return round(rpm, 1), round(feed, 3)


def risk_flag(vibration: float, pressure: float, depth_m: float) -> RiskLevel:
    """Недоверенная классификация риска;
    ДВБ воспринимает результат только как входные данные."""
    score = 0
    if vibration > 0.75:
        score += 2
    if pressure > 180.0:
        score += 2
    if depth_m > 95.0:
        score += 1
    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"
