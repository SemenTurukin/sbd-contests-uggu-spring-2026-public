"""Доверенные политики безопасности для АБУ."""

from __future__ import annotations

from dataclasses import dataclass, field

from src_solution.abu.tcb.domain import Domain


@dataclass(frozen=True)
class SafetyPolicy:
    """Ограничения, применяемые доверенной вычислительной базой."""
    max_depth_m: float = 200.0
    max_rpm: float = 300.0
    emergency_vibration_threshold: float = 0.9
    allowed_actions: frozenset[str] = frozenset(
        {
            "health",
            "start_mission",
            "mission_tick",
            "ai_suggest",
            "status",
        }
    )
    allowed_edges: frozenset[tuple[Domain, Domain]] = field(
        default_factory=lambda: frozenset(
            {
                (Domain.OTHER, Domain.TCB),
                (Domain.DIGITAL_MINE, Domain.TCB),
                (Domain.REGULATOR, Domain.TCB),
                (Domain.TCB, Domain.OTHER),
            }
        )
    )


DEFAULT_POLICY = SafetyPolicy()
