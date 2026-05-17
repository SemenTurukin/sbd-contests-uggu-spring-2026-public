"""Доверенный автомат состояний миссии АБУ."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from src_solution.abu.tcb.domain import Domain
from src_solution.abu.tcb.event_log import EventLevel, trusted_event_log
from src_solution.abu.tcb.policies import DEFAULT_POLICY, SafetyPolicy
from src_solution.abu.tcb.safety import should_emergency_stop
from src_solution.abu.tcb.security_monitor import trusted_request


@dataclass
class MissionState:
    """Доверенное состояние миссии."""
    mission_id: str
    target_depth_m: float
    depth_m: float = 0.0
    rpm: float = 0.0
    torque_nm: float = 2000.0
    pressure: float = 120.0
    vibration_samples: list[float] = field(default_factory=list)
    status: str = "running"


class MissionController:
    """Контроллер миссии, принимающий только
    подтверждённые монитором изменения."""

    def __init__(self, policy: SafetyPolicy = DEFAULT_POLICY) -> None:
        self.policy = policy
        self.current: MissionState | None = None

    def start_mission(
        self,
        target_depth_m: float,
        max_rpm: float = 150.0,
    ) -> MissionState:
        response = trusted_request(
            Domain.DIGITAL_MINE,
            "start_mission",
            {
                "target_depth_m": target_depth_m,
                "depth_m": 0.0,
                "rpm": max_rpm,
            },
        )
        if not response.accepted:
            raise ValueError(response.reason)

        mission = MissionState(
            mission_id=str(uuid.uuid4()),
            target_depth_m=float(target_depth_m),
            rpm=min(float(max_rpm), self.policy.max_rpm),
        )
        self.current = mission
        trusted_event_log.record(
            EventLevel.INFO,
            f"mission_started id={mission.mission_id}",
        )
        return mission

    def tick(
        self,
        risk: str = "low",
        suggested_rpm: float = 150.0,
    ) -> MissionState:
        if self.current is None:
            raise RuntimeError("no active mission")

        mission = self.current
        if mission.status != "running":
            return mission

        next_depth = round(
            min(mission.depth_m + 0.5, mission.target_depth_m),
            2,
        )
        rpm = min(float(suggested_rpm), self.policy.max_rpm)

        response = trusted_request(
            Domain.OTHER,
            "mission_tick",
            {
                "target_depth_m": mission.target_depth_m,
                "depth_m": next_depth,
                "rpm": rpm,
            },
        )
        if not response.accepted:
            mission.status = "blocked"
            trusted_event_log.record(
                EventLevel.ERROR,
                f"mission_blocked reason={response.reason}",
            )
            return mission

        mission.depth_m = next_depth
        mission.rpm = rpm
        mission.torque_nm = 2000 + mission.depth_m * 30
        mission.pressure = 120 + mission.depth_m * 0.4
        mission.vibration_samples.append(
            0.1 + 0.05 * (mission.depth_m % 3),
        )

        if mission.depth_m >= mission.target_depth_m:
            mission.status = "completed"
            trusted_event_log.record(
                EventLevel.INFO,
                "mission_completed_target_depth",
            )
        elif should_emergency_stop(risk, mission.vibration_samples):
            mission.status = "emergency"
            trusted_event_log.record(
                EventLevel.CRITICAL,
                "emergency_stop_triggered",
            )
        else:
            trusted_event_log.record(
                EventLevel.INFO,
                f"mission_tick depth={mission.depth_m}",
            )

        return mission
