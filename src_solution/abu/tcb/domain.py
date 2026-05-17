"""Объекты запроса и ответа для контроля доменных границ АБУ."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Domain(str, Enum):
    """Домены выполнения АБУ."""
    TCB = "tcb"
    OTHER = "other"
    DIGITAL_MINE = "digital_mine"
    REGULATOR = "regulator"


@dataclass(frozen=True)
class DomainRequest:
    """Запрос, пересекающий доменную границу безопасности АБУ."""
    source: Domain
    target: Domain
    action: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DomainResponse:
    """Ответ, сформированный доверенным монитором."""
    accepted: bool
    reason: str
    payload: dict[str, Any] = field(default_factory=dict)
