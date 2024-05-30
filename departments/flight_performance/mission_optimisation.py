import aerosandbox as asb
import aerosandbox.numpy as np
import casadi
import pandas as pd

from data.concept_parameters.aircraft import Aircraft
from departments.flight_performance.mission_profile import Phase
from departments.flight_performance.power_calculations import power, power_required, acceleration_power
from sizing_tools.model import Model


class MissionProfileOptimization(Model):
    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)
        self.n_timesteps = 100
        self.opti = asb.Opti()
        self.init_phase_variables(Phase.CLIMB, 0)
        self.set_constraints(Phase.CLIMB)

    @property
    def necessary_parameters(self):
        return [
            'cruise_altitude',
            'range',
            # 'tbd'
        ]

    def init_phase_variables(self, phase: Phase, start_time):
        self.end_final = self.opti.variable(init_guess=start_time + 50, lower_bound=start_time+1, upper_bound=10000)
        self.time = np.linspace(start_time, self.end_final, self.n_timesteps)

        self.x = self.opti.variable(init_guess=np.linspace(0, ac.range, self.n_timesteps), lower_bound=0)
        self.y = self.opti.variable(init_guess=np.zeros(self.n_timesteps), lower_bound=0)
        self.v_x = self.opti.derivative_of(self.x, with_respect_to=self.time, derivative_init_guess=1)
        self.v_y = self.opti.derivative_of(self.y, with_respect_to=self.time, derivative_init_guess=0)
        self.a_x = self.opti.derivative_of(self.v_x, with_respect_to=self.time, derivative_init_guess=0)
        self.a_y = self.opti.derivative_of(self.v_y, with_respect_to=self.time, derivative_init_guess=0)

        self.power_required = power_required(phase, self.aircraft, self.v_x, self.v_y, self.y)
        self.acceleration_power = acceleration_power(self.a_x, self.a_y, self.v_x, self.v_y, self.aircraft.total_mass)
        self.total_power = self.power_required #+ self.acceleration_power
        self.total_energy = np.sum(np.trapz(self.total_power) * np.diff(self.time))

    def set_constraints(self, phase: Phase):
        self.opti.subject_to([
            self.v_x >= 0,
        ])
        match phase:
            case phase.VERTICAL_CLIMB:
                self.opti.subject_to([
                    self.v_y >= 0,
                ])
            case phase.CLIMB:
                self.opti.subject_to([
                    self.x[0] == 0,
                    self.y[0] == 0,  # tbchanged
                    self.y[-1] == self.aircraft.cruise_altitude,
                    self.v_x[0] == self.aircraft.v_stall,
                    self.v_x[-1] == self.aircraft.cruise_velocity,
                    # self.a_y == 0,
                ])

        # self.opti.subject_to([
        #     self.horizontal_speeds[int(Phase.TAKEOFF)] == 0,
        #     self.vertical_speeds[int(Phase.TAKEOFF)] == 0,
        #     self.horizontal_speeds[int(Phase.LANDING)] == 0,
        #     self.vertical_speeds[int(Phase.LANDING)] == 0,
        #     self.horizontal_speeds[int(Phase.HOVER)] == 0,
        #     self.vertical_speeds[int(Phase.HOVER)] == 0,
        #     self.vertical_speeds[int(Phase.VERTICAL_CLIMB)] >= 0,
        #     self.horizontal_speeds[int(Phase.VERTICAL_CLIMB)] == 0,
        #     self.vertical_speeds[int(Phase.VERTICAL_DESCENT)] <= 0,
        #     self.vertical_speeds[int(Phase.CLIMB)] >= 0,
        #     self.vertical_speeds[int(Phase.CRUISE)] == 0,
        #     self.vertical_speeds[int(Phase.DESCENT)] <= 0,
        # ])
        #
        # self.opti.subject_to([
        #     self.altitudes[0] == 0,
        #     self.altitudes[-1] == 0,
        #     self.altitudes[int(Phase.CLIMB)] == self.aircraft.cruise_altitude,
        #     self.altitudes[int(Phase.CRUISE)] == self.aircraft.cruise_altitude,
        # ])
        #
        # self.opti.subject_to([
        #     self.distances[0] == 0,
        #     self.distances[-1] == self.aircraft.range,
        # ])



    def run(self, verbose=True):
        # Optimize
        self.opti.minimize(self.total_energy)

        # Post-process
        try:
            sol = self.opti.solve(verbose=verbose)
            self.time = sol(self.time)
            self.x = sol(self.x)
            self.y = sol(self.y)
            self.v_x = sol(self.v_x)
            self.v_y = sol(self.v_y)
            self.a_x = sol(self.a_x)
            self.a_y = sol(self.a_y)
            self.power_required = sol(self.power_required)
            self.acceleration_power = sol(self.acceleration_power)
            self.total_power = sol(self.total_power)
            self.total_energy = sol(self.total_energy)
        except Exception as e:
            print(e)
            self.time = self.opti.debug.value(self.time)
            self.x = self.opti.debug.value(self.x)
            self.y = self.opti.debug.value(self.y)
            self.v_x = self.opti.debug.value(self.v_x)
            self.v_y = self.opti.debug.value(self.v_y)
            self.a_x = self.opti.debug.value(self.a_x)
            self.a_y = self.opti.debug.value(self.a_y)
            self.power_required = self.opti.debug.value(self.power_required)
            self.acceleration_power = self.opti.debug.value(self.acceleration_power)
            self.total_power = self.opti.debug.value(self.total_power)
            self.total_energy = self.opti.debug.value(self.total_energy)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame({
            'Time [s]': self.time,
            'Distance [m]': self.x,
            'Altitude [m]': self.y,
            'Horizontal Speed [m/s]': self.v_x,
            'Vertical Speed [m/s]': self.v_y,
            'Horizontal Acceleration [m/s2]': self.a_x,
            'Vertical acceleration [m/s2]': self.a_y,
            'power_required': self.power_required,
            'acceleration_power': self.acceleration_power,
            'Power [W]': self.total_power,
        })

if __name__ == '__main__':
    from departments.flight_performance.plots import *
    ac = Aircraft.load()
    mission_profile_optimization = MissionProfileOptimization(ac)
    mission_profile_optimization.run()

    df = mission_profile_optimization.to_dataframe()
    print(df.to_string())
    # plot_per_phase(df)
    plot_over_distance(df)
