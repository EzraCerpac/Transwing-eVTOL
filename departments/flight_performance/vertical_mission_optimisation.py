from enum import Enum

import aerosandbox as asb
import aerosandbox.numpy as np
import pandas as pd

from data.concept_parameters.aircraft import AC
from departments.aerodynamics.cl_cd_polars import Aero
from model.airplane_models.rotating_wing import rot_wing
from sizing_tools.formula.aero import hover_thrust_from_power, rotor_disk_area
from sizing_tools.model import Model

ALPHA_i = 0


class OptParam(Enum):
    TIME = 'time'
    ENERGY = 'energy'
    MAX_POWER = 'maximum power'
    TRADE_OFF = 'time * energy'


# E423
class VerticalMissionProfileOptimization(Model):

    def __init__(self, aircraft: AC, opt_param: OptParam, n_timesteps=100):
        super().__init__(aircraft.data)
        self.parametric = aircraft.parametric
        aero = Aero(self.parametric,
                    altitude=self.aircraft.cruise_altitude,
                    velocity=self.aircraft.cruise_velocity)
        self.c_l_over_alpha_func = lambda alpha: aero.c_l_over_alpha_func(alpha
                                                                          )
        # self.aero = asb.AeroBuildup(
        #     airplane=self.parametric,
        #     op_point=asb.OperatingPoint(
        #         atmosphere=asb.Atmosphere(altitude=self.aircraft.cruise_altitude),
        #         velocity=self.aircraft.cruise_velocity,
        #         alpha=self.alpha,
        #     ),
        # ).run()

        self.opti = asb.Opti()
        self.opt_param = opt_param
        self.n_timesteps = n_timesteps

        self.init(self.vertical_constraints, self.vertical_dynamics)

    @property
    def necessary_parameters(self):
        return [
            'cruise_altitude',
            'range',
            # 'tbd'
        ]

    def init(self, constraint_func: callable, dynamic_func: callable):
        constraint_func()

        self.max_power = self.opti.variable(
            init_guess=self.aircraft.mission_profile.TAKEOFF.power / 2,
            log_transform=True,
            upper_bound=self.aircraft.mission_profile.TAKEOFF.power)
        self.opti.subject_to([
            self.max_power < self.aircraft.mission_profile.TAKEOFF.power,
            self.max_power > 100000,
        ])
        self.power_available = self.thrust_level * self.max_power
        disk_area = rotor_disk_area(self.aircraft.propeller_radius) * self.aircraft.motor_prop_count
        self.thrust = hover_thrust_from_power(self.power_available, disk_area, self.aircraft.figure_of_merit,
                                              self.dyn.op_point.atmosphere.density())
        dynamic_func()
        self.dyn.add_gravity_force()
        self.dyn.constrain_derivatives(self.opti, self.time)

        self.total_energy = np.sum(
            np.trapz(self.power_available) * np.diff(self.time))
        # self.opti.subject_to(
        #     self.total_energy <= self.aircraft.mission_profile.energy)

    def vertical_constraints(self):
        self.end_time = self.opti.variable(init_guess=100, log_transform=True, upper_bound=300)
        self.time = np.linspace(0, self.end_time, self.n_timesteps)
        self.trans_altitude = self.opti.parameter(value=100)
        self.dyn = asb.DynamicsPointMass1DVertical(
            mass_props=asb.MassProperties(mass=self.aircraft.total_mass,
                                          Ixx=1000,
                                          Iyy=500,
                                          Izz=500),
            z_e=self.opti.variable(init_guess=np.linspace(0, -self.trans_altitude, self.n_timesteps), upper_bound=0),
            w_e=self.opti.variable(init_guess=np.concatenate([np.linspace(0, -self.aircraft.rate_of_climb, self.n_timesteps // 2),
                                                                np.linspace(-self.aircraft.rate_of_climb, 0, self.n_timesteps - self.n_timesteps // 2)])),
        )
        self.thrust_level = self.opti.variable(init_guess=0.9,
                                               n_vars=self.n_timesteps,
                                               log_transform=True,
                                               upper_bound=1)
        self.opti.subject_to([
            self.dyn.altitude[0] == 0,
            self.dyn.altitude[-1] == self.trans_altitude,
            self.dyn.altitude >= 0,
            self.dyn.w_e[0] == 0,
            self.dyn.w_e <= 0,
            # self.dyn.w_e[-1] >= -2,
            self.end_time < 30,
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

    def vertical_dynamics(self, use_aero: bool = False):
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

    def run(self, max_iter: int = 1000, verbose: bool = True):
        opt_param = {
            OptParam.TIME: self.end_time,
            OptParam.ENERGY: self.total_energy,
            OptParam.MAX_POWER: self.max_power,
            OptParam.TRADE_OFF: self.time[-1] * self.total_energy,
        }[self.opt_param]
        # Optimize
        self.opti.minimize(opt_param)

        # Post-process
        sol = self.opti.solve(verbose=verbose,
                              max_iter=max_iter,
                              behavior_on_failure='return_last')
        self.time = sol(self.time)
        self.dyn = sol(self.dyn)
        self.thrust_level = sol(self.thrust_level)
        self.max_power = sol(self.max_power)
        self.power_available = sol(self.power_available)
        self.thrust = sol(self.thrust)
        self.total_energy = sol(self.total_energy)
        # self.CL = sol(self.CL)
        print(f"\nOptimized for {self.opt_param.value}:")
        print(f"Total energy: {self.total_energy / 3600000:.1f} kWh")
        print(f"Total time: {self.time[-1]:.1f} s")
        print(f"Max power: {self.max_power / 1000:.1f} kW")

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame({
            'time':
                self.time,
            'x':
                self.dyn.x_e,
            'z':
                self.dyn.z_e,
            'speed':
                self.dyn.speed,
            'gamma':
                self.dyn.gamma,
            'alpha':
                self.dyn.alpha,
            'horizontal speed':
                self.dyn.u_e,
            'vertical speed':
                self.dyn.w_e,
            # 'C_L':
            #     self.CL,
            'altitude':
                -self.dyn.z_e,
            'energy altitude':
                self.dyn.op_point.energy_altitude(),
            'power':
                self.power_available,
            'thrust':
                self.thrust,
            'thrust_level':
                self.thrust_level,
        })


if __name__ == '__main__':
    from departments.flight_performance.plots import *

    ac = rot_wing
    ac.data.v_stall = 20.
    ac.data.wing.area = 16
    mission_profile_optimization = VerticalMissionProfileOptimization(
        ac, opt_param=OptParam.MAX_POWER, n_timesteps=80)
    mission_profile_optimization.run(max_iter=1000)

    df = mission_profile_optimization.to_dataframe()
    # print(df.to_string())
    # plot_step_density(df)
    plot_over_distance_vertical(df)
    plot_over_time_vertical(df)
