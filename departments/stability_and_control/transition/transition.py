import aerosandbox as asb
import aerosandbox.numpy as np
from scipy.constants import g

from data.concept_parameters.aircraft import AC
from departments.flight_performance.mission_optimalisation.optimalisation import Optimalisation, OptParam
from aircraft_models import trans_wing

ALPHA_i = 0


# E423
class TransitionOpt(Optimalisation):

    def __init__(self, aircraft: AC, opt_param: OptParam, *args, **kwargs):
        super().__init__(aircraft, opt_param, *args, **kwargs)

    def init(self):
        self.end_time = self.opti.variable(init_guess=2000, log_transform=True)

        self.constraints()

        # self.max_power = self.opti.variable(
        #     init_guess=self.aircraft.mission_profile.TAKEOFF.power / 2,
        #     log_transform=True,
        #     upper_bound=self.aircraft.mission_profile.TAKEOFF.power)

        self.dynamics()
        self.dyn.add_gravity_force()
        self.dyn.constrain_derivatives(self.opti, self.time, method='simpson')

        self.total_energy = np.sum(
            np.trapz(self.power_available) * np.diff(self.time))
        # self.opti.subject_to(
        #     self.total_energy <= self.aircraft.mission_profile.energy)

    def constraints(self):
        self.end_time = 60# self.opti.variable(init_guess=20, log_transform=True)
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
        self.transval = np.linspace(1, 0, self.n_timesteps)


        self.opti.subject_to([
            self.dyn.x_e[0] == 0,
            # np.diff(self.dyn.x_e) > 0,
            # self.dyn.x_e[-1] == 100,
            # self.dyn.altitude[0] == 100,
            # self.dyn.altitude >= 90,
            # self.dyn.altitude[-1] == 100,
            self.dyn.altitude == 100,
            self.dyn.u_b[0] == 0,
            self.dyn.u_b >= 0,
            # self.dyn.w_b == 0,
            # self.dyn.speed >= self.dyn.speed[-1],
            # self.dyn.speed[-1] <= self.aircraft.v_stall,
            # self.dyn.q[0] == 0,
            # self.dyn.theta[0] == 0,
            # self.dyn.alpha[0] == -9,
            # self.thrust_level[0] == 0.5,
            # self.thrust_level < 1,
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
            # np.diff(self.thrust_level) < 0.01,
            # np.diff(self.thrust_level) > -0.01,
            # np.diff(self.elevator_deflection) < 0.1,
            # np.diff(self.elevator_deflection) > -0.1,
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
        aero = [asb.AeroBuildup(
            airplane=self.parametric_fn(trans_val),
            op_point=self.dyn.op_point,
        ).run() for trans_val in self.transval]
        aero = {k: np.concatenate([a[k] for a in aero])
                for k in aero[0].keys()}

        self.CL = aero['CL']
        self.dyn.add_force(
            *aero['F_w'],
            axes='wind',
        )
        self.dyn.add_moment(
            *aero['M_w'],
            axes='wind',
        )

        self.thrust_per_engine = self.opti.variable(
            init_guess=self.aircraft.total_mass * g / self.parametric.propulsors,
            n_vars=(self.n_timesteps, self.parametric.propulsors),
            log_transform=True,
            lower_bound=0,
        )
        self.thrust = np.sum(self.thrust_per_engine, axis=1)

        for i, propulsor in enumerate(self.parametric.propulsors):
            thrust = self.thrust_per_engine[:, i]
            self.dyn.add_force(
                Fx=thrust * propulsor.xyz_normal[0],
                Fz=thrust * propulsor.xyz_normal[2],
                axes='body',
            )
            self.dyn.add_moment(
                My=thrust *
                   np.cross(propulsor.xyz_normal, propulsor.xyz_c)[1],
                axes='body',
            )


if __name__ == '__main__':
    from departments.flight_performance.mission_optimalisation.plots import *

    ac = trans_wing
    ac.data.v_stall = 20.
    mission_profile_optimization = TransitionOpt(ac,
                                                 opt_param=OptParam.ENERGY,
                                                 n_timesteps=20,
                                                 max_iter=30)
    mission_profile_optimization.run()

    df = mission_profile_optimization.to_dataframe()
    # print(df.to_string())
    mission_profile_optimization.plot_over_distance()
    mission_profile_optimization.plot_logs_over_distance()

    # aero = Aero(ac.parametric,
    #             velocity=ac.data.cruise_velocity,
    #             altitude=ac.data.cruise_altitude)
    # aero.plot_cl_cd_polars()
