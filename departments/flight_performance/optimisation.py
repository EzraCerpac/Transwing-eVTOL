import aerosandbox as asb
import aerosandbox.numpy as np
import matplotlib.pyplot as plt
from aerosandbox.weights.mass_properties_of_shapes import mass_properties_from_radius_of_gyration

from data.concept_parameters.aircraft import AC
from model.airplane_models.cessna152 import cessna
from model.airplane_models.rotating_wing import rot_wing
from utility.plotting import show


class TrajectoryOptimisation:
    def __init__(self, aircraft: AC):
        self.aircraft_data = aircraft.data
        self.airplane = aircraft.parametric
        self.time_final_guess = 100
        self.time = None
        self.dynamic_point = None

    @property
    def mass_props(self) -> asb.MassProperties:
        props = mass_properties_from_radius_of_gyration(
            mass=self.aircraft_data.total_mass,
            radius_of_gyration_x=2,
            radius_of_gyration_y=3,
            radius_of_gyration_z=3,
        )
        props.x_cg = 1
        return props

    def optimise_distance_maximising_glide(self) -> any:
        opti = asb.Opti()

        self.time = np.cosspace(
            0,
            opti.variable(init_guess=self.time_final_guess, log_transform=True),
            100
        )
        N = np.length(self.time)

        time_guess = np.linspace(0, self.time_final_guess, N)

        ### Create a dynamics instance
        init_state = {
            "x_e": 0,
            "z_e": -self.aircraft_data.cruise_altitude,
            "speed": self.aircraft_data.cruise_velocity,
            "gamma": 0,
        }

        self.dynamic_point = asb.DynamicsPointMass2DSpeedGamma(
            mass_props=self.mass_props,
            x_e=opti.variable(init_state["speed"] * time_guess),
            z_e=opti.variable(np.linspace(init_state["z_e"], 0, N)),
            speed=opti.variable(init_guess=init_state["speed"], n_vars=N),
            gamma=opti.variable(init_guess=0, n_vars=N, lower_bound=-np.pi / 2, upper_bound=np.pi / 2),
            alpha=opti.variable(init_guess=5, n_vars=N, lower_bound=-5, upper_bound=15),
        )
        # Constrain the initial state
        for k in self.dynamic_point.state.keys():
            opti.subject_to(
                self.dynamic_point.state[k][0] == init_state[k]
            )

        ### Add in forces
        self.dynamic_point.add_gravity_force()

        aero = asb.AeroBuildup(
            airplane=self.airplane,
            op_point=self.dynamic_point.op_point
        ).run()

        self.dynamic_point.add_force(
            *aero["F_w"],
            axes="wind"
        )

        ### Constrain the altitude to be above ground at all times
        opti.subject_to(
            self.dynamic_point.altitude > 0
        )

        ### Finalize the problem
        self.dynamic_point.constrain_derivatives(opti, self.time)  # Apply the dynamics constraints created up to this point

        opti.minimize(-self.dynamic_point.x_e[-1])  # Go as far downrange as you can

        ### Solve it
        self.sol = opti.solve()

        ### Substitute the optimization variables in the dynamics instance with their solved values (in-place)
        self.dynamic_point = self.sol(self.dynamic_point)
        return self.dynamic_point

    def plot_3D(self):
        if self.dynamic_point is None:
            self.optimise_distance_maximising_glide()
        plotter = self.dynamic_point.draw(
            vehicle_model=self.airplane,
            show=False
        )
        plotter.camera.enable_parallel_projection()
        plotter.camera_position = 'xz'
        plotter.camera.roll = 180
        plotter.camera.azimuth = 180
        plotter.show()

    @show
    def plot_vars_over_time(self) -> tuple[plt.Figure, plt.Axes]:
        from matplotlib import pyplot as plt
        if self.dynamic_point is None:
            self.optimise_distance_maximising_glide()
        fig, ax = plt.subplots(2, 2, figsize=(8, 6))
        plt.sca(ax[0, 0])
        plt.plot(self.dynamic_point.x_e, self.dynamic_point.altitude)
        plt.xlabel("Range [m]")
        plt.ylabel("Altitude [m]")

        plt.sca(ax[0, 1])
        plt.plot(self.sol(self.time), self.dynamic_point.speed)
        plt.xlabel("Time [sec]")
        plt.ylabel("Speed (True) [m/s]")

        plt.sca(ax[1, 0])
        plt.plot(self.sol(self.time), self.dynamic_point.alpha)
        plt.xlabel("Time [sec]")
        plt.ylabel("Angle of Attack [deg]")

        plt.sca(ax[1, 1])
        plt.plot(self.sol(self.time), np.degrees(self.dynamic_point.gamma))
        plt.xlabel("Time [sec]")
        plt.ylabel("Flight Path Angle [deg]")

        return fig, ax


if __name__ == '__main__':
    opt = TrajectoryOptimisation(aircraft=rot_wing)
    opt.plot_vars_over_time()
