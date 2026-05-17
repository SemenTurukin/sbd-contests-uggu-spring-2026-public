"""Тесты недоверенных вспомогательных компонентов АБУ."""

from src_solution.abu.other.analytics import (
    anomaly_vibration,
    regime_suggest,
    risk_flag,
    smooth_vibration_window,
)
from src_solution.abu.other.numpy_workflow import (
    smooth_vibration_window as smooth_np,
)
from src_solution.abu.other.pseudo_ai import (
    anomaly_vibration as ai_anomaly,
    regime_suggest as ai_regime,
    risk_flag as ai_risk,
)


def test_numpy_workflow_empty_samples():
    """Проверяем обработку пустого окна вибрации."""
    assert smooth_np([]) == 0.0


def test_numpy_workflow_average_window():
    """Проверяем скользящее среднее по последним значениям."""
    assert smooth_np([1.0, 2.0, 3.0], window=2) == 2.5


def test_pseudo_ai_anomaly_empty_and_single():
    """Проверяем граничные случаи эвристики аномалии."""
    assert ai_anomaly([]) == 1.0
    assert ai_anomaly([0.5]) == 0.0


def test_pseudo_ai_anomaly_regular_window():
    """Проверяем расчёт аномалии на обычном окне."""
    value = ai_anomaly([0.1, 0.2, 0.3, 0.4, 0.9])
    assert 0.0 <= value <= 1.0


def test_pseudo_ai_regime_normal_and_high_torque():
    """Проверяем рекомендацию режима при обычном и высоком моменте."""
    rpm_normal, feed_normal = ai_regime(10.0, 2000.0)
    rpm_high_torque, feed_high_torque = ai_regime(10.0, 6000.0)

    assert rpm_normal > rpm_high_torque
    assert feed_normal == feed_high_torque


def test_pseudo_ai_risk_levels():
    """Проверяем уровни риска псевдо-ИИ."""
    assert ai_risk(0.1, 120.0, 10.0) == "low"
    assert ai_risk(0.8, 120.0, 10.0) == "medium"
    assert ai_risk(0.8, 200.0, 100.0) == "high"


def test_analytics_facade_reexports_functions():
    """Проверяем фасад аналитики."""
    assert anomaly_vibration([]) == 1.0
    assert regime_suggest(1.0, 1000.0)[0] > 0
    assert risk_flag(0.1, 120.0, 10.0) == "low"
    assert smooth_vibration_window([1.0, 2.0, 3.0]) == 2.0


def test_numpy_workflow_custom_window_larger_than_data():
    """Проверяем окно больше количества значений."""
    assert smooth_np([2.0, 4.0], window=10) == 3.0


def test_numpy_workflow_zero_window_uses_available_values():
    """Проверяем устойчивость при нулевом окне."""
    assert smooth_np([1.0, 2.0, 3.0], window=0) == 2.0


def test_pseudo_ai_regime_low_depth():
    """Проверяем рекомендацию режима на малой глубине."""
    rpm, feed = ai_regime(0.0, 1000.0)

    assert rpm > 0
    assert feed > 0


def test_pseudo_ai_regime_high_depth():
    """Проверяем рекомендацию режима на большой глубине."""
    rpm, feed = ai_regime(1000.0, 1000.0)

    assert rpm > 0
    assert feed > 0


def test_pseudo_ai_risk_high_by_vibration_only():
    """Проверяем высокий риск по вибрации."""
    assert ai_risk(1.0, 100.0, 10.0) in {"medium", "high"}


def test_pseudo_ai_risk_high_by_pressure_only():
    """Проверяем риск по давлению."""
    assert ai_risk(0.1, 100.0, 1000.0) in {"medium", "high"}


def test_analytics_facade_matches_pseudo_ai():
    """Проверяем, что фасад аналитики возвращает те же результаты."""
    samples = [0.1, 0.2, 0.3]

    assert anomaly_vibration(samples) == ai_anomaly(samples)
    assert risk_flag(0.1, 120.0, 10.0) == ai_risk(0.1, 120.0, 10.0)
