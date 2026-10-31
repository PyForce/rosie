from rosie.hardware.drive.models import PIDState
from rosie.models import PIDGains

RESTING_PID = PIDState(error_1=0.0, error_2=0.0, power=0.0)


def regulate_speed(
    gains: PIDGains, max_power: float, state: PIDState, error: float
) -> tuple[float, PIDState]:
    """
    One step of the incremental speed PID: the power for one motor changes by
    kc (e - e₋₁) + ki e + kd (e - 2 e₋₁ + e₋₂), within -max_power and max_power.
    Also what the next step needs to know.
    """
    power = (
        gains.kc * (error - state.error_1)
        + gains.ki * error
        + state.power
        + gains.kd * (error - 2 * state.error_1 + state.error_2)
    )
    power = min(max(power, -max_power), max_power)
    return power, PIDState(error_1=error, error_2=state.error_1, power=power)
