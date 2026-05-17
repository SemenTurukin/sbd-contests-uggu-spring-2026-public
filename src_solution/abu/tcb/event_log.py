"""Доверенный журнал событий безопасности АБУ."""

from __future__ import annotations

import threading
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path


class EventLevel(str, Enum):
    """Уровень важности события аудита."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventLog:
    """Полный журнал событий и ограниченный кольцевой буфер."""

    def __init__(
        self,
        log_dir: Path | None = None,
        ring_size: int = 10,
    ) -> None:
        self._dir = log_dir or Path.cwd() / "var" / "abu_solution_logs"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._full_path = self._dir / "abu_events_full.log"
        self._ring_path = self._dir / "abu_events_ring.txt"
        self._ring: deque[str] = deque(maxlen=max(1, ring_size))
        self._lock = threading.Lock()

    def record(self, level: EventLevel, message: str) -> None:
        """Записывает событие в память и на диск."""
        safe_message = message.replace("\n", " ").replace("\r", " ")
        ts = datetime.now(timezone.utc).isoformat()
        line = f"{ts}\t{level.value}\t{safe_message}"
        with self._lock:
            self._ring.append(line)
            with self._full_path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
            self._ring_path.write_text(
                "".join(f"{item}\n" for item in self._ring),
                encoding="utf-8",
            )

    def ring_snapshot(self) -> list[str]:
        """Возвращает текущие строки кольцевого буфера."""
        with self._lock:
            return list(self._ring)

    def read_full_tail(self, max_lines: int = 500) -> str:
        """Возвращает последние строки полного журнала."""
        if not self._full_path.is_file():
            return ""
        lines = self._full_path.read_text(encoding="utf-8").splitlines()
        return "\n".join(lines[-max(1, max_lines):])


trusted_event_log = EventLog()
