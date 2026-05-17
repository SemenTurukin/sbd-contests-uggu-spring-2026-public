from pathlib import Path

from src_solution.abu.tcb.event_log import EventLevel, EventLog


def test_solution_event_log_ring_and_tail(tmp_path: Path):
    log = EventLog(tmp_path, ring_size=2)
    log.record(EventLevel.INFO, "one")
    log.record(EventLevel.WARNING, "two")
    log.record(EventLevel.ERROR, "three")
    ring = log.ring_snapshot()
    assert len(ring) == 2
    assert "two" in ring[0]
    assert "three" in ring[1]
    assert "one" in log.read_full_tail()


def test_solution_event_log_sanitizes_multiline(tmp_path: Path):
    log = EventLog(tmp_path)
    log.record(EventLevel.CRITICAL, "bad\nline")
    assert "bad line" in log.read_full_tail()
