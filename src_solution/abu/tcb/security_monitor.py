"""Доверенный монитор безопасности, контролирующий все доменные вызовы АБУ."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src_solution.abu.tcb.domain import (
    Domain,
    DomainRequest,
    DomainResponse,
)

from src_solution.abu.tcb.event_log import (
    EventLevel,
    EventLog,
    trusted_event_log,
)

from src_solution.abu.tcb.policies import (
    DEFAULT_POLICY,
    SafetyPolicy,
)

from src_solution.abu.tcb.safety import (
    enforce_depth_cap,
    enforce_rpm_cap,
)


@dataclass
class SecurityMonitor:
    """Точка применения политик для доверенных и недоверенных доменов."""

    policy: SafetyPolicy = DEFAULT_POLICY
    event_log: EventLog = trusted_event_log

    def mediate(self, request: DomainRequest) -> DomainResponse:
        """Проверяет междоменный запрос и возвращает доверенный ответ."""
        if (request.source, request.target) not in self.policy.allowed_edges:
            self.event_log.record(
                EventLevel.ERROR,
                f"domain_violation source={request.source} target={request.target}",
            )
            return DomainResponse(False, "domain_violation")
        if request.action not in self.policy.allowed_actions:
            self.event_log.record(
                EventLevel.WARNING,
                f"policy_violation action={request.action}",
            )
            return DomainResponse(False, "action_not_allowed")
        if request.action in {"start_mission", "mission_tick"}:
            return self._validate_mission_payload(request.payload)
        self.event_log.record(EventLevel.INFO, f"request_allowed action={request.action}")
        return DomainResponse(True, "allowed", dict(request.payload))

    def _validate_mission_payload(self, payload: dict[str, Any]) -> DomainResponse:
        depth = float(payload.get("depth_m", 0.0))
        target = float(payload.get("target_depth_m", self.policy.max_depth_m))
        rpm = float(payload.get("rpm", 0.0))
        if target > self.policy.max_depth_m or depth > self.policy.max_depth_m:
            self.event_log.record(EventLevel.ERROR, "depth_policy_violation")
            return DomainResponse(False, "depth_policy_violation")
        if not enforce_depth_cap(depth, target + 1e-6):
            self.event_log.record(EventLevel.ERROR, "depth_cap_violation")
            return DomainResponse(False, "depth_cap_violation")
        if not enforce_rpm_cap(rpm, self.policy.max_rpm):
            self.event_log.record(EventLevel.ERROR, "rpm_policy_violation")
            return DomainResponse(False, "rpm_policy_violation")
        self.event_log.record(EventLevel.INFO, "mission_payload_allowed")
        return DomainResponse(True, "allowed", dict(payload))


def trusted_request(
    source: Domain,
    action: str,
    payload: dict[str, Any] | None = None,
) -> DomainResponse:
    monitor = SecurityMonitor()
    request = DomainRequest(source, Domain.TCB, action, payload or {})
    return monitor.mediate(request)
