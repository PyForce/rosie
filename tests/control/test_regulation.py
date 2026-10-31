from rosie.control.regulation import go_to_point
from rosie.models import Pose, RegulationGains, Wheels

WHEELS = Wheels(radius=0.05, separation=0.3, encoder_resolution=360, max_speed=10.0)


def test_backs_up_onto_a_target_behind() -> None:
    left, right = go_to_point(Pose(0, 0, 0), Pose(-1, 0, 0), WHEELS, RegulationGains())
    assert left == right < 0
