from src_solution.abu.tcb.mission_control import MissionController
from src_solution.abu.tcb.placeholder import tcb_health


def test_tcb_health():
    assert tcb_health() == "ok"


def test_mission_controller_completes_short_mission():
    controller = MissionController()
    mission = controller.start_mission(1.0, 120.0)
    assert mission.status == "running"
    controller.tick(risk="low", suggested_rpm=120.0)
    mission = controller.tick(risk="low", suggested_rpm=120.0)
    assert mission.status == "completed"
    assert mission.depth_m == 1.0


def test_mission_controller_blocks_unsafe_start():
    controller = MissionController()
    try:
        controller.start_mission(1000.0, 120.0)
    except ValueError as exc:
        assert "depth" in str(exc)
    else:
        raise AssertionError("unsafe mission must be blocked")
