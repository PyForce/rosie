from rosie.motion.models import PIDHistory, SpeedControl

RESTING_PID = PIDHistory(0.0, 0.0, 0.0)


def pid(
    gains: SpeedControl, max_power: float, history: PIDHistory, error: float
) -> tuple[float, PIDHistory]:
    """
    One step of the incremental speed PID: the power for one motor, from -max_power to
    max_power, and what the next step needs to know.
    """
    if gains.ki == 0:
        action = error * gains.kc
    else:
        action = error * gains.kc + (gains.ki - gains.kc) * history.error_1 + history.action_1

    if gains.kd != 0:
        action = (
            gains.kc * (error - history.error_1)
            + gains.ki * error
            + history.action_1
            + gains.kd * (error - 2 * history.error_1 + history.error_2)
        )

    action = min(max(action, -max_power), max_power)
    return action, PIDHistory(error_1=error, error_2=history.error_1, action_1=action)
