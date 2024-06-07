import aerosandbox as asb
import aerosandbox.numpy as np

from data.concept_parameters.aircraft import AC
from departments.flight_performance.mission_optimalisation.optimalisation import Optimalisation, OptParam
from aircraft_models import rot_wing

ALPHA_i = 0


# E423
class TransitionOpt(Optimalisation):

    def __init__(self, aircraft: AC, opt_param: OptParam, *args, **kwargs):
        super().__init__(aircraft, opt_param, *args, **kwargs)

    def init(self):
        self.end_time = self.opti.variable(init_guess=2000, log_transform=True)

        self.constraints()

        self.max_power = self.opti.variable(
            init_guess=self.aircraft.mission_profile.TAKEOFF.power / 3,
            log_transform=True,
            upper_bound=self.aircraft.mission_profile.TAKEOFF.power / 2)
        self.power_available = self.thrust_level * self.max_power
        self.thrust = self.power_available * self.aircraft.propulsion_efficiency / self.dyn.speed

        self.dynamics()
        self.dyn.add_gravity_force()
        self.dyn.constrain_derivatives(self.opti, self.time, method='simpson')

        self.total_energy = np.sum(
            np.trapz(self.power_available) * np.diff(self.time))
        # self.opti.subject_to(
        #     self.total_energy <= self.aircraft.mission_profile.energy)

    def constraints(self):
        self.end_time = self.opti.variable(init_guess=20, log_transform=True)
        self.time = np.linspace(0, self.end_time, self.n_timesteps)
        self.dyn = asb.DynamicsRigidBody2DBody(
            mass_props=asb.mass_properties_from_radius_of_gyration(
                self.aircraft.total_mass,
                radius_of_gyration_x=1,
                radius_of_gyration_y=5,
                radius_of_gyration_z=1),
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
            np.diff(self.dyn.x_e) > 0,
            # self.dyn.x_e[-1] == 100,
            # self.end_time == 100,
            self.dyn.altitude[0] == 100,
            self.dyn.altitude >= 0,
            self.dyn.altitude[-1] == 0,
            # self.dyn.altitude == 100,
            self.dyn.u_b[0] == self.aircraft.cruise_velocity,
            self.dyn.u_b >= self.aircraft.v_stall,
            # self.dyn.w_b == 0,
            # self.dyn.speed >= self.dyn.speed[-1],
            # self.dyn.speed[-1] <= self.aircraft.v_stall,
            self.dyn.q[0] == 0,
            # self.dyn.theta[0] - self.dyn.alpha[0] == 0,
            self.dyn.theta[0] == 0,
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

    def dynamics(self):
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

        thrust_per_engine = self.thrust / len(self.parametric.propulsors)
        for propulsor in self.parametric.propulsors:
            self.dyn.add_force(
                Fx=thrust_per_engine * propulsor.xyz_normal[0],
                Fz=thrust_per_engine * propulsor.xyz_normal[2],
                axes='body',
            )
            self.dyn.add_moment(
                My=thrust_per_engine *
                np.cross(propulsor.xyz_normal, propulsor.xyz_c)[1],
                axes='body',
            )


if __name__ == '__main__':
    from departments.flight_performance.mission_optimalisation.plots import *

    ac = rot_wing
    ac.data.v_stall = 20.
    mission_profile_optimization = TransitionOpt(
        ac, opt_param=OptParam.MAX_DISTANCE, n_timesteps=20, max_iter=1000)
    mission_profile_optimization.run()

    # df = mission_profile_optimization.to_dataframe()
    # print(df.to_string())

    mission_profile_optimization.plot_logs_over_distance()
    mission_profile_optimization.plot_logs_over_time()
    mission_profile_optimization.plot_over_distance()
    # mission_profile_optimization.plot_over_time()
    mission_profile_optimization.dyn.draw(vehicle_model=ac.parametric,
                                          scale_vehicle_model=5)

    # aero = Aero(ac.parametric,
    #             velocity=ac.data.cruise_velocity,
    #             altitude=ac.data.cruise_altitude)
    # aero.plot_cl_cd_polars()
