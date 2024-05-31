import aerosandbox as asb
import aerosandbox.numpy as np
import pandas as pd

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.formula.aero import C_D_from_CL
from sizing_tools.model import Model

ALPHA_i = 0


class MissionProfileOptimization(Model):

    def __init__(self, aircraft: Aircraft, n_timesteps=500):
        super().__init__(aircraft)
        self.opti = asb.Opti()
        self.n_timesteps = n_timesteps
        self.init_horizontal_config()

    @property
    def necessary_parameters(self):
        return [
            'cruise_altitude',
            'range',
            # 'tbd'
        ]

    def init_horizontal_config(self):
        self.time = self.opti.variable(
            init_guess=np.linspace(0, 100, self.n_timesteps))
        self.opti.subject_to([
            self.time[0] == 0,
            np.diff(self.time) > 0,
        ])

        self.dyn = asb.DynamicsPointMass2DSpeedGamma(
            mass_props=asb.MassProperties(mass=self.aircraft.total_mass,
                                          Ixx=1000,
                                          Iyy=500,
                                          Izz=500),
            x_e=np.cosspace(0, self.aircraft.range, self.n_timesteps),
            z_e=self.opti.variable(init_guess=np.linspace(
                0, -self.aircraft.cruise_altitude, self.n_timesteps)),
            speed=self.opti.variable(init_guess=self.aircraft.cruise_velocity,
                                     n_vars=self.n_timesteps),
            gamma=self.opti.variable(init_guess=0,
                                     n_vars=self.n_timesteps,
                                     lower_bound=-np.pi / 2,
                                     upper_bound=np.pi / 2),
            alpha=self.opti.variable(init_guess=0,
                                     n_vars=self.n_timesteps,
                                     lower_bound=-30,
                                     upper_bound=60),
        )
        self.opti.subject_to([
            self.dyn.altitude[0] == 50,
            self.dyn.altitude >= 50,
            self.dyn.altitude[-1] == 50,
            self.dyn.speed[0] == self.aircraft.v_stall,
            self.dyn.speed[-1] == self.aircraft.v_stall,
            self.dyn.gamma[0] == 0,
            self.dyn.gamma[-1] == 0,
        ])
        start_cruise_distance = 0.1 * self.aircraft.range
        end_cruise_distance = 0.9 * self.aircraft.range
        start_cruise_index = np.argmin(
            np.abs(self.dyn.x_e - start_cruise_distance))
        end_cruise_index = np.argmin(np.abs(self.dyn.x_e -
                                            end_cruise_distance))
        cruise_altitude = self.opti.variable(
            init_guess=self.aircraft.cruise_altitude, log_transform=True)
        cruise_velocity = self.opti.variable(
            init_guess=self.aircraft.cruise_velocity, log_transform=True)
        self.opti.subject_to([
            self.dyn.altitude[start_cruise_index] == cruise_altitude,
            self.dyn.altitude[end_cruise_index] == cruise_altitude,
            self.dyn.speed[start_cruise_index] == cruise_velocity,
            self.dyn.speed[end_cruise_index] == cruise_velocity,
            np.diff(self.dyn.speed[start_cruise_index:end_cruise_index]) /
            np.diff(self.time[start_cruise_index:end_cruise_index]) == 0,
            self.dyn.gamma[start_cruise_index:end_cruise_index] == 0,
            self.dyn.altitude <= cruise_altitude,
            self.dyn.speed <= cruise_velocity,
        ])

        pitch_rate = np.diff(np.degrees(self.dyn.gamma)) / np.diff(self.time)
        self.opti.subject_to([
            pitch_rate < 2,
            pitch_rate > -2,
        ])

        CL = 3 * np.sind(2 * self.dyn.alpha)
        CD = C_D_from_CL(CL, self.aircraft.estimated_CD0,
                         self.aircraft.wing.aspect_ratio,
                         self.aircraft.wing.oswald_efficiency_factor)

        lift = self.dyn.op_point.dynamic_pressure(
        ) * self.aircraft.wing.area * CL
        drag = self.dyn.op_point.dynamic_pressure(
        ) * self.aircraft.wing.area * CD

        self.thrust_level = self.opti.variable(init_guess=0.5,
                                               n_vars=self.n_timesteps,
                                               lower_bound=0,
                                               upper_bound=1)
        self.max_power = self.opti.variable(
            init_guess=self.aircraft.mission_profile.TAKEOFF.power,
            log_transform=True,
            upper_bound=self.aircraft.mission_profile.TAKEOFF.power)
        self.power_available = self.thrust_level * self.max_power
        self.thrust = self.power_available / self.dyn.speed * self.aircraft.propulsion_efficiency
        # self.opti.subject_to([
        #     self.thrust[:-1] * np.cos(ALPHA_i) - drag[:-1] - self.dyn.mass_props.mass * g * np.sin(self.dyn.gamma[:-1]) == \
        #     self.dyn.mass_props.mass * np.diff(self.dyn.speed) / np.diff(self.time),
        #     self.thrust[:-1] * np.sin(ALPHA_i) + lift[:-1] - self.dyn.mass_props.mass * g * np.cos(self.dyn.gamma[:-1]) == \
        #     self.dyn.mass_props.mass * self.dyn.speed[:-1] * np.diff(self.dyn.gamma) / np.diff(self.time),
        # ])

        self.dyn.add_force(
            Fx=-drag,
            Fz=-lift,
            axes='wind',
        )
        self.dyn.add_gravity_force()
        self.dyn.add_force(
            Fx=self.thrust * np.cos(ALPHA_i),
            Fz=self.thrust * np.sin(ALPHA_i),
            axes='wind',
        )
        self.dyn.constrain_derivatives(self.opti, self.time)

        self.power_required = drag * self.dyn.speed
        self.total_energy = np.sum(
            np.trapz(self.power_available) * np.diff(self.time))
        self.opti.subject_to(
            self.total_energy <= self.aircraft.mission_profile.energy)

    def run(self, verbose=True):
        # Optimize
        self.opti.minimize(self.time[-1])

        # Post-process
        try:
            sol = self.opti.solve(verbose=verbose)
            self.time = sol(self.time)
            self.dyn = sol(self.dyn)
            self.thrust_level = sol(self.thrust_level)
            self.max_power = sol(self.max_power)
            self.power_available = sol(self.power_available)
            self.thrust = sol(self.thrust)
            self.power_required = sol(self.power_required)
            self.total_energy = sol(self.total_energy)
        except Exception as e:
            print(e)
            self.time = self.opti.debug.value(self.time)
            self.dyn.x_e = self.opti.debug.value(self.dyn.x_e)
            self.dyn.z_e = self.opti.debug.value(self.dyn.z_e)
            self.dyn.speed = self.opti.debug.value(self.dyn.speed)
            self.dyn.gamma = self.opti.debug.value(self.dyn.gamma)
            self.dyn.alpha = self.opti.debug.value(self.dyn.alpha)
            self.thrust_level = self.opti.debug.value(self.thrust_level)
            self.max_power = self.opti.debug.value(self.max_power)
            self.power_available = self.opti.debug.value(self.power_available)
            self.thrust = self.opti.debug.value(self.thrust)
            self.power_required = self.opti.debug.value(self.power_required)
            self.total_energy = self.opti.debug.value(self.total_energy)
        print(f"Total energy: {self.total_energy / 3600000:.1f} kWh")
        print(f"Max power: {self.max_power / 1000:.1f} kW")

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame({
            'time': self.time,
            'x': self.dyn.x_e,
            'z': self.dyn.z_e,
            'speed': self.dyn.speed,
            'gamma': self.dyn.gamma,
            'alpha': self.dyn.alpha,
        })


if __name__ == '__main__':
    from departments.flight_performance.plots import *

    ac = Aircraft.load()
    mission_profile_optimization = MissionProfileOptimization(ac,
                                                              n_timesteps=50)
    mission_profile_optimization.run()

    df = mission_profile_optimization.to_dataframe()
    # print(df.to_string())
    # plot_per_phase(df)
    # plot_dynamic(mission_profile_optimization.dyn)
    plot_over_distance(df)
