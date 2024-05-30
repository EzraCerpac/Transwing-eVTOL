import aerosandbox as asb
import aerosandbox.numpy as np
import casadi
import pandas as pd

from data.concept_parameters.aircraft import Aircraft
from departments.flight_performance.mission_profile import Phase
from departments.flight_performance.power_calculations import power
from sizing_tools.model import Model


class MissionProfileOptimization(Model):

    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)
        self.opti = asb.Opti()
        self.init_variables()
        self.set_constraints()

    @property
    def necessary_parameters(self):
        return [
            'cruise_altitude',
            'range',
            # 'tbd'
        ]

    def init_variables(self):
        n_vars = len(Phase)
        self.durations = self.opti.variable(init_guess=10,
                                            n_vars=n_vars,
                                            lower_bound=0)
        self.horizontal_speeds = self.opti.variable(init_guess=10,
                                                    n_vars=n_vars,
                                                    lower_bound=0,
                                                    upper_bound=100)
        self.vertical_speeds = self.opti.variable(init_guess=0,
                                                  n_vars=n_vars,
                                                  lower_bound=-100,
                                                  upper_bound=100)
        self.altitudes = casadi.cumsum(self.vertical_speeds * self.durations)
        self.distances = casadi.cumsum(self.horizontal_speeds * self.durations)
        self.powers = np.array([
            power(phase, self.aircraft, horizontal_speed, vertical_speed,
                  altitude)
            for phase, horizontal_speed, vertical_speed, altitude in zip(
                Phase, self.horizontal_speeds.nz, self.vertical_speeds.nz,
                self.altitudes.nz)
        ])
        self.energies = self.powers * self.durations
        self.total_energy = np.sum(self.energies)

    def set_constraints(self):
        self.opti.subject_to([
            self.horizontal_speeds[int(Phase.TAKEOFF)] == 0,
            self.vertical_speeds[int(Phase.TAKEOFF)] == 0,
            self.horizontal_speeds[int(Phase.LANDING)] == 0,
            self.vertical_speeds[int(Phase.LANDING)] == 0,
            self.horizontal_speeds[int(Phase.HOVER)] == 0,
            self.vertical_speeds[int(Phase.HOVER)] == 0,
            self.vertical_speeds[int(Phase.VERTICAL_CLIMB)] >= 0,
            self.horizontal_speeds[int(Phase.VERTICAL_CLIMB)] == 0,
            self.vertical_speeds[int(Phase.VERTICAL_DESCENT)] <= 0,
            self.vertical_speeds[int(Phase.CLIMB)] >= 0,
            self.vertical_speeds[int(Phase.CRUISE)] == 0,
            self.vertical_speeds[int(Phase.DESCENT)] <= 0,
        ])

        self.opti.subject_to([
            self.altitudes[0] == 0,
            self.altitudes[-1] == 0,
            self.altitudes[int(Phase.CLIMB)] == self.aircraft.cruise_altitude,
            self.altitudes[int(Phase.CRUISE)] == self.aircraft.cruise_altitude,
        ])

        self.opti.subject_to([
            self.distances[0] == 0,
            self.distances[-1] == self.aircraft.range,
        ])

    def run(self, verbose=True):
        # Optimize
        self.opti.minimize(self.total_energy)

        # Post-process
        try:
            sol = self.opti.solve(verbose=verbose)
            self.durations = sol.value(self.durations)
            self.horizontal_speeds = sol.value(self.horizontal_speeds)
            self.vertical_speeds = sol.value(self.vertical_speeds)
            self.altitudes = sol.value(self.altitudes)
            self.distances = sol.value(self.distances)
            self.powers = sol.value(self.powers)
            self.energies = sol.value(self.energies)
            self.total_energy = sol.value(self.total_energy)
        except Exception as e:
            print(e)
            self.durations = self.opti.debug.value(self.durations)
            self.horizontal_speeds = self.opti.debug.value(
                self.horizontal_speeds)
            self.vertical_speeds = self.opti.debug.value(self.vertical_speeds)
            self.altitudes = self.opti.debug.value(self.altitudes)
            self.distances = self.opti.debug.value(self.distances)
            self.powers = self.opti.debug.value(self.powers)
            self.energies = self.opti.debug.value(self.energies)
            self.total_energy = self.opti.debug.value(self.total_energy)

    def to_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame({
            "Phase": [phase.name for phase in Phase],
            "Duration [s]": self.durations,
            "Horizontal Speed [m/s]": self.horizontal_speeds,
            "Vertical Speed [m/s]": self.vertical_speeds,
            "Altitude [m]": self.altitudes,
            "Distance [m]": self.distances,
            "Power [W]": self.powers,
            "Energy [J]": self.energies,
        })
        return df


if __name__ == '__main__':
    from departments.flight_performance.plots import *
    ac = Aircraft.load()
    mission_profile_optimization = MissionProfileOptimization(ac)
    mission_profile_optimization.run()
    df = mission_profile_optimization.to_dataframe()
    print(df.to_string())
    plot_per_phase(df)
    plot_over_distance(df)
