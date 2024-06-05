from enum import Enum

import aerosandbox as asb
import aerosandbox.numpy as np
import pandas as pd

from data.concept_parameters.aircraft import AC
from departments.aerodynamics.cl_cd_polars import Aero
from model.airplane_models.rotating_wing import rot_wing
from sizing_tools.formula.aero import C_D_from_CL
from sizing_tools.model import Model

ALPHA_i = 0


class OptParam(Enum):
    TIME = 'time'
    ENERGY = 'energy'
    MAX_POWER = 'maximum power'
    TRADE_OFF = 'time * energy'


# E423
class MissionProfileOptimization(Model):

    def __init__(self, aircraft: AC, opt_param: OptParam, n_timesteps=100):
        super().__init__(aircraft.data)
        self.parametric = aircraft.parametric

        self.opti = asb.Opti()
        self.opt_param = opt_param
        self.n_timesteps = n_timesteps

        self.init(self.horizontal_constraints, self.horizontal_dynamics)
        # self.init(self.vertical_constraints, self.init_vertical_dynamics)

    @property
    def necessary_parameters(self):
        return [
            'cruise_altitude',
            'range',
            # 'tbd'
        ]

    def init(self, constraint_func: callable, dynamic_func: callable):
        self.end_time = self.opti.variable(init_guess=2000, log_transform=True)

        constraint_func()

        self.max_power = self.opti.variable(
            init_guess=self.aircraft.mission_profile.TAKEOFF.power / 3,
            log_transform=True,
            upper_bound=self.aircraft.mission_profile.TAKEOFF.power / 2)
        self.power_available = self.thrust_level * self.max_power
        self.thrust = self.power_available * self.aircraft.propulsion_efficiency / self.dyn.speed

        dynamic_func()
        self.dyn.add_gravity_force()
        self.dyn.constrain_derivatives(self.opti, self.time, method='simpson')

        self.total_energy = np.sum(
            np.trapz(self.power_available) * np.diff(self.time))
        # self.opti.subject_to(
        #     self.total_energy <= self.aircraft.mission_profile.energy)

    def horizontal_constraints(self):
        self.end_time = self.opti.variable(init_guess=20, log_transform=True)
        self.time = np.linspace(0, self.end_time, self.n_timesteps)
        self.dyn = asb.DynamicsRigidBody2DBody(
            mass_props=asb.MassProperties(mass=self.aircraft.total_mass,
                                          Ixx=1000,
                                          Iyy=500,
                                          Izz=500),
            x_e=self.opti.variable(init_guess=np.linspace(
                0, 100, self.n_timesteps),
                                   lower_bound=0,
                                   upper_bound=self.aircraft.range),
            z_e=self.opti.variable(init_guess=-100,
                                   n_vars=self.n_timesteps,
                                   upper_bound=0),
            u_b=self.opti.variable(init_guess=self.aircraft.v_stall,
                                   n_vars=self.n_timesteps,
                                   lower_bound=0),
            w_b=self.opti.variable(init_guess=0,
                                   n_vars=self.n_timesteps,
                                   lower_bound=-50,
                                   upper_bound=50),
            theta=self.opti.variable(init_guess=0,
                                     n_vars=self.n_timesteps,
                                     lower_bound=-np.pi / 2,
                                     upper_bound=np.pi / 2),
            q=self.opti.variable(init_guess=0,
                                 n_vars=self.n_timesteps,
                                 lower_bound=-np.radians(5),
                                 upper_bound=np.radians(5)),
        )
        # self.gamma = np.arctan(self.dyn.w_b / self.dyn.u_b)
        # self.alpha = self.dyn.theta - self.gamma
        self.thrust_level = self.opti.variable(init_guess=0.5,
                                               n_vars=self.n_timesteps,
                                               log_transform=True,
                                               upper_bound=1)
        self.elevator_deflection = self.opti.variable(init_guess=-1,
                                                      n_vars=self.n_timesteps,
                                                      lower_bound=30,
                                                      upper_bound=30)
        self.parametric.wings[1].set_control_surface_deflections({
            'Elevator':
            self.elevator_deflection,
        })

        self.opti.subject_to([
            self.dyn.x_e[0] == 0,
            # np.diff(self.dyn.x_e) > 0,
            self.dyn.x_e[-1] == 100,
            # self.dyn.altitude[0] == 100,
            # self.dyn.altitude >= 90,
            # self.dyn.altitude[-1] == 100,
            self.dyn.altitude == 100,
            self.dyn.u_b[0] == self.aircraft.v_stall,
            self.dyn.u_b >= self.aircraft.v_stall,
            # self.dyn.w_b == 0,
            # self.dyn.speed >= self.dyn.speed[-1],
            # self.dyn.speed[-1] <= self.aircraft.v_stall,
            self.dyn.q[0] == 0,
            # self.dyn.theta[0] == 0,
            # self.dyn.alpha[0] == -9,
            self.thrust_level[0] == 0.5,
            self.thrust_level < 1,
        ])

        # pitchrate = self.dyn.state_derivatives()['gamma']
        # alpha_derivative = self.opti.derivative_of(self.dyn.alpha, self.time,
        #                                            .1)
        # thrust_derivative = self.opti.derivative_of(self.thrust_level,
        #                                             self.time, .1)

        self.opti.subject_to([
            #     pitchrate < .05,
            #     pitchrate > -.05,
            #     alpha_derivative < .5,
            #     alpha_derivative > -.5,
            #     # thrust_derivative < .001,
            #     # thrust_derivative > -.01,
            np.diff(self.thrust_level) < 0.01,
            np.diff(self.thrust_level) > -0.01,
            np.diff(self.elevator_deflection) < 0.1,
            np.diff(self.elevator_deflection) > -0.1,
        ])
        # self.opti.subject_to([
        #     # np.diff(self.dyn.speed) < 2,
        #     # np.diff(self.dyn.speed) > -2,
        #     # np.diff(self.dyn.alpha) < 1,
        #     # np.diff(self.dyn.alpha) > -1,
        #     np.diff(self.dyn.gamma) < .1,
        #     np.diff(self.dyn.gamma) > .1,
        # ])

    def horizontal_dynamics(self):
        aero = asb.AeroBuildup(
            airplane=self.parametric,
            op_point=self.dyn.op_point,
        ).run()
        self.CL = aero['CL']
        self.dyn.add_force(
            *aero['F_w'],
            axes='wind',
        )
        self.dyn.add_moment(
            *aero['M_w'],
            axes='wind',
        )

        self.dyn.add_force(
            Fx=self.thrust * np.cos(ALPHA_i),
            Fz=self.thrust * np.sin(ALPHA_i),
            axes='body',
        )

    def run(self, max_iter: int = 1000, verbose: bool = True):
        opt_param = {
            OptParam.TIME: self.time[-1],
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
        self.elevator_deflection = sol(self.elevator_deflection)
        self.thrust_level = sol(self.thrust_level)
        self.max_power = sol(self.max_power)
        self.power_available = sol(self.power_available)
        self.thrust = sol(self.thrust)
        self.total_energy = sol(self.total_energy)
        self.CL = sol(self.CL)
        print(f"\nOptimized for {self.opt_param.value}:")
        # print(f"Total energy: {self.total_energy / 3600000:.1f} kWh")
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
            # 'gamma':
            # self.dyn.gamma,
            'elevator deflection':
            self.elevator_deflection,
            'alpha':
            self.dyn.alpha,
            'C_L':
            self.CL,
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
    mission_profile_optimization = MissionProfileOptimization(
        ac, opt_param=OptParam.ENERGY, n_timesteps=33)
    mission_profile_optimization.run(max_iter=1000)

    df = mission_profile_optimization.to_dataframe()
    # print(df.to_string())
    # plot_step_density(df)
    plot_over_time(df)
    plot_over_distance(df)

    # aero = Aero(ac.parametric,
    #             velocity=ac.data.cruise_velocity,
    #             altitude=ac.data.cruise_altitude)
    # aero.plot_cl_cd_polars()
