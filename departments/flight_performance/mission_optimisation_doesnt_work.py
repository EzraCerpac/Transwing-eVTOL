from dataclasses import dataclass

import aerosandbox as asb
import aerosandbox.numpy as np
import casadi

opti = asb.Opti()

@dataclass
class MissionPhase:
    duration: float | casadi.MX
    horizontal_speed: float | casadi.MX
    vertical_speed: float | casadi.MX

@dataclass
class MissionProfile:
    # startup: MissionPhase(1, 0, 0)
    takeoff = MissionPhase(1, 0, 0)
    vertical_climb = MissionPhase(
        duration=opti.variable(10, lower_bound=0),
        horizontal_speed=opti.variable(0, lower_bound=0),
        vertical_speed=opti.variable(10, lower_bound=0),
    )
    transition1 = MissionPhase(
        duration=opti.variable(10, lower_bound=0),
        horizontal_speed=opti.variable(0, lower_bound=0),
        vertical_speed=opti.variable(0),
    )
    climb = MissionPhase(
        duration=opti.variable(10, lower_bound=0),
        horizontal_speed=opti.variable(10, lower_bound=0),
        vertical_speed=opti.variable(10, lower_bound=0),
    )
    cruise = MissionPhase(
        duration=opti.variable(100, lower_bound=0),
        horizontal_speed=opti.variable(50, lower_bound=0),
        vertical_speed=0,
    )
    descent = MissionPhase(
        duration=opti.variable(10, lower_bound=0),
        horizontal_speed=opti.variable(10, lower_bound=0),
        vertical_speed=opti.variable(10, upper_bound=0),
    )
    transition2 = MissionPhase(
        duration=opti.variable(10, lower_bound=0),
        horizontal_speed=opti.variable(0, lower_bound=0),
        vertical_speed=opti.variable(0),
    )
    hover = MissionPhase(
        duration=opti.variable(0, lower_bound=0),
        horizontal_speed=opti.variable(0),
        vertical_speed=0,
    )
    vertical_descent = MissionPhase(
        duration=opti.variable(10, lower_bound=0),
        horizontal_speed=0,
        vertical_speed=opti.variable(10, upper_bound=0),
    )
    landing = MissionPhase(1, 0, 0)

    def __post_init__(self):
        self.phases = [
            self.takeoff,
            self.vertical_climb,
            self.transition1,
            self.climb,
            self.cruise,
            self.descent,
            self.transition2,
            self.hover,
            self.vertical_descent,
            self.landing,
        ]

def mission_profile_objective(mission_profile: MissionProfile):
    return sum(
        phase.duration
        for phase in mission_profile.phases
    )

mission_profile = MissionProfile()
objective = mission_profile_objective(mission_profile)

opti.minimize(objective)
sol = opti.solve()
print(sol(objective))
for phase in mission_profile.phases:
    phase_vars = [var for var in [phase.duration, phase.horizontal_speed, phase.vertical_speed] if isinstance(var, casadi.MX)]
    phase_values = sol.value(phase_vars)
    print(*phase_values)