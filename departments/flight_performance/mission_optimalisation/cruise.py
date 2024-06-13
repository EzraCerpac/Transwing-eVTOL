import aerosandbox as asb
import aerosandbox.numpy as np

from data.concept_parameters.aircraft import AC
from departments.aerodynamics.cl_cd_polars import CLCDPolar
from departments.flight_performance.mission_optimalisation.optimalisation import Optimalisation, OptParam
from departments.flight_performance.mission_optimalisation.power_required import power_from_thrust
from sizing_tools.formula.aero import C_D_from_CL

ALPHA_i = 0


class CruiseOpt(Optimalisation):

    def __init__(self, aircraft: AC, opt_param: OptParam, *args, **kwargs):
        aero = CLCDPolar(aircraft.parametric,
                         altitude=aircraft.data.cruise_altitude,
                         velocity=aircraft.data.cruise_velocity)
        self.c_l_over_alpha_func = lambda alpha: aero.c_l_over_alpha_func(alpha
                                                                          )
        super().__init__(aircraft, opt_param, *args, **kwargs)
        self.parametric = aircraft.parametric
        # self.aero = asb.AeroBuildup(
        #     airplane=self.parametric,
        #     op_point=asb.OperatingPoint(
        #         atmosphere=asb.Atmosphere(altitude=self.aircraft.cruise_altitude),
        #         velocity=self.aircraft.cruise_velocity,
        #         alpha=self.alpha,
        #     ),
        # ).run()

    def init(self):
        self.end_time = self.opti.variable(init_guess=2000, log_transform=True)

        self.dyn = asb.DynamicsPointMass2DSpeedGamma(
            mass_props=asb.MassProperties(mass=self.aircraft.total_mass,
                                          Ixx=1000,
                                          Iyy=500,
                                          Izz=500),
            x_e=self.opti.variable(init_guess=np.cosspace(
                0, self.aircraft.range, self.n_timesteps),
                lower_bound=0,
                upper_bound=self.aircraft.range),
            z_e=self.opti.variable(init_guess=np.linspace(
                0, -self.aircraft.cruise_altitude, self.n_timesteps),
                upper_bound=0),
            speed=self.opti.variable(init_guess=self.aircraft.cruise_velocity,
                                     n_vars=self.n_timesteps,
                                     log_transform=True),
            gamma=self.opti.variable(init_guess=0,
                                     n_vars=self.n_timesteps,
                                     lower_bound=-np.radians(15),
                                     upper_bound=np.radians(15)),
            alpha=self.opti.variable(init_guess=0,
                                     n_vars=self.n_timesteps,
                                     lower_bound=-10,
                                     upper_bound=20),
        )

        self.max_power = self.opti.parameter(350_000)
        self.thrust = self.opti.variable(init_guess=1000, n_vars=self.n_timesteps, log_transform=True)
        self.power = power_from_thrust(self.thrust, self.dyn.speed)
        self.thrust_level = self.max_power / self.power

        self.constraints()

        self.dynamics()
        self.dyn.add_gravity_force()
        self.dyn.constrain_derivatives(self.opti, self.time, method='simpson')

        self.total_energy = np.sum(np.trapz(self.power) * np.diff(self.time))
        # self.opti.subject_to(
        #     self.total_energy <= self.aircraft.mission_profile.energy)

    def constraints(self):
        # a = np.diff(self.dyn.speed) / np.diff(self.time)
        # self.a_x = a * np.cos(self.dyn.gamma[:-1])
        # self.a_z = a * np.sin(self.dyn.gamma[:-1])
        self.opti.subject_to([
            self.dyn.x_e[1] == 0,
            self.dyn.x_e[-1] == self.aircraft.range - 8000,
            np.diff(self.dyn.x_e) > 0,
            self.dyn.altitude[0] == 100,
            self.dyn.altitude >= 100,
            self.dyn.altitude[-1] == 100,
            self.dyn.speed[0] == 45,
            self.dyn.speed[:self.n_timesteps//2] >= self.dyn.speed[0],
            self.dyn.speed[self.n_timesteps//2:] >= self.dyn.speed[-1],
            self.dyn.speed[-1] <= 45,
            self.dyn.speed[-1] >= 40,
            self.dyn.gamma[0] == 0,
            self.dyn.gamma[-1] == 0,
            self.dyn.gamma < np.radians(15),
            self.dyn.gamma > np.radians(-15),
            self.thrust_level < 1,
        ])

        self.cruise_constraints()

        pitchrate = self.dyn.state_derivatives()['gamma']
        alpha_derivative = self.opti.derivative_of(self.dyn.alpha, self.time,
                                                   .1)
        thrust_derivative = self.opti.derivative_of(self.thrust_level,
                                                    self.time, .1)
        acceleration = self.dyn.state_derivatives()['speed']
        vertical_acceleration = np.diff(self.dyn.w_e) / np.diff(self.time)
        self.opti.subject_to([
            pitchrate < .05,
            pitchrate > -.05,
            alpha_derivative < .5,
            alpha_derivative > -.5,
            # thrust_derivative < .001,
            # thrust_derivative > -.01,
            np.diff(self.thrust_level) < 0.01,
            np.diff(self.thrust_level) > -0.01,
            acceleration < .1,
            acceleration > -.1,
            vertical_acceleration < .1,
            vertical_acceleration > -.1,
        ])
        self.opti.subject_to([
            # np.diff(self.dyn.speed) < 2,
            # np.diff(self.dyn.speed) > -2,
            # np.diff(self.dyn.alpha) < 1,
            # np.diff(self.dyn.alpha) > -1,
            np.diff(self.dyn.gamma) < .1,
            np.diff(self.dyn.gamma) > .1,
        ])

    def cruise_constraints(self):
        start_cruise_time = self.opti.variable(init_guess=300,
                                               log_transform=True)
        end_cruise_time = self.opti.variable(init_guess=1500,
                                             log_transform=True)
        self.opti.subject_to([
            start_cruise_time > 300,
            start_cruise_time < end_cruise_time - 0.4 * self.end_time,
            end_cruise_time < self.end_time - 300,
        ])
        cruise_steps = self.n_timesteps // 3
        start_cruise_index = self.n_timesteps // 3
        end_cruise_index = start_cruise_index + cruise_steps
        climb_time = np.cosspace(0, start_cruise_time, start_cruise_index)
        cruise_time = np.cosspace(start_cruise_time + .1, end_cruise_time - .1,
                                  cruise_steps)
        descent_time = np.cosspace(end_cruise_time, self.end_time,
                                   self.n_timesteps - end_cruise_index)
        self.time = np.concatenate([climb_time, cruise_time, descent_time])
        cruise_altitude = self.opti.variable(
            init_guess=self.aircraft.cruise_altitude, log_transform=True)
        cruise_speed = self.opti.parameter(self.aircraft.cruise_velocity)  # enforced because power-curve is probably not correct
        self.opti.subject_to([
            cruise_altitude >= self.aircraft.cruise_altitude,
            # cruise_speed >= self.aircraft.cruise_velocity,
            # cruise_speed <= self.aircraft.cruise_velocity,
        ])
        self.opti.subject_to([
            self.dyn.altitude[start_cruise_index:end_cruise_index] ==
            cruise_altitude,
            self.dyn.speed[start_cruise_index:end_cruise_index] ==
            cruise_speed,
            self.dyn.alpha[start_cruise_index:end_cruise_index] ==
            self.dyn.alpha[end_cruise_index],
            self.dyn.gamma[start_cruise_index:end_cruise_index] ==
            self.dyn.gamma[end_cruise_index],
            self.thrust_level[start_cruise_index:end_cruise_index] ==
            self.thrust_level[end_cruise_index],
        ])
        self.opti.subject_to([
            self.dyn.altitude <= cruise_altitude,
            self.dyn.speed <= cruise_speed,
            # self.dyn.op_point.energy_altitude() <= self.dyn.op_point[start_cruise_index].energy_altitude(),
            np.diff(self.dyn.altitude[:start_cruise_index]) > 0,
            np.diff(self.dyn.altitude[end_cruise_index:]) < 0,
            np.diff(self.dyn.speed[:start_cruise_index]) > 0,
            np.diff(self.dyn.speed[end_cruise_index:]) < 0,
            np.diff(self.power[end_cruise_index:]) < 0,
            # self.power[end_cruise_index:] == 0,
        ])

    def dynamics(self, use_aero: bool = False):
        if use_aero:
            aero = asb.AeroBuildup(
                airplane=self.parametric,
                op_point=self.dyn.op_point,
            ).run()
            self.CL = aero['CL']
            self.dyn.add_force(
                *aero['F_w'],
                axes='wind',
            )
        else:
            self.CL = np.array([
                self.c_l_over_alpha_func(alpha) for alpha in self.dyn.alpha.nz
            ])
            # self.CL = 3 * np.sind(2 * self.dyn.alpha)
            CD = C_D_from_CL(self.CL, self.aircraft.estimated_CD0,
                             self.aircraft.wing.aspect_ratio,
                             self.aircraft.wing.oswald_efficiency_factor)
            lift = self.dyn.op_point.dynamic_pressure(
            ) * self.aircraft.wing.area * self.CL
            drag = self.dyn.op_point.dynamic_pressure(
            ) * self.aircraft.wing.area * CD
            self.dyn.add_force(
                Fx=-drag,
                Fz=-lift,
                axes='wind',
            )

        self.dyn.add_force(
            Fx=self.thrust * np.cos(ALPHA_i),
            Fz=self.thrust * np.sin(ALPHA_i),
            axes='body',
        )


if __name__ == '__main__':
    from aircraft_models import rot_wing
    ac = rot_wing
    # ac.data.v_stall = 20.
    mission_profile_optimization = CruiseOpt(ac,
                                             opt_param=OptParam.ENERGY,
                                             n_timesteps=80,
                                             max_iter=1000)
    mission_profile_optimization.run()

    # df = mission_profile_optimization.to_dataframe()
    # print(df.to_string())

    # mission_profile_optimization.plot_logs_over_time()
    mission_profile_optimization.plot_over_time()
    mission_profile_optimization.plot_over_distance()

    # aero = CLCDPolar(ac.parametric,
         #             velocity=ac.data.cruise_velocity,
    #             altitude=ac.data.cruise_altitude)
    # aero.plot_cl_cd_polars()
