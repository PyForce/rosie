from rosie.control.regulation import go_to_point
from rosie.models import Pose, Wheels

WHEELS = Wheels(radius=0.05, distance=0.3, encoder_steps=360, max_speed=10.0)


def test_backs_up_onto_a_target_behind() -> None:
    left, right = go_to_point(Pose(0, 0, 0), Pose(-1, 0, 0), WHEELS)
    assert left == right < 0
