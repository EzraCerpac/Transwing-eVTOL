from enum import Enum

import aerosandbox as asb
import aerosandbox.numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import AC
from departments.aerodynamics.cl_cd_polars import CLCDPolar
from departments.flight_performance.mission_optimalisation.optimalisation import Optimalisation, OptParam
from aircraft_models import trans_wing
from sizing_tools.formula.aero import hover_thrust_from_power, rotor_disk_area
from sizing_tools.model import Model

ALPHA_i = 0


# E423
class VerticalDescent(Optimalisation):

    def __init__(self, aircraft: AC, opt_param: OptParam, *args, **kwargs):
        aero = CLCDPolar(aircraft.parametric_fn(1),
                         altitude=aircraft.data.cruise_altitude,
                         velocity=aircraft.data.cruise_velocity)
        self.c_l_over_alpha_func = lambda alpha: aero.c_l_over_alpha_func(alpha
                                                                          )
        super().__init__(aircraft, opt_param, *args, **kwargs)
        self.parametric = aircraft.parametric_fn(1)

    def init(self):
        self.constraints()

        self.max_power = self.opti.variable(
            init_guess=self.aircraft.mission_profile.vertical_climb.state.power,
            log_transform=True,
)
        self.opti.subject_to([
            # self.max_power < self.aircraft.mission_profile.TAKEOFF.power,
            self.max_power > 100000,
            self.max_power < 300000,
        ])
        self.power = self.thrust_level * self.max_power
        disk_area = rotor_disk_area(
            self.aircraft.propeller_radius) * self.aircraft.motor_prop_count
        self.thrust = hover_thrust_from_power(
            self.power, disk_area, self.aircraft.figure_of_merit,
            self.dyn.op_point.atmosphere.density())

        self.dynamics()
        self.dyn.add_gravity_force()
        self.dyn.constrain_derivatives(self.opti, self.time)

        self.total_energy = np.sum(
            np.trapz(self.power) * np.diff(self.time))
        # self.opti.subject_to(
        #     self.total_energy <= self.aircraft.mission_profile.energy)

    def constraints(self):
        self.end_time = self.opti.variable(init_guess=100,
                                           log_transform=True,
                                           upper_bound=300)
        self.time = np.linspace(0, self.end_time, self.n_timesteps)
        self.trans_altitude = self.opti.parameter(value=100)
        self.dyn = asb.DynamicsPointMass1DVertical(
            mass_props=asb.MassProperties(mass=self.aircraft.total_mass,
                                          Ixx=1000,
                                          Iyy=500,
                                          Izz=500),
            z_e=self.opti.variable(init_guess=np.linspace(
                -self.trans_altitude, 0, self.n_timesteps),
                                   upper_bound=0),
            w_e=self.opti.variable(init_guess=np.concatenate([
                np.linspace(0, self.aircraft.rate_of_climb,
                            self.n_timesteps // 2),
                np.linspace(self.aircraft.rate_of_climb, 0, self.n_timesteps -
                            self.n_timesteps // 2)
            ])),
        )
        self.thrust_level = self.opti.variable(init_guess=0.9,
                                               n_vars=self.n_timesteps,
                                               log_transform=True,
                                               upper_bound=1)
        self.opti.subject_to([
            self.dyn.altitude[0] == self.trans_altitude,
            self.dyn.altitude[-1] == 0,
            self.dyn.altitude >= 0,
            self.dyn.w_e[0] == 0,
            self.dyn.w_e >= 0,
            self.dyn.w_e[-1] < 0.5,
            # self.dyn.w_e[-1] >= -2,
            self.end_time < 60,
            # self.thrust_level[0] == 1e-8,
            self.thrust_level < 1,
            # self.thrust_level[-1] == 0.9,
        ])

        a_v = np.diff(self.dyn.w_e) / np.diff(self.time)
        self.opti.subject_to([
            a_v <= 2,
            a_v >= -2,
            # np.diff(self.thrust_level) < 0.01,
            # np.diff(self.thrust_level) > -0.01,
        ])
        self.opti.subject_to([
            # np.diff(self.dyn.speed) < 2,
            # np.diff(self.dyn.speed) > -2,
            # np.diff(self.dyn.alpha) < 1,
            # np.diff(self.dyn.alpha) > -1,
            # np.diff(self.dyn.gamma) < .1,
            # np.diff(self.dyn.gamma) > .1,
        ])

    def dynamics(self, use_aero: bool = False):
        if use_aero:
            raise NotImplementedError
        else:
            pass
            # CD = 0.028
            # drag = self.dyn.op_point.dynamic_pressure(
            # ) * self.aircraft.wing.area * CD
            # self.dyn.add_force(
            #     Fx=0,
            #     Fz=0,
            #     axes='wind',
            # )

        self.dyn.add_force(Fz=-self.thrust)

    def plot_over_distance(self) -> tuple[plt.Figure, plt.Axes]:
        raise TypeError(
            "1D vertical optimization does not have a distance axis")

    def plot_logs_over_distance(self) -> tuple[plt.Figure, plt.Axes]:
        raise TypeError(
            "1D vertical optimization does not have a distance axis")


if __name__ == '__main__':
    ac = trans_wing
    mission_profile_optimization = VerticalDescent(ac,
                                               opt_param=OptParam.ENERGY,
                                               n_timesteps=501,
                                               max_iter=1000,
                                               n_logs=100)
    mission_profile_optimization.run()

    df = mission_profile_optimization.to_dataframe()
    # print(df.to_string())
    mission_profile_optimization.plot_over_time()
    # mission_profile_optimization.plot_logs_over_time()
    mission_profile_optimization.save_data()

    mission_profile_optimization.plot_alt_and_thrust_over_time()
